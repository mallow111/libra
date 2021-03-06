.. _api-node:

=====
Nodes
=====


.. _api-node-list:

List All Load Balancer Nodes
----------------------------

Operation
~~~~~~~~~

+------------+-----------------------------------+----------+--------------------------------------------------------+
| Resource   | Operation                         | Method   | Path                                                   |
+============+===================================+==========+========================================================+
| Node       | Get list of load balancer nodes   | GET      | {baseURI}/{ver}/loadbalancers/{loadbalancerId}/nodes   |
+------------+-----------------------------------+----------+--------------------------------------------------------+

Description
~~~~~~~~~~~

List all nodes for a specified load balancer.

Request Data
~~~~~~~~~~~~

None required.

Query Parameters Supported
~~~~~~~~~~~~~~~~~~~~~~~~~~

None required.

Required HTTP Header Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**X-Auth-Token**

Request Body
~~~~~~~~~~~~

None required.

Normal Response Code
~~~~~~~~~~~~~~~~~~~~

+--------------------+---------------+
| HTTP Status Code   | Description   |
+====================+===============+
| 200                | OK            |
+--------------------+---------------+

Response Body
~~~~~~~~~~~~~

The response body contains the load balancer nodes requested or 404, if
not found.

Error Response Codes
~~~~~~~~~~~~~~~~~~~~

+--------------------+----------------+
| HTTP Status Code   | Description    |
+====================+================+
| 400                | Bad Request    |
+--------------------+----------------+
| 401                | Unauthorized   |
+--------------------+----------------+
| 404                | Not Found      |
+--------------------+----------------+
| 405                | Not Allowed    |
+--------------------+----------------+
| 500                | LBaaS Fault    |
+--------------------+----------------+

Example
~~~~~~~

**Curl Example**

::

    curl -H "X-Auth-Token: TOKEN" https://uswest.region-b.geo-1.lbaas.hpcloudsvc.com/v1.1/loadbalancers/100/nodes

**Response**

::

    {
        "nodes" : [
                {
                    "id":"410",
                    "address":"10.1.1.1",
                    "port":"80",
                    "condition":"ENABLED",
                    "status":"ONLINE"
                },
                {
                    "id":"236",
                    "address":"10.1.1.2",
                    "port":"80",
                    "condition":"ENABLED",
                    "status":"ONLINE"
                },
                {
                    "id":"2815",
                    "address":"10.1.1.3",
                    "port":"83",
                    "condition":"DISABLED",
                    "status":"OFFLINE"
                },
                ]
    }

.. _api-node-status:

Get Load Balancer Node
----------------------

Operation
~~~~~~~~~~~~~~

+------------+-------------------------------------+----------+-----------------------------------------------------------------+
| Resource   | Operation                           | Method   | Path                                                            |
+============+=====================================+==========+=================================================================+
| Node       | Get a specific load balancer node   | GET      | {baseURI}/{ver}/loadbalancers/{loadbalancerId}/nodes/{nodeId}   |
+------------+-------------------------------------+----------+-----------------------------------------------------------------+

Description
~~~~~~~~~~~

This operation retrieves the configuration of a node.

Request Data
~~~~~~~~~~~~

None required.

Query Parameters Supported
~~~~~~~~~~~~~~~~~~~~~~~~~~

None required.

Required HTTP Header Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**X-Auth-Token**

Request Body
~~~~~~~~~~~~~~~~~

None required.

Normal Response Code
~~~~~~~~~~~~~~~~~~~~

+--------------------+---------------+
| HTTP Status Code   | Description   |
+====================+===============+
| 200                | OK            |
+--------------------+---------------+

Response Body
~~~~~~~~~~~~~

The response body contains the load balancer node requested or 404, if
not found.

Error Response Codes
~~~~~~~~~~~~~~~~~~~~

+--------------------+----------------+
| HTTP Status Code   | Description    |
+====================+================+
| 400                | Bad Request    |
+--------------------+----------------+
| 401                | Unauthorized   |
+--------------------+----------------+
| 404                | Not Found      |
+--------------------+----------------+
| 405                | Not Allowed    |
+--------------------+----------------+
| 500                | LBaaS Fault    |
+--------------------+----------------+

Example
~~~~~~~

**Curl Example**

::

        curl -H "X-Auth-Token: TOKEN" https://uswest.region-b.geo-1.lbaas.hpcloudsvc.com/v1.1/loadbalancers/100/nodes/410

**Response**

