# graph/ — repo knowledge graph

`graph.json` is a compact map of the codebase. **Query it; never dump it whole.**

## Schema

- `meta`  : { project, version, generated (YYYY-MM-DD), note }
- `nodes` : [ { id, kind, path, desc } ]
- `edges` : [ { from, to, rel } ]

- **kind**: `entrypoint` · `module` · `controller` · `config`.
- **rel** (examples): `creates`, `configures`, `instantiates`, `runs_in`, `simulates`,
  `uses`, `tuned_by`, `evaluates`, `drives`, `feeds`, `optional`.

## Query recipes (jq)

```bash
# What does the factory connect to?
jq '.edges[] | select(.from=="factory")' graph.json

# Where does X live?
jq '.nodes[] | select(.id=="runner") | .path' graph.json

# All controllers
jq '.nodes[] | select(.kind=="controller") | .id' graph.json

# Everything that feeds the simulation runner
jq '.edges[] | select(.to=="runner")' graph.json
```

## Visual

```bash
python .agents/graph/render_graph.py   # -> graph.html (open in any browser, offline)
```

## Maintenance

- Update `graph.json` whenever module structure changes, then regenerate `graph.html`.
- Keep it small — nodes/edges that matter for "what calls what", not every file.
