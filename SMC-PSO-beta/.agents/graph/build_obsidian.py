#!/usr/bin/env python3
"""
build_obsidian.py -- Convert graph.json into a highly polished, interactive Obsidian vault.

Generates:
1. Markdown files organized by kind with premium Callouts and local clickable code links.
2. An interactive visual map using Obsidian Canvas (SMC-PSO-beta.canvas).
3. A Welcome.md dashboard featuring live Mermaid diagrams and statistics.
4. Pre-configured .obsidian files to enforce a dark theme layout.
"""

import json
import re
import shutil
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
GRAPH_JSON = HERE / "graph.json"
VAULT_DIR = HERE / "SMCSPSO"
PROJECT_ROOT = Path("E:/Projects/University/SMC-PSO-beta")

def sanitize_filename(name: str) -> str:
    """Replace Windows-forbidden characters and spaces with a single underscore."""
    sanitized = re.sub(r'[\\/:*?"<>|\s]+', '_', name)
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('_')
    return sanitized or "empty_id"

def clean_vault_except_config():
    """Remove previously generated folders, markdown, and canvas files, preserving .obsidian configs."""
    if not VAULT_DIR.exists():
        return
        
    for item in VAULT_DIR.iterdir():
        if item.is_dir():
            if item.name == ".obsidian":
                continue
            try:
                shutil.rmtree(item)
            except Exception as e:
                print(f"Warning: Could not remove directory {item}: {e}")
        elif item.is_file():
            if item.suffix.lower() in (".md", ".canvas"):
                item.unlink(missing_ok=True)

def format_label(node_id: str) -> str:
    """Format node ID to a beautiful title, handling common acronyms."""
    acronyms = {"cli": "CLI", "pso": "PSO", "hil": "HIL", "dip": "DIP", "sta": "STA", "fdi": "FDI", "smc": "SMC"}
    parts = node_id.split('_')
    formatted_parts = []
    for p in parts:
        if p.lower() in acronyms:
            formatted_parts.append(acronyms[p.lower()])
        else:
            formatted_parts.append(p.capitalize())
    return " ".join(formatted_parts)

def write_obsidian_settings():
    """Write preconfigured theme files to ensure Obsidian launches in dark mode."""
    obsidian_dir = VAULT_DIR / ".obsidian"
    obsidian_dir.mkdir(parents=True, exist_ok=True)
    
    appearance = {
        "theme": "obsidian",
        "themeMode": "dark",
        "accentColor": "#89b4fa"
    }
    app_settings = {
        "theme": "obsidian",
        "legacyLayout": False
    }
    
    (obsidian_dir / "appearance.json").write_text(json.dumps(appearance, indent=2), encoding="utf-8")
    (obsidian_dir / "app.json").write_text(json.dumps(app_settings, indent=2), encoding="utf-8")

