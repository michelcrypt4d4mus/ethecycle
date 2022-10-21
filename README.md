To launch:

```bash
cp .env.example .env

# edit local copy of .env to set TXION_DATA_DIR as the location of some txion data
vi .env

# docker-compose should build / pull / launch everything
docker-compose run --rm shell
```

# Resources
GraphML / GraphSON: https://tinkerpop.apache.org/docs/3.4.1/dev/io/
