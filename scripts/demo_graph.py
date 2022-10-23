"""
Scratch pad with some copy/paste of the example graphs that only come in the Java packages.
"""

from gremlin_python.process.graph_traversal import __, id_, select, unfold

from ethecycle.graph import delete_graph, g, write_graph

delete_graph()
v1 = g.addV('person').property('name','marko').next()
v2 = g.addV('person').property('name','stephen').next()
g.V(v1).addE('knows').to(v2).property('weight', 0.75).iterate()
write_graph('graph.xml')


delete_graph()

#g.addV('VA').property('id', 'i4').property('PartitionKey', 'test').addV('VA').property('id', 'i5').property('PartitionKey', 'test').addE('EAA').from_(__.V('i4')).to(__.V('i5'))

g.V().property("prop1", "prop1_val").as_("a") \
 .V().property("prop2", "prop2_val").as_("b") \
 .addE("some_relationship") \
 .property("prop1_val_weight", 0.1) \
 .from_("a").to("b") \
 .from_("a").to("b") \
 .property("prop1_val_weight", 0.2).iterate()

write_graph('graph.xml')

# marko = g.addV(id_, 1, T.label, "person");
# marko.property("name", "marko", id_, 0l);
# marko.property("age", 29, id_, 1l);
# final Vertex vadas = g.addV(id_, 2, T.label, "person");
# vadas.property("name", "vadas", id_, 2l);
# vadas.property("age", 27, id_, 3l);
# final Vertex lop = g.addV(id_, 3, T.label, "software");
# lop.property("name", "lop", id_, 4l);
# lop.property("lang", "java", id_, 5l);
# final Vertex josh = g.addV(id_, 4, T.label, "person");
# josh.property("name", "josh", id_, 6l);
# josh.property("age", 32, id_, 7l);
# final Vertex ripple = g.addV(id_, 5, T.label, "software");
# ripple.property("name", "ripple", id_, 8l);
# ripple.property("lang", "java", id_, 9l);
# final Vertex peter = g.addV(id_, 6, T.label, "person");
# peter.property("name", "peter", id_, 10l);
# peter.property("age", 35, id_, 11l);

# marko.addE("knows", vadas, id_, 7, "weight", 0.5d);
# marko.addE("knows", josh, id_, 8, "weight", 1.0d);
# marko.addE("created", lop, id_, 9, "weight", 0.4d);
# josh.addE("created", ripple, id_, 10, "weight", 1.0d);
# josh.addE("created", lop, id_, 11, "weight", 0.4d);
# peter.addE("created", lop, id_, 12, "weight", 0.2d);

