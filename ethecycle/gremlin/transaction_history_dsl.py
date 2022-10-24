"""
TODO: DOES NOT WORK YET

Transaction history appropriate DSL to ensure the arrow of time (AKA "next edge block_number is greater
that last traversed edge"). To use connect with:

  chain_history = traversal(TimeTraversal).with_remote(DriverRemoteConnection('ws://localhost:8182/gremlin', 'g'))

See: https://tinkerpop.apache.org/docs/current/reference/#gremlin-python-dsl
How to record steps: https://recolabs.dev/post/gremlin-python-algorithm-development-from-the-ground-up#How-Can-I-Save-Values-During-Traversals%3F
"""
from gremlin_python.process.graph_traversal import GraphTraversal
from gremlin_python.process.graph_traversal import __ as AnonymousTraversal
from gremlin_python.process.traversal import Bytecode, P
from gremlin_python.structure.graph import GraphTraversalSource

from ethecycle.util.string_constants import *


class TimeTraversal(GraphTraversal):
    # def knows(self, person_name):
    #     return self.out('knows').has_label('person').has('name', person_name)

    # def youngest_friends_age(self):
    #     return self.out('knows').has_label('person').values('age').min()

    def in_block_range(self, start_block: int, end_block: int) -> GraphTraversal:
        """Analyze only transactions found in block numbers between start_block and end_block."""
        return self.outE().is_(P.gte(start_block)).and_(P.lte(end_block))


class __(AnonymousTraversal):
    graph_traversal = TimeTraversal

    # @classmethod
    # def knows(cls, *args):
    #     return cls.graph_traversal(None, None, Bytecode()).knows(*args)

    # @classmethod
    # def youngest_friends_age(cls, *args):
    #     return cls.graph_traversal(None, None, Bytecode()).youngest_friends_age(*args)

    @classmethod
    def in_block_range(cls, *args):
        return cls.graph_traversal(None, None, Bytecode()).in_block_range(*args)


class TimeTraversalSource(GraphTraversalSource):
    def __init__(self, *args, **kwargs):
        super(TimeTraversalSource, self).__init__(*args, **kwargs)
        self.graph_traversal = TimeTraversal

    def transactions(self, *args):
        start_block_number = 0 if len(args) == 0 else args[0]
        traversal = self.get_graph_traversal()
        traversal.bytecode.add_step('E')
        traversal.bytecode.add_step('has', 'block_number', P.gte(start_block_number))
