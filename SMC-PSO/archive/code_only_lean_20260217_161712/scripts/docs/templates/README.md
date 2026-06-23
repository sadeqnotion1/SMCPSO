# Documentation Templates

This directory contains Jinja2 templates for automated documentation generation.

## Templates

### 1. `module_template.md`

**Purpose**: Document entire Python modules with embedded source code

**Variables**:
- `{module_name}`: Module name (e.g., "controllers.smc.classical")
- `{module_docstring}`: Extracted module-level docstring
- `{relative_path}`: Path to source file relative to docs/
- `{module_path}`: Full module path
- `{submodule_list}`: List of submodules (auto-generated)
- `{class_list}`: List of classes with summaries
- `{function_list}`: List of functions with summaries
- `{constants_list}`: Module-level constants
- `{usage_examples}`: Code examples from docstrings or tests
- `{dependencies_list}`: Import dependencies
- `{cross_references}`: Links to related modules
- `{loc}`: Lines of code count
- `{last_modified}`: Last modification timestamp

**Placeholders** (for manual completion):
- `{architecture_diagram_placeholder}`: Add Mermaid diagrams in Weeks 6-7
- `{detailed_components}`: Detailed explanations (Weeks 2-5)

### 2. `class_template.md`

**Purpose**: Document classes with mathematical foundations and usage examples

**Variables**:
- `{class_name}`: Class name
- `{class_docstring}`: Extracted class docstring
- `{file_path}`: Source file path
- `{line_number}`: Line number where class is defined
- `{constructor_signature}`: `__init__` method signature with types
- `{parameter_table}`: Markdown table of parameters
- `{methods_documentation}`: Auto-generated method summaries
- `{attributes_documentation}`: Class and instance attributes
- `{initialization_example}`: Example class instantiation
- `{basic_usage_example}`: Simple usage pattern
- `{advanced_usage_example}`: Advanced usage pattern
- `{base_classes}`: Parent classes
- `{known_subclasses}`: Child classes (if any)
- `{time_complexity}`: O(...) notation
- `{space_complexity}`: O(...) notation
- `{typical_runtime}`: Empirical performance data

**Placeholders**:
- `{theory_section_placeholder}`: Mathematical foundations (Week 8)
- `{inheritance_diagram}`: UML class diagrams (Week 7)

### 3. `function_template.md`

**Purpose**: Document functions with algorithm explanations and line-by-line commentary

**Variables**:
- `{function_name}`: Function name
- `{function_signature}`: Full signature with type hints
- `{function_docstring}`: Extracted docstring
- `{file_path}`: Source file path
- `{line_number}`: Line number where function is defined
- `{parameter_table}`: Markdown table of parameters with types
- `{return_documentation}`: Return value description
- `{usage_example}`: Minimal working example
- `{edge_cases}`: Known edge cases and handling
- `{exceptions_documentation}`: Exceptions that may be raised
- `{related_functions}`: Cross-references to similar functions
- `{function_type}`: "Module function", "Static method", "Class method", etc.
- `{key_lines}`: Line numbers to emphasize (algorithm core)

**Placeholders**:
- `{algorithm_description}`: High-level algorithm explanation
- `{line_by_line_explanation}`: Detailed code walkthrough

## Usage

### With Documentation Generator

```bash
# Generate documentation for entire module
python scripts/docs/generate_code_docs.py --module controllers

# Generate for specific file
python scripts/docs/generate_code_docs.py --file src/controllers/smc/classical/controller.py

# Generate all documentation
python scripts/docs/generate_code_docs.py --all
```

### Manual Template Rendering

```python
from jinja2 import Environment, FileSystemLoader
import ast

# Load template
env = Environment(loader=FileSystemLoader('scripts/docs/templates'))
template = env.get_template('module_template.md')

# Prepare context from AST analysis
context = {
    'module_name': 'controllers.smc.classical',
    'module_docstring': extract_module_docstring('src/controllers/smc/classical/controller.py'),
    'relative_path': '../../../src/controllers/smc/classical/controller.py',
    # ... other variables
}

# Render
output = template.render(context)

# Save
with open('docs/reference/controllers/smc/classical/controller.md', 'w') as f:
    f.write(output)
```

## Variable Extraction Guidelines

### AST Parsing
```python
import ast

def extract_classes(source_code):
    """Extract class definitions from Python source."""
    tree = ast.parse(source_code)
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({
                'name': node.name,
                'docstring': ast.get_docstring(node),
                'line_number': node.lineno,
                'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
            })
    return classes
```

### Docstring Extraction
```python
def extract_module_docstring(file_path):
    """Extract module-level docstring."""
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    return ast.get_docstring(tree) or "No module docstring available."
```

### Parameter Tables
```python
def generate_parameter_table(function_node):
    """Generate markdown table from function parameters."""
    args = function_node.args
    params = []
    for arg in args.args:
        param_name = arg.arg
        annotation = ast.unparse(arg.annotation) if arg.annotation else 'Any'
        params.append(f"| `{param_name}` | `{annotation}` | TODO |")

    table = "| Parameter | Type | Description |\n"
    table += "|-----------|------|-------------|\n"
    table += "\n".join(params)
    return table
```

## Template Customization

### Adding New Placeholders

1. Add placeholder to template: `{new_placeholder}`
2. Update extraction logic in generator script
3. Document in this README

### Conditional Sections

Use Jinja2 conditionals for optional content:

```markdown
{% if has_mathematical_theory %}
## Mathematical Foundations
{mathematical_theory}
{% endif %}
```

## Quality Standards

### Complete Templates Must Have:

1. **Full source code**: Always use literalinclude directive
2. **Working examples**: All code examples must be runnable
3. **Type information**: Use type hints from source code
4. **Cross-references**: Link to related components
5. **Performance data**: Include complexity analysis

### Optional Sections (Placeholders):

1. **Theory sections**: Mathematical foundations (Week 8)
2. **Diagrams**: Architecture and UML (Week 7)
3. **Advanced examples**: Domain-specific tutorials (Week 6)

## Testing Templates

```bash
# Validate template syntax
python -c "from jinja2 import Environment, FileSystemLoader; \
           env = Environment(loader=FileSystemLoader('scripts/docs/templates')); \
           env.get_template('module_template.md')"

# Test rendering with sample data
python scripts/docs/test_templates.py
```

## Version History

- **v1.0** (2025-10-03): Initial templates for Week 1 automation
- Planned: v1.1 with theory section templates (Week 8)
- Planned: v1.2 with diagram integration (Week 7)
