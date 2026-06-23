#!/usr/bin/env python3
"""Render .agents/graph/graph.json into a self-contained offline graph.html.

Stdlib only (no third-party dependencies). Usage:
    python .agents/graph/render_graph.py
    python .agents/graph/render_graph.py --in graph.json --out graph.html
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from string import Template

HERE = Path(__file__).resolve().parent

# Template uses $-placeholders (string.Template) so literal CSS/JS braces need no escaping.
_HTML = Template("""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>$title \u2014 knowledge graph</title>
<style>
  body { margin:0; background:#0b0f1a; color:#cdd6f4; font:14px/1.4 system-ui, sans-serif; }
  header { padding:12px 16px; border-bottom:1px solid #1e2536; }
  header b { color:#89b4fa; }
  #canvas { width:100vw; height:calc(100vh - 52px); display:block; }
  .hint { color:#6c7086; font-size:12px; }
</style></head>
<body>
<header><b>$title</b> knowledge graph
  <span class="hint">\u2014 $n_nodes nodes, $n_edges edges \u00b7 drag to pan \u00b7 scroll to zoom</span>
</header>
<canvas id="canvas"></canvas>
<script>
const NODES = $nodes_js;
const EDGES = $edges_js;
const cv = document.getElementById('canvas');
const ctx = cv.getContext('2d');
function resize() { cv.width = innerWidth; cv.height = innerHeight - 52; }
resize(); addEventListener('resize', () => { resize(); layout(); draw(); });
const idx = {}; NODES.forEach((n, i) => idx[n.id] = i);
function layout() {
  const R = Math.min(cv.width, cv.height) * 0.36;
  NODES.forEach((n, i) => {
    const a = (i / NODES.length) * Math.PI * 2;
    n._x = Math.cos(a) * R; n._y = Math.sin(a) * R;
  });
}
let zoom = 1, panx = 0, pany = 0, drag = null;
cv.addEventListener('mousedown', e => drag = { x: e.clientX, y: e.clientY, px: panx, py: pany });
addEventListener('mouseup', () => drag = null);
addEventListener('mousemove', e => {
  if (!drag) return;
  panx = drag.px + (e.clientX - drag.x);
  pany = drag.py + (e.clientY - drag.y);
  draw();
});
cv.addEventListener('wheel', e => {
  e.preventDefault();
  zoom *= e.deltaY < 0 ? 1.1 : 0.9;
  zoom = Math.max(0.3, Math.min(4, zoom));
  draw();
}, { passive: false });
function pos(n) {
  return [cv.width / 2 + panx + n._x * zoom, cv.height / 2 + pany + n._y * zoom];
}
function draw() {
  ctx.clearRect(0, 0, cv.width, cv.height);
  ctx.strokeStyle = '#313244'; ctx.lineWidth = 1; ctx.font = '12px system-ui';
  EDGES.forEach(e => {
    const a = NODES[idx[e.from]], b = NODES[idx[e.to]];
    if (!a || !b) return;
    const pa = pos(a), pb = pos(b);
    ctx.beginPath(); ctx.moveTo(pa[0], pa[1]); ctx.lineTo(pb[0], pb[1]); ctx.stroke();
    if (e.rel) { ctx.fillStyle = '#6c7086'; ctx.fillText(e.rel, (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2); }
  });
  NODES.forEach(n => {
    const p = pos(n);
    ctx.beginPath(); ctx.arc(p[0], p[1], 6, 0, Math.PI * 2);
    ctx.fillStyle = '#89b4fa'; ctx.fill();
    ctx.fillStyle = '#cdd6f4'; ctx.fillText(n.id, p[0] + 9, p[1] + 4);
  });
}
layout(); draw();
</script>
</body></html>
""")


def build_html(graph: dict) -> str:
    meta = graph.get("meta", {})
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    return _HTML.substitute(
        title=html.escape(str(meta.get("project", "repo"))),
        n_nodes=len(nodes),
        n_edges=len(edges),
        nodes_js=json.dumps(nodes),
        edges_js=json.dumps(edges),
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Render graph.json to graph.html")
    ap.add_argument("--in", dest="inp", default=str(HERE / "graph.json"))
    ap.add_argument("--out", dest="out", default=str(HERE / "graph.html"))
    args = ap.parse_args()
    graph = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    Path(args.out).write_text(build_html(graph), encoding="utf-8")
    print("Wrote %s (%d nodes, %d edges)" % (args.out, len(graph.get("nodes", [])), len(graph.get("edges", []))))


if __name__ == "__main__":
    main()
