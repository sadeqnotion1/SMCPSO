# HIL Disaster Recovery Guide

**Business Continuity and Incident Response for Production HIL Systems**

**Version:** 1.0
**Date:** 2025-11-10
**Status:** Complete (replaces stub from 2025-10-07)

---

## Executive Summary

**What This Guide Covers:**
This guide provides disaster recovery (DR) procedures for production Hardware-in-the-Loop (HIL) systems. When something goes wrong, you need a plan to recover quickly. Common disasters include hardware failure, network outage, and power loss. A good DR plan minimizes downtime, prevents data loss, and gets your system back online fast.

**Who Should Read This:**
- Operations engineers managing production HIL systems
- DevOps teams responsible for keeping systems running
- Incident response teams who handle emergencies

**What You Need to Know First:**
- Understanding of [HIL Production Checklist](hil-production-checklist.md) - basic production setup
- Familiarity with [HIL Safety Validation](hil-safety-validation.md) - safety procedures

**Key Recovery Targets:**
These metrics define how fast you need to recover from different types of incidents.

- **RTO (Recovery Time Objective):** <15 minutes
  - Maximum time the system can be down before business impact
  - Example: After hardware failure, you have 15 minutes to switch to backup

- **RPO (Recovery Point Objective):** <5 minutes data loss
  - Maximum acceptable data loss measured in time
  - Example: Lose at most the last 5 minutes of experimental data

- **MTTR (Mean Time To Repair):** <30 minutes
  - Average time to fix and restore full operation
  - Example: Most incidents resolved within 30 minutes

**Why These Targets Matter:**
Production HIL systems often run continuous experiments. Even brief downtime can invalidate hours of data collection. For example, a 30-minute outage during a 4-hour test means starting over. Fast recovery preserves your work and maintains system reliability.

---

## Part 1: Disaster Classification

**Why Classification Matters:**
Not all problems are equal. A complete power failure needs immediate action. A single sensor glitch can wait. This classification system helps you respond appropriately based on severity.

### 1.1 Severity Levels

Understanding severity levels helps you decide how urgently to respond and who to notify.

**Level 1: Critical (Red) - Drop Everything**
Signs you're seeing a critical incident:
- Complete system outage (nothing works)
- Hardware damage risk (smoke, unusual sounds, extreme temps)
- Data loss imminent (disk full, corrupted state)

**What to Do:**
Immediate escalation + emergency shutdown. Don't try to save data. Protect the hardware first.

**Level 2: Major (Orange) - Act Within 15 Minutes**
Signs you're seeing a major incident:
- Degraded performance (system running at less than 50% capacity)
- Network connectivity issues (frequent disconnects)
- Controller malfunction (control loop unstable)

**What to Do:**
Escalate to on-call engineer within 15 minutes. System is degraded but not destroyed. You have time to diagnose properly.

**Level 3: Minor (Yellow) - Log and Schedule**
Signs you're seeing a minor incident:
- Transient errors (occasional glitches that self-correct)
- Single component failure with redundancy (backup is working)
- Performance degradation (less than 50% capacity loss)

**What to Do:**
Monitor and log the issue. Schedule repair during the next maintenance window. No urgent action needed.

### 1.2 Disaster Scenarios

| Scenario | Severity | RTO | Recovery Procedure |
|----------|----------|-----|-------------------|
| Hardware failure (plant) | Critical | 15 min | Switch to backup hardware |
| Hardware failure (controller) | Major | 10 min | Restart on standby server |
| Network outage | Critical | 5 min | Failover to backup network |
| Power loss | Critical | 2 min | UPS + graceful shutdown |
| Software crash | Major | 3 min | Automatic restart from checkpoint |
| Data corruption | Major | 10 min | Restore from last backup |
| Configuration error | Minor | 5 min | Rollback to previous config |
| Cyber attack | Critical | Varies | Isolate + forensics + rebuild |

---

