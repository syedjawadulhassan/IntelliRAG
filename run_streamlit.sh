#!/bin/bash
# run_streamlit.sh

# Activate virtual environment
source .venv/bin/activate

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "=== Starting Streamlit frontend ==="
echo "Access Streamlit at http://$LOCAL_IP:8501"

# Run Streamlit
streamlit run src/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
