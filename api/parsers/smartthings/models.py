"""Samsung Smartthings database models."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from util.dbsession import engine
from util import convert_macaddr


Base = declarative_base()


class Location(Base):
    """Hub locations."""

    __tablename__ = 'sam_locations'

    _id = Column(Integer, primary_key=True)
    location_id = Column(String(36), unique=True)
    name = Column(String)
    temperature_scale = Column(String(1))
    timezone = Column(String)
    coordinates = Column(String)

    def __init__(self, location_id, name, temperature_scale,
                 timezone, coordinates):
        """Initialize location information."""
        self.location_id = location_id
        self.name = name
        self.temperature_scale = temperature_scale
        self.timezone = timezone
        self.coordinates = coordinates


class Hub(Base):
    """Device Hubs."""

    __tablename__ = 'sam_hubs'

    _id = Column(Integer, primary_key=True)
    name = Column(String)
    hub_id = Column(String, unique=True)
    location_id = Column(Integer, ForeignKey('sam_locations._id'))
    last_serverping = Column(DateTime)
    last_hubping = Column(DateTime)
    create_date = Column(DateTime)
    last_update = Column(DateTime)
    last_booted = Column(DateTime)
    ip_address = Column(String)
    mac_address = Column(String)

    location = relationship('Location', backref=backref('sam_hubs', order_by=_id))

    def __init__(self, hub_id, name, last_serverping, last_hubping, create_date,
                 last_update, last_booted, ip_address, mac_address):
        """Initialize hub information."""
        self.hub_id = hub_id
        self.name = name
        self.last_serverping = last_serverping
        self.last_hubping = last_hubping
        self.create_date = create_date
        self.last_update = last_update
        self.last_booted = last_booted
        self.ip_address = ip_address
        self.mac_address = convert_macaddr(mac_address)


class Device(Base):
    """Device lists."""

    __tablename__ = 'sam_devices'

    _id = Column(Integer, primary_key=True)
    name = Column(String)
    label = Column(String)
    device_id = Column(String, unique=True)
    hub_id = Column(Integer, ForeignKey('sam_hubs._id'))
    device_type = Column(String)
    create_date = Column(DateTime)
    last_update = Column(DateTime)
    version = Column(String)
    zigbee_id = Column(String(16))
    network_id = Column(String(4))

    hub = relationship('Hub', backref=backref('sam_devices', order_by=_id))

    def __init__(self, device_id, name, label, device_type, create_date,
                 last_update, version, zigbee_id, network_id):
        """Initialize device information."""
        self.device_id = device_id
        self.name = name
        self.label = label
        self.device_type = device_type
        self.create_date = create_date
        self.last_update = last_update
        self.version = version
        self.zigbee_id = zigbee_id
        self.network_id = network_id


class Event(Base):
    """Event lists."""

    __tablename__ = 'sam_events'

    _id = Column(Integer, primary_key=True)
    event_time = Column(DateTime)
    location_id = Column(Integer, ForeignKey('sam_locations._id'))
    hub_id = Column(Integer, ForeignKey('sam_hubs._id'))
    device_id = Column(Integer, ForeignKey('sam_devices._id'))
    event_type = Column(String)
    value = Column(String)
    displayed_text = Column(String)

    location = relationship('Location', backref=backref('sam_events', order_by=_id))
    hub = relationship('Hub', backref=backref('sam_events', order_by=_id))
    device = relationship('Device', backref=backref('sam_events', order_by=_id))

    def __init__(self, event_time, event_type, value, displayed_text):
        """Initialize event information."""
        self.event_time = self.event_time
        self.event_type = event_type
        self.value = value
        self.displayed_text = displayed_text


# Create model
Base.metadata.create_all(engine)