## Part 2: Backup Strategies

**Why Backups Matter:**
Backups are your insurance policy. When disaster strikes, you need to restore configuration and data quickly. This section shows you how to automate backups so you never lose critical information.

**Three Types of Backups:**
1. **Configuration Backups** - Save your settings (config files, gains, parameters)
2. **State Checkpoints** - Save the running state (so you can resume mid-experiment)
3. **Data Logging** - Save experimental results (your valuable research data)

### 2.1 Configuration Backups

**What Gets Backed Up:**
Configuration files define how your system runs. This includes controller gains, simulation parameters, and environment settings. If you lose these, you'll have to reconfigure everything from scratch.

**Automated Backup Script:**
This bash script runs automatically every 4 hours. It saves your configuration files, compresses them, and deletes old backups after 30 days.

```bash
#!/bin/bash
# /opt/hil/scripts/backup_config.sh

BACKUP_DIR="/opt/hil/backups/config"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup config files
cp config.yaml "${BACKUP_DIR}/config_${TIMESTAMP}.yaml"
cp optimization_results/production_gains.json "${BACKUP_DIR}/gains_${TIMESTAMP}.json"

# Backup git commit hash
git rev-parse HEAD > "${BACKUP_DIR}/git_commit_${TIMESTAMP}.txt"

# Compress and archive
tar -czf "${BACKUP_DIR}/config_backup_${TIMESTAMP}.tar.gz" \
  config.yaml \
  optimization_results/production_gains.json \
  .env

# Retain last 30 days
find "${BACKUP_DIR}" -name "*.tar.gz" -mtime +30 -delete
```

**Cron Schedule:**

```bash
# Backup config every 4 hours
0 */4 * * * /opt/hil/scripts/backup_config.sh

# Daily offsite sync
0 2 * * * rsync -avz /opt/hil/backups/ backup-server:/hil-backups/
```

### 2.2 State Checkpointing

**What State Checkpointing Does:**
Imagine running a 4-hour experiment. At hour 3, the system crashes.

Without checkpoints, you start from zero and lose all 3 hours of work. With checkpoints saved every minute, you resume from hour 2:59 and only lose 1 minute. Checkpointing saves time and preserves data.

**How It Works:**
The checkpoint manager saves the system state to disk every 60 seconds. This includes pendulum angles, velocities, and controller gains. If the system crashes and restarts, it loads the most recent checkpoint and continues from there.

**Implementation:**
This Python class handles automatic checkpointing. It tracks when the last checkpoint was saved and saves a new one every 60 seconds (configurable).

```python
import json
import time

class HILCheckpoint:
    def __init__(self, checkpoint_interval=60.0):
        self.checkpoint_interval = checkpoint_interval
        self.last_checkpoint = time.time()

    def should_checkpoint(self):
        return (time.time() - self.last_checkpoint) > self.checkpoint_interval

    def save_checkpoint(self, state, controller_state, simulation_time):
        checkpoint = {
            'timestamp': time.time(),
            'simulation_time': simulation_time,
            'system_state': state.tolist(),
            'controller_state': controller_state,
            'controller_type': controller_state.get('type'),
            'adaptive_gain': controller_state.get('K', None)
        }

        with open('/tmp/hil_checkpoint.json', 'w') as f:
            json.dump(checkpoint, f)

        self.last_checkpoint = time.time()

    def load_checkpoint(self):
        try:
            with open('/tmp/hil_checkpoint.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
```

**Usage Example:**

```python
checkpoint_mgr = HILCheckpoint(checkpoint_interval=60.0)  # Every 60s

for step in range(num_steps):
    # Normal operation
    u = controller.compute_control(state)

    # Periodic checkpointing
    if checkpoint_mgr.should_checkpoint():
        checkpoint_mgr.save_checkpoint(
            state=state,
            controller_state=controller.get_state(),
            simulation_time=step * dt
        )
```

### 2.3 Data Logging Redundancy

**Why Dual Logging:**
Your experimental data is irreplaceable. Controller performance metrics, sensor readings, and test results represent hours or days of work.

Dual logging writes data to two locations simultaneously. If one storage device fails, you still have the other copy. This redundancy protects against hardware failure.

**How Dual Logging Works:**
The system writes data to two locations: local disk and network storage. Local disk is fast and immediate. Network storage is slower but survives local hardware failure.

Both logs run in parallel. If network storage is slow or unavailable, the local log continues working. This ensures you never lose data due to network issues.

**Implementation:**

```python
# Primary: Local disk
logger_local = DataLogger('/opt/hil/data/run_{timestamp}.npz')

# Secondary: Network storage
logger_network = DataLogger('//backup-server/hil-data/run_{timestamp}.npz')

# Log to both
for step in range(num_steps):
    logger_local.log(time, state, control)
    logger_network.log(time, state, control)  # Asynchronous
```

---

## Part 3: Recovery Procedures

**Why Order of Operations Matters:**
Recovery steps must follow a specific sequence. Doing them out of order can corrupt data or cause safety hazards. Always verify each step completes successfully before moving to the next. This systematic approach prevents cascading failures.

**Recovery Strategy:**
Detect → Stop → Assess → Restore → Validate → Resume

### 3.1 Hardware Failure Recovery

**Plant Server Failure:**

```bash
# Detection
if ! ping -c 1 plant-server >/dev/null 2>&1; then
    echo "Plant server unreachable - initiating failover"

    # Automatic failover to backup
    export HIL_PLANT_IP=192.168.1.101  # Backup plant server
    python simulate.py --run-hil --resume-from-checkpoint

    # Alert operations
    send_alert "Plant failover to backup (192.168.1.101)"
fi
```

**Controller Server Failure:**

```bash
# Watchdog detects controller crash
systemctl status hil-controller || {
    echo "Controller crashed - restarting from checkpoint"

    # Load last checkpoint
    CHECKPOINT=$(ls -t /tmp/hil_checkpoint*.json | head -1)

    # Restart controller
    systemctl start hil-controller --checkpoint=${CHECKPOINT}

    # Verify recovery
    sleep 5
    if systemctl is-active hil-controller; then
        echo "Recovery successful"
    else
        echo "Recovery failed - escalating"
        page_oncall_engineer
    fi
}
```

### 3.2 Network Outage Recovery

**Automatic Network Failover:**

```python
def handle_network_outage():
    """
    Detect and recover from network outages
    """
    # Detection: No state received for 2× control period
    timeout_threshold = 2 * dt

    if time_since_last_packet() > timeout_threshold:
        logger.warning("Network timeout detected")

        # Try backup network interface
        switch_to_backup_network()

        # Wait for reconnection
        reconnect_timeout = 5.0  # seconds
        if wait_for_reconnection(timeout=reconnect_timeout):
            logger.info("Reconnected via backup network")
            return True
        else:
            logger.error("Backup network also failed - emergency stop")
            trigger_emergency_stop()
            return False
```

### 3.3 Configuration Rollback

**Automated Rollback:**

```bash
#!/bin/bash
# rollback_config.sh

# List available backups
echo "Available config backups:"
ls -lt /opt/hil/backups/config/*.tar.gz | head -10

# Prompt for selection
read -p "Select backup timestamp (YYYYmmdd_HHMMSS): " TIMESTAMP

# Restore backup
BACKUP_FILE="/opt/hil/backups/config/config_backup_${TIMESTAMP}.tar.gz"

if [ -f "$BACKUP_FILE" ]; then
    # Stop HIL system
    systemctl stop hil-controller
    systemctl stop hil-plant

    # Backup current config (just in case)
    cp config.yaml config.yaml.before_rollback

    # Extract backup
    tar -xzf "$BACKUP_FILE"

    # Restart HIL system
    systemctl start hil-plant
    sleep 2
    systemctl start hil-controller

    echo "Rollback complete - verify system operation"
else
    echo "Backup file not found: $BACKUP_FILE"
    exit 1
fi
```

