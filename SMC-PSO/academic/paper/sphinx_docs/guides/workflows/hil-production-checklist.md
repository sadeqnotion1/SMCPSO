# HIL Production Deployment Checklist

A comprehensive pre-deployment checklist for production Hardware-in-the-Loop (HIL) systems. Use this guide to ensure your DIP SMC HIL setup is ready for reliable operation.

---

## Overview

This checklist helps you validate HIL system readiness before deploying controllers to production or critical testing environments.

**When to Use This:**
- Before first production deployment
- After major system changes
- Quarterly validation reviews
- Post-incident recovery verification

**Time Required:** 4-6 hours for full checklist (first time), 1-2 hours for regular reviews

---

## Quick Start

**Minimum Viable Deployment (30 minutes):**
1. Run basic safety tests (emergency stop, timeout)
2. Verify network latency <10ms
3. Test manual mode operation
4. Confirm logging is active

**Full Production Deployment (4-6 hours):**
Complete all sections below

---

## 1. Pre-Deployment Validation

### Safety Validation Tests

**Critical Safety Features:**
```python
# Test emergency stop
python simulate.py --run-hil --test-emergency-stop

# Test communication timeout handling
python simulate.py --run-hil --test-timeout

# Test invalid command rejection
python simulate.py --run-hil --test-invalid-commands
```

**Checklist:**
- [ ] Emergency stop triggers within 100ms
- [ ] Timeout detection works (disconnect plant, verify controller stops)
- [ ] Invalid commands rejected (out-of-bounds, NaN, inf values)
- [ ] Safe fallback behavior verified (plant returns to safe state)
- [ ] All safety interlocks tested

**Verification:**
```bash
# Should show all safety tests PASS
grep "Safety Test" hil_test_log.txt
```

### Performance Benchmarks

**Latency Requirements:**
```python
# Measure round-trip latency
from src.hil.plant_server import PlantServer
from src.utils.monitoring.latency import LatencyMonitor

monitor = LatencyMonitor(dt=0.01)
# Run 1000 iterations, measure p50, p95, p99
```

**Benchmarks:**
- [ ] P50 latency <5ms
- [ ] P95 latency <10ms
- [ ] P99 latency <20ms
- [ ] Zero dropped packets in 10-minute test
- [ ] Controller achieves <3s settling time
- [ ] Chattering <10% of control signal

**Verification:**
```bash
# Check latency stats
python -c "from src.utils.monitoring.latency import analyze_latency; analyze_latency('hil_latency.log')"
```

### Communication Reliability

**Network Tests:**
```bash
# Test plant server startup
python -m src.hil.plant_server --port 5555

# Test client connection
python -m src.hil.controller_client --host localhost --port 5555

# Run 10-minute stability test
timeout 600 python simulate.py --run-hil --log-latency
```

**Checklist:**
- [ ] Plant server starts without errors
- [ ] Client connects within 1 second
- [ ] No connection drops in 10-minute test
- [ ] Reconnection works after intentional disconnect
- [ ] Port conflicts detected and handled

### Fault Injection Tests

**Test Scenarios:**
```python
# Simulate network delay
tc qdisc add dev lo root netem delay 50ms

# Simulate packet loss
tc qdisc add dev lo root netem loss 5%

# Verify controller handles gracefully
python simulate.py --run-hil --fault-injection
```

**Checklist:**
- [ ] 50ms delay: Controller remains stable
- [ ] 5% packet loss: Graceful degradation
- [ ] Plant crash: Controller detects and stops
- [ ] Client crash: Plant returns to safe state
- [ ] Corrupted data: Rejected with error log

### Controller Parameter Validation

**Verify Tuned Gains:**
```bash
# Load production gains
python simulate.py --load optimization_results/production_gains.json --run-hil

# Verify performance matches offline simulation
python scripts/validate_hil_performance.py
```

**Checklist:**
- [ ] All gains within valid ranges
- [ ] Performance matches offline simulation (±10%)
- [ ] Robustness to initial conditions verified
- [ ] Monte Carlo results: >95% success rate

