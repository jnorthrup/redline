#!/bin/bash

# Comment out unused variable 'refresh_rate' in redline/status_line.py
gsed -i '11s/^/# /' redline/status_line.py

# Comment out unused attribute '_last_render' in redline/status_line.py
gsed -i '18s/^/# /' redline/status_line.py
gsed -i '45s/^/# /' redline/status_line.py
gsed -i '89s/^/# /' redline/status_line.py

# Comment out unused method 'exit_cleanly' in redline/status_line.py
gsed -i '71s/^/# /' redline/status_line.py

# Comment out unused import 'List' in redline/supervisor/supervisor.py
gsed -i '5s/^/# /' redline/supervisor/supervisor.py

# Comment out unused import 'Tuple' in redline/supervisor/supervisor.py
gsed -i '5s/^/# /' redline/supervisor/supervisor.py

# Comment out unused attribute 'tools' in redline/supervisor/supervisor.py
gsed -i '177s/^/# /' redline/supervisor/supervisor.py

# Comment out unused method 'execute_tool' in redline/supervisor/supervisor.py
gsed -i '190s/^/# /' redline/supervisor/supervisor.py

# Comment out unused variable 'input_data' in redline/supervisor/supervisor.py
gsed -i '190s/^/# /' redline/supervisor/supervisor.py

# Comment out unused attribute 'tool_manager' in redline/supervisor/supervisor.py
gsed -i '206s/^/# /' redline/supervisor/supervisor.py

# Comment out unused variable 'refresh_rate' in status_line.py
gsed -i '8s/^/# /' status_line.py

# Comment out unused attribute '_last_render' in status_line.py
gsed -i '14s/^/# /' status_line.py
gsed -i '24s/^/# /' status_line.py

# Comment out unused import 'pytest' in tests/test_status_line.py
gsed -i '5s/^/# /' tests/test_status_line.py