### 3.4 Data Recovery

**Restore Corrupted Data:**

```python
def recover_corrupted_data(corrupted_file):
    """
    Attempt to recover data from corrupted .npz file
    """
    import numpy as np

    try:
        # Try direct load
        data = np.load(corrupted_file, allow_pickle=True)
        return data
    except Exception as e:
        logger.warning(f"Direct load failed: {e}")

        # Try loading from backup
        backup_file = corrupted_file.replace('.npz', '_backup.npz')
        if os.path.exists(backup_file):
            logger.info(f"Loading from backup: {backup_file}")
            return np.load(backup_file)

        # Try partial recovery
        logger.warning("Attempting partial recovery")
        return attempt_partial_recovery(corrupted_file)
```

---

## Part 4: Failover Mechanisms

**Why Automatic Failover Needs Testing:**
Automatic failover sounds great until it fails when you need it most. Untested failover mechanisms often have hidden bugs that only appear during real disasters. Regular testing ensures your backup systems actually work under pressure.

**Failover Types:**
- **Hot Standby**: Backup runs continuously, instant switch (0-second downtime)
- **Warm Standby**: Backup on but idle, quick start (5-30 second downtime)
- **Cold Standby**: Backup off, manual start (1-5 minute downtime)

### 4.1 Hot Standby Configuration

**Primary-Standby Setup:**

```yaml
# /etc/hil/cluster.yaml
cluster:
  primary:
    plant_ip: 192.168.1.100
    controller_ip: 192.168.1.50
    priority: 100

  standby:
    plant_ip: 192.168.1.101
    controller_ip: 192.168.1.51
    priority: 50

  failover:
    health_check_interval: 5  # seconds
    failover_threshold: 3      # failed checks before failover
    automatic: true
```

**Failover Logic:**

```python
class FailoverManager:
    def __init__(self, primary, standby, threshold=3):
        self.primary = primary
        self.standby = standby
        self.threshold = threshold
        self.failed_checks = 0
        self.current_active = 'primary'

    def health_check(self):
        """Check if primary is responsive"""
        try:
            response = ping(self.primary['plant_ip'], timeout=1.0)
            if response:
                self.failed_checks = 0
                return True
            else:
                self.failed_checks += 1
                return False
        except Exception:
            self.failed_checks += 1
            return False

    def should_failover(self):
        return self.failed_checks >= self.threshold

    def execute_failover(self):
        """Switch to standby system"""
        logger.critical(f"Failing over to standby after {self.failed_checks} failures")

        # Update active endpoints
        os.environ['HIL_PLANT_IP'] = self.standby['plant_ip']
        os.environ['HIL_CONTROLLER_IP'] = self.standby['controller_ip']

        # Restart HIL with new endpoints
        restart_hil_system()

        self.current_active = 'standby'
        self.failed_checks = 0

        # Alert operations
        send_alert(f"Failover to standby completed")
```

### 4.2 Load Balancing (Multi-Plant)

**For Parallel Testing:**

```python
plants = [
    {'ip': '192.168.1.100', 'status': 'active'},
    {'ip': '192.168.1.101', 'status': 'active'},
    {'ip': '192.168.1.102', 'status': 'active'}
]

def select_plant():
    """Round-robin load balancing"""
    active_plants = [p for p in plants if p['status'] == 'active']
    if not active_plants:
        raise RuntimeError("No active plants available")

    # Simple round-robin
    plant = active_plants[next_plant_index % len(active_plants)]
    return plant['ip']
```

---

## Part 5: Disaster Recovery Drills

### 5.1 Drill Schedule

**Quarterly Drills:**

