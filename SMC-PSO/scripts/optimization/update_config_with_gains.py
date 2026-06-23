#==========================================================================================\\\
#=================== scripts/optimization/update_config_with_gains.py ====================\\\
#==========================================================================================\\\

"""
Update config.yaml with optimized gains from PSO results.

Reads gains_*_chattering.json files and updates config.yaml controllers section.
"""

import json
import yaml
import sys
from pathlib import Path
from datetime import datetime

def load_optimized_gains():
    """Load all optimized gains from JSON files."""
    controllers = ['classical_smc', 'adaptive_smc', 'sta_smc']
    gains_data = {}

    for ctrl in controllers:
        json_file = Path(f'gains_{ctrl}_chattering.json')

        if not json_file.exists():
            print(f"Warning: {json_file} not found, skipping {ctrl}")
            continue

        try:
            with open(json_file) as f:
                data = json.load(f)

            gains = data.get('gains')
            metrics = data.get('metrics', {})
            chattering = metrics.get('chattering_index')

            if gains:
                gains_data[ctrl] = {
                    'gains': gains,
                    'chattering': chattering,
                    'timestamp': data.get('timestamp', 'unknown')
                }
                print(f"✓ Loaded {ctrl}: gains={gains}, chattering={chattering:.3f}")
            else:
                print(f"✗ {ctrl}: No gains found in JSON")

        except Exception as e:
            print(f"✗ Error loading {ctrl}: {e}")

    return gains_data

def update_config(gains_data, dry_run=False):
    """Update config.yaml with optimized gains."""
    config_file = Path('config.yaml')

    if not config_file.exists():
        print("✗ config.yaml not found!")
        return False

    # Backup original
    if not dry_run:
        backup_file = f".archive/config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        Path(backup_file).parent.mkdir(parents=True, exist_ok=True)

        with open(config_file) as f:
            with open(backup_file, 'w') as bf:
                bf.write(f.read())

        print(f"✓ Backup saved: {backup_file}")

    # Load config
    with open(config_file) as f:
        config = yaml.safe_load(f)

    # Update gains in both controllers and controller_defaults
    if 'controllers' not in config:
        config['controllers'] = {}
    if 'controller_defaults' not in config:
        config['controller_defaults'] = {}

    updated_count = 0
    for ctrl, data in gains_data.items():
        # Update controllers section
        if ctrl not in config['controllers']:
            config['controllers'][ctrl] = {}

        # Update controller_defaults section
        if ctrl not in config['controller_defaults']:
            config['controller_defaults'][ctrl] = {}

        # Store old gains for comparison
        old_gains_ctrl = config['controllers'][ctrl].get('gains', [])
        old_gains_default = config['controller_defaults'][ctrl].get('gains', [])

        # Update with new gains (both locations)
        config['controllers'][ctrl]['gains'] = data['gains']
        config['controller_defaults'][ctrl]['gains'] = data['gains']

        print(f"\n{ctrl}:")
        print(f"  Old gains (controllers): {old_gains_ctrl}")
        print(f"  Old gains (defaults):    {old_gains_default}")
        print(f"  New gains:               {data['gains']}")
        print(f"  Chattering index:        {data['chattering']:.3f}")

        updated_count += 1

    # Save updated config
    if not dry_run:
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        print(f"\n✓ Updated config.yaml with {updated_count} controllers")
        return True
    else:
        print(f"\n[DRY RUN] Would update {updated_count} controllers")
        return True

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Update config.yaml with optimized PSO gains"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without actually updating'
    )

    args = parser.parse_args()

    print("="*80)
    print("CONFIG UPDATE SCRIPT - Issue #12")
    print("="*80)
    print()

    # Load optimized gains
    gains_data = load_optimized_gains()

    if not gains_data:
        print("\n✗ No optimized gains found!")
        print("Make sure PSO optimization has completed and JSON files exist.")
        sys.exit(1)

    print(f"\nFound {len(gains_data)} controllers with optimized gains")

    # Update config
    print("\n" + "="*80)
    print("Updating config.yaml...")
    print("="*80)

    success = update_config(gains_data, dry_run=args.dry_run)

    if success:
        if not args.dry_run:
            print("\n✓✓✓ CONFIG UPDATE COMPLETE ✓✓✓")
            print("\nNext steps:")
            print("1. Verify changes: git diff config.yaml")
            print("2. Test with updated config: python simulate.py --ctrl classical_smc")
            print("3. Commit: git add config.yaml && git commit")
        else:
            print("\n[DRY RUN] No files were modified")
            print("Run without --dry-run to actually update config.yaml")

        sys.exit(0)
    else:
        print("\n✗ Config update failed")
        sys.exit(1)

if __name__ == '__main__':
    main()