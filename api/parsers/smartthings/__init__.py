"""Smartthings api parser module."""
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone, utc

from parsers.log import log

import requests
import os


class Smartthings(object):
    """Smartthings API."""

    def __init__(self, access_token):
        """Construct Smartthings API."""
        self._log = log()

        self.access_token = access_token
        self.timezones = {}

        self.isLogined = False
        self.check_login()

    def get_source(self, url):
        """Get HTML source."""
        self._log.debug("Smartthings API: {}".format(url))
        return requests.get(url, params={
            'access_token': self.access_token
        }).text

    def html_mapping(self, source):
        """Beautifulsoup HTML parser."""
        return BeautifulSoup(source, 'html.parser')

    def strip_text(self, text):
        """Strip text and replace unusual values."""
        return text.strip().replace('\n', ' ').replace('\t', '')

    def check_login(self):
        """Check to login samsung smartthings server."""
        self._log.info("Checking access token validation")
        if "Welcome" in self.get_source('https://graph.api.smartthings.com/'):
            self._log.info("Validation check successful")
            self.isLogined = True
        else:
            self._log.error("Invalid access token. Please check your access token")

    def extract_name(self, value):
        """Extract name from html element."""
        return self.strip_text(
            value.find(attrs={'class': 'property-value'}).text)

    def extract_id(self, link):
        """Extract ID from href link."""
        return os.path.basename(link)

    def naming_key(self, key):
        """Naming key in dictionary."""
        if '(' in key:
            key = key.split('(')[0].strip()

        return self.strip_text(key.lower().replace(' ', '_'))

    def normalize_linked_options(self, options):
        """Normalize linked option in value."""
        if options:
            return [
                {'name': option.text, 'id': self.extract_id(
                    option.a['href'].replace('/show', ''))}
                for option in options
            ]
        else:
            return None

    def normalize_time(self, value, location_id):
        try:
            if "AM" in value or "PM" in value:
                if "UTC" not in value:
                    # convert value as location_id timezone
                    value = value.split('M')[0] + "M"
                    value = datetime.strptime(value, '%Y-%m-%d %I:%M %p')
                    return self.timezones[location_id].localize(value).astimezone(utc)

            return datetime.strptime(value, '%Y-%m-%d %I:%M %p %Z')
        except:
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')

    def get_locations(self):
        """Get list of locations."""
        self._log.info("Parsing account registered locations")
        locations = []
        source = self.get_source(
            'https://graph.api.smartthings.com/location/list')
        soup = self.html_mapping(source)

        for location in soup.find_all('tr')[1:]:
            info = location.find('a')
            locations.append({
                'id': os.path.basename(info['href']),
                'name': info.text.strip()
            })

        return locations

    def get_location_info(self, id):
        """Get specific information mapping with location id."""
        self._log.info("Parsing location information by id - {}".format(id))
        location = {'id': id}
        source = self.get_source(
            'https://graph-na04-useast2.api.smartthings.com/location/show/{}'.format(id))
        soup = self.html_mapping(source)
        rows = soup.find_all('tr', class_='fieldcontain')

        location['name'] = rows[0].td.text.strip()

        for row in rows[1:-6]:
            key = row.find(class_='property-label').text
            value = row.find_all(attrs={
                'aria-labelledby': lambda x: x and x.endswith('-label') and x != 'property-label'})

            # if value is not null
            if value:
                # if linked option
                if len(value) > 1:
                    value = self.normalize_linked_options(value)
                else:
                    if value[0].a:
                        value = {
                            'name': value[0].text.strip(),
                            'id': self.extract_id(value[0].a['href'])
                        }
                    else:
                        value = value[0].text.strip()
            else:
                value = None

            location[self.naming_key(key)] = value

        # set timezone to convert datetime zone
        self.timezones[id] = timezone(location['time_zone'])

        return location

    def get_hub_info(self, id, location_id):
        """Get hub information."""
        self._log.info("Parsing hub information by id - {}".format(id))
        source = self.get_source(
            'https://graph-na04-useast2.api.smartthings.com/hub/show/{}'.format(id))
        soup = self.html_mapping(source)

        hub, devices = soup.find_all('div', attrs={'class': 'table-wrap'})

        name, hub_id, status, firmware_version, hardware_version,\
            location, last_serverping, last_hubping,\
            create_date, last_update, ip_address, mac_address,\
            last_booted, battery, settings, zigbee, zwave = hub.find_all('tr')[:-2]

        data = {
            'name': self.extract_name(name),
            'id': self.extract_name(hub_id),
            'status': self.extract_name(status),
            'firmware_version': self.extract_name(firmware_version),
            'hardware_version': self.extract_name(hardware_version),
            'location': self.extract_name(location),
            'last_serverping': self.normalize_time(self.extract_name(last_serverping), location_id),
            'last_hubping': self.normalize_time(self.extract_name(last_hubping), location_id),
            'create_date': self.normalize_time(self.extract_name(create_date), location_id),
            'last_update': self.normalize_time(self.extract_name(last_update), location_id),
            'ip_address': self.extract_name(ip_address),
            'mac_address': self.extract_name(mac_address),
            'last_booted': self.normalize_time(self.extract_name(last_booted), location_id),
            'battery': self.extract_name(battery),
            'settings': self.extract_name(settings),
            'zigbee': self.extract_name(zigbee),
            'zwave': self.extract_name(zwave),
            'devices': [],
        }

        # get devices connected hub
        for device in devices.find_all('tr')[1:]:
            display_name, device_type, zigbee_id, network_id, status,\
                location, last_activity = device.find_all('td')

            data['devices'].append({
                'id': self.extract_id(display_name.a['href']),
                'name': display_name.text,
                'type': device_type.text,
                'zigbee_id': zigbee_id.text,
                'network_id': network_id.text,
                'status': status.text.strip(),
                'location': location.text,
                'last_activity': last_activity.text,
            })

        return data

    def get_hub_events(self, id, location_id):
        """Get hub events."""
        self._log.info("Parsing hub events by id - {}".format(id))
        events = []
        source = self.get_source(
            'https://graph-na04-useast2.api.smartthings.com/hub/{}/events?source=true'.format(id))
        soup = self.html_mapping(source)

        for event in soup.find('tbody', class_='events-table').find_all('tr'):
            date, source, event_type, name, value,\
                user, displayed_text = event.find_all('td')
            events.append({
                'date': self.normalize_time(self.strip_text(date.text), location_id),
                'source': self.strip_text(source.text),
                'type': event_type.text,
                'name': self.strip_text(name.text),
                'value': self.strip_text(value.text),
                'user': self.strip_text(user.text),
                'displayed_text': self.strip_text(displayed_text.text)
            })

        return events

    def get_devices(self):
        """Get list of devices."""
        self._log.info("Parsing account registered devices")
        devices = []
        source = self.get_source(
            '{}/device/list'.format(self.endpoint_url))
        soup = self.html_mapping(source)

        for device in soup.find_all('tr')[1:]:
            display_name, device_type, location, hub, zigbee_id, network_id,\
                status, execution_location, last_activity = device.find_all('td')

            devices.append({
                'name': display_name.text,
                'id': self.extract_id(display_name.a['href']),
                'type': device_type.text,
                'location': {
                    'name': location.text,
                    'id': self.extract_id(location.a['href']),
                },
                'hub': {
                    'name': hub.text,
                    'id': self.extract_id(hub.a['href']),
                },
                'zigbee_id': zigbee_id.text,
                'network_id': network_id.text,
                'status': status.text,
                'execution_location': execution_location.text,
                'last_activity': last_activity.text,
            })

        return devices

    def get_device_info(self, id, location_id):
        """Get device information by device id."""
        self._log.info("Parsing device information by id - {}".format(id))
        source = self.get_source(
            'https://graph-na04-useast2.api.smartthings.com/device/show/{}'.format(id))
        soup = self.html_mapping(source)

        try:
            name, label, device_type, version, zigbee_id, network_id,\
                status, hub, create_date, last_update, data, description,\
                firmware, states, _, location, _, use_by = soup.find_all('tr', class_='fieldcontain')
        except:
            # if preference not found
            name, label, device_type, version, zigbee_id, network_id,\
                status, hub, create_date, last_update, data, description,\
                firmware, states, location, _, use_by = soup.find_all('tr', class_='fieldcontain')            

        device = {
            'name': self.extract_name(name),
            'label': self.extract_name(label),
            'type': self.extract_name(device_type),
            'version': self.extract_name(version),
            'zigbee_id': self.extract_name(zigbee_id),
            'network_id': self.extract_name(network_id),
            'status': self.extract_name(status),
            'hub': {
                'name': self.extract_name(hub),
                'id': self.extract_id(hub.a['href'])
            },
            'create_date': self.normalize_time(self.extract_name(create_date), location_id),
            'last_update': self.normalize_time(self.extract_name(last_update), location_id),
            'description': self.extract_name(description),
            'firmware': self.extract_name(firmware),
            'location': self.extract_name(location),
            'use_by': []
        }

        for smartapp in use_by.find_all('li'):
            device['use_by'].append({
                'name': self.strip_text(smartapp.text),
                'id': self.extract_id(smartapp.a['href'])
            })

        return device

    def get_device_events(self, id, location_id):
        """Get device events."""
        self._log.info("Parsing device events by id - {}".format(id))
        events = []
        url = "https://graph-na04-useast2.api.smartthings.com/event/listAclEvents?all=true&source=&max=200"\
              "&id={}&type=device&eventType=".format(id)
        source = self.get_source(url)
        soup = self.html_mapping(source)

        for event in soup.find('tbody', class_='events-table').find_all('tr'):
            date, source, event_type, name, value, user, displayed_text, changed = event.find_all('td')
            events.append({
                'date': self.normalize_time(self.strip_text(date.text), location_id),
                'source': self.strip_text(source.text),
                'type': event_type.text,
                'name': self.strip_text(name.text),
                'value': self.strip_text(value.text),
                'user': self.strip_text(user.text),
                'displayed_text': self.strip_text(displayed_text.text),
                'changed': self.strip_text(changed.text)
            })

        return events

    def get_device_states(self, device, attribute):
        """Get device states."""
        self._log.info("Parsing device {} states by id - {}".format(attribute, device))
        states = []
        source = self.get_source(
            'https://graph-na04-useast2.api.smartthings.com/device/states/{}?attribute={}'.format(device, attribute))
        soup = self.html_mapping(source)

        for state in soup.find('tbody').find_all('tr'):
            date, name, value, units = state.find_all('td')
            states.append({
                'date': self.strip_text(date.text),
                'name': self.strip_text(name.text),
                'value': self.strip_text(value.text),
                'units': self.strip_text(units.text),
            })

        return states

    def get_smartapps(self, id):
        """Get SmartApps mapping with location id."""
        self._log.info("Parsing smartapps by location  id - {}".format(id))
        smartapps = []
        source = self.get_source(
            'https://graph-na04-useast2.api.smartthings.com/location/installedSmartApps/{}'.format(id))
        soup = self.html_mapping(source)

        for smartapp in soup.find_all(class_='app-edit'):
            smartapps.append({
                'name': smartapp.text,
                'id': self.extract_id(smartapp['data-path'])
            })

        return smartapps

    def __del__(self):
        """Destruct Smartthings API."""
        self._log.info("Finishing Samsung Smartthings cloud service parser...")
        del self