| Quarter | Drill Type | Duration | Participants |
|---------|-----------|----------|--------------|
| Q1 | Hardware failure | 1 hour | Ops + DevOps |
| Q2 | Network outage | 30 min | Ops + Network |
| Q3 | Configuration rollback | 30 min | Ops |
| Q4 | Full disaster (combined) | 2 hours | All teams |

### 5.2 Hardware Failure Drill

**Procedure:**

```bash
# 1. Announce drill
echo "DRILL: Simulating plant server failure at $(date)"

# 2. Simulate failure (disconnect network)
sudo iptables -A INPUT -s 192.168.1.100 -j DROP
sudo iptables -A OUTPUT -d 192.168.1.100 -j DROP

# 3. Observe failover
# - Controller should detect timeout within 2× control period
# - Failover to backup should complete within 15 minutes

# 4. Restore connectivity
sudo iptables -F

# 5. Verify recovery
python scripts/validation/verify_hil_health.py

# 6. Document results
echo "Failover time: XX minutes" >> drill_results.txt
```

**Success Criteria:**
- Failover detected within 30 seconds
- Switchover completed within 15 minutes
- No data loss (checkpoint within 5 minutes of failure)
- System operational post-recovery

### 5.3 Configuration Rollback Drill

**Procedure:**

```bash
# 1. Deliberately introduce bad configuration
sed -i 's/max_force: 150.0/max_force: 9999.0/' config.yaml

# 2. Detect issue (should fail validation)
python simulate.py --validate-config

# 3. Rollback to last known good config
./scripts/rollback_config.sh

# 4. Verify system operational
python simulate.py --run-hil --duration 10.0

# 5. Document rollback time
```

**Target RTO:** <5 minutes

---

## Part 6: Incident Management

### 6.1 Incident Response Workflow

```mermaid
graph TD
    A[Incident Detected] --> B{Severity?}
    B -->|Critical| C[Emergency Shutdown]
    B -->|Major| D[Escalate to On-Call]
    B -->|Minor| E[Log and Monitor]

    C --> F[Execute DR Plan]
    D --> F
    F --> G[Restore from Backup/Failover]
    G --> H[Verify Recovery]
    H --> I{Successful?}
    I -->|Yes| J[Resume Operations]
    I -->|No| K[Escalate + Manual Intervention]

    J --> L[Post-Incident Review]
    K --> L
    E --> L
```

### 6.2 Incident Log Template

**Why Documentation Matters:**
Incident logs help you learn from failures and improve your disaster recovery processes. Document every incident, even minor ones.

**Template:**

```markdown
# Incident Report: [ID]

**Date/Time:** 2025-11-10 14:32 UTC
**Severity:** Major
**Reporter:** [Name]
**On-Call:** [Name]

## Summary
Brief description of incident

## Timeline
- 14:32: Incident detected (controller timeout)
- 14:33: Emergency stop triggered
- 14:35: Failover to backup initiated
- 14:38: Backup controller online
- 14:40: System verified operational
- **Total Downtime:** 8 minutes

## Root Cause
Primary controller server experienced kernel panic due to memory corruption

## Impact
- 8 minutes of downtime
- Data loss: 3 minutes (last checkpoint at 14:29)
- No hardware damage
- No safety violations

## Recovery Actions
1. Emergency stop triggered automatically
2. Failover to backup server
3. Resumed from checkpoint (14:29)
4. Verified system operational

## Prevention
- Install memory error detection (EDAC)
- Increase checkpoint frequency (60s → 30s)
- Add health check monitoring

## Lessons Learned
- Failover worked as designed (RTO: 8min < 15min target)
- Checkpoint system prevented major data loss
- Need faster detection of memory issues

**Status:** Closed
**Follow-Up Actions:** [Ticket IDs]
```

### 6.3 Escalation Matrix

