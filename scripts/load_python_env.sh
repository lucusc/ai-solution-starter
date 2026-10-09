#!/bin/bash

echo 'Creating Python virtual environment ".venv"...'
python3 -m venv .venv

echo 'Installing script dependencies into the virtual environment...'
.venv/bin/python -m pip --quiet --disable-pip-version-check install -r scripts/requirements.txt
