# Service Function Chain (SFC) and Validation

## Overview

This system now uses a single simplified Service Function Chain (SFC) for email traffic.

## Chain

FW → encryption → SMTP server → spam filter → decryption → receiver

## Orchestration Flow (Simplified)

- Single chain is defined in `orchestration/orchestration_config.yml` under `email_simple`.
- The orchestrator always selects this chain and allocates only real VNFs (`firewall`, `encryption`, `spamfilter`).
- Non-VNF steps (`smtp_server`, `decryption`, `receiver`) are logical hops and are not allocated.

## Performance Targets

Targets remain unchanged and are configured in `performance_targets` within `orchestration/orchestration_config.yml`.

## Build and Run

Use the existing scripts to build VNF images, start orchestration, and monitor metrics. Only the three VNFs are required.
