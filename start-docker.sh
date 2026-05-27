#!/bin/bash
# Docker compose up with proper setup

echo "Setting up Bus Fare Monitor..."

# Copy config if not exists
if [ ! -f config.json ]; then
    cp config.json.sample config.json
    echo "Config file created. Edit config.json with your settings."
fi

# Copy env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Environment file created. Edit .env with your credentials."
fi

echo "Build and starting services..."
docker-compose up -d

echo "Done! Run 'docker-compose logs -f' to view logs."
