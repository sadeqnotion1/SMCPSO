"""
Exercise 5 Solution: Controller Selection for Application
==========================================================

Select best controller for high-disturbance mobile robot.

Author: DIP-SMC-PSO Development Team
Date: November 12, 2025
"""


def analyze_requirements():
    """Analyze application requirements and recommend controller."""
    print("[INFO] Exercise 5: Controller Selection")
    print("[INFO] Application: Mobile robot, high-disturbance environment")

    print("\n[REQUIREMENTS]")
    print("  1. High disturbances: ±50N forces (frequent collisions)")
    print("  2. Moderate uncertainty: ±15% payload variation")
    print("  3. Energy constraint: Battery-powered (prefer efficiency)")
    print("  4. Smoothness preference: Passenger comfort")

    print("\n[CONTROLLER EVALUATION]")

    controllers = {
        'Classical SMC': {
            'disturbance_rejection': 'FAIR',
            'uncertainty_handling': 'FAIR',
            'energy_efficiency': 'GOOD',
            'smoothness': 'FAIR'
        },
        'STA SMC': {
            'disturbance_rejection': 'GOOD',
            'uncertainty_handling': 'GOOD',
            'energy_efficiency': 'GOOD',
            'smoothness': 'EXCELLENT'
        },
        'Adaptive SMC': {
            'disturbance_rejection': 'EXCELLENT',
            'uncertainty_handling': 'EXCELLENT',
            'energy_efficiency': 'FAIR',
            'smoothness': 'GOOD'
        },
        'Hybrid STA': {
            'disturbance_rejection': 'EXCELLENT',
            'uncertainty_handling': 'EXCELLENT',
            'energy_efficiency': 'FAIR',
            'smoothness': 'EXCELLENT'
        }
    }

    for name, metrics in controllers.items():
        print(f"\n  {name}:")
        print(f"    Disturbance Rejection: {metrics['disturbance_rejection']}")
        print(f"    Uncertainty Handling: {metrics['uncertainty_handling']}")
        print(f"    Energy Efficiency: {metrics['energy_efficiency']}")
        print(f"    Smoothness: {metrics['smoothness']}")

    print("\n[DECISION TREE]")
    print("  High Disturbances? YES")
    print("    → Moderate Uncertainty? YES")
    print("      → Energy Critical? NO (acceptable compromise)")
    print("        → Smoothness Preferred? YES")
    print("          → SELECTION: Hybrid Adaptive STA")

    print("\n[RECOMMENDATION]")
    recommendation = """
For the mobile robot application with high disturbances (±50N collisions) and
moderate uncertainty (±15% payload variation), I recommend the **Hybrid Adaptive STA**
controller. This controller provides EXCELLENT disturbance rejection and uncertainty
handling while maintaining EXCELLENT smoothness for passenger comfort. Although energy
efficiency is rated as FAIR, the battery constraint is not critical enough to outweigh
the performance and comfort benefits. The super-twisting algorithm reduces chattering
compared to classical SMC, while the adaptive component ensures robustness across the
entire payload range. Alternative: Pure Adaptive SMC if energy efficiency becomes more
critical, but smoothness will be slightly compromised.
    """
    print(recommendation.strip())

    return 'Hybrid Adaptive STA', recommendation


if __name__ == "__main__":
    selected_controller, reasoning = analyze_requirements()
    print(f"\n[SELECTED CONTROLLER]: {selected_controller}")
    print("\n[SUCCESS] Exercise 5 complete!")
