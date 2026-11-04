# CryptoPulse Deployment

## Overview

The Binance WebSocket collector runs as a systemd service
on the Azure master VM.

Service name: cryptopulse.service

## Requirements

- Linux with systemd
- Python 3.14 (current tested environment)
- Python package: websockets==17.4
- CryptoPulse GitHub repository
- Internet access to Binance WebSocket API

## Installation

1. Clone the CryptoPulse repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:

   python -m pip install -r requirements.txt

4. Copy deployment/systemd/cryptopulse.service
   to /etc/systemd/system/.

5. Adjust User, WorkingDirectory and ExecStart
   in the service file to match the target machine.

6. Reload systemd:

   sudo systemctl daemon-reload

7. Start and enable the service:

   sudo systemctl enable --now cryptopulse.service

## Service Management

Check status:

    systemctl status cryptopulse.service

View logs:

    journalctl -u cryptopulse.service -f

Stop collection:

    sudo systemctl stop cryptopulse.service

Restart collection:

    sudo systemctl restart cryptopulse.service

## Storage

Raw events are stored in:

    data/raw/btcusdt_YYYY-MM-DD.jsonl

The collector has a 2 GB JSONL storage limit.

Data files are excluded from Git using .gitignore.

## Current Status

The collector has been successfully tested on the
Azure master VM and deployed as a background service.

Kafka, Spark and HDFS ingestion are planned for
later development phases.
