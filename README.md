To launch:

```bash
cp .env.example .env

# edit local copy of .env to set TXION_DATA_DIR as the location of some txion data
vi .env

# docker-compose should build / pull / launch everything
scripts/docker_shell.sh
```

There's no persistence though the `gremlin-server` container will stay up (and keep the graph in memory) til you explicitly stop it with `docker stop`.
See [gremlin_graph.py](gremlin_graph.py) for example of how to connect and write stuff.

### Useful Commands
1. Get shell on the Tinkergraph server: `scripts/gremlin_server_shell.sh` (shouldn't be many reasons to do this)

# Questions
1. IIRC you said the txion amounts were already correctly adjusted for decimals?  (AKA divided by `10^18` for most tokens)

# Resources
GraphML / GraphSON: https://tinkerpop.apache.org/docs/3.4.1/dev/io/