::

    {
        "id":"410",
        "address":"10.1.1.2",
        "port":"80",
        "condition":"ENABLED",
        "status":"ONLINE"
    }

.. _api-node-create:

Create Load Balancer Node
-------------------------

Operation
~~~~~~~~~

+------------+-----------------------------------+----------+--------------------------------------------------------+
| Resource   | Operation                         | Method   | Path                                                   |
+============+===================================+==========+========================================================+
| Node       | Create a new load balancer node   | POST     | {baseURI}/{ver}/loadbalancers/{loadbalancerId}/nodes   |
+------------+-----------------------------------+----------+--------------------------------------------------------+

Description
~~~~~~~~~~~

Add a new node to any existing load balancer. When a node is added, it is
assigned a unique identifier that can be used for mutating operations
such as changing the condition, or removing the node from the load
balancer. When a node is added to a load balancer it is enabled by
default.

Relevant weights can be assigned to nodes using the weight attribute of the
node element. The weight of a node determines the portion of requests or
connections it services compared to the other nodes of the load balancer. For
example, if node A has a weight of 2 and node B has a weight of 1, then the
loadbalancer will forward twice as many requests to node A than to node B. If
the weight attribute is not specified, then the node's weight is implicitly
set to "1". Weight values from 1 to 256 are allowed.

Request Data
~~~~~~~~~~~~

The request must contain information regarding the new node to be added.
More than one node can be added at a time.

Query Parameters Supported
~~~~~~~~~~~~~~~~~~~~~~~~~~

None required.

Required HTTP Header Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**X-Auth-Token**

Request Body
~~~~~~~~~~~~

The request body defines the attributes of the new node to be created.

Normal Response Code
~~~~~~~~~~~~~~~~~~~~

+--------------------+---------------+
| HTTP Status Code   | Description   |
+====================+===============+
| 202                | Accepted      |
+--------------------+---------------+

Response Body
~~~~~~~~~~~~~

The response body contains the load balancer requested or 404, if not
found.

Error Response Codes
~~~~~~~~~~~~~~~~~~~~

+--------------------+----------------+
| HTTP Status Code   | Description    |
+====================+================+
| 400                | Bad Request    |
+--------------------+----------------+
| 401                | Unauthorized   |
+--------------------+----------------+
| 404                | Not Found      |
+--------------------+----------------+
| 405                | Not Allowed    |
+--------------------+----------------+
| 413                | Over Limit     |
+--------------------+----------------+
| 500                | LBaaS Fault    |
+--------------------+----------------+

Example
~~~~~~~

**Contents of Request file nodes.json**

::

    {
        "nodes": [
                    {
                        "address": "10.1.1.1",
                        "port": "80",
                        "weight": "2"
                    },
                    {
                        "address": "10.2.2.1",
                        "port": "80",
                        "weight": "4"
                    },
                    {
                        "address": "10.2.2.2",
                        "port": "88",
                        "condition": "DISABLED"
                    }
            ]
    }

**Curl Request**

::

        curl -X POST -H "X-Auth-Token: TOKEN" --data-binary "@nodes.json" https://uswest.region-b.geo-1.lbaas.hpcloudsvc.com/v1.1/loadbalancers/100/nodes

**Response**

::

    {
        "nodes": [
                    {
                        "id": "7298",
                        "address": "10.1.1.1",
                        "port": "80",
                        "condition": "ENABLED",
                        "status": "ONLINE",
                        "weight": "2"
                    },
                    {
                        "id": "293",
                        "address": "10.2.2.1",
                        "port": "80",
                        "condition": "ENABLED",
                        "status": "OFFLINE",
                        "weight": "4"
                    },
                    {
                        "id": "183",
                        "address": "10.2.2.2",
                        "port": "88",
                        "condition": "DISABLED",
                        "status": "OFFLINE"
                    }
            ]
    }

.. _api-node-modify:

Update Load Balancer Node Condition
-----------------------------------

Operation
~~~~~~~~~

+------------+-------------------------------+----------+-----------------------------------------------------------------+
| Resource   | Operation                     | Method   | Path                                                            |
+============+===============================+==========+=================================================================+
| Node       | Update a load balancer node   | PUT      | {baseURI}/{ver}/loadbalancers/{loadbalancerId}/nodes/{nodeId}   |
+------------+-------------------------------+----------+-----------------------------------------------------------------+

Description
~~~~~~~~~~~

