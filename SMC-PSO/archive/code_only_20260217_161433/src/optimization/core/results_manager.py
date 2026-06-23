#======================================================================================\\\
#====================== src/optimization/core/results_manager.py ======================\\\
#======================================================================================\\\

"""
PSO Optimization Results Management and Serialization.

This module provides comprehensive management of PSO optimization results including
serialization, loading, analysis, and comparison capabilities. It ensures reproducible
optimization workflows and enables advanced result analysis.

Features:
- Comprehensive result serialization (JSON, HDF5, NPZ)
- Metadata tracking and provenance
- Result comparison and benchmarking
- Statistical analysis of optimization runs
- Convergence analysis and visualization
- Result validation and integrity checking

References:
- IEEE Standard for Software Configuration Management Plans
- Best practices for scientific computing reproducibility
"""

from __future__ import annotations

import json
import logging
import numpy as np
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import warnings

try:
    import h5py
    HDF5_AVAILABLE = True
except ImportError:
    HDF5_AVAILABLE = False

from src.utils.numerical_stability import EPSILON_DIV


@dataclass
class OptimizationMetadata:
    """Comprehensive metadata for optimization results."""
    timestamp: str
    controller_type: str
    algorithm: str
    config_hash: str
    seed: Optional[int]
    n_particles: int
    n_iterations: int
    bounds: Dict[str, Tuple[float, float]]
    convergence_criteria: Dict[str, Any]
    system_info: Dict[str, Any]
    git_commit: Optional[str] = None
    optimization_duration: Optional[float] = None
    evaluation_count: Optional[int] = None


@dataclass
class OptimizationResults:
    """Complete optimization results structure."""
    metadata: OptimizationMetadata
    best_cost: float
    best_gains: List[float]
    convergence_history: List[float]
    position_history: Optional[List[List[float]]] = None
    fitness_evaluations: Optional[List[float]] = None
    diversity_metrics: Optional[List[float]] = None
    constraint_violations: Optional[List[int]] = None
    final_population: Optional[List[List[float]]] = None
    statistics: Optional[Dict[str, Any]] = None