def main():
    if not GRAPH_JSON.exists():
        print(f"Error: graph.json not found at {GRAPH_JSON}")
        sys.exit(1)
        
    try:
        graph = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error parsing graph.json: {e}")
        sys.exit(1)

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    meta = graph.get("meta", {})
    
    print(f"Loaded graph: {len(nodes)} nodes, {len(edges)} edges.")
    
    # Calculate degree dynamically
    degrees = {n.get("id"): 0 for n in nodes if n.get("id")}
    for e in edges:
        s = e.get("from") or e.get("source")
        t = e.get("to") or e.get("target")
        if s in degrees:
            degrees[s] += 1
        if t in degrees:
            degrees[t] += 1
            
    # Clean up and prepare vault structure
    clean_vault_except_config()
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    write_obsidian_settings()
    
    # Map node IDs to paths and sanitized filenames
    id_to_filename = {}
    id_to_rel_path = {}
    used_filenames = set()
    
    for n in nodes:
        node_id = n.get("id")
        if not node_id:
            continue
        base = sanitize_filename(node_id)
        candidate = base
        counter = 1
        while candidate.lower() in used_filenames:
            candidate = f"{base}_{counter}"
            counter += 1
        used_filenames.add(candidate.lower())
        id_to_filename[node_id] = candidate
        
        community = n.get("kind", "module")
        id_to_rel_path[node_id] = f"{community}/{candidate}.md"

    # Build incoming and outgoing maps
    outgoing = {n.get("id"): [] for n in nodes if n.get("id")}
    incoming = {n.get("id"): [] for n in nodes if n.get("id")}
    
    for e in edges:
        s = e.get("from") or e.get("source")
        t = e.get("to") or e.get("target")
        if not s or not t:
            continue
        if s not in outgoing:
            outgoing[s] = []
        if t not in incoming:
            incoming[t] = []
        outgoing[s].append(e)
        incoming[t].append(e)

    # 4. Generate markdown file for each node
    for n in nodes:
        node_id = n.get("id")
        if not node_id or node_id not in id_to_filename:
            continue
            
        filename = id_to_filename[node_id]
        community = n.get("kind", "module")
        community_folder_name = sanitize_filename(community)
        community_dir = VAULT_DIR / community_folder_name
        community_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = community_dir / f"{filename}.md"
        
        label = format_label(node_id)
        node_type = n.get("kind", "unknown")
        location = n.get("path", "")
        degree = degrees.get(node_id, 0)
        summary = n.get("desc", "")
        
        # Clickable local file link if file exists
        local_link_str = ""
        if location:
            # Clean location string for paths (remove wildcard/multiple files)
            first_path_part = location.split("+")[0].strip()
            absolute_code_path = PROJECT_ROOT / first_path_part
            local_link_str = f" ([open file](file:///{absolute_code_path.as_posix()}))"

        lines = [
            "---",
            f"id: \"{node_id}\"",
            f"label: \"{label}\"",
            f"type: \"{node_type}\"",
            f"community: \"{community}\"",
            f"location: \"{location}\"",
            f"degree: {degree}",
            "---",
            "",
            f"# {label}",
            "",
            f"> [!abstract] Description",
            f"> {summary or '*No description available.*'}",
            "",
            f"> [!info] Metadata",
            f"> - **Kind/Type**: `{node_type}`",
            f"> - **Location**: `{location}`{local_link_str}",
            f"> - **Degree**: `{degree}`",
            "",
            "## Outgoing Connections",
            ""
        ]
        
        out_edges = outgoing.get(node_id, [])
        if out_edges:
            for oe in out_edges:
                target_id = oe.get("to") or oe.get("target")
                edge_rel = oe.get("rel", "references")
                
                target_node = next((node for node in nodes if node.get("id") == target_id), None)
                target_label = format_label(target_id) if target_node else target_id
                
                if target_id in id_to_filename:
                    target_file = id_to_filename[target_id]
                    link = f"[[{target_file}|{target_label}]]"
                else:
                    link = f"`{target_label}` (external)"
                
                lines.append(f"- {link} (relation: `{edge_rel}`)")
        else:
            lines.append("*None*")
        lines.append("")
        
        lines.append("## Incoming Connections")
        lines.append("")
        in_edges = incoming.get(node_id, [])
        if in_edges:
            for ie in in_edges:
                source_id = ie.get("from") or ie.get("source")
                edge_rel = ie.get("rel", "references")
                
                source_node = next((node for node in nodes if node.get("id") == source_id), None)
                source_label = format_label(source_id) if source_node else source_id
                
                if source_id in id_to_filename:
                    source_file = id_to_filename[source_id]
                    link = f"[[{source_file}|{source_label}]]"
                else:
                    link = f"`{source_label}` (external)"
                
                lines.append(f"- {link} (relation: `{edge_rel}`)")
        else:
            lines.append("*None*")
            
        filepath.write_text("\n".join(lines), encoding="utf-8")

    # 5. Generate Welcome.md dashboard
    communities_nodes = {}
    for n in nodes:
        node_id = n.get("id")
        if not node_id or node_id not in id_to_filename:
            continue
        community = n.get("kind", "module")
        communities_nodes.setdefault(community, []).append(n)
        
    sorted_nodes_by_degree = sorted(
        [n for n in nodes if n.get("id") in id_to_filename],
        key=lambda x: degrees.get(x.get("id"), 0),
        reverse=True
    )
    god_nodes = sorted_nodes_by_degree[:6]

    # Generate Mermaid block
    mermaid_lines = ["```mermaid", "flowchart TD"]
    for n in nodes:
        node_id = n.get("id")
        label = format_label(node_id)
        kind = n.get("kind", "module")
        
        # Shapes based on Kind
        if kind == "entrypoint":
            mermaid_lines.append(f"    {node_id}([{label}])")
        elif kind == "controller":
            mermaid_lines.append(f"    {node_id}{{{label}}}")
        elif kind == "config":
            mermaid_lines.append(f"    {node_id}[/{label}/]")
        else:
            mermaid_lines.append(f"    {node_id}[{label}]")

    for e in edges:
        s = e.get("from") or e.get("source")
        t = e.get("to") or e.get("target")
        rel = e.get("rel", "")
        if s and t:
            mermaid_lines.append(f"    {s} -- {rel} --> {t}")
    mermaid_lines.append("```")

    welcome_lines = [
        f"# {meta.get('project', 'SMC-PSO')} Architecture Dashboard",
        "",
        "Welcome to the interactive Obsidian representation of the **SMC-PSO-beta** codebase.",
        "",
        "> [!info] Vault Statistics",
        f"> - **Nodes**: {len(nodes)} (code modules/layers)",
        f"- **Edges**: {len(edges)} (import & structural relationships)",
        f"- **Generated**: `{meta.get('generated', 'N/A')}`",
        "",
        "---",
        "",
        "## Visual System Map",
        "Double-click any box below (in Reading view) to preview relations:",
        "",
        "\n".join(mermaid_lines),
        "",
        "---",
        "",
        "> [!star] Key Hubs (Most Connected Modules)",
    ]
    
    for gn in god_nodes:
        gn_id = gn.get("id")
        gn_file = id_to_filename[gn_id]
        gn_label = format_label(gn_id)
        gn_type = gn.get("kind", "unknown")
        gn_degree = degrees.get(gn_id, 0)
        gn_desc = gn.get("desc", "")
        gn_desc_short = gn_desc[:120] + "..." if len(gn_desc) > 120 else gn_desc
        welcome_lines.append(f"- [[{gn_file}|{gn_label}]] (`{gn_type}`, degree: {gn_degree}) — {gn_desc_short}")
        
    welcome_lines.extend([
        "",
        "---",
        "",
        "## System Layers & Folders",
    ])
    
    for comm in sorted(communities_nodes.keys()):
        comm_nodes = communities_nodes[comm]
        comm_folder = sanitize_filename(comm)
        welcome_lines.append(f"### [[{comm_folder}/|{comm.title()}]] ({len(comm_nodes)} nodes)")
        sorted_comm_nodes = sorted(comm_nodes, key=lambda x: degrees.get(x.get("id"), 0), reverse=True)[:5]
        links = []
        for cn in sorted_comm_nodes:
            cn_id = cn.get("id")
            cn_file = id_to_filename[cn_id]
            cn_label = format_label(cn_id)
            links.append(f"[[{cn_file}|{cn_label}]]")
        welcome_lines.append("  " + " · ".join(links))
        
    welcome_lines.extend([
        "",
        "---",
        "",
        "## Quick Tips",
        "1. **Obsidian Canvas**: Check the [[SMC-PSO-beta.canvas|Visual white-board canvas]] for an interactive, layed-out diagram.",
        "2. **Graph View**: Open `Ctrl + G` inside Obsidian to see an active simulation of your imports.",
        "3. **Local File Links**: Clicking the `[open file]` links in node metadata will launch that file in your IDE directly.",
    ])
    
    welcome_file = VAULT_DIR / "Welcome.md"
    welcome_file.write_text("\n".join(welcome_lines), encoding="utf-8")

    # 6. Generate Obsidian Canvas (.canvas JSON format)
    # Define a clean layered layout for the 17 nodes
    layer_map = {
        "config": 0,
        "entrypoint": 1,
        "controller": 3,
        "module": 5 # Modules are split up by ID categories below
    }
    
    # Refined layering
    layer_assignments = {
        "config": 0,
        "cli": 1,
        "web": 1,
        "factory": 2,
        "smc_classical": 3,
        "smc_sta": 3,
        "smc_adaptive": 3,
        "smc_hybrid": 3,
        "pso": 4,
        "cost": 4,
        "runner": 5,
        "vector_sim": 5,
        "safety_guards": 5,
        "plant_models": 6,
        "analysis": 6,
        "hil": 6,
        "utils": 6
    }
    
    # Colors: 1=red, 2=orange, 3=yellow, 4=green, 5=cyan, 6=purple
    color_assignments = {
        "entrypoint": "5",   # Cyan
        "config": "3",       # Yellow
        "controller": "6",   # Purple
        # Modules
        "factory": "2",      # Orange
        "pso": "1",          # Red
        "cost": "1",         # Red
        "runner": "4",       # Green
        "vector_sim": "4",   # Green
        "safety_guards": "4",# Green
        "plant_models": "2", # Orange
        "analysis": "2",     # Orange
        "hil": "2",          # Orange
        "utils": "2"         # Orange
    }

    # Group by layer for position calculations
    layer_columns = {i: [] for i in range(7)}
    for n in nodes:
        node_id = n.get("id")
        if not node_id:
            continue
        l = layer_assignments.get(node_id, 5)
        layer_columns[l].append(node_id)
        
    canvas_nodes = []
    # Position mappings for edges
    node_positions = {}
    
    card_width = 250
    card_height = 130
    x_gap = 400
    y_gap = 200

    for col_idx, node_ids in layer_columns.items():
        node_ids.sort()
        num_nodes = len(node_ids)
        for row_idx, node_id in enumerate(node_ids):
            x = col_idx * x_gap
            y = (row_idx - (num_nodes - 1) / 2) * y_gap
            
            # Find kind for color
            node_data = next((node for node in nodes if node.get("id") == node_id), {})
            kind = node_data.get("kind", "module")
            color = color_assignments.get(node_id, color_assignments.get(kind, "2"))
            
            canvas_nodes.append({
                "id": node_id,
                "type": "file",
                "file": id_to_rel_path[node_id],
                "x": int(x),
                "y": int(y),
                "width": card_width,
                "height": card_height,
                "color": color
            })
            node_positions[node_id] = {"x": x, "y": y}

    canvas_edges = []
    edge_counter = 1
    for e in edges:
        s = e.get("from") or e.get("source")
        t = e.get("to") or e.get("target")
        rel = e.get("rel", "")
        if not s or not t or s not in node_positions or t not in node_positions:
            continue
            
        pos_s = node_positions[s]
        pos_t = node_positions[t]
        
        # Decide connecting sides based on positions
        if pos_s["x"] < pos_t["x"]:
            from_side = "right"
            to_side = "left"
        elif pos_s["x"] > pos_t["x"]:
            from_side = "left"
            to_side = "right"
        else:
            if pos_s["y"] < pos_t["y"]:
                from_side = "bottom"
                to_side = "top"
            else:
                from_side = "top"
                to_side = "bottom"

        canvas_edges.append({
            "id": f"edge_{edge_counter}",
            "fromNode": s,
            "fromSide": from_side,
            "toNode": t,
            "toSide": to_side,
            "label": rel
        })
        edge_counter += 1

    canvas_json = {
        "nodes": canvas_nodes,
        "edges": canvas_edges
    }
    
    canvas_file = VAULT_DIR / "SMC-PSO-beta.canvas"
    canvas_file.write_text(json.dumps(canvas_json, indent=2), encoding="utf-8")
    
    print(f"Generated SMC-PSO-beta.canvas visual board at {canvas_file}")
    print("Obsidian vault settings written to .obsidian/")
    print("Obsidian vault regeneration complete!")

if __name__ == "__main__":
    main()
