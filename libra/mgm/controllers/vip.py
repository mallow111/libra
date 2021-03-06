# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import socket
import time
from novaclient import exceptions
from oslo.config import cfg

from libra.mgm.nova import Node
from libra.openstack.common import log


LOG = log.getLogger(__name__)


class BuildIpController(object):

    RESPONSE_FIELD = 'response'
    RESPONSE_SUCCESS = 'PASS'
    RESPONSE_FAILURE = 'FAIL'

    def __init__(self, msg):
        self.msg = msg

    def run(self):
        try:
            nova = Node()
        except Exception:
            LOG.exception("Error initialising Nova connection")
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        LOG.info("Creating a requested floating IP")
        try:
            ip_info = nova.vip_create()
        except exceptions.ClientException:
            LOG.exception(
                'Error getting a Floating IP'
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg
        LOG.info("Floating IP {0} created".format(ip_info['id']))
        self.msg['id'] = ip_info['id']
        self.msg['ip'] = ip_info['ip']
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg


class AssignIpController(object):

    RESPONSE_FIELD = 'response'
    RESPONSE_SUCCESS = 'PASS'
    RESPONSE_FAILURE = 'FAIL'

    def __init__(self, msg):
        self.msg = msg

    def run(self):
        try:
            nova = Node()
        except Exception:
            LOG.exception("Error initialising Nova connection")
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        LOG.info(
            "Assigning Floating IP {0} to {1}"
            .format(self.msg['ip'], self.msg['name'])
        )
        try:
            node_id = nova.get_node(self.msg['name'])
            LOG.info(
                'Node name {0} identified as ID {1}'
                .format(self.msg['name'], node_id)
            )
            nova.vip_assign(node_id, self.msg['ip'])
            if cfg.CONF['mgm']['tcp_check_port']:
                self.check_ip(self.msg['ip'],
                              cfg.CONF['mgm']['tcp_check_port'])
        except:
            LOG.exception(
                'Error assigning Floating IP {0} to {1}'
                .format(self.msg['ip'], self.msg['name'])
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg

    def check_ip(self, ip, port):
        # TCP connect check to see if floating IP was assigned correctly
        loop_count = 0
        while True:
            try:
                sock = socket.socket()
                sock.settimeout(5)
                sock.connect((ip, port))
                sock.close()
                return True
            except socket.error:
                try:
                    sock.close()
                except:
                    pass
                loop_count += 1
                if loop_count >= 5:
                    LOG.error(
                        "TCP connect error after floating IP assign {0}"
                        .format(ip)
                    )
                    raise
                time.sleep(2)


class RemoveIpController(object):

    RESPONSE_FIELD = 'response'
    RESPONSE_SUCCESS = 'PASS'
    RESPONSE_FAILURE = 'FAIL'

    def __init__(self, msg):
        self.msg = msg

    def run(self):
        try:
            nova = Node()
        except Exception:
            LOG.exception("Error initialising Nova connection")
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        LOG.info(
            "Removing Floating IP {0} from {1}"
            .format(self.msg['ip'], self.msg['name'])
        )
        try:
            node_id = nova.get_node(self.msg['name'])
            nova.vip_remove(node_id, self.msg['ip'])
        except:
            LOG.exception(
                'Error removing Floating IP {0} from {1}'
                .format(self.msg['ip'], self.msg['name'])
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg


class DeleteIpController(object):

    RESPONSE_FIELD = 'response'
    RESPONSE_SUCCESS = 'PASS'
    RESPONSE_FAILURE = 'FAIL'

    def __init__(self, msg):
        self.msg = msg

    def run(self):
        try:
            nova = Node()
        except Exception:
            LOG.exception("Error initialising Nova connection")
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        LOG.info(
            "Deleting Floating IP {0}"
            .format(self.msg['ip'])
        )
        try:
            nova.vip_delete(self.msg['ip'])
        except:
            LOG.exception(
                'Error deleting Floating IP {0}'
                .format(self.msg['ip'])
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg
