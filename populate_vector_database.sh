#!/bin/bash

# Export PYTHON_PATH to the current folder
export PYTHONPATH=$(pwd)

# Export OPENAI_API_KEY (replace "your_openai_api_key_here" with your actual API key)
export OPENAI_API_KEY="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"

# Execute the Python file (replace "your_python_file.py" with the name of your Python file)
python populate_vector_database.py