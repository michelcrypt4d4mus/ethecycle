#!/usr/local/bin/python
"""
Pull the air routes and load it.
"""
from os import path
from subprocess import check_call

from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal

#from ethecycle.graph import g  # TODO: pythohn is Complaining about relative imports..

TINKERPOP_URI = 'ws://tinkerpop:8182/gremlin'
AIR_ROUTES_XML_PATH = 'tests/fixture_files/air-routes-small-latest.xml'
AIR_ROUTES_XML_TINKERPOP_PATH = path.join('/ethecycle', AIR_ROUTES_XML_PATH)
WGET_CMD = f"wget https://raw.githubusercontent.com/krlawrence/graph/master/sample-data/air-routes-small-latest.graphml -O {AIR_ROUTES_XML_PATH}"


# Retrieve file if need be
if not path.exists(AIR_ROUTES_XML_PATH):
    check_call(WGET_CMD.split())

g = traversal().withRemote(DriverRemoteConnection(TINKERPOP_URI, 'g'))
g.io(AIR_ROUTES_XML_TINKERPOP_PATH).read().iterate()
