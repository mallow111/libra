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

import logging
from libra.tests.base import TestCase
import libra.tests.mock_objects
from libra import __version__ as libra_version
from libra import __release__ as libra_release
from libra.openstack.common import log
from libra.worker.controller import LBaaSController as c
from libra.worker.drivers.base import LoadBalancerDriver
from libra.worker.drivers.haproxy.driver import HAProxyDriver

LOG = log.getLogger(__name__)


class TestWorkerController(TestCase):
    def setUp(self):
        super(TestWorkerController, self).setUp()
        self.driver = HAProxyDriver('libra.tests.mock_objects.FakeOSServices',
                                    None, None, None)

    def testBadAction(self):
        msg = {
            c.ACTION_FIELD: 'BOGUS'
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn(c.RESPONSE_FIELD, response)
        self.assertEquals(response[c.RESPONSE_FIELD], c.RESPONSE_FAILURE)

    def testCaseSensitive(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            'LoAdBaLaNcErS': [{'protocol': 'http'}]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)

    def testUpdate(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            c.LBLIST_FIELD: [
                {
                    'protocol': 'http',
                    'nodes': [
                        {
                            'id': 1234,
                            'address': '10.0.0.1',
                            'port': 80
                        }
                    ]
                }
            ]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn(c.RESPONSE_FIELD, response)
        self.assertEquals(response[c.RESPONSE_FIELD], c.RESPONSE_SUCCESS)

    def testSuspend(self):
        msg = {
            c.ACTION_FIELD: 'SUSPEND'
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn(c.RESPONSE_FIELD, response)
        self.assertEquals(response[c.RESPONSE_FIELD], c.RESPONSE_SUCCESS)

    def testEnable(self):
        msg = {
            c.ACTION_FIELD: 'ENABLE'
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn(c.RESPONSE_FIELD, response)
        self.assertEquals(response[c.RESPONSE_FIELD], c.RESPONSE_SUCCESS)

    def testDelete(self):
        msg = {
            c.ACTION_FIELD: 'DELETE'
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn(c.RESPONSE_FIELD, response)
        self.assertEquals(response[c.RESPONSE_FIELD], c.RESPONSE_SUCCESS)

    def testUpdateMissingNodeID(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            c.LBLIST_FIELD: [
                {
                    'protocol': 'http',
                    'nodes': [
                        {
                            'address': '10.0.0.1',
                            'port': 80
                        }
                    ]
                }
            ]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg, "Missing node 'id'")

    def testUpdateEmptyNodeID(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            c.LBLIST_FIELD: [
                {
                    'protocol': 'http',
                    'nodes': [
                        {
                            'id': '',
                            'address': '10.0.0.1',
                            'port': 80
                        }
                    ]
                }
            ]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg, "Missing node 'id'")

    def testUpdateMissingLBs(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE'
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg, "Missing '%s' element" % c.LBLIST_FIELD)

    def testUpdateMissingNodes(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            c.LBLIST_FIELD: [{'protocol': 'http'}]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg, "Missing 'nodes' element")

    def testUpdateMissingProto(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            c.LBLIST_FIELD: [
                {
                    'nodes': [
                        {
                            'id': 1234,
                            'address': '10.0.0.1',
                            'port': 80
                        }
                    ]
                }
            ]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg, "Missing required 'protocol' value.")

    def testUpdateGoodMonitor(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            c.LBLIST_FIELD: [
                {
                    'protocol': 'http',
                    'nodes': [
                        {
                            'id': 1234,
                            'address': '10.0.0.1',
                            'port': 80
                        }
                    ],
                    'monitor': {
                        'type': 'CONNECT',
                        'delay': 60,
                        'timeout': 30,
                        'attempts': 1,
                        'path': '/healthcheck'
                    }
                }
            ]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertNotIn('badRequest', response)
        self.assertEquals(response[c.RESPONSE_FIELD], c.RESPONSE_SUCCESS)

    def testUpdateMonitorMissingType(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            c.LBLIST_FIELD: [
                {
                    'protocol': 'http',
                    'nodes': [
                        {
                            'id': 1234,
                            'address': '10.0.0.1',
                            'port': 80
                        }
                    ],
                    'monitor': {
                        'delay': 60,
                        'timeout': 30,
                        'attempts': 1,
                        'path': '/healthcheck'
                    }
                }
            ]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg, "Missing monitor value 'type'")

    def testUpdateMonitorMissingDelay(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            c.LBLIST_FIELD: [
                {
                    'protocol': 'http',
                    'nodes': [
                        {
                            'id': 1234,
                            'address': '10.0.0.1',
                            'port': 80
                        }
                    ],
                    'monitor': {
                        'type': 'CONNECT',
                        'timeout': 30,
                        'attempts': 1,
                        'path': '/healthcheck'
                    }
                }
            ]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg, "Missing monitor value 'delay'")

    def testUpdateMonitorMissingTimeout(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            c.LBLIST_FIELD: [
                {
                    'protocol': 'http',
                    'nodes': [
                        {
                            'id': 1234,
                            'address': '10.0.0.1',
                            'port': 80
                        }
                    ],
                    'monitor': {
                        'type': 'CONNECT',
                        'delay': 60,
                        'attempts': 1,
                        'path': '/healthcheck'
                    }
                }
            ]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg, "Missing monitor value 'timeout'")

    def testUpdateMonitorMissingAttempts(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            c.LBLIST_FIELD: [
                {
                    'protocol': 'http',
                    'nodes': [
                        {
                            'id': 1234,
                            'address': '10.0.0.1',
                            'port': 80
                        }
                    ],
                    'monitor': {
                        'type': 'CONNECT',
                        'delay': 60,
                        'timeout': 30,
                        'path': '/healthcheck'
                    }
                }
            ]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg, "Missing monitor value 'attempts'")

    def testUpdateMonitorMissingPath(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            c.LBLIST_FIELD: [
                {
                    'protocol': 'http',
                    'nodes': [
                        {
                            'id': 1234,
                            'address': '10.0.0.1',
                            'port': 80
                        }
                    ],
                    'monitor': {
                        'type': 'CONNECT',
                        'delay': 60,
                        'timeout': 30,
                        'attempts': 1
                    }
                }
            ]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn(c.RESPONSE_FIELD, response)
        self.assertEquals(response[c.RESPONSE_FIELD], c.RESPONSE_SUCCESS)

    def testBadAlgorithm(self):
        msg = {
            c.ACTION_FIELD: 'UPDATE',
            c.LBLIST_FIELD: [
                {
                    'protocol': 'http',
                    'algorithm': 'BOGUS',
                    'nodes': [
                        {
                            'id': 1234,
                            'address': '10.0.0.1',
                            'port': 80
                        }
                    ]
                }
            ]
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn(c.RESPONSE_FIELD, response)
        self.assertEquals(response[c.RESPONSE_FIELD], c.RESPONSE_FAILURE)

    def testDiscover(self):
        msg = {
            c.ACTION_FIELD: 'DISCOVER'
        }
        controller = c(self.driver, msg)
        response = controller.run()
        self.assertIn('version', response)
        self.assertIn('release', response)
        self.assertEquals(response[c.RESPONSE_FIELD], c.RESPONSE_SUCCESS)
        self.assertEquals(response['version'], libra_version)
        self.assertEquals(response['release'], libra_release)

    def testArchiveMissingMethod(self):
        msg = {
            c.ACTION_FIELD: 'ARCHIVE'
        }
        null_driver = LoadBalancerDriver()
        controller = c(null_driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg, "Missing '%s' element" % c.OBJ_STORE_TYPE_FIELD)

    def testArchiveInvalidMethod(self):
        msg = {
            c.ACTION_FIELD: 'ARCHIVE',
            c.OBJ_STORE_TYPE_FIELD: 'bad'
        }
        null_driver = LoadBalancerDriver()
        controller = c(null_driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)

    def testArchiveSwiftRequiredParams(self):
        null_driver = LoadBalancerDriver()

        # Missing basepath field
        msg = {
            c.ACTION_FIELD: 'ARCHIVE',
            c.OBJ_STORE_TYPE_FIELD: 'Swift',
            c.OBJ_STORE_ENDPOINT_FIELD: "https://example.com",
            c.OBJ_STORE_TOKEN_FIELD: "XXXX",
            c.LBLIST_FIELD: [{'protocol': 'http', 'id': '123'}]
        }
        controller = c(null_driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg,
                          "Missing '%s' element" % c.OBJ_STORE_BASEPATH_FIELD)

        # Missing endpoint field
        msg = {
            c.ACTION_FIELD: 'ARCHIVE',
            c.OBJ_STORE_TYPE_FIELD: 'Swift',
            c.OBJ_STORE_BASEPATH_FIELD: "/lbaaslogs",
            c.OBJ_STORE_TOKEN_FIELD: "XXXX",
            c.LBLIST_FIELD: [{'protocol': 'http', 'id': '123'}]
        }
        controller = c(null_driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg,
                          "Missing '%s' element" % c.OBJ_STORE_ENDPOINT_FIELD)

        # Missing token field
        msg = {
            c.ACTION_FIELD: 'ARCHIVE',
            c.OBJ_STORE_TYPE_FIELD: 'Swift',
            c.OBJ_STORE_BASEPATH_FIELD: "/lbaaslogs",
            c.OBJ_STORE_ENDPOINT_FIELD: "https://example.com",
            c.LBLIST_FIELD: [{'protocol': 'http', 'id': '123'}]
        }
        controller = c(null_driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg,
                          "Missing '%s' element" % c.OBJ_STORE_TOKEN_FIELD)

        # Missing load balancer field
        msg = {
            c.ACTION_FIELD: 'ARCHIVE',
            c.OBJ_STORE_TYPE_FIELD: 'Swift',
            c.OBJ_STORE_BASEPATH_FIELD: "/lbaaslogs",
            c.OBJ_STORE_ENDPOINT_FIELD: "https://example.com",
            c.OBJ_STORE_TOKEN_FIELD: "XXXX"
        }
        controller = c(null_driver, msg)
        response = controller.run()
        self.assertIn('badRequest', response)
        msg = response['badRequest']['validationErrors']['message']
        self.assertEquals(msg, "Missing '%s' element" % c.LBLIST_FIELD)

    def testArchiveNotImplemented(self):
        msg = {
            c.ACTION_FIELD: 'ARCHIVE',
            c.OBJ_STORE_TYPE_FIELD: 'Swift',
            c.OBJ_STORE_BASEPATH_FIELD: "/lbaaslogs",
            c.OBJ_STORE_ENDPOINT_FIELD: "https://example.com",
            c.OBJ_STORE_TOKEN_FIELD: "XXXX",
            c.LBLIST_FIELD: [{'protocol': 'http', 'id': '123'}]
        }
        null_driver = LoadBalancerDriver()
        controller = c(null_driver, msg)
        response = controller.run()
        self.assertEquals(response[c.RESPONSE_FIELD], c.RESPONSE_FAILURE)
        self.assertIn(c.ERROR_FIELD, response)
        self.assertEquals(response[c.ERROR_FIELD],
                          "Selected driver does not support ARCHIVE action.")
