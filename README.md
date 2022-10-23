To launch docker containers:

```bash
cp .env.example .env

# edit local copy of .env to set TXION_DATA_DIR as the location of some txion CSVs
vi .env

# docker-compose should build / pull / launch everything and leave you in a bash shell
scripts/docker_shell.sh
```

Once you are in the container shell, to load CSV (optionally filtered for a single token's txions):

```
# Show help:
./load_transaction_csv.py --help

# Load only USDT txions from CSV file /trondata/output_100000_lines.csv
./load_transaction_csv.py /trondata/output_100000_lines.csv --token USDT
```

To run Gremlin queries I use the `bpython` REPL (same as python REPL but has better tab completion, shows args of methods, etc.) Once yr in the REPL you can get the Gremlin graph object (the one that sends queries) from the [Graph](ethecycle/graph.py) class like this:

```python
from ethecycle.graph import g

# Example query for 1000 txions:
txions = g.E().limit(1000).elementMap().toList()

# Find cycles
cycles = Graph.find_cycles(max_cycle_length=3, limit=100)
```

Note that there's no persistence though the `gremlin-server` container will stay up (and keep the graph in memory) til you explicitly stop it with `docker stop`.

### Other Useful Commands
1. Get shell on the Tinkergraph server: `scripts/gremlin_server_shell.sh` (note that for any bulk loading or writing to/from XML files to occur the file (or destination dir, for writes) must be accessible from the Gremlin server container)


# Questions
1. IIRC you said the txion amounts were already correctly adjusted for decimals?  (AKA divided by `10^18` for most tokens)
1. Current unique ID for edge is `transaction_id = f"{self.transaction_hash}-{self.log_index}"`. Does that make sense?

# Resources
* [Gremlin query tutorials](https://kelvinlawrence.net/book/Gremlin-Graph-Guide.html) (Note these are not in python so the code may be slightly different than shown)
* [Tinkerpop Gremlin documentation](https://tinkerpop.apache.org/docs/current/reference/#_tinkerpop_documentation)
* [Gremlin traversal steps documentation](https://tinkerpop.apache.org/docs/current/reference/#general-steps)

### Python Differences from Java/Groovy

| Java | Python |
|------|--------|
| `as('a')` | `as_('a')` |
| `from('a')` | `from_('a')` |
| `vadas.property("name", "vadas", id_, 2l)`  | `vadas.property('name', 'vadas').property('id', 2)` |
