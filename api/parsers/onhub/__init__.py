"""Onhub diagnostic report parser."""
from zlib import decompress, MAX_WBITS

from parsers.log import log

import json


class Onhub(object):
    """Parse Onhub diagnostic report."""

    def __init__(self, path):
        """Construct onhub class."""
        import parsers.onhub.diagnosticreport_pb2 as diagnostic
        import parsers.onhub.models as models

        self._log = log()

        self._log.info("Starting Onhub diagnostic report parser...")

        dr = diagnostic.DiagnosticReport()

        try:
            dr.ParseFromString(open(path, 'rb').read())
            self.report = self.generate_report(dr)

            # set stations
            _stations = self.report['infoJSON']['_apState']['_stations']
            self.stations = []

            for station in _stations:
                if station['_connected']:
                    ip_address = station['_ipAddresses'][0]
                else:
                    ip_address = ''

                mac_address = self.search_macaddr(station['_id'])

                self.stations.append(models.Station(station['_dhcpHostname'], station['_id'],
                                     station['_lastSeenSecondsSinceEpoch'],
                                     station['_connected'], station['_guest'], ip_address, mac_address))

            # set commands
            _commands = self.report['commandOutput']
            self.commands = []

            for command in _commands:
                self.commands.append(models.Command(
                                     command['command'], command['output']))

            self.settings = []

            self.settings.append(
                models.Settings('generateTime', self.report['unixTime']))

        except IOError:
            self._log.error("Unable to read diagnostic report",
                            exc_info=True)
        except:
            self._log.error("Unable to parse report", exc_info=True)

    def search_macaddr(self, _id):
        """Search mac address from unknown table."""
        for row in self.report['unknownPairs']:
            if row['unknown1'] == _id:
                return row['unknown2']

        return ""

    def generate_report(self, dr):
        """Generate jsonify report."""
        self._log.info("Generating jsonify diagnostic report")
        result = {
            'version': dr.version,
            'whirlwindVersion': dr.whirlwindVersion,
            'stormVersion': dr.stormVersion,
            'unknown1': dr.unknown1,
            'unixTime': dr.unixTime,
            'infoJSON': json.loads(dr.infoJSON),
            'networkConfig': dr.networkConfig,
            'wanInfo': dr.wanInfo,
            'commandOutput': [],
            'unknownPairs': [],
            'fileLengths': [],
            'files': [],
        }

        # add command outputs
        for command in dr.commandOutputs:
            result['commandOutput'].append({
                'command': command.command,
                'output': command.output
            })

        # add unknown pairs
        for pair in dr.unknownPairs:
            result['unknownPairs'].append({
                'unknown1': pair.unknown1,
                'unknown2': pair.unknown2
            })

        # add file lengths
        for file in dr.fileLengths:
            result['fileLengths'].append({
                'path': file.path,
                'length': file.length
            })

        # add file data
        for file in dr.files:
            try:
                result['files'].append({
                    'path': file.path,
                    'content': decompress(file.content, 16 + MAX_WBITS)
                })
            except:
                result['files'].append({
                    'path': file.path,
                    'content': file.content
                })

        return result

    def __del__(self):
        """Destruct onhub class."""
        self._log.info("Finishing Onhub diagnostic report parser...")
        del self
