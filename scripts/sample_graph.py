#!/usr/local/bin/python
import sys
from os import path

sys.path.append(path.realpath(path.join(path.dirname(__file__), path.pardir)))

from ethecycle.graph import print_graph_sample

print_graph_sample()
