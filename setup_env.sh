
#!/bin/bash

# Create virtual environment in /tmp
python3 -m venv /tmp/redline_env

# Activate the virtual environment
source /tmp/redline_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt