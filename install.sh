#!/bin/bash

set -euo pipefail

# python venv setup
/opt/python/bin/python -m venv venv
./venv/bin/pip install -U pip -r requirements.txt
./venv/bin/python -m poetry build
./venv/bin/pip install -e .
# system setup
sudo useradd -r --home /opt/inventory inventory
sudo chown -R inventory. /opt/inventory
sudo chmod -R g-rwx,o-rwx /opt/inventory
sudo cp systemd/inventory.service /etc/systemd/system/
sudo systemctl start inventory
sudo systemctl enable inventory