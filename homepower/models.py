# coding: utf-8

from sqlalchemy import (
    engine_from_config,
    Column,
    Integer,
    Float,
    DateTime,
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from zope.sqlalchemy import ZopeTransactionExtension


class BaseModel(object):
    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=BaseModel)
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


def initialize_sql(settings, prefix="sqlalchemy.", **kwargs):
    engine = engine_from_config(settings, prefix, **kwargs)
    if not DBSession.registry.has():
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine


class WattLog(Base):
    __tablename__ = 'watt_logs'

    value = Column(Float)
    created_at = Column(DateTime, nullable=False, default=func.now())
