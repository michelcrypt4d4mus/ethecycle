# Transaction Graph DB
* Wallet addresses are vertices AKA nodes
* ERC20 Transactions are edges and contain properties like `value`, `block_number`, etc.

### Prerequisites
This is known to work with these versions of `docker` and `docker-compose`.

```
$ docker-compose --version
Docker Compose version v2.10.2

$ docker --version
Docker version 20.10.17, build 100c701
```

# Usage
To launch docker containers and load graph data:

```bash
# Clone repo and cd into the repo directory
git clone https://github.com/michelcrypt4d4mus/ethecycle.git
cd ethecycle

# Edit local copy of .env to set TXION_DATA_DIR as the location of some txion CSVs
cp .env.example .env
# Use vi or whatever editor you prefer
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

### Troubleshooting
If you get a message about how the gremlin-server is not available at `tinkerpop:8182` I suspect you just have to wait for the server to come up.  However if waiting doesn't seem to help it may be worth trying to relaunch the containers with `docker-compose up`.

### Other Useful Commands
1. Get shell on the Tinkergraph server: `scripts/gremlin_server_shell.sh` (note that for any bulk loading or writing to/from XML files to occur the file (or destination dir, for writes) must be accessible from the Gremlin server container)


# Questions
1. IIRC you said the txion amounts were already correctly adjusted for decimals?  (AKA divided by `10^18` for most tokens)
1. Current unique ID for edge is `transaction_id = f"{self.transaction_hash}-{self.log_index}"`. Does that make sense?
1. Do you have a rough estimate as far as blocks per hour and/or blocks per day?
1. Are there lists of tokens with their contract addresses available somewhere for each blockchain? (Esp. any blockchains we may care about)

# Potential Queries
1. Identify the largest short term pass through wallets (AKA wallets with large xfers in and out in a short time frame that end up w/0 balances and are not used again)

# Resources
* [Gremlin Query Cheat Sheet](https://dkuppitz.github.io/gremlin-cheat-sheet/101.html), [Advanced Cheet Sheet](https://dkuppitz.github.io/gremlin-cheat-sheet/102.html) (includes `cyclicPath()` element)
* [Gremlin query book by Kelvin Lawrence](https://kelvinlawrence.net/book/Gremlin-Graph-Guide.html). Best resource I have found. Note these are not in python so the code may be slightly different than shown.
* [Tinkerpop Gremlin official documentation](https://tinkerpop.apache.org/docs/current/reference/#_tinkerpop_documentation)
* [Gremlin traversal steps documentation](https://tinkerpop.apache.org/docs/current/reference/#general-steps)
* [Domain Specific Language Writing](https://tinkerpop.apache.org/docs/current/reference/#gremlin-python-dsl)
* [Gremlin Python common imports](https://tinkerpop.apache.org/docs/current/reference/#python-imports)
* [Gremlin algorithm development](https://recolabs.dev/post/gremlin-python-algorithm-development-from-the-ground-up)
* [More Gremlin examples](https://www.doanduyhai.com/blog/?p=13374)
* [Tuning Gremlin queries](https://docs.aws.amazon.com/neptune/latest/userguide/gremlin-traversal-tuning.html)
* [Air routes `graphml`](https://raw.githubusercontent.com/krlawrence/graph/master/sample-data/air-routes-small-latest.graphml) Useful data to learn with. Can be loaded with script in repo by running: `scripts/demo_data/load_air_routes_demo_data.py`

### Python Differences from Java/Groovy

Gremlin's Python bindings are different from Java's in a few important cases. [See this section of the docs](https://github.com/apache/tinkerpop/blob/3.4-dev/docs/src/reference/gremlin-variants.asciidoc#differences-1) or [this small python script in official repo](https://github.com/apache/tinkerpop/blob/master/gremlin-python/src/main/python/example.py). Some examples:

| Java | Python |
|------|--------|
| `as('a')` | `as_('a')` |
| `from('a')` | `from_('a')` |
| `vadas.property("name", "vadas", id_, 2l)`  | `vadas.property('name', 'vadas').property('id', 2)` |

[Here's a good gist with a lot of python specific queries](https://gist.github.com/okram/f193d5616563a69ad5714a42c504276f).

### Other Technologies
* [ArangoDB](https://www.arangodb.com/) - Second most commonly recommended after Neo4j.
* [Apache AGE](https://age.apache.org) - Postgres extension. No Tinkerpop support, only OpenCypher.
* [ArcadeDB](https://arcadedb.com) - New fork of OrientDB. Gremlin and OpenCypher support.
* [MemGraph](https://memgraph.com) - In memory graph DB.
* TigerGraph comes up sometimes

### Other Resources
* [Article on supernodes and Neo4j](https://medium.com/neo4j/graph-modeling-all-about-super-nodes-d6ad7e11015b)
