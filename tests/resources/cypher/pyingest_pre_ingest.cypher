CREATE INDEX rel_range_index_name FOR ()-[r:KNOWS]-() ON (r.since);
CREATE INDEX composite_range_node_index_name FOR (n:Person) ON (n.age, n.country);