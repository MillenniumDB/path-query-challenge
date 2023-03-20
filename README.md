# Challenges
Each challenge consist in a dataset and a set of path queries to be executed in a graph database.
Each query can be executed under any of the following path semantics:
- **Endpoints**:
    - For queries where the start and end nodes of the path are fixed, this is just true/false.
    - For queries where only the start node of the path is fixed, this returns all nodes that are reachable from that node via property path.
    - For queries where neither the start or end nodes are fixed, this returns all pairs of nodes
connected by the property path.
- **Any path**: For each answer returned by endpoints, we also provide a single
path witnessing this result.

- **Shortest path**: For each answer returned by **endpoints**, we also provide a
single shortest path witnessing this result.

- **All shortest paths**: For each answer returned by **endpoints**, we also return
all shortest paths witnessing this result.

- **All trails**: For each answer returned by **endpoints**, we also return all trails
(i.e. paths not repeating any edges) witnessing this result.

- **All simple paths**: For each answer returned by **endpoints**, we also return all simple paths (i.e. paths not repeating any nodes) witnessing this result.

We also provide an implementation that can execute queries with at least one fixed node under any of the path semantics mentioned before. [This document](/MDB.md) explains how to execute path queries on MillenniumDB.

# Challenge 1

## Dataset
The data is a [N-Triples File](https://www.w3.org/TR/n-triples/) available to download from [Figshare](https://figshare.com/s/50b7544ad6b1f51de060).

## Queries
The queries are from the benchmark [WDBench](https://github.com/MillenniumDB/WDBench) and you can find them in the `queries` folder of this repository.

# Challenge 2
## Dataset
The data is a graph of diamonds that can be generate with [this script](/scripts/generate_diamond.py), the first parameter is how many diamonds will be generated, and the second parameter is the output type (NT|NEO4J|MDB). Example:
- `python3 scripts/generate_diamond.py 1000 NT`

## Queries
We have only one query, which is the transitive closure. In SPARQL the property path is:
```
<http://ex.cl/N0> <http://ex.cl/A>* ?x
```
And in cypher the query is:
```
MATCH p=( ({id:"N0"})-[:A*0..]->(x) ) RETURN p
```