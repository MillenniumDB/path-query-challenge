Not all SPARQL property path queries can be written as a cypher graph pattern.

We generated a set with all the queries that can be expressed with a cypher graph pattern (`default`), and then we generated a subset with the cypher patterns that can go inside operators like `shortestPath` and `allShortestPaths`.