class OptimizationResultsManager:
    """
    Advanced management system for PSO optimization results.

    This class provides comprehensive functionality for storing, loading, analyzing,
    and comparing optimization results with full provenance tracking.
    """

    def __init__(self, results_directory: Optional[Path] = None):
        self.results_dir = Path(results_directory) if results_directory else Path("optimization_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Create subdirectories for organization
        (self.results_dir / "runs").mkdir(exist_ok=True)
        (self.results_dir / "analysis").mkdir(exist_ok=True)
        (self.results_dir / "comparisons").mkdir(exist_ok=True)

    def save_results(self, results: OptimizationResults,
                    run_id: Optional[str] = None,
                    format: str = "json") -> Path:
        """
        Save optimization results with comprehensive metadata.

        Parameters
        ----------
        results : OptimizationResults
            Complete optimization results to save
        run_id : str, optional
            Custom run identifier. If None, generates timestamp-based ID
        format : str
            Serialization format ('json', 'hdf5', 'npz')

        Returns
        -------
        Path
            Path to saved results file
        """
        if run_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_id = f"{results.metadata.controller_type}_{timestamp}"

        # Add statistics if not present
        if results.statistics is None:
            results.statistics = self._calculate_statistics(results)

        if format.lower() == "json":
            return self._save_json(results, run_id)
        elif format.lower() == "hdf5":
            return self._save_hdf5(results, run_id)
        elif format.lower() == "npz":
            return self._save_npz(results, run_id)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _save_json(self, results: OptimizationResults, run_id: str) -> Path:
        """Save results in JSON format."""
        filepath = self.results_dir / "runs" / f"{run_id}.json"

        # Convert numpy arrays to lists for JSON serialization
        serializable_results = self._make_json_serializable(results)

        with open(filepath, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)

        self.logger.info(f"Saved optimization results to {filepath}")
        return filepath

    def _save_hdf5(self, results: OptimizationResults, run_id: str) -> Path:
        """Save results in HDF5 format for large datasets."""
        if not HDF5_AVAILABLE:
            warnings.warn("HDF5 not available, falling back to NPZ format")
            return self._save_npz(results, run_id)

        filepath = self.results_dir / "runs" / f"{run_id}.h5"

        with h5py.File(filepath, 'w') as f:
            # Metadata group
            meta_grp = f.create_group('metadata')
            for key, value in asdict(results.metadata).items():
                if value is not None:
                    if isinstance(value, dict):
                        subgrp = meta_grp.create_group(key)
                        for subkey, subvalue in value.items():
                            subgrp.attrs[subkey] = subvalue
                    else:
                        meta_grp.attrs[key] = value

            # Results data
            data_grp = f.create_group('data')
            data_grp.attrs['best_cost'] = results.best_cost
            data_grp.create_dataset('best_gains', data=np.array(results.best_gains))
            data_grp.create_dataset('convergence_history', data=np.array(results.convergence_history))

            if results.position_history:
                data_grp.create_dataset('position_history', data=np.array(results.position_history))
            if results.fitness_evaluations:
                data_grp.create_dataset('fitness_evaluations', data=np.array(results.fitness_evaluations))
            if results.final_population:
                data_grp.create_dataset('final_population', data=np.array(results.final_population))

        self.logger.info(f"Saved optimization results to {filepath}")
        return filepath

    def _save_npz(self, results: OptimizationResults, run_id: str) -> Path:
        """Save results in NumPy NPZ format."""
        filepath = self.results_dir / "runs" / f"{run_id}.npz"

        # Prepare data for NPZ
        save_data = {
            'metadata': np.array([json.dumps(asdict(results.metadata))], dtype='U'),
            'best_cost': np.array([results.best_cost]),
            'best_gains': np.array(results.best_gains),
            'convergence_history': np.array(results.convergence_history)
        }

        if results.position_history:
            save_data['position_history'] = np.array(results.position_history)
        if results.fitness_evaluations:
            save_data['fitness_evaluations'] = np.array(results.fitness_evaluations)
        if results.final_population:
            save_data['final_population'] = np.array(results.final_population)
        if results.statistics:
            save_data['statistics'] = np.array([json.dumps(results.statistics)], dtype='U')

        np.savez_compressed(filepath, **save_data)

        self.logger.info(f"Saved optimization results to {filepath}")
        return filepath

    def load_results(self, filepath: Union[str, Path]) -> OptimizationResults:
        """
        Load optimization results from file.

        Parameters
        ----------
        filepath : Union[str, Path]
            Path to results file

        Returns
        -------
        OptimizationResults
            Loaded optimization results
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Results file not found: {filepath}")

        if filepath.suffix == '.json':
            return self._load_json(filepath)
        elif filepath.suffix == '.h5':
            return self._load_hdf5(filepath)
        elif filepath.suffix == '.npz':
            return self._load_npz(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")

    def _load_json(self, filepath: Path) -> OptimizationResults:
        """Load results from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Reconstruct metadata
        metadata_dict = data['metadata']
        metadata = OptimizationMetadata(**metadata_dict)

        # Reconstruct results
        results = OptimizationResults(
            metadata=metadata,
            best_cost=data['best_cost'],
            best_gains=data['best_gains'],
            convergence_history=data['convergence_history'],
            position_history=data.get('position_history'),
            fitness_evaluations=data.get('fitness_evaluations'),
            diversity_metrics=data.get('diversity_metrics'),
            constraint_violations=data.get('constraint_violations'),
            final_population=data.get('final_population'),
            statistics=data.get('statistics')
        )

        return results

    def _load_npz(self, filepath: Path) -> OptimizationResults:
        """Load results from NPZ file."""
        data = np.load(filepath, allow_pickle=True)

        # Reconstruct metadata
        metadata_dict = json.loads(str(data['metadata'][0]))
        metadata = OptimizationMetadata(**metadata_dict)

        # Reconstruct results
        results = OptimizationResults(
            metadata=metadata,
            best_cost=float(data['best_cost'][0]),
            best_gains=data['best_gains'].tolist(),
            convergence_history=data['convergence_history'].tolist(),
            position_history=data.get('position_history', np.array([])).tolist() if 'position_history' in data else None,
            fitness_evaluations=data.get('fitness_evaluations', np.array([])).tolist() if 'fitness_evaluations' in data else None,
            final_population=data.get('final_population', np.array([])).tolist() if 'final_population' in data else None,
            statistics=json.loads(str(data['statistics'][0])) if 'statistics' in data else None
        )

        return results

    def compare_results(self, result_paths: List[Union[str, Path]],
                       metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compare multiple optimization results.

        Parameters
        ----------
        result_paths : List[Union[str, Path]]
            Paths to result files to compare
        metrics : List[str], optional
            Metrics to compare ('best_cost', 'convergence_speed', 'final_diversity')

        Returns
        -------
        Dict[str, Any]
            Comparison analysis
        """
        if metrics is None:
            metrics = ['best_cost', 'convergence_speed', 'diversity', 'stability']

        results = [self.load_results(path) for path in result_paths]

        comparison = {
            'summary': {},
            'detailed_metrics': {},
            'statistical_tests': {},
            'recommendations': []
        }

        # Best cost comparison
        if 'best_cost' in metrics:
            costs = [r.best_cost for r in results]
            comparison['summary']['best_costs'] = costs
            comparison['summary']['best_overall'] = min(costs)
            comparison['summary']['worst_overall'] = max(costs)
            comparison['summary']['cost_improvement'] = (max(costs) - min(costs)) / max(costs) * 100

        # Convergence speed comparison
        if 'convergence_speed' in metrics:
            convergence_speeds = []
            for r in results:
                # Calculate iterations to 95% of final value
                final_cost = r.convergence_history[-1]
                target_cost = final_cost * 1.05  # 5% above final
                converged_iter = next((i for i, cost in enumerate(r.convergence_history)
                                     if cost <= target_cost), len(r.convergence_history))
                convergence_speeds.append(converged_iter)

            comparison['summary']['convergence_iterations'] = convergence_speeds

        # Statistical significance testing
        if len(results) >= 2:
            comparison['statistical_tests'] = self._perform_statistical_tests(results)

        # Generate recommendations
        comparison['recommendations'] = self._generate_comparison_recommendations(results, comparison)

        return comparison

    def _calculate_statistics(self, results: OptimizationResults) -> Dict[str, Any]:
        """Calculate comprehensive statistics for optimization results."""
        stats = {
            'convergence_analysis': {},
            'performance_metrics': {},
            'quality_indicators': {}
        }

        # Convergence analysis
        convergence = np.array(results.convergence_history)
        stats['convergence_analysis'] = {
            'final_cost': float(convergence[-1]),
            'initial_cost': float(convergence[0]),
            'improvement_ratio': float((convergence[0] - convergence[-1]) / convergence[0]),
            'convergence_rate': float(np.mean(np.diff(convergence))),
            'stagnation_periods': self._detect_stagnation_periods(convergence),
            'convergence_stability': float(np.std(convergence[-10:]) / np.mean(convergence[-10:]))
        }

        # Performance metrics
        stats['performance_metrics'] = {
            'total_evaluations': results.metadata.evaluation_count or len(convergence),
            'successful_convergence': convergence[-1] < convergence[0] * 0.1,
            'optimization_efficiency': float((convergence[0] - convergence[-1]) / len(convergence))
        }

        # Quality indicators
        if results.final_population:
            pop_array = np.array(results.final_population)
            stats['quality_indicators'] = {
                'population_diversity': float(np.mean(np.std(pop_array, axis=0))),
                'solution_spread': float(np.linalg.norm(np.max(pop_array, axis=0) - np.min(pop_array, axis=0))),
                'clustering_coefficient': self._calculate_clustering_coefficient(pop_array)
            }

        return stats

    def _detect_stagnation_periods(self, convergence: np.ndarray,
                                  threshold: float = 1e-6) -> List[Tuple[int, int]]:
        """Detect periods of stagnation in convergence history."""
        stagnation_periods = []
        in_stagnation = False
        start_idx = 0

        for i in range(1, len(convergence)):
            improvement = abs(convergence[i-1] - convergence[i])
            if improvement < threshold:
                if not in_stagnation:
                    start_idx = i - 1
                    in_stagnation = True
            else:
                if in_stagnation:
                    stagnation_periods.append((start_idx, i - 1))
                    in_stagnation = False

        if in_stagnation:
            stagnation_periods.append((start_idx, len(convergence) - 1))

        return stagnation_periods

    def _calculate_clustering_coefficient(self, population: np.ndarray) -> float:
        """Calculate clustering coefficient of final population."""
        if len(population) < 3:
            return 0.0

        # Simple clustering metric based on pairwise distances
        distances = []
        for i in range(len(population)):
            for j in range(i+1, len(population)):
                dist = np.linalg.norm(population[i] - population[j])
                distances.append(dist)

        mean_distance = np.mean(distances)
        std_distance = np.std(distances)

        # Issue #13: Standardized division protection
        return float(std_distance / (mean_distance + EPSILON_DIV))

    def _perform_statistical_tests(self, results: List[OptimizationResults]) -> Dict[str, Any]:
        """Perform statistical significance tests on results."""
        try:
            from scipy import stats
        except ImportError:
            return {'error': 'SciPy not available for statistical tests'}

        tests = {}

        # Collect best costs
        costs = [r.best_cost for r in results]

        if len(costs) >= 2:
            # Mann-Whitney U test for two groups
            if len(set(costs)) > 1:  # Check for variation
                statistic, p_value = stats.mannwhitneyu(costs[:len(costs)//2], costs[len(costs)//2:],
                                                       alternative='two-sided')
                tests['mann_whitney'] = {
                    'statistic': float(statistic),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }

        # Convergence rate comparison
        if len(results) >= 2:
            convergence_rates = []
            for r in results:
                convergence = np.array(r.convergence_history)
                rate = np.mean(np.abs(np.diff(convergence)))
                convergence_rates.append(rate)

            if len(set(convergence_rates)) > 1:
                var_statistic, var_p_value = stats.levene(*[np.array(r.convergence_history) for r in results])
                tests['convergence_variance'] = {
                    'statistic': float(var_statistic),
                    'p_value': float(var_p_value),
                    'significant': var_p_value < 0.05
                }

        return tests

    def _generate_comparison_recommendations(self, results: List[OptimizationResults],
                                           comparison: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on comparison analysis."""
        recommendations = []

        # Cost-based recommendations
        if 'best_costs' in comparison['summary']:
            costs = comparison['summary']['best_costs']
            cost_variation = np.std(costs) / np.mean(costs)

            if cost_variation > 0.1:
                recommendations.append(
                    "High variation in final costs suggests parameter sensitivity. "
                    "Consider multiple runs with different seeds."
                )

            if len(costs) > 1 and min(costs) < np.mean(costs) * 0.8:
                recommendations.append(
                    "One run achieved significantly better results. "
                    "Investigate configuration differences."
                )

        # Convergence-based recommendations
        if 'convergence_iterations' in comparison['summary']:
            convergence_times = comparison['summary']['convergence_iterations']
            if max(convergence_times) > min(convergence_times) * 2:
                recommendations.append(
                    "Significant differences in convergence speed detected. "
                    "Consider adaptive PSO parameters."
                )

        # Statistical test recommendations
        if 'statistical_tests' in comparison:
            tests = comparison['statistical_tests']
            if 'mann_whitney' in tests and tests['mann_whitney']['significant']:
                recommendations.append(
                    "Statistically significant differences found between runs. "
                    "Results suggest genuine performance differences."
                )

        if not recommendations:
            recommendations.append("All runs show consistent performance. Configuration appears robust.")

        return recommendations

    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert object to JSON-serializable format."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, OptimizationResults):
            return {
                'metadata': asdict(obj.metadata),
                'best_cost': obj.best_cost,
                'best_gains': obj.best_gains,
                'convergence_history': obj.convergence_history,
                'position_history': obj.position_history,
                'fitness_evaluations': obj.fitness_evaluations,
                'diversity_metrics': obj.diversity_metrics,
                'constraint_violations': obj.constraint_violations,
                'final_population': obj.final_population,
                'statistics': obj.statistics
            }
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj

    def generate_results_summary(self, run_id_pattern: str = "*") -> Dict[str, Any]:
        """Generate summary of all results matching pattern."""
        result_files = list(self.results_dir.glob(f"runs/{run_id_pattern}.*"))

        if not result_files:
            return {'error': 'No result files found'}

        summary = {
            'total_runs': len(result_files),
            'by_controller': {},
            'performance_statistics': {},
            'recent_trends': {}
        }

        all_results = []
        for filepath in result_files:
            try:
                results = self.load_results(filepath)
                all_results.append(results)
            except Exception as e:
                self.logger.warning(f"Failed to load {filepath}: {e}")

        # Group by controller type
        for results in all_results:
            ctrl_type = results.metadata.controller_type
            if ctrl_type not in summary['by_controller']:
                summary['by_controller'][ctrl_type] = {
                    'count': 0,
                    'best_cost': float('inf'),
                    'worst_cost': 0,
                    'avg_cost': 0,
                    'costs': []
                }

            ctrl_summary = summary['by_controller'][ctrl_type]
            ctrl_summary['count'] += 1
            ctrl_summary['best_cost'] = min(ctrl_summary['best_cost'], results.best_cost)
            ctrl_summary['worst_cost'] = max(ctrl_summary['worst_cost'], results.best_cost)
            ctrl_summary['costs'].append(results.best_cost)

        # Calculate averages
        for ctrl_type, ctrl_data in summary['by_controller'].items():
            ctrl_data['avg_cost'] = np.mean(ctrl_data['costs'])
            ctrl_data['std_cost'] = np.std(ctrl_data['costs'])

        return summary


def create_optimization_metadata(controller_type: str, config: Dict[str, Any],
                                seed: Optional[int] = None) -> OptimizationMetadata:
    """
    Create optimization metadata from configuration.

    Parameters
    ----------
    controller_type : str
        Type of controller being optimized
    config : Dict[str, Any]
        Configuration dictionary
    seed : int, optional
        Random seed used

    Returns
    -------
    OptimizationMetadata
        Complete metadata object
    """
    # Generate configuration hash for reproducibility
    config_str = json.dumps(config, sort_keys=True, default=str)
    config_hash = hashlib.md5(config_str.encode()).hexdigest()

    # Extract PSO configuration
    pso_config = config.get('pso', {})
    bounds_config = pso_config.get('bounds', {})

    # Create bounds dictionary
    bounds = {}
    if isinstance(bounds_config, dict):
        if 'min' in bounds_config and 'max' in bounds_config:
            for i, (min_val, max_val) in enumerate(zip(bounds_config['min'], bounds_config['max'])):
                bounds[f'param_{i}'] = (min_val, max_val)

    # Get system information
    import platform
    system_info = {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'architecture': platform.architecture()[0],
        'processor': platform.processor()
    }

    return OptimizationMetadata(
        timestamp=datetime.now().isoformat(),
        controller_type=controller_type,
        algorithm='PSO',
        config_hash=config_hash,
        seed=seed,
        n_particles=pso_config.get('n_particles', 100),
        n_iterations=pso_config.get('iters', 200),
        bounds=bounds,
        convergence_criteria={
            'max_iterations': pso_config.get('iters', 200),
            'tolerance': 1e-6
        },
        system_info=system_info
    )