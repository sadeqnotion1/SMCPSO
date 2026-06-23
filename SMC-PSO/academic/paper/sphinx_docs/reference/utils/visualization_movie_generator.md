# utils.visualization.movie_generator

**Source:** `src\utils\visualization\movie_generator.py`

## Module Overview Complete

visualization plan for the entire DIP control project

. Provides movie generation features for documenting


and presenting the complete control engineering project with professional
quality animations and analysis visualizations. ## Complete Source Code ```{literalinclude} ../../../src/utils/visualization/movie_generator.py
:language: python
:linenos:
```

---

## Classes

### `MovieScene`

Configuration for a movie scene.

#### Source Code ```

{literalinclude} ../../../src/utils/visualization/movie_generator.py
:language: python
:pyobject: MovieScene
:linenos:
```

---

## `ProjectMovieGenerator`

Complete visualization plan generator for the entire DIP control project. Creates professional-quality movies that document:

- System dynamics and behavior
- Control algorithm performance
- Comparison studies
- Optimization results
- Statistical analysis #### Source Code ```{literalinclude} ../../../src/utils/visualization/movie_generator.py
:language: python
:pyobject: ProjectMovieGenerator
:linenos:
``` #### Methods (15) ##### `__init__(self, output_dir)` Initialize movie generator. [View full source →](#method-projectmoviegenerator-__init__) ##### `create_complete_project_movie(self, project_data, movie_title, fps)` Create a complete movie documenting the entire project. [View full source →](#method-projectmoviegenerator-create_complete_project_movie) ##### `_create_movie_scenes(self, project_data)` Create all movie scenes for the complete project documentation. [View full source →](#method-projectmoviegenerator-_create_movie_scenes) ##### `_compile_scenes_to_movie(self, scenes, output_path, fps)` Compile all scenes into a single movie file. [View full source →](#method-projectmoviegenerator-_compile_scenes_to_movie) ##### `_create_animation_scene(self, scene, output_path, fps)` Create an animated scene. [View full source →](#method-projectmoviegenerator-_create_animation_scene) ##### `_create_static_scene(self, scene, output_path, fps)` Create a static information scene. [View full source →](#method-projectmoviegenerator-_create_static_scene) ##### `_create_comparison_scene(self, scene, output_path, fps)` Create a controller comparison scene. [View full source →](#method-projectmoviegenerator-_create_comparison_scene) ##### `_create_analysis_scene(self, scene, output_path, fps)` Create an analysis visualization scene. [View full source →](#method-projectmoviegenerator-_create_analysis_scene) ##### `_create_optimization_analysis(self, fig, data)` Create PSO optimization analysis plots. [View full source →](#method-projectmoviegenerator-_create_optimization_analysis) ##### `_create_statistical_analysis(self, fig, data)` Create statistical analysis plots. [View full source →](#method-projectmoviegenerator-_create_statistical_analysis) ##### `_format_project_info(self, info)` Format project information for display. [View full source →](#method-projectmoviegenerator-_format_project_info) ##### `_merge_videos(self, video_files, output_path)` Merge multiple video files using ffmpeg. [View full source →](#method-projectmoviegenerator-_merge_videos) ##### `create_project_trailer(self, project_data, duration)` Create a short trailer/summary of the project. [View full source →](#method-projectmoviegenerator-create_project_trailer) ##### `_extract_highlights(self, project_data)` Extract highlight results for trailer. [View full source →](#method-projectmoviegenerator-_extract_highlights) ##### `_summarize_results(self, project_data)` Summarize key project results. [View full source →](#method-projectmoviegenerator-_summarize_results)

---

## Dependencies This module imports: - `from __future__ import annotations`
- `import matplotlib.pyplot as plt`
- `import matplotlib.animation as animation`
- `import numpy as np`
- `from typing import List, Dict, Any, Optional, Tuple`
- `import os`
- `from dataclasses import dataclass`
- `from .animation import DIPAnimator, MultiSystemAnimator`
- `from .static_plots import ControlPlotter, SystemVisualization` ## Architecture Diagram ```{mermaid}
graph TD A[Component] --> B[Subcomponent 1] A --> C[Subcomponent 2] B --> D[Output] C --> D style A fill:#e1f5ff style D fill:#e8f5e9
``` ## Usage Examples ### Example 1: Basic Usage ```python
# Basic usage example

from src.utils import Component component = Component()
result = component.process(data)
``` ### Example 2: Advanced Configuration ```python
# Advanced configuration
component = Component( option1=value1, option2=value2
)
``` ### Example 3: Integration with Framework ```python
# Integration example

from src.simulation import SimulationRunner runner = SimulationRunner()
runner.use_component(component)
``` ### Example 4: Performance Optimization ```python
# Performance-optimized usage
component = Component(enable_caching=True)
``` ### Example 5: Error Handling ```python
# Error handling

try: result = component.process(data)
except ComponentError as e: print(f"Error: {e}")
```
