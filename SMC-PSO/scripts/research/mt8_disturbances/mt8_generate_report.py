"""
MT-8 Report Generator: Create Comprehensive Disturbance Rejection Report

Generates a complete markdown report comparing baseline and robust PSO performance:
- Executive summary with key improvements
- Detailed controller-by-controller analysis
- Statistical validation results
- Performance comparison tables
- Success criteria assessment

Usage:
    python scripts/mt8_generate_report.py
    python scripts/mt8_generate_report.py --output benchmarks/MT8_COMPLETE_REPORT.md
    python scripts/mt8_generate_report.py --baseline benchmarks/MT8_disturbance_rejection.json --validation benchmarks/MT8_robust_validation_all.json
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_baseline_results(filepath: str) -> Dict:
    """Load baseline disturbance rejection results."""
    with open(filepath, 'r') as f:
        return json.load(f)


def load_validation_results(filepath: str) -> Dict:
    """Load robust PSO validation results."""
    with open(filepath, 'r') as f:
        return json.load(f)


def load_pso_summary(filepath: str) -> Dict:
    """Load PSO optimization summary."""
    with open(filepath, 'r') as f:
        return json.load(f)


def generate_executive_summary(
    baseline: Dict,
    validation: Dict,
    pso_summary: Dict
) -> str:
    """Generate executive summary section."""

    summary = []
    summary.append("# MT-8: Disturbance Rejection Analysis - Complete Report")
    summary.append("")
    summary.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("")
    summary.append("## Executive Summary")
    summary.append("")

    # Count total success/failure
    total_controllers = len(validation)
    scenarios = ['step', 'impulse', 'sinusoidal', 'random']

    # Aggregate statistics
    total_scenarios = total_controllers * len(scenarios)
    successful_scenarios = 0
    avg_convergence = 0.0
    avg_overshoot_improvement = 0.0

    for controller, data in validation.items():
        for scenario in scenarios:
            if scenario in data['validation']:
                conv_rate = data['validation'][scenario]['convergence_rate']
                successful_scenarios += (1 if conv_rate >= 0.95 else 0)
                avg_convergence += conv_rate

            if scenario in data.get('comparison_to_baseline', {}):
                avg_overshoot_improvement += data['comparison_to_baseline'][scenario]['overshoot_improvement_pct']

    avg_convergence /= total_scenarios
    avg_overshoot_improvement /= total_scenarios

    summary.append(f"**Controllers Tested:** {total_controllers}")
    summary.append(f"**Disturbance Scenarios:** {len(scenarios)}")
    summary.append(f"**Total Test Cases:** {total_scenarios}")
    summary.append(f"**Successful (≥95% convergence):** {successful_scenarios}/{total_scenarios} ({successful_scenarios/total_scenarios*100:.1f}%)")
    summary.append("")
    summary.append(f"**Average Convergence Rate:** {avg_convergence*100:.1f}%")
    summary.append(f"**Average Overshoot Improvement:** {avg_overshoot_improvement:+.1f}%")
    summary.append("")

    # PSO optimization details
    summary.append("### Optimization Parameters")
    summary.append("")
    summary.append(f"- **Algorithm:** Robust PSO (PySwarms)")
    summary.append(f"- **Particles:** {pso_summary.get('particles', 30)}")
    summary.append(f"- **Iterations:** {pso_summary.get('iterations', 50)}")
    summary.append(f"- **Fitness Function:** 50% nominal + 50% disturbed (step + impulse)")
    summary.append(f"- **Total Optimizations:** {len(pso_summary.get('results', []))}")
    summary.append("")

    return "\n".join(summary)


def generate_controller_analysis(
    controller_name: str,
    baseline: Dict,
    validation: Dict
) -> str:
    """Generate detailed analysis for a single controller."""

    analysis = []
    analysis.append(f"## {controller_name}")
    analysis.append("")

    # Extract baseline results for this controller
    baseline_results = {}
    for result in baseline['results']:
        if result['controller_name'] == controller_name:
            baseline_results[result['disturbance_type']] = result

    # Gains
    gains = validation[controller_name]['gains']
    analysis.append("### Optimized Gains")
    analysis.append("")
    analysis.append("```")
    for i, gain in enumerate(gains):
        analysis.append(f"  k{i+1} = {gain:.4f}")
    analysis.append("```")
    analysis.append("")

    # Performance table
    analysis.append("### Performance Comparison")
    analysis.append("")
    analysis.append("| Scenario | Baseline Overshoot | Robust Overshoot | Improvement | Convergence |")
    analysis.append("|----------|-------------------:|------------------:|------------:|------------:|")

    val_data = validation[controller_name]['validation']
    comp_data = validation[controller_name].get('comparison_to_baseline', {})

    for scenario in ['step', 'impulse', 'sinusoidal', 'random']:
        if scenario in baseline_results and scenario in val_data:
            baseline_os = baseline_results[scenario]['max_overshoot']
            robust_os = val_data[scenario]['overshoot_mean']
            robust_std = val_data[scenario]['overshoot_std']
            conv_rate = val_data[scenario]['convergence_rate']

            improvement = comp_data.get(scenario, {}).get('overshoot_improvement_pct', 0.0)

            analysis.append(
                f"| {scenario.capitalize():10s} | {baseline_os:12.1f}° | "
                f"{robust_os:9.1f} ± {robust_std:.1f}° | "
                f"{improvement:+9.1f}% | {conv_rate*100:9.1f}% |"
            )

    analysis.append("")

    # Detailed metrics
    analysis.append("### Detailed Metrics (Mean ± Std)")
    analysis.append("")

    for scenario in ['step', 'impulse', 'sinusoidal', 'random']:
        if scenario in val_data:
            data = val_data[scenario]
            analysis.append(f"**{scenario.capitalize()} Disturbance:**")
            analysis.append(f"- Settling Time: {data['settling_time_mean']:.2f} ± {data['settling_time_std']:.2f} s")
            analysis.append(f"- Overshoot: {data['overshoot_mean']:.2f} ± {data['overshoot_std']:.2f}°")
            analysis.append(f"- Recovery Time: {data['recovery_time_mean']:.2f} ± {data['recovery_time_std']:.2f} s")
            analysis.append(f"- Control Effort: {data['control_effort_mean']:.2f} ± {data['control_effort_std']:.2f}")
            analysis.append(f"- Convergence Rate: {data['convergence_rate']*100:.1f}% ({int(data['convergence_rate']*data['num_trials'])}/{data['num_trials']} trials)")
            analysis.append("")

    return "\n".join(analysis)


def generate_success_criteria(validation: Dict) -> str:
    """Generate success criteria assessment section."""

    criteria = []
    criteria.append("## Success Criteria Assessment")
    criteria.append("")
    criteria.append("### Target Metrics")
    criteria.append("")
    criteria.append("| Criterion | Target | Status |")
    criteria.append("|-----------|--------|--------|")

    # Compute aggregate statistics
    scenarios = ['step', 'impulse', 'sinusoidal', 'random']
    total_tests = len(validation) * len(scenarios)

    # Convergence rate
    convergence_rates = []
    for controller, data in validation.items():
        for scenario in scenarios:
            if scenario in data['validation']:
                convergence_rates.append(data['validation'][scenario]['convergence_rate'])

    avg_convergence = sum(convergence_rates) / len(convergence_rates)
    convergence_status = "[OK]" if avg_convergence >= 0.95 else "[WARNING]" if avg_convergence >= 0.80 else "[ERROR]"

    criteria.append(f"| Convergence Rate | ≥95% | {avg_convergence*100:.1f}% {convergence_status} |")

    # Overshoot reduction
    overshoot_improvements = []
    for controller, data in validation.items():
        for scenario in scenarios:
            if scenario in data.get('comparison_to_baseline', {}):
                overshoot_improvements.append(
                    data['comparison_to_baseline'][scenario]['overshoot_improvement_pct']
                )

    avg_overshoot_improvement = sum(overshoot_improvements) / len(overshoot_improvements)
    overshoot_status = "[OK]" if avg_overshoot_improvement > 50 else "[WARNING]" if avg_overshoot_improvement > 30 else "[INFO]"

    criteria.append(f"| Overshoot Reduction | >50% | {avg_overshoot_improvement:+.1f}% {overshoot_status} |")

    # Settling time
    settling_times = []
    for controller, data in validation.items():
        for scenario in scenarios:
            if scenario in data['validation']:
                settling_times.append(data['validation'][scenario]['settling_time_mean'])

    avg_settling = sum(settling_times) / len(settling_times)
    settling_status = "[OK]" if avg_settling < 3.0 else "[WARNING]" if avg_settling < 5.0 else "[ERROR]"

    criteria.append(f"| Settling Time | <3.0s | {avg_settling:.2f}s {settling_status} |")

    criteria.append("")

    # Overall assessment
    all_ok = (avg_convergence >= 0.95 and avg_overshoot_improvement > 50 and avg_settling < 3.0)
    partial_ok = (avg_convergence >= 0.80 and avg_overshoot_improvement > 30 and avg_settling < 5.0)

    criteria.append("### Overall Status")
    criteria.append("")
    if all_ok:
        criteria.append("[OK] **MT-8 COMPLETE:** All success criteria met. Disturbance rejection validated.")
    elif partial_ok:
        criteria.append("[WARNING] **MT-8 PARTIAL:** Some criteria met. Further tuning recommended.")
    else:
        criteria.append("[ERROR] **MT-8 INCOMPLETE:** Success criteria not met. Additional optimization required.")

    criteria.append("")

    return "\n".join(criteria)


def generate_recommendations(validation: Dict) -> str:
    """Generate recommendations and next steps."""

    recs = []
    recs.append("## Recommendations")
    recs.append("")

    # Analyze which controllers performed best/worst
    controller_scores = {}
    scenarios = ['step', 'impulse', 'sinusoidal', 'random']

    for controller, data in validation.items():
        total_conv = 0.0
        for scenario in scenarios:
            if scenario in data['validation']:
                total_conv += data['validation'][scenario]['convergence_rate']
        controller_scores[controller] = total_conv / len(scenarios)

    best_controller = max(controller_scores, key=controller_scores.get)
    worst_controller = min(controller_scores, key=controller_scores.get)

    recs.append(f"**Best Performing Controller:** {best_controller} ({controller_scores[best_controller]*100:.1f}% avg convergence)")
    recs.append(f"**Worst Performing Controller:** {worst_controller} ({controller_scores[worst_controller]*100:.1f}% avg convergence)")
    recs.append("")

    # Specific recommendations
    recs.append("### For Production Use:")
    recs.append("")
    recs.append(f"1. **Recommended Controller:** {best_controller}")
    recs.append("2. **Gain Tuning:** Use robust PSO gains from this optimization")
    recs.append("3. **Validation:** Run 1000-trial Monte Carlo before deployment")
    recs.append("4. **Monitoring:** Track convergence rate and overshoot in real-time")
    recs.append("")

    # Future work
    recs.append("### Future Work:")
    recs.append("")
    recs.append("1. Test with additional disturbance magnitudes (5N, 15N, 20N)")
    recs.append("2. Multi-objective PSO (Pareto frontier for settling vs overshoot)")
    recs.append("3. Adaptive gain scheduling based on disturbance detection")
    recs.append("4. Hardware-in-the-loop validation with real disturbances")
    recs.append("")

    return "\n".join(recs)


def main():
    parser = argparse.ArgumentParser(description='MT-8 Report Generator')
    parser.add_argument(
        '--baseline',
        type=str,
        default='benchmarks/MT8_disturbance_rejection.json',
        help='Baseline results file'
    )
    parser.add_argument(
        '--validation',
        type=str,
        default='benchmarks/MT8_robust_validation_all.json',
        help='Robust validation results file'
    )
    parser.add_argument(
        '--pso-summary',
        type=str,
        default='optimization_results/mt8_robust_pso_summary.json',
        help='PSO optimization summary file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='benchmarks/MT8_COMPLETE_REPORT.md',
        help='Output markdown file'
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("MT-8: Report Generator")
    logger.info("=" * 80)

    # Load all data
    logger.info(f"Loading baseline from: {args.baseline}")
    baseline = load_baseline_results(args.baseline)

    logger.info(f"Loading validation from: {args.validation}")
    validation = load_validation_results(args.validation)

    logger.info(f"Loading PSO summary from: {args.pso_summary}")
    pso_summary = load_pso_summary(args.pso_summary)

    # Generate report sections
    logger.info("Generating report sections...")

    sections = []

    # Executive summary
    sections.append(generate_executive_summary(baseline, validation, pso_summary))
    sections.append("")

    # Controller-by-controller analysis
    for controller_name in sorted(validation.keys()):
        sections.append(generate_controller_analysis(controller_name, baseline, validation))
        sections.append("")

    # Success criteria
    sections.append(generate_success_criteria(validation))
    sections.append("")

    # Recommendations
    sections.append(generate_recommendations(validation))

    # Write report
    report_content = "\n".join(sections)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(report_content)

    logger.info(f"Report saved to: {args.output}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
