#!/bin/bash
uvicorn enhanced_api:app --host 0.0.0.0 --port ${PORT:-8000}