"""Amazon Alexa database models."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

from util.dbsession import engine


Base = declarative_base()


class History(Base):
    """Alexa command history."""

    __tablename__ = 'al_historys'

    _id = Column(Integer, primary_key=True)
    activity_name = Column(String)
    activity_time = Column(DateTime)
    status = Column(String)
    response = Column(String)
    command = Column(String)
    audio_link = Column(String)

    def __init__(self, activity_name, activity_time, status,
                 response, command, audio_link):
        """Initialize history."""
        self.activity_name = activity_name
        self.activity_time = activity_time
        self.status = status
        self.response = response
        self.command = command
        self.audio_link = audio_link


class Setting(Base):
    """Setting model."""

    __tablename__ = 'al_settings'

    _id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)

    def __init__(self, key, value):
        """Initialize settings method."""
        self.key = key
        self.value = value


# Create model
Base.metadata.create_all(engine)
