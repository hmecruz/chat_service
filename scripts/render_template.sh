#!/bin/bash

set -e

# Navigate to the script directory and move up to the project root
cd "$(dirname "$0")/.."

# Load environment variables from .env
if [ ! -f ".env" ]; then
  echo "❌ .env file not found in project root"
  exit 1
fi

export $(grep -v '^#' .env | xargs)

# Check if the template exists
if [ ! -f "ejabberd.yml.template" ]; then
  echo "❌ ejabberd.yml.template not found in project root"
  exit 1
fi

# Render the template
envsubst < ejabberd.yml.template > ejabberd.yml

echo "✅ Successfully rendered ejabberd.yml"

