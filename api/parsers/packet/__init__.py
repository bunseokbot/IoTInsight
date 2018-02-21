"""Packet parser."""
from pyshark import FileCapture

from util.dbsession import session

from parsers.log import log


class Packet(object):
    """Packet filter by IoT related packet."""

    def __init__(self, path):
        """Construct packet class."""
        self._log = log()

        import parsers.packet.models as models

        self._log.info("Reading {} packet file.".format(path))
        try:
            self.pcapfile = FileCapture(path, display_filter='coap or xmpp or mqtt')
        except:
            self.log.error("Unable to read {} packet file".format(path),
                           exc_info=True)
        self.packets = []

        for packet in self.pcapfile:
            time = int(float(packet.frame_info.time_epoch))
            src_macaddr = packet.eth.src
            dst_macaddr = packet.eth.dst

            protocol = packet.highest_layer

            src_ipaddr = packet.ip.src
            dst_ipaddr = packet.ip.dst

            if protocol == "COAP":
                src_port = packet.udp.srcport
                dst_port = packet.udp.dstport
                message = self.parse_coap(packet.coap)

            elif protocol == "XMPP":
                src_port = packet.tcp.srcport
                dst_port = packet.tcp.dstport
                message = self.parse_xmpp(packet.xmpp)

            elif protocol == "MQTT":
                src_port = packet.tcp.srcport
                dst_port = packet.tcp.dstport
                message = self.parse_mqtt(packet.mqtt)

            self.packets.append(models.Packet(
                time, src_macaddr, dst_macaddr, src_ipaddr, src_port,
                dst_ipaddr, dst_port, protocol, message
            ))

        self.pcapfile.close()

    def get_method(self, code):
        """Get method from coap code."""
        if code == "0.01":
            return "GET"

        elif code == "0.02":
            return "POST"

        elif code == "0.03":
            return "PUT"

        elif code == "0.04":
            return "DELETE"

        else:
            return "Unassigned"

    def packet_type(self, _type):
        """Get type of coap packet."""
        if _type == 0x00:
            return "Confirmable"

        elif _type == 0x01:
            return "Non-confirmable"

        elif _type == 0x02:
            return "Acknowledgement"

        elif _type == 0x03:
            return "Reset"

    def get_msgtype(self, _type):
        """Get message type of MQTT."""
        if _type == 0x01:
            return "CONNECT"

        elif _type == 0x02:
            return "CONNACK"

        elif _type == 0x03:
            return "PUBLISH"

        elif _type == 0x04:
            return "PUBACK"

        elif _type == 0x05:
            return "PUBREC"

        elif _type == 0x06:
            return "PUBREL"

        elif _type == 0x07:
            return "PUBCOMP"

        elif _type == 0x08:
            return "SUBSCRIBE"

        elif _type == 0x09:
            return "SUBACK"

        elif _type == 0x0A:
            return "UNSUBSCRIBE"

        elif _type == 0x0B:
            return "UNSUBACK"

        elif _type == 0x0C:
            return "PINGREQ"

        elif _type == 0x0D:
            return "PINGRESP"

        elif _type == 0x0E:
            return "DISCONNECT"

        else:
            return "Reserved"

    def get_qostype(self, qos):
        """Get QoS type in MQTT."""
        if qos == 0x00:
            return "Fire and Forget"

        elif qos == 0x01:
            return "Acknowledged delivery"

        elif qos == 0x02:
            return "Assured delivery"

        else:
            return "Reserved"

    def parse_coap(self, packet):
        """Parse CoAP packet."""
        message = {
            'message_id': packet.mid,
            'code': self.get_method(packet.code),
            'type': self.packet_type(int(packet.type)),
        }

        if message['type'] == "Confirmable":
            try:
                message['token'] = packet.token
            except:
                pass

            try:
                message['payload'] = {
                    'description': packet.payload_desc,
                    'data': packet.payload.binary_value.decode(),
                }
            except:
                pass

        return message

    def parse_xmpp(self, packet):
        """Parse XMPP Protocol."""
        return {
            'xml_tag': packet.xml_tag
        }

    def parse_mqtt(self, packet):
        """Parse MQTT Protocol."""
        message = {
            'qos': self.get_qostype(int(packet.qos)),
            'retain': bool(packet.retain),
            'message_type': self.get_msgtype(int(packet.msgtype)),
        }

        try:
            message['topic'] = packet.topic
            message['message'] = packet.msg
        except:
            pass

        try:
            message['client_id'] = packet.clientid
        except:
            pass

        return message

    def __del__(self):
        """Destruct packet class."""
        self._log.info("Finishing packet parser...")
        del self
