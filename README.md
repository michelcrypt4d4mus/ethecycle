To launch docker containers:

```bash
cp .env.example .env

# edit local copy of .env to set TXION_DATA_DIR as the location of some txion CSVs
vi .env

# docker-compose should build / pull / launch everything and leave you in a bash shell
scripts/docker_shell.sh
```

Once you are in the container shell, to load CSV (optionally filtered for a single token's txions) see `--help`:

```
./load_transaction_csv.py --help
```

To run Gremlin queries I use the `bpython` REPL (same as python REPL but has better tab completion, shows args of methods, etc.) Once yr in the REPL you can get the Gremlin graph object (the one that sends queries) from the [Graph](ethecycle/graph.py) class like this:

```python
from ethecycle.graph import Graph

g = Graph.graph

# Example query for 1000 txions:
txions = g.E().limit(1000).elementMap().toList()
```

Note that there's no persistence though the `gremlin-server` container will stay up (and keep the graph in memory) til you explicitly stop it with `docker stop`.

### Other Useful Commands
1. Get shell on the Tinkergraph server: `scripts/gremlin_server_shell.sh` (note that for any bulk loading or writing to/from XML files to occur the file (or destination dir, for writes) must be accessible from the Gremlin server container)


# Questions
1. IIRC you said the txion amounts were already correctly adjusted for decimals?  (AKA divided by `10^18` for most tokens)
1. Current unique ID for edge is `transaction_id = f"{self.transaction_hash}-{self.log_index}"`. Does that make sense?

# Resources
* [Tinkerpop Gremlin documentation](https://tinkerpop.apache.org/docs/current/reference/#_tinkerpop_documentation)
