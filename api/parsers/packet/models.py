"""Packet Database Model."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from util.dbsession import engine
from util import convert_time, convert_macaddr

import json


Base = declarative_base()


class Packet(Base):
    """Packet model."""

    __tablename__ = 'packets'

    _id = Column(Integer, primary_key=True)
    time = Column(Integer)
    src_macaddr = Column(String(17))
    dst_macaddr = Column(String(17))
    src_ipaddr = Column(String)
    src_port = Column(Integer)
    dst_ipaddr = Column(String)
    dst_port = Column(Integer)
    protocol = Column(String(4))
    message = Column(String)

    def __init__(self, time, src_macaddr, dst_macaddr,
                 src_ipaddr, src_port, dst_ipaddr, dst_port, protocol, message):
        """Initialize Packet model."""
        self.time = convert_time(time)
        self.src_macaddr = convert_macaddr(src_macaddr)
        self.dst_macaddr = convert_macaddr(dst_macaddr)
        self.src_ipaddr = src_ipaddr
        self.src_port = src_port
        self.dst_ipaddr = dst_ipaddr
        self.dst_port = dst_port
        self.protocol = protocol
        self.message = json.dumps(message)

# Create model
Base.metadata.create_all(engine)
