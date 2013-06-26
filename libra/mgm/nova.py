# Copyright 2012 Hewlett-Packard Development Company, L.P.
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

import uuid
import time
import sys
import urllib

from novaclient import client
from novaclient import exceptions


class NotFound(Exception):
    pass


class BuildError(Exception):
    def __init__(self, msg, node_name, node_id=0):
        self.msg = msg
        self.node_name = node_name
        self.node_id = node_id

    def __str__(self):
        return self.msg


class Node(object):
    def __init__(self, username, password, tenant, auth_url, region, keyname,
                 secgroup, image, node_type, node_basename=None):
        self.nova = client.HTTPClient(
            username,
            password,
            tenant,
            auth_url,
            region_name=region,
            no_cache=True,
            service_type='compute'
        )
        self.keyname = keyname
        self.secgroup = secgroup
        self.node_basename = node_basename
        # Replace '_' with '-' in basename
        if self.node_basename:
            self.node_basename = self.node_basename.replace('_', '-')

        if image.isdigit():
            self.image = image
        else:
            self.image = self._get_image(image)

        if node_type.isdigit():
            self.node_type = node_type
        else:
            self.node_type = self._get_flavor(node_type)

    def build(self):
        """ create a node, test it is running """
        node_id = uuid.uuid1()
        try:
            body = self._create(node_id)
        except exceptions.ClientException:
            raise BuildError(
                'Error creating node, exception {exc}'
                .format(exc=sys.exc_info()[0]), node_id
            )

        server_id = body['server']['id']
        # try for 40 * 3 seconds
        waits = 40
        while waits > 0:
            time.sleep(3)
            resp, status = self.status(server_id)
            status = status['server']
            if status['status'] == 'ACTIVE':
                return status
            elif not status['status'].startswith('BUILD'):
                raise BuildError(
                    'Error spawning node, status {stat}'
                    .format(stat=status['status']),
                    node_id, server_id,
                )
            waits = waits - 1

        raise BuildError('Timeout creating node', node_id, server_id)

    def delete(self, node_id):
        """ delete a node """
        try:
            resp = self._delete(node_id)
        except exceptions.ClientException:
            return False, 'Error deleting node {nid} exception {exc}'.format(
                nid=node_id, exc=sys.exc_info()[0]
            )

        if resp.status_code != 204:
            return False, 'Error deleting node {nid} status {stat}'.format(
                nid=node_id, stat=resp.status_code
            )

        return True, ''

    def _create(self, node_id):
        """ create a nova node """
        url = "/servers"
        if self.node_basename:
            node_name = '{0}-{1}'.format(self.node_basename, node_id)
        else:
            node_name = '{0}'.format(node_id)
        body = {"server": {
                "name": node_name,
                "imageRef": self.image,
                "key_name": self.keyname,
                "flavorRef": self.node_type,
                "max_count": 1,
                "min_count": 1,
                "networks": [],
                "security_groups": [{"name": self.secgroup}]
                }}
        resp, body = self.nova.post(url, body=body)
        return body

    def status(self, node_id):
        """ used to keep scanning to see if node is up """
        url = "/servers/{0}".format(node_id)
        try:
            resp, body = self.nova.get(url)
        except exceptions.NotFound:
            msg = "Could not find node with id {0}".format(node_id)
            raise NotFound(msg)

        return resp, body

    def _delete(self, node_id):
        """ delete a nova node, return 204 succeed """
        url = "/servers/{0}".format(node_id)
        resp, body = self.nova.delete(url)

        return resp

    # TODO: merge get_node and _get_image to remove duplication of code

    def get_node(self, node_name):
        """ tries to find a node from the name """
        args = {'name': node_name}
        url = "/servers?{0}".format(urllib.urlencode(args))
        try:
            resp, body = self.nova.get(url)
        except exceptions.NotFound:
            msg = "Could not find node with name {0}".format(node_name)
            raise NotFound(msg)
        if resp.status_code not in [200, 203]:
            msg = "Error {0} searching for node with name {1}".format(
                resp.status_code, node_name
            )
            raise NotFound(msg)
        if len(body['servers']) != 1:
            msg = "Could not find node with name {0}".format(node_name)
            raise NotFound(msg)
        return body['servers'][0]['id']

    def _get_image(self, image_name):
        """ tries to find an image from the name """
        args = {'name': image_name}
        url = "/images?{0}".format(urllib.urlencode(args))
        resp, body = self.nova.get(url)
        if resp.status_code not in [200, 203]:
            msg = "Error {0} searching for image with name {1}".format(
                resp.status_code, image_name
            )
            raise NotFound(msg)
        if len(body['images']) != 1:
            msg = "Could not find image with name {0}".format(image_name)
            raise NotFound(msg)
        return body['images'][0]['id']

    def _get_flavor(self, flavor_name):
        """ tries to find a flavor from the name """
        url = "/flavors"
        resp, body = self.nova.get(url)
        if resp.status_code not in [200, 203]:
            msg = "Error {0} searching for flavor with name {1}".format(
                resp.status_code, flavor_name
            )
            raise NotFound(msg)
        for flavor in body['flavors']:
            if flavor['name'] == flavor_name:
                return flavor['id']
        msg = "Could not find flavor with name {0}".format(flavor_name)
        raise NotFound(msg)
