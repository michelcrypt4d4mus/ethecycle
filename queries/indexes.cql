// Create index (not sure this is the right one)
//   TODO: maybe create an index on wallet creation date and/or first txion block_number?
//   TODO: needs more research but seems like two separate indexes will work better than one composite:
//         https://neo4j.com/docs/cypher-manual/5/indexes-for-search-performance/#administration-indexes-single-vs-composite-index
//   TODO: run this when docker setup happens?

// Index txns on block_number
CREATE RANGE INDEX idx_txn_block_number IF NOT EXISTS
FOR ()-[r:TXN]-()
ON (r.block_number);

// Index txns on num_tokens
CREATE RANGE INDEX idx_txn_num_tokens IF NOT EXISTS
FOR ()-[r:TXN]-()
ON (r.num_tokens)
