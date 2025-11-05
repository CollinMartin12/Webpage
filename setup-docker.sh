#!/bin/bash

# Docker setup script for the Microblog application
# Make sure Docker is installed and running before executing this script

echo "🐳 Setting up Microblog with Docker and MariaDB"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first:"
    echo "   https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is installed and running"

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker compose down -v 2>/dev/null || docker-compose down -v 2>/dev/null || true

# Build and start the containers
echo "🏗️  Building and starting containers..."
if command -v "docker compose" &> /dev/null; then
    docker compose up --build -d
else
    docker-compose up --build -d
fi

# Wait a moment for containers to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if containers are running
echo "📊 Container status:"
if command -v "docker compose" &> /dev/null; then
    docker compose ps
else
    docker-compose ps
fi

echo ""
echo "🎉 Setup complete!"
echo "📱 Web application: http://localhost:5000"
echo "🗄️  Database: localhost:3306"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker compose logs -f"
echo "   Stop:      docker compose down"
echo "   Restart:   docker compose restart"
echo "   Reset all: docker compose down -v && docker compose up --build"
