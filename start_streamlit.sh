#!/bin/bash
# Start script for Streamlit deployment on Render

streamlit run streamlit_app.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --browser.gatherUsageStats=false
