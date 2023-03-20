Instructions for replicate the experiments in MillenniumDB

## Compile MillenniumDB
- clone the [MillenniumDB repository](https://github.com/MillenniumDB/MillenniumDB/tree/path_query_challenge) at the `path_query_challenge` branch
    - `git clone -b path_query_challenge git@github.com:MillenniumDB/MillenniumDB.git`
- Follow the instructions on the [README](https://github.com/MillenniumDB/MillenniumDB/blob/path_query_challenge/README.md) to build the project.

## Database creation
- Transform the [N-Triples File](https://www.w3.org/TR/n-triples/) downloaded from [Figshare](https://figshare.com/s/50b7544ad6b1f51de060) to the text format for MillenniumDB:
    - `python3 scripts/nt_to_mdb.py truthy_direct_properties.nt truthy_direct_properties.mdb`

- Execute the bulk loading:
    - `build/Release/bin/create_db truthy_direct_properties.mdb tests/dbs/wikidata`

## Execute query set
Before executing the script you need to edit some paths to match the correct folders on your machine:
```python
MDB_PATH = f'/home/user/MillenniumDB' # where you cloned MillenniumDB repo
OUTPUT_PATH = f'/home/user/results'   # results and logs will be written here, folder must exist
```

Then you can run the script choosing the desired parameters:
- `python3 scripts/benchmark_mdb.py [query_file] [ANY|SIMPLE|TRAILS|ALL|ALL_COUNT] [bfs|dfs] [cache|naive] [btree|trie]`

    for example:
    - `python3 scripts/benchmark_mdb.py queries/set_I.txt ANY bfs cache btree`

### Considerations for the parameters
- The param block `[ANY|SIMPLE|TRAILS|ALL|ALL_COUNT]` selects the desired semantics of returned paths. Here `ALL` stands for `ALL SHORTEST`. The semantics of `ANY` will depend on the selected algorithm (see `[bfs|dfs]` below).

- The param block `[btree|trie]` selects the data access method. The `btree` option uses the disk data stored in B+trees and buffered into main memory. The `trie` option stores the data in main memory using a compact sparse array representation. The `trie` is constructed on the fly as needed.

- The param block `[cache|naive]` tells us whether the in-memory representation is loaded each time a new query is fired (`naive`), or if we cache previously loaded relations (`cache`).

- The param bloc `[bfs|dfs]` selects the algorithm applied to evaluate the queries. Note that `bfs` combined with `ANY` gives a single shortest path, while `dfs` with `ANY` gives an arbitrary path.

- The param `dfs` is only considered when using `ANY|SIMPLE|TRAILS`, because `ALL|ALL_COUNT` don't have an dfs implementation.

- The params `[cache|naive]` are only considered when using `trie`. They don't have any impact when using `btree`.

