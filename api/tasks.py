"""Task file."""
from celery import Celery, signals
from configparser import ConfigParser
from datetime import datetime

# load parsers
from parsers.smartthings import Smartthings
from parsers.alexa import Alexa
from parsers.packet import Packet

from parsers.onhub import Onhub

# load model mapping with service parsers
import parsers.smartthings.models as smartmodels
import parsers.alexa.models as alexamodels

# load packet model for image parsers
import parsers.onhub.models as onhubmodels
import parsers.packet.models as packetmodels

from parsers.log import log
from util.dbsession import session

import json


conf = ConfigParser()
conf.read('config.ini')

REDIS_URL = 'redis://{}:{}/{}'.format(
    conf['redis']['host'], conf['redis']['port'], conf['redis']['db'])

app = Celery(
    'tasks',
    broker=REDIS_URL, backend=REDIS_URL)

logger = log()

logger.info("Starting Celery tasks - backend: {}".format(REDIS_URL))


@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    """Disable celery default logging."""
    pass


def get_packet(path):
    """Get packet information from tcpdump file."""
    logger.debug("Get packet information from {}".format(path))
    packet = Packet(path)

    session.add_all(packet.packets)
    session.commit()

    del packet


def get_onhub(path):
    """Get Onhub information from diagnostic report file."""
    logger.debug("Get Onhub diagnostic report from {}".format(path))
    onhub = Onhub(path)

    session.add_all(onhub.stations)
    session.add_all(onhub.commands)
    session.add_all(onhub.settings)

    session.commit()

    del onhub


def get_smartthings(access_token):
    """Get smartthings report."""
    logger.debug("Get smartthings cloud service by access_token")
    things = Smartthings(access_token)
    locations = things.get_locations()

    for location in locations:
        locateinfo = things.get_location_info(location['id'])
        try:
            session.add(smartmodels.Location(
                locateinfo['id'], locateinfo['name'], locateinfo['temperature_scale'],
                locateinfo['time_zone'], locateinfo['coordinates']
            ))

            if locateinfo['hubs']:
                hubinfo = things.get_hub_info(locateinfo['hubs']['id'], locateinfo['id'])
                session.add(smartmodels.Hub(
                    hubinfo['id'], hubinfo['name'], hubinfo['last_serverping'],
                    hubinfo['last_hubping'], hubinfo['create_date'], hubinfo['last_update'],
                    hubinfo['last_booted'], hubinfo['ip_address'], hubinfo['mac_address']
                ))

                for device in hubinfo['devices']:
                    deviceinfo = things.get_device_info(device['id'], locateinfo['id'])
                    session.add(smartmodels.Device(
                        device['id'], deviceinfo['name'], deviceinfo['label'], deviceinfo['type'],
                        deviceinfo['create_date'], deviceinfo['last_update'], deviceinfo['version'],
                        deviceinfo['zigbee_id'], deviceinfo['network_id']
                    ))

                    for event in things.get_device_events(device['id'], locateinfo['id']):
                        session.add(smartmodels.Event(
                            event['date'], event['type'], event['value'], event['displayed_text']
                        ))
        except:
            logger.error(
                "Error while parsing device information from {} location id".format(location['id']),
                exc_info=True)

    session.commit()
    del things


def get_alexa():
    """Collect alexa report."""
    logger.debug("Get alexa cloud service by activating chromedriver")
    alexa = Alexa()

    if alexa.isLogined:
        scan_count = 200

        try:
            # listup all activities
            for i in range(1, scan_count, 50):
                data = alexa.get_data('https://alexa.amazon.com/api/activities?startTime=&size=50&offset={}'.format(i))
                for activity in data['activities']:
                    try:
                        description = json.loads(activity['description'])
                        summary = description['summary']
                    except:
                        summary = ''

                    session.add(alexamodels.History(
                        activity['id'],
                        datetime.utcfromtimestamp(activity['creationTimestamp'] / 1e3),
                        activity['activityStatus'],
                        activity['domainAttributes'],
                        summary,
                        "https://alexa.amazon.com/api/utterance/audio/data?id={}".format(activity['utteranceId'])
                    ))

            # smart homes
            details = alexa.get_data("https://alexa.amazon.com/api/phoenix")['networkDetail']
            locations = json.loads(details)['locationDetails']['locationDetails']

            for location in locations.keys():
                for service in locations[location]['amazonBridgeDetails']['amazonBridgeDetails'].keys():
                    data = locations[location]['amazonBridgeDetails']['amazonBridgeDetails'][service]
                    for app in data['applianceDetails']['applianceDetails'].keys():
                        appdata = data['applianceDetails']['applianceDetails'][app]
                        report = {
                            'manufacturer': appdata['manufacturerName'],
                            'description': appdata['friendlyDescription'],
                            'friendlyName': appdata['friendlyName'],
                            'applianceTypes': appdata['applianceTypes']
                        }
                        session.add(alexamodels.Setting(
                            'SMARTHOME',
                            json.dumps(report)
                        ))

            # devices
            devices = alexa.get_data("https://alexa.amazon.com/api/device-preferences")['devicePreferences']
            for device in devices:
                report = {
                    'serialNumber': device['deviceSerialNumber'],
                    'type': device['deviceType'],
                    'locale': device['locale'],
                    'postal': device['postalCode'],
                    'customerId': device['searchCustomerId'],
                    'timezone': device['timeZoneId'],
                    'region': device['timeZoneRegion']
                }

                module = alexa.get_data(
                    "https://alexa.amazon.com/api/device-wifi-details?deviceSerialNumber={}&deviceType={}".format(
                        report['serialNumber'], report['type']))

                try:
                    report['macAddress'] = module['macAddress']
                except:
                    report['macAddress'] = ''

                session.add(alexamodels.Setting(
                    'DEVICE',
                    json.dumps(report)
                ))

            # wifi config
            wifis = alexa.get_data("https://alexa.amazon.com/api/wifi/configs")['values']
            for wifi in wifis:
                session.add(alexamodels.Setting(
                    'WIFI',
                    json.dumps(wifi)
                ))

            # bluetooth
            bluetooths = alexa.get_data("https://alexa.amazon.com/api/bluetooth")['bluetoothStates']
            for bluetooth in bluetooths:
                report = {
                    'serialNumber': bluetooth['deviceSerialNumber'],
                    'deviceType': bluetooth['deviceType'],

                }

            # accounts
            accounts = alexa.get_data("https://alexa.amazon.com/api/household")['accounts']
            for account in accounts:
                report = {
                    'email': account['email'],
                    'fullname': account['fullName'],
                    'id': account['id'],
                    'role': account['role']
                }
                session.add(alexamodels.Setting(
                    'ACCOUNT',
                    json.dumps(report)
                ))

            session.commit()
        except:
            logger.error("Exception while handling alexa parser", exc_info=True)

    alexa.driver.quit()

    del alexa


@app.task(bind=True)
def cloud_service(self, service, access_token=None, username=None,
                  password=None):
    """Cloud level forensic using account information."""
    logger.debug("Cloud level {} service analysis".format(service))
    self.update_state(state='processing')
    if service == "alexa":
        get_alexa()
        return True

    elif service == "smartthings":
        get_smartthings(access_token)
        return True

    else:
        return False


@app.task(bind=True)
def image_file(self, image_type, filepath):
    """Image file level forensic."""
    logger.debug("Image level {} file {} analysis".format(image_type, filepath))
    self.update_state(state='processing')
    if image_type == "packet":
        get_packet(filepath)
        return True
    elif image_type == "onhub":
        get_onhub(filepath)
        return True
    else:
        return False
