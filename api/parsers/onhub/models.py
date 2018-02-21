"""Google Onhub database models."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

from util.dbsession import engine
from util import convert_time, convert_macaddr


Base = declarative_base()


class Station(Base):
    """Signal stations."""

    __tablename__ = 'on_stations'

    _id = Column(Integer, primary_key=True)
    hostname = Column(String)
    device_id = Column(String)
    lastseen_time = Column(DateTime)
    is_connected = Column(Boolean)
    is_guest = Column(Boolean)
    ip_address = Column(String)
    mac_address = Column(String)

    def __init__(self, hostname, device_id, lastseen_time, is_connected,
                 is_guest, ip_address, mac_address):
        """Station initialize."""
        self.hostname = hostname
        self.device_id = device_id
        self.lastseen_time = convert_time(lastseen_time)
        self.is_connected = is_connected
        self.is_guest = is_guest
        self.ip_address = ip_address
        self.mac_address = convert_macaddr(mac_address)


class Command(Base):
    """Execute Commands."""

    __tablename__ = 'on_commands'

    _id = Column(Integer, primary_key=True)
    command = Column(String)
    output = Column(Text)

    def __init__(self, command, output):
        """Command initialize."""
        self.command = command
        self.output = output


class Settings(Base):
    """Onhub settings."""

    __tablename__ = 'on_settings'

    _id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(Text)

    def __init__(self, key, value):
        """Setting initialize."""
        self.key = key
        self.value = value


# Create model
Base.metadata.create_all(engine)