---

## 2. Infrastructure Requirements

### Network Infrastructure

**Network Configuration:**
```bash
# Verify network interface
ifconfig | grep -A 5 "lo\|eth0"

# Test bandwidth
iperf3 -s  # On plant machine
iperf3 -c <plant_host>  # On controller machine

# Check firewall rules
sudo iptables -L | grep 5555
```

**Checklist:**
- [ ] Dedicated network interface (not shared with other traffic)
- [ ] Bandwidth ≥100 Mbps
- [ ] Firewall allows port 5555 (or configured port)
- [ ] Static IP addresses configured
- [ ] DNS resolution working (if using hostnames)
- [ ] Network monitoring enabled

### Hardware Specifications

**Plant Server:**
- [ ] CPU: ≥2 cores, 2.0+ GHz
- [ ] RAM: ≥4 GB available
- [ ] Disk: ≥10 GB free for logs
- [ ] OS: Linux/Windows with Python 3.9+
- [ ] ZeroMQ installed (pyzmq)

**Controller Client:**
- [ ] CPU: ≥2 cores, 2.0+ GHz
- [ ] RAM: ≥2 GB available
- [ ] Disk: ≥5 GB free for logs
- [ ] OS: Linux/Windows with Python 3.9+
- [ ] ZeroMQ installed (pyzmq)

**Verification:**
```bash
# Check CPU
lscpu | grep "CPU(s)\|MHz"

# Check RAM
free -h

# Check disk
df -h | grep "/$"

# Check Python version
python --version

# Check ZeroMQ
python -c "import zmq; print(zmq.zmq_version())"
```

### Backup and Recovery

**Backup Strategy:**
```bash
# Backup configuration
cp config.yaml config.yaml.backup.$(date +%Y%m%d)

# Backup gains
cp optimization_results/production_gains.json gains.backup.$(date +%Y%m%d).json

# Backup code (if deployed separately)
git archive --format=tar.gz -o dip-smc-backup-$(date +%Y%m%d).tar.gz HEAD
```

**Checklist:**
- [ ] Configuration files backed up daily
- [ ] Optimized gains backed up
- [ ] Code version tagged in Git
- [ ] Backup restoration tested (verify from backup)
- [ ] Offsite backup configured

### Monitoring and Alerting

**Monitoring Setup:**
```python
# Enable monitoring
from src.utils.monitoring.latency import LatencyMonitor
from src.utils.monitoring.deadline import DeadlineMonitor

monitor = LatencyMonitor(dt=0.01, alert_threshold=20.0)  # Alert if >20ms
```

**Checklist:**
- [ ] Latency monitoring active
- [ ] Deadline miss alerts configured
- [ ] CPU/memory monitoring enabled
- [ ] Disk space alerts set (warn at 80%, critical at 90%)
- [ ] Network error rate monitoring
- [ ] Alert destinations configured (email, Slack, PagerDuty)

### Logging Infrastructure

**Log Configuration:**
```python
# config.yaml
hil:
  logging:
    level: INFO
    file: logs/hil_production.log
    max_size_mb: 100
    rotation: daily
    retention_days: 30
```

**Checklist:**
- [ ] Log directory exists and is writable
- [ ] Log rotation configured
- [ ] Log retention policy set
- [ ] Sensitive data not logged (gains are OK, state is OK)
- [ ] Log aggregation configured (if multi-machine)
- [ ] Log parsing/analysis tools ready

### Documentation

**Required Documentation:**
```
docs/
├── hil_deployment/
│   ├── architecture_diagram.png
│   ├── network_topology.md
│   ├── runbook.md
│   ├── troubleshooting.md
│   └── contact_list.md
```

**Checklist:**
- [ ] System architecture documented
- [ ] Network topology diagram available
- [ ] Runbook complete (startup, shutdown, restart procedures)
- [ ] Troubleshooting guide written
- [ ] Contact list updated (on-call, escalation)
- [ ] Change log maintained

---

## 3. Security & Compliance

### Security Audit

**Security Checklist:**
```bash
# Check for default passwords
grep -r "password.*=.*admin\|root\|1234" config.yaml

# Verify TLS enabled (if using secure transport)
grep "tls\|ssl\|secure" config.yaml

# Check file permissions
ls -l config.yaml optimization_results/production_gains.json
# Should NOT be world-readable
```

**Checklist:**
- [ ] No default passwords in use
- [ ] All credentials stored securely (not in code)
- [ ] TLS/encryption enabled for sensitive data
- [ ] File permissions restricted (640 or 600 for configs)
- [ ] Security patches applied to OS and dependencies
- [ ] Vulnerability scan completed

### Access Control

**User Permissions:**
```bash
# Create HIL operator user
sudo useradd -m -s /bin/bash hil_operator

# Set up restricted permissions
sudo chown hil_operator:hil_operator /opt/dip-smc/
sudo chmod 750 /opt/dip-smc/

# Verify sudo access (if needed)
sudo -l -U hil_operator
```

**Checklist:**
- [ ] Dedicated service account created
- [ ] Least-privilege access enforced
- [ ] SSH key authentication required
- [ ] Password authentication disabled
- [ ] Multi-factor authentication enabled (if applicable)
- [ ] Audit trail for privileged actions

### Compliance Requirements

**Regulatory Compliance (if applicable):**

**Checklist:**
- [ ] Data retention policy complies with regulations
- [ ] Privacy requirements met (no PII logged)
- [ ] Export control restrictions verified
- [ ] Industry-specific standards met (e.g., IEC 61508 for safety)
- [ ] Third-party audit passed (if required)
- [ ] Compliance documentation up to date

### Incident Response

**Incident Response Plan:**
```markdown
# Severity Levels
- P0: System down, safety compromised
- P1: Performance degraded >50%
- P2: Minor issues, workaround available

# Response Times
- P0: Immediate response, 15-minute SLA
- P1: 1-hour response, 4-hour resolution SLA
- P2: Next business day
```

**Checklist:**
- [ ] Incident response plan documented
- [ ] Escalation procedures defined
- [ ] Post-mortem template ready
- [ ] Blameless culture established
- [ ] Runbook for common incidents
- [ ] Contact information current

### Audit Trail

**Logging for Audit:**
```python
# Enable audit logging
import logging
audit_logger = logging.getLogger('audit')
audit_logger.info(f"Deployment started by {user} at {timestamp}")
audit_logger.info(f"Configuration changed: {diff}")
audit_logger.info(f"Gains updated: {old_gains} -> {new_gains}")
```

**Checklist:**
- [ ] All configuration changes logged
- [ ] All gain updates logged with user
- [ ] All system starts/stops logged
- [ ] Audit logs tamper-evident (write-once)
- [ ] Audit logs retained per policy
- [ ] Regular audit log reviews scheduled

---

## 4. Operational Readiness

### On-Call Procedures

**On-Call Setup:**
```markdown
# Primary On-Call
- Name: [Engineer Name]
- Phone: [Phone Number]
- Slack: @[username]
- Availability: 24/7

# Secondary On-Call
- Name: [Backup Engineer]
- Phone: [Phone Number]
- Escalation: After 30 minutes

# Escalation Path
1. Primary on-call (0-30 min)
2. Secondary on-call (30-60 min)
3. Team lead (60+ min)
4. Director (critical incidents)
```

**Checklist:**
- [ ] On-call rotation defined
- [ ] On-call schedule published
- [ ] Alerting system configured
- [ ] Escalation paths documented
- [ ] On-call compensation arranged
- [ ] On-call handoff process defined

### Training

**Operator Training:**
```markdown
# Training Modules
1. System Overview (1 hour)
2. Normal Operations (2 hours)
3. Emergency Procedures (1 hour)
4. Troubleshooting (2 hours)
5. Hands-on Practice (4 hours)

# Certification
- Written test (80% pass required)
- Practical exam (supervised operation)
- Recertification: Annual
```

**Checklist:**
- [ ] Training materials created
- [ ] All operators trained
- [ ] Training completion documented
- [ ] Hands-on practice completed
- [ ] Emergency drills conducted
- [ ] Recertification schedule set

### Runbooks and SOPs

**Required Runbooks:**
```
runbooks/
├── startup.md           # How to start HIL system
├── shutdown.md          # How to stop HIL system gracefully
├── restart.md           # How to restart after issues
├── update_gains.md      # How to update controller parameters
├── log_analysis.md      # How to analyze logs
└── emergency.md         # Emergency procedures
```

**Checklist:**
- [ ] Startup runbook complete and tested
- [ ] Shutdown runbook complete and tested
- [ ] Restart runbook complete and tested
- [ ] Gain update procedure documented
- [ ] Log analysis guide written
- [ ] Emergency procedures accessible

### Rollback Procedures

**Rollback Strategy:**
```bash
# Rollback script example
#!/bin/bash
# rollback_hil.sh

echo "Stopping HIL system..."
./shutdown_hil.sh

echo "Restoring previous configuration..."
cp config.yaml.backup config.yaml

echo "Restoring previous gains..."
cp gains.backup.json optimization_results/production_gains.json

echo "Restarting HIL system..."
./startup_hil.sh

echo "Verifying rollback..."
./verify_hil.sh
```

**Checklist:**
- [ ] Rollback procedure documented
- [ ] Rollback tested in staging
- [ ] Backup versions identified
- [ ] Rollback time <5 minutes
- [ ] Rollback success criteria defined
- [ ] Post-rollback verification automated

### Capacity Planning

**Capacity Metrics:**
```python
# Monitor resource usage
import psutil

cpu_percent = psutil.cpu_percent(interval=1)
memory_percent = psutil.virtual_memory().percent
disk_percent = psutil.disk_usage('/').percent

# Alert if >80%
```

**Checklist:**
- [ ] CPU usage <50% average, <80% peak
- [ ] Memory usage <60% average, <80% peak
- [ ] Disk usage <70%
- [ ] Network bandwidth <50% capacity
- [ ] Growth projections documented
- [ ] Scaling plan defined

### Disaster Recovery

**Disaster Recovery Plan:**
```markdown
# Recovery Time Objective (RTO): 1 hour
# Recovery Point Objective (RPO): 24 hours

# Recovery Steps:
1. Provision new hardware/VM
2. Install OS and dependencies
3. Restore code from Git
4. Restore configuration from backup
5. Restore gains from backup
6. Run verification tests
7. Resume operation
```

**Checklist:**
- [ ] Disaster recovery plan documented
- [ ] RTO and RPO defined
- [ ] Recovery tested in simulation
- [ ] Offsite backups verified
- [ ] Alternative hardware identified
- [ ] Recovery time <RTO

---

## 5. Performance Baselines

### Baseline Metrics

**Establish Baselines:**
```python
# Run baseline tests
python simulate.py --run-hil --baseline --runs 100

# Metrics collected:
# - Settling time: 2.3s ± 0.2s
# - Overshoot: 5% ± 2%
# - Steady-state error: <1%
# - Control effort: 15N ± 5N
# - Chattering: 8% ± 2%
```

**Checklist:**
- [ ] Baseline settling time recorded
- [ ] Baseline overshoot recorded
- [ ] Baseline control effort recorded
- [ ] Baseline chattering recorded
- [ ] Baseline latency recorded
- [ ] Baseline success rate recorded (>95%)

### Performance Regression Tests

**Regression Test Suite:**
```bash
# Run regression tests
pytest tests/test_hil_regression.py -v

# Should test:
# - Settling time within baseline ±20%
# - Latency within baseline ±50%
# - Success rate ≥baseline - 5%
```

**Checklist:**
- [ ] Regression test suite exists
- [ ] All regression tests passing
- [ ] Regression tests run on each deployment
- [ ] Performance trends monitored
- [ ] Alerts on regression >20%

### Resource Utilization

**Resource Monitoring:**
```bash
# Monitor during 1-hour test
top -b -d 1 -n 3600 | grep python > resource_usage.log

# Analyze
python scripts/analyze_resource_usage.py resource_usage.log
```

**Checklist:**
- [ ] CPU usage acceptable (<80% peak)
- [ ] Memory usage stable (no leaks)
- [ ] Disk I/O reasonable (<10 MB/s)
- [ ] Network traffic expected (~1 KB/s per control loop)
- [ ] No resource warnings during 1-hour test

### Scalability Validation

**Scalability Tests:**
```python
# Test with multiple controllers (if applicable)
for i in range(1, 11):
    run_hil_with_n_controllers(n=i)
    measure_latency()

# Verify latency scales linearly or better
```

**Checklist:**
- [ ] Single controller performance baseline
- [ ] Multi-controller performance tested (if applicable)
- [ ] Latency scaling acceptable
- [ ] Resource usage scaling linear
- [ ] Max concurrent controllers identified

### Load Testing

**Load Test:**
```bash
# Run maximum load for 10 minutes
python simulate.py --run-hil --duration 600 --high-frequency

# Should maintain:
# - Latency <20ms P99
# - No deadline misses
# - Stable performance
```

**Checklist:**
- [ ] Load test completed successfully
- [ ] No performance degradation under load
- [ ] No errors during load test
- [ ] System recovers after load test
- [ ] Load test automated

### Stress Testing

**Stress Test:**
```bash
# Push beyond normal limits
python simulate.py --run-hil --stress-test

# Inject:
# - High frequency disturbances
# - Rapid setpoint changes
# - Large initial condition errors
```

**Checklist:**
- [ ] Stress test passed (system remains stable)
- [ ] Graceful degradation observed
- [ ] No crashes under stress
- [ ] System recovers after stress
- [ ] Stress test limits documented

---

## 6. Final Verification

### Pre-Flight Checklist

**Final Checks (15 minutes):**
```bash
# 1. Version check
git describe --tags

# 2. Config validation
python -c "from src.config import load_config; load_config('config.yaml')"

# 3. Quick smoke test
python simulate.py --run-hil --duration 60

# 4. Verify monitoring active
curl http://localhost:9090/metrics  # If using Prometheus

# 5. Check logs
tail -f logs/hil_production.log
```

**Checklist:**
- [ ] Correct code version deployed
- [ ] Configuration valid
- [ ] Smoke test passed
- [ ] Monitoring active
- [ ] Logs flowing
- [ ] All team members notified

### Sign-Off

**Deployment Approval:**
```markdown
# Deployment Authorization

Date: [YYYY-MM-DD]
System: DIP SMC HIL
Version: [Git Tag]

Approved By:
- [ ] Developer: _________________ Date: _______
- [ ] QA: _______________________ Date: _______
- [ ] Operations: _______________ Date: _______
- [ ] Manager: __________________ Date: _______

Deployment Window: [Start Time] to [End Time]
```

**Checklist:**
- [ ] All sections above completed
- [ ] All approvals obtained
- [ ] Deployment window scheduled
- [ ] Rollback plan ready
- [ ] On-call coverage confirmed
- [ ] Post-deployment verification plan ready

---

## Related Guides

**HIL Workflows:**
- [HIL Workflow Guide](hil-workflow.md) - Basic HIL usage
- [HIL Safety Validation](hil-safety-validation.md) - Detailed safety testing
- [HIL Disaster Recovery](hil-disaster-recovery.md) - Recovery procedures
- [HIL Multi-Machine Setup](hil-multi-machine.md) - Multi-machine configuration

**Other Resources:**
- [Getting Started](../getting-started.md) - System overview
- [Configuration Guide](../api/configuration.md) - Configuration options
- [Monitoring Guide](../how-to/testing-validation.md) - Monitoring setup

---

**Last Updated:** November 10, 2025
**Status:** Complete (replaces "Under Construction" checklist)
**Review Schedule:** Quarterly or after major changes
