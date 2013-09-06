# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the 'License'); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from sqlalchemy import Table, Column, Integer, ForeignKey, create_engine
from sqlalchemy import INTEGER, VARCHAR, BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker, Session
import sqlalchemy.types as types
import time
import random
import ConfigParser
from pecan import conf
import logging


DeclarativeBase = declarative_base()
metadata = DeclarativeBase.metadata

loadbalancers_devices = Table(
    'loadbalancers_devices',
    metadata,
    Column('loadbalancer', Integer, ForeignKey('loadbalancers.id')),
    Column('device', Integer, ForeignKey('devices.id'))
)


class FormatedDateTime(types.TypeDecorator):
    '''formats date to match iso 8601 standards
    '''

    impl = types.DateTime

    def process_result_value(self, value, dialect):
        return value.strftime('%Y-%m-%dT%H:%M:%S')


class Limits(DeclarativeBase):
    __tablename__ = 'global_limits'
    id = Column(u'id', Integer, primary_key=True, nullable=False)
    name = Column(u'name', VARCHAR(length=128), nullable=False)
    value = Column(u'value', BIGINT(), nullable=False)


class PoolBuilding(DeclarativeBase):
    __tablename__ = 'pool_building'
    id = Column(u'id', Integer, primary_key=True, nullable=False)
    server_id = Column(u'server_id', Integer, nullable=False)
    qty = Column(u'qty', Integer, nullable=False)


class Vip(DeclarativeBase):
    __tablename__ = 'vips'
    id = Column(u'id', Integer, primary_key=True, nullable=False)
    ip = Column(u'ip', Integer, nullable=True)
    device = Column(u'device', Integer, ForeignKey('devices.id'))


class Device(DeclarativeBase):
    """device model"""
    __tablename__ = 'devices'
    #column definitions
    az = Column(u'az', INTEGER(), nullable=False)
    created = Column(u'created', FormatedDateTime(), nullable=False)
    floatingIpAddr = Column(
        u'floatingIpAddr', VARCHAR(length=128), nullable=False
    )
    id = Column(u'id', BIGINT(), primary_key=True, nullable=False)
    name = Column(u'name', VARCHAR(length=128), nullable=False)
    publicIpAddr = Column(u'publicIpAddr', VARCHAR(length=128), nullable=False)
    status = Column(u'status', VARCHAR(length=128), nullable=False)
    type = Column(u'type', VARCHAR(length=128), nullable=False)
    updated = Column(u'updated', FormatedDateTime(), nullable=False)
    vip = relationship("Vip", uselist=False, backref="devices")


class LoadBalancer(DeclarativeBase):
    """load balancer model"""
    __tablename__ = 'loadbalancers'
    #column definitions
    algorithm = Column(u'algorithm', VARCHAR(length=80), nullable=False)
    errmsg = Column(u'errmsg', VARCHAR(length=128))
    id = Column(u'id', BIGINT(), primary_key=True, nullable=False)
    name = Column(u'name', VARCHAR(length=128), nullable=False)
    port = Column(u'port', INTEGER(), nullable=False)
    protocol = Column(u'protocol', VARCHAR(length=128), nullable=False)
    status = Column(u'status', VARCHAR(length=50), nullable=False)
    statusDescription = Column(u'errmsg', VARCHAR(length=128), nullable=True)
    tenantid = Column(u'tenantid', VARCHAR(length=128), nullable=False)
    updated = Column(u'updated', FormatedDateTime(), nullable=False)
    created = Column(u'created', FormatedDateTime(), nullable=False)
    nodes = relationship(
        'Node', backref=backref('loadbalancers', order_by='Node.id')
    )
    monitors = relationship(
        'HealthMonitor', backref=backref(
            'loadbalancers',
            order_by='HealthMonitor.lbid')
    )
    devices = relationship(
        'Device', secondary=loadbalancers_devices, backref='loadbalancers',
        lazy='joined'
    )


class Node(DeclarativeBase):
    """node model"""
    __tablename__ = 'nodes'
    #column definitions
    address = Column(u'address', VARCHAR(length=128), nullable=False)
    enabled = Column(u'enabled', Integer(), nullable=False)
    id = Column(u'id', BIGINT(), primary_key=True, nullable=False)
    lbid = Column(
        u'lbid', BIGINT(), ForeignKey('loadbalancers.id'), nullable=False
    )
    port = Column(u'port', INTEGER(), nullable=False)
    status = Column(u'status', VARCHAR(length=128), nullable=False)
    weight = Column(u'weight', INTEGER(), nullable=False)


class HealthMonitor(DeclarativeBase):
    """monitors model"""
    __tablename__ = 'monitors'
    #column definitions
    lbid = Column(
        u'lbid', BIGINT(), ForeignKey('loadbalancers.id'), primary_key=True,
        nullable=False
    )
    type = Column(u'type', VARCHAR(length=128), nullable=False)
    delay = Column(u'delay', INTEGER(), nullable=False)
    timeout = Column(u'timeout', INTEGER(), nullable=False)
    attempts = Column(
        u'attemptsBeforeDeactivation', INTEGER(), nullable=False
    )
    path = Column(u'path', VARCHAR(length=2000))


class RoutingSession(Session):
    """ If an engine is already in use, re-use it.  Otherwise we can end up
        with deadlocks in Galera, see http://tinyurl.com/9h6qlly
        switch engines every 60 seconds of idle time """

    engines = []
    last_engine = None
    last_engine_time = 0

    def get_bind(self, mapper=None, clause=None):
        if not RoutingSession.engines:
            self._build_engines()

        if (
            RoutingSession.last_engine
            and time.time() < RoutingSession.last_engine_time + 60
        ):
            RoutingSession.last_engine_time = time.time()
            return RoutingSession.last_engine
        engine = random.choice(RoutingSession.engines)
        RoutingSession.last_engine = engine
        RoutingSession.last_engine_time = time.time()
        return engine

    def _build_engines(self):
        config = ConfigParser.SafeConfigParser()
        config.read([conf.conffile])
        for section in conf.database:
            db_conf = config._sections[section]

            conn_string = '''mysql://%s:%s@%s:%d/%s''' % (
                db_conf['username'],
                db_conf['password'],
                db_conf['host'],
                db_conf.get('port', 3306),
                db_conf['schema']
            )

            if 'ssl_key' in db_conf:
                ssl_args = {'ssl': {
                    'cert': db_conf['ssl_cert'],
                    'key': db_conf['ssl_key'],
                    'ca': db_conf['ssl_ca']
                }}

                engine = create_engine(
                    conn_string, isolation_level="READ COMMITTED",
                    pool_size=20, connect_args=ssl_args, pool_recycle=3600
                )
            else:
                engine = create_engine(
                    conn_string, isolation_level="READ COMMITTED",
                    pool_size=20, pool_recycle=3600
                )
            RoutingSession.engines.append(engine)


class db_session(object):
    def __init__(self):
        self.session = None
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        for x in xrange(10):
            try:
                self.session = sessionmaker(class_=RoutingSession)()
                self.session.execute("SELECT 1")
                return self.session
            except:
                self.logger.error(
                    'Could not connect to DB server: {0}'.format(
                        RoutingSession.last_engine.url
                    )
                )
                RoutingSession.last_engine = None
        self.logger.error('Could not connect to any DB server')
        return None

    def __exit__(self, type, value, traceback):
        self.session.close()
        return False