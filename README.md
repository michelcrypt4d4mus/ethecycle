To launch:

```bash
cp .env.example .env

# edit local copy of .env to set TXION_DATA_DIR as the location of some txion data
vi .env

# docker-compose should build / pull / launch everything
docker-compose run --rm shell
```

There's no persistence though the `gremlin-server` container will stay up (and keep the graph in memory) til you explicitly stop it with `docker stop`.
See [gremlin_graph.py](gremlin_graph.py) for example of how to connect and write stuff.

# Questions
1. IIRC you said the txion amounts were already correctly adjusted for decimals?  (AKA divided by `10^18` for most tokens)

# Resources
GraphML / GraphSON: https://tinkerpop.apache.org/docs/3.4.1/dev/io/