| Incident Type | Primary Contact | Secondary | Escalation Time |
|---------------|----------------|-----------|-----------------|
| Hardware Failure | Ops Engineer | DevOps Lead | 15 min |
| Network Outage | Network Admin | Ops Engineer | 10 min |
| Software Crash | Developer On-Call | Tech Lead | 20 min |
| Security Incident | Security Team | CTO | Immediate |
| Data Loss | Data Engineer | Ops Lead | 15 min |

---

## Part 7: Post-Disaster Validation

**Why Validation Matters:**
After recovering from a disaster, you must verify that everything works correctly. Don't assume recovery was successful. Run validation checks to confirm the system is healthy before resuming normal operations.

### 7.1 System Health Check

```bash
#!/bin/bash
# post_recovery_validation.sh

echo "Running post-recovery validation..."

# 1. Network connectivity
ping -c 3 192.168.1.100 && echo "[OK] Plant reachable" || echo "[ERROR] Plant unreachable"

# 2. Controller status
systemctl is-active hil-controller && echo "[OK] Controller running" || echo "[ERROR] Controller stopped"

# 3. Configuration integrity
python simulate.py --validate-config && echo "[OK] Config valid" || echo "[ERROR] Config invalid"

# 4. Quick smoke test
timeout 30 python simulate.py --run-hil --duration 5.0 && echo "[OK] Smoke test passed" || echo "[ERROR] Smoke test failed"

# 5. Data logging
[ -f "/opt/hil/data/latest.npz" ] && echo "[OK] Logging active" || echo "[ERROR] Logging failed"

# 6. Safety checks
python scripts/validation/test_emergency_stop.py && echo "[OK] E-stop functional" || echo "[ERROR] E-stop failed"

echo "Validation complete"
```

### 7.2 Data Integrity Check

```python
def verify_data_integrity(data_file):
    """
    Verify recovered data has no corruption
    """
    data = np.load(data_file)

    checks = {
        'time_monotonic': check_time_monotonic(data['time']),
        'no_nans': check_no_nans(data['state']),
        'state_bounds': check_state_in_bounds(data['state']),
        'control_bounds': check_control_in_bounds(data['control']),
        'continuity': check_continuity(data['state'])
    }

    all_passed = all(checks.values())

    if not all_passed:
        logger.error(f"Data integrity check failed: {checks}")

    return all_passed
```

---

## Appendix A: Quick Reference

### A.1 Emergency Contacts

```text
Operations Engineer (Primary): +1-XXX-XXX-XXXX
DevOps Lead (Secondary): +1-XXX-XXX-XXXX
Security Team (24/7): security@company.com
Escalation Hotline: +1-XXX-XXX-XXXX (CTO)
```

### A.2 Recovery Commands

```bash
# Emergency shutdown
sudo systemctl stop hil-controller hil-plant

# Restart from last checkpoint
python simulate.py --run-hil --resume-from-checkpoint

# Rollback configuration
./scripts/rollback_config.sh

# Verify system health
./scripts/post_recovery_validation.sh

# Manual failover
export HIL_PLANT_IP=192.168.1.101  # Backup
python simulate.py --run-hil
```

### A.3 RTO/RPO Summary

| Scenario | RTO Target | Typical RTO | RPO Target | Typical RPO |
|----------|-----------|-------------|------------|-------------|
| Hardware failure | 15 min | 8-12 min | 5 min | 2-3 min |
| Network outage | 5 min | 2-4 min | 5 min | 1-2 min |
| Software crash | 3 min | 1-2 min | 5 min | 0-1 min |
| Config rollback | 5 min | 3-4 min | 0 min | 0 min |

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Authors:** Claude Code (AI), DIP-SMC-PSO Development Team
**Status:** Production-Ready

**Replaces:** hil-disaster-recovery.md stub (2025-10-07, 42 lines)
**Changelog:**
- 2025-11-10: Complete rewrite from stub to production guide (42 → 650+ lines)
- Added 7 comprehensive sections on disaster recovery
- Integrated backup strategies, failover mechanisms, incident management
- Included drill procedures, validation workflows, RTO/RPO metrics
