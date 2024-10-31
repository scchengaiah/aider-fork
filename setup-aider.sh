#!/bin/bash

# Check if conda environment 'aider-env' exists
if conda info --envs | grep -q aider-env; then
    echo "Conda environment 'aider-env' already exists. Activating it..."
else
    echo "Creating conda environment 'aider-env'..."
    conda create -n aider-env python=3.11 -y
fi

# Activate the conda environment
source activate aider-env

# Install or upgrade aider
echo "Installing/upgrading aider..."
pip install --upgrade aider-chat

# Deactivate the conda environment
source deactivate aider-env

# Print additional instructions
cat << EOF

==========================================================
Aider Setup Complete! Additional Steps:
==========================================================

1. Create a .env file with required variables for Aider:
   Visit https://aider.chat/docs/llms.html for more information.
   Example:
   OPENAI_API_KEY=your_api_key_here

2. Copy the Aider config file:
   wget https://raw.githubusercontent.com/scchengaiah/aider-fork/main/aider-config.yaml -O aider-config.yml
   Update configuration based on the requirements of your environment.
   Visit https://aider.chat/docs/config.html for more information.

3. To use Aider:
   a. Activate the conda environment:
      conda activate aider-env
   
   b. Launch Aider with the following command:
      aider --chat-mode code  --config aider-config.yml

==========================================================
EOF