Every node in the load balancer is either enabled or disabled which
determines its role within the load balancer. When the node has
condition='ENABLED' the node is permitted to accept new connections. Its
status will eventually become 'ONLINE' to reflect this configuration.
When the node has condition='DISABLED' the node is not permitted to
accept any new connections. Existing connections to the node are
forcibly terminated. The nodes status changes to OFFLINE once the
configuration has been successfully applied.

Relevant weights can be assigned to nodes using the weight attribute of the
node element. The weight of a node determines the portion of requests or
connections it services compared to the other nodes of the load balancer. For
example, if node A has a weight of 2 and node B has a weight of 1, then the
loadbalancer will forward twice as many requests to node A than to node B. If
the weight attribute is not specified, then the node's weight is implicitly
set to "1". Weight values from 1 to 256 are allowed.

The node IP and port are immutable attributes and cannot be modified
with a PUT request. Supplying an unsupported attribute will result in a
fault. A load balancer supports a maximum number of nodes. The
maximum number of nodes per load balancer is returned when querying the
limits of the load balancer service.

Request Data
~~~~~~~~~~~~

Request data includes the desired condition of the node as well as the
optional weight of the node.

Query Parameters Supported
~~~~~~~~~~~~~~~~~~~~~~~~~~

None required.

Required HTTP Header Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**X-Auth-Token**

Request Body
~~~~~~~~~~~~

The request body includes the node 'condition' attribute and its desired
state.

Normal Response Code
~~~~~~~~~~~~~~~~~~~~

+--------------------+---------------+
| HTTP Status Code   | Description   |
+====================+===============+
| 202                | Accepted      |
+--------------------+---------------+

Response Body
~~~~~~~~~~~~~

None.

Error Response Codes
~~~~~~~~~~~~~~~~~~~~

+--------------------+----------------+
| HTTP Status Code   | Description    |
+====================+================+
| 400                | Bad Request    |
+--------------------+----------------+
| 401                | Unauthorized   |
+--------------------+----------------+
| 404                | Not Found      |
+--------------------+----------------+
| 405                | Not Allowed    |
+--------------------+----------------+
| 500                | LBaaS Fault    |
+--------------------+----------------+

Example
~~~~~~~

**Contents of Request file node.json**

::

    {
        "condition": "DISABLED",
    }

    OR

    {
        "condition": "ENABLED",
        "weight": "2"
    }

**Curl Request**

::

    curl -X PUT -H "X-Auth-Token: TOKEN" --data-binary "@node.json" https://uswest.region-b.geo-1.lbaas.hpcloudsvc.com/v1.1/loadbalancers/100/nodes/100

**Response**

status with no response body.

.. _api-node-delete:

Delete Load Balancer Node
-------------------------

Operation
~~~~~~~~~~~~~~

+------------+-------------------------------+----------+-----------------------------------------------------------------+
| Resource   | Operation                     | Method   | Path                                                            |
+============+===============================+==========+=================================================================+
| Node       | Delete a load balancer node   | DELETE   | {baseURI}/{ver}/loadbalancers/{loadbalancerId}/nodes/{nodeId}   |
+------------+-------------------------------+----------+-----------------------------------------------------------------+

Description
~~~~~~~~~~~

Delete node for a load balancer.

.. note::
    A load balancer must have at least one node. Attempting to remove the last
    node of a load balancer will result in a 401 error.

Request Data
~~~~~~~~~~~~

None required.

Query Parameters Supported
~~~~~~~~~~~~~~~~~~~~~~~~~~

None required.

Required HTTP Header Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**X-Auth-Token**

Request Body
~~~~~~~~~~~~

None required.

Normal Response Code
~~~~~~~~~~~~~~~~~~~~
+--------------------+---------------+
| HTTP Status Code   | Description   |
+====================+===============+
| 202                | Accepted      |
+--------------------+---------------+

Response Body
~~~~~~~~~~~~~

None.

Error Response Codes
~~~~~~~~~~~~~~~~~~~~

+--------------------+----------------+
| HTTP Status Code   | Description    |
+====================+================+
| 400                | Bad Request    |
+--------------------+----------------+
| 401                | Unauthorized   |
+--------------------+----------------+
| 404                | Not Found      |
+--------------------+----------------+
| 405                | Not Allowed    |
+--------------------+----------------+
| 500                | LBaaS Fault    |
+--------------------+----------------+

Example
~~~~~~~

**Curl Request**

::

        curl -X DELETE -H "X-Auth-Token: TOKEN" https://uswest.region-b.geo-1.lbaas.hpcloudsvc.com/v1.1/loadbalancers/100/nodes/100

**Response**

status with no response body.