# Monitoring & Alerting Setup Guide

**Feature**: 002-claude-code - WebSocket/Claude Code Logging  
**Last Updated**: 2025-10-25

---

## Overview

This guide covers setting up monitoring and alerting for the logging feature to ensure:
- Early detection of issues
- Performance baseline establishment
- Automatic incident response
- Operational visibility

---

## Key Metrics to Monitor

### Application Metrics

| Metric | Type | Threshold | Alert When |
|--------|------|-----------|-----------|
| Error Rate | Counter | < 10/hour | > 20 errors/hour |
| Response Time P95 | Histogram | < 10s | > 30s |
| Response Time P99 | Histogram | < 30s | > 60s |
| Successful Messages | Counter | Growing | No growth for 30min |
| Database Connections | Gauge | < 50 | > 80% of max |
| Log File Size | Gauge | < 3GB | > 2.5GB |

### Infrastructure Metrics

| Metric | Type | Threshold | Alert When |
|--------|------|-----------|-----------|
| CPU Usage | Gauge | < 70% | > 85% |
| Memory Usage | Gauge | < 80% | > 90% |
| Disk Usage | Gauge | < 80% | > 90% |
| Network I/O | Gauge | Normal | Spike detected |
| Service Uptime | Availability | 99.5% | < 99.5% |

---

## Setup Options

### Option 1: Prometheus + Grafana (Open Source)

**Installation**:

```bash
# Install Prometheus
docker run -d --name prometheus \
  -p 9090:9090 \
  -v /etc/prometheus:/etc/prometheus \
  prom/prometheus

# Install Grafana
docker run -d --name grafana \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana
```

**Prometheus Configuration** (`/etc/prometheus/prometheus.yml`):

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'claude-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

**Application Instrumentation** (`backend/src/main.py`):

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response

# Metrics
command_errors = Counter('claude_command_errors_total', 'Total command errors')
command_duration = Histogram('claude_command_duration_seconds', 'Command execution time')
active_connections = Gauge('claude_active_connections', 'Active WebSocket connections')

# Expose metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

# Use in handlers
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(...):
    active_connections.inc()
    try:
        # ... websocket logic
    except Exception as e:
        command_errors.inc()
    finally:
        active_connections.dec()
```

---

### Option 2: Datadog (Managed Service)

**Installation**:

```bash
# Install Datadog Agent
DD_AGENT_MAJOR_VERSION=7 DD_API_KEY=${DD_API_KEY} \
  DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_agent.sh)"

# Configure Datadog for Python
pip install datadog
```

**Application Instrumentation**:

```python
from datadog import initialize, api
from datadog.util.compat import json

options = {
    'api_key': os.getenv('DATADOG_API_KEY'),
    'app_key': os.getenv('DATADOG_APP_KEY')
}

initialize(**options)

# Log to Datadog
api.Event.create(
    title="Claude command executed",
    text=f"Session: {session_id}, Duration: {execution_time}ms",
    tags=["claude", "logging"]
)
```

---

### Option 3: ELK Stack (Elasticsearch + Logstash + Kibana)

**Installation**:

```bash
# Start ELK stack
docker-compose up -d elasticsearch kibana logstash
```

**Logstash Configuration** (`/etc/logstash/conf.d/claude.conf`):

```
input {
  file {
    path => "/var/log/claude-backend/app.log"
    start_position => "beginning"
  }
}

filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} - %{DATA:logger_name} - %{LOGLEVEL:level} - %{GREEDYDATA:message}" }
  }
  
  # Parse session/user/connection IDs
  grok {
    match => { "message" => "Session: %{UUID:session_id}" }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "claude-logs-%{+YYYY.MM.dd}"
  }
}
```

---

## Alert Rules

### Critical Alerts (Page On-Call)

```yaml
# Alert: Backend Down
- alert: BackendDown
  expr: up{job="claude-backend"} == 0
  for: 2m
  annotations:
    summary: "Claude backend is down"
    description: "Backend has been down for 2 minutes"

# Alert: High Error Rate
- alert: HighErrorRate
  expr: rate(claude_command_errors_total[5m]) > 0.333
  for: 5m
  annotations:
    summary: "High command error rate (> 33% in 5m)"
    description: "{{ $value }} errors per second"

# Alert: Response Time Critical
- alert: ResponseTimeCritical
  expr: histogram_quantile(0.95, claude_command_duration_seconds) > 60
  for: 5m
  annotations:
    summary: "P95 response time > 60 seconds"
```

### Warning Alerts (Email/Slack)

```yaml
# Alert: Slow Response Time
- alert: SlowResponseTime
  expr: histogram_quantile(0.95, claude_command_duration_seconds) > 30
  for: 10m
  annotations:
    summary: "P95 response time > 30 seconds"

# Alert: High CPU Usage
- alert: HighCPU
  expr: node_cpu_utilization > 0.85
  for: 5m
  annotations:
    summary: "CPU usage > 85%"

# Alert: Disk Space Low
- alert: DiskSpaceLow
  expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
  for: 5m
  annotations:
    summary: "Less than 10% disk space remaining"
```

---

## Dashboard Setup

### Grafana Dashboard Example

```json
{
  "dashboard": {
    "title": "Claude Backend - Logging Feature",
    "panels": [
      {
        "title": "Command Success Rate",
        "targets": [
          {
            "expr": "rate(claude_command_success_total[5m]) / rate(claude_command_total[5m])"
          }
        ]
      },
      {
        "title": "Command Duration (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, claude_command_duration_seconds)"
          }
        ]
      },
      {
        "title": "Active Connections",
        "targets": [
          {
            "expr": "claude_active_connections"
          }
        ]
      },
      {
        "title": "Errors per Minute",
        "targets": [
          {
            "expr": "rate(claude_command_errors_total[1m])"
          }
        ]
      }
    ]
  }
}
```

---

## Log Aggregation Setup

### Filebeat to Logstash

**filebeat.yml**:

```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/claude-backend/app.log
  tags: ["claude-backend"]

output.logstash:
  hosts: ["logstash:5000"]
```

### Query Examples

**Find errors for specific session**:

```json
{
  "query": {
    "term": {
      "session_id": "abc-123-def-456"
    }
  },
  "filter": [
    {"term": {"level": "ERROR"}}
  ]
}
```

**Response time distribution**:

```json
{
  "aggs": {
    "response_times": {
      "histogram": {
        "field": "execution_time_ms",
        "interval": 1000
      }
    }
  }
}
```

---

## Incident Response Playbooks

### Incident: High Error Rate

**Detection**: Error rate > 20/hour for > 5 minutes

**Response**:

1. Page on-call engineer
2. Check backend logs: `grep ERROR logs/app.log | tail -50`
3. Check Claude process: `ps aux | grep claude`
4. If Claude crashed:
   ```bash
   systemctl restart claude-backend
   ```
5. Monitor recovery in Grafana
6. Post-incident review

### Incident: Slow Response Time

**Detection**: P95 response > 60 seconds

**Response**:

1. Check system resources: `top`, `df -h`
2. Check database: `SHOW PROCESSLIST;`
3. Enable SQL logging: `SQLALCHEMY_LOG_LEVEL=INFO`
4. Identify slow queries and optimize
5. Monitor query times in logs

### Incident: Backend Down

**Detection**: Backend unreachable for > 2 minutes

**Response**:

1. Page on-call engineer immediately
2. Check service status: `systemctl status claude-backend`
3. Check logs: `tail -100 /var/log/claude-backend/app.log`
4. Restart service:
   ```bash
   systemctl restart claude-backend
   ```
5. Verify health: `curl http://localhost:8000/health`
6. If still down, escalate to database/infrastructure team

---

## Health Check Endpoints

**Application Health**:

```bash
curl http://localhost:8000/health
# Expected: 200 OK
```

**Detailed Health**:

```bash
curl http://localhost:8000/health/detailed
# Response:
# {
#   "status": "healthy",
#   "backend": "up",
#   "database": "connected",
#   "claude_process": "running",
#   "log_file": "writable"
# }
```

**Metrics Endpoint**:

```bash
curl http://localhost:8000/metrics
# Prometheus-formatted metrics
```

---

## Maintenance

### Weekly

- [ ] Review error logs for patterns
- [ ] Check alert accuracy (false positives?)
- [ ] Verify backup procedures working

### Monthly

- [ ] Analyze performance trends
- [ ] Update alert thresholds if needed
- [ ] Test incident response procedures

### Quarterly

- [ ] Review monitoring effectiveness
- [ ] Update dashboards
- [ ] Capacity planning

---

## References

- [OPERATIONAL_RUNBOOK.md](./OPERATIONAL_RUNBOOK.md) - Incident response
- [LOGGING_GUIDE.md](./LOGGING_GUIDE.md) - Log configuration
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [ELK Stack Guide](https://www.elastic.co/guide/en/elastic-stack/current/index.html)

