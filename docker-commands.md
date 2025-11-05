
# Docker Commands for Microblog Website
# =====================================
# This file contains all the essential Docker commands for building, running, 
# debugging, and managing your Flask + MariaDB application.

# =============================================================================
# BASIC OPERATIONS
# =============================================================================

# Build and start containers (first time or after changes)
docker compose up --build

# Start containers in detached mode (background)
docker compose up -d

# Start with rebuild (when you change Dockerfile or requirements)
docker compose up --build -d

# Stop all containers
docker compose down

# Stop containers and remove volumes (COMPLETE RESET - fresh database)
docker compose down -v

# Restart specific service
docker compose restart web
docker compose restart mariadb

# Reset database completely and repopulate
docker compose down -v
docker compose up -d
docker exec -it microblog_web python test_data.py

# Stop and remove everything (containers, networks, volumes)
docker compose down -v --remove-orphans

# =============================================================================
# MONITORING AND DEBUGGING
# =============================================================================

# Check status of all containers
docker compose ps

# View logs from all services
docker compose logs

# View logs from specific service
docker compose logs web
docker compose logs mariadb

# Follow logs in real-time (Ctrl+C to exit)
docker compose logs -f
docker compose logs -f web

# View last N lines of logs
docker compose logs --tail=20 web
docker compose logs --tail=50 mariadb

# =============================================================================
# DATABASE ACCESS AND DEBUGGING
# =============================================================================

# Connect to MariaDB as application user
docker exec -it microblog_mariadb mysql -u microblog_user -pmicroblog_password microblog_db

# Connect to MariaDB as root user
docker exec -it microblog_mariadb mysql -u root -prootpassword

# Check database structure (run inside MySQL shell)
# SHOW TABLES;
# DESCRIBE user;
# DESCRIBE trip;

# Run SQL commands from command line
docker exec -it microblog_mariadb mysql -u microblog_user -pmicroblog_password microblog_db -e "SHOW TABLES;"
docker exec -it microblog_mariadb mysql -u microblog_user -pmicroblog_password microblog_db -e "DESCRIBE user;"

# Check MariaDB status
docker exec microblog_mariadb mysqladmin -u root -prootpassword status

# =============================================================================
# CONTAINER DEBUGGING
# =============================================================================

# Access shell inside web container
docker exec -it microblog_web bash

# Access shell inside database container
docker exec -it microblog_mariadb bash

# Check container resource usage
docker stats

# View detailed container information
docker inspect microblog_web
docker inspect microblog_mariadb

# Check container processes
docker exec microblog_web ps aux

# =============================================================================
# DEVELOPMENT WORKFLOW
# =============================================================================

# When you make code changes (Python files, templates):
docker compose restart web

# When you change requirements.txt or Dockerfile:
docker compose down
docker compose up --build

# When you want fresh database (reset all data):
docker compose down -v
docker compose up

# When you change docker-compose.yml:
docker compose down
docker compose up

# =============================================================================
# TROUBLESHOOTING COMMANDS (USED DURING DEBUGGING)
# =============================================================================

# These commands helped us debug the issues you encountered:

# 1. Check if containers are actually running
docker compose ps

# 2. Find what's using a port (if you get "port already in use" error)
lsof -i :5000
lsof -i :5001
lsof -i :3306

# 3. Check Flask application errors
docker compose logs web --tail=50

# 4. Verify database table structure
docker exec -it microblog_mariadb mysql -u microblog_user -pmicroblog_password microblog_db -e "DESCRIBE user;"

# 5. Check if database connection works
docker exec microblog_mariadb mysqladmin -u microblog_user -pmicroblog_password ping

# 6. View real-time logs during testing
docker compose logs -f web

# 7. Check disk space (containers can fail if disk is full)
docker system df

# 8. Clean up unused Docker resources
docker system prune
docker system prune -a  # Remove unused images too

# =============================================================================
# EMERGENCY COMMANDS
# =============================================================================

# If everything is broken, nuclear option (removes ALL Docker data):
# WARNING: This will delete ALL your Docker containers, images, volumes!
# docker system prune -a --volumes

# Remove only this project's containers and volumes:
docker compose down -v --remove-orphans

# Force remove containers if they're stuck:
docker rm -f microblog_web microblog_mariadb

# Remove specific volumes if they're corrupted:
docker volume rm project_web_mariadb_data

# =============================================================================
# PRODUCTION DEPLOYMENT COMMANDS
# =============================================================================

# For production deployment (when ready):
docker compose -f docker-compose.prod.yml up -d

# View production logs:
docker compose -f docker-compose.prod.yml logs -f

# Update production deployment:
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up --build -d

# =============================================================================
# USEFUL ONE-LINERS
# =============================================================================

# Quick restart everything with fresh database:
docker compose down -v && docker compose up --build -d

# Check if web app is responding:
curl http://localhost:5001

# Quick database query:
docker exec microblog_mariadb mysql -u microblog_user -pmicroblog_password microblog_db -e "SELECT COUNT(*) FROM user;"

# View all Docker networks:
docker network ls

# View container IP addresses:
docker inspect microblog_web | grep IPAddress
docker inspect microblog_mariadb | grep IPAddress

# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================

# Your application uses these environment variables (set in docker-compose.yml):
# FLASK_APP=microblog
# FLASK_ENV=development
# DB_HOST=mariadb
# DB_PORT=3306
# DB_USER=microblog_user
# DB_PASSWORD=microblog_password
# DB_NAME=microblog_db

# =============================================================================
# FILE LOCATIONS IN CONTAINERS
# =============================================================================

# Web container:
# - App code: /app/
# - Wait script: /app/wait-for-db.sh
# - Python: /usr/local/bin/python

# Database container:
# - Data: /var/lib/mysql
# - Config: /etc/mysql/
# - Init scripts: /docker-entrypoint-initdb.d/

# =============================================================================
# COMMON WORKFLOWS
# =============================================================================

# Daily development workflow:
# 1. docker compose up -d
# 2. Make code changes
# 3. docker compose restart web (if needed)
# 4. docker compose logs -f web (to check for errors)
# 5. docker compose down (when done)

# Testing with fresh database:
# 1. docker compose down -v
# 2. docker compose up --build
# 3. Test your application
# 4. Check logs: docker compose logs -f

# Debugging database issues:
# 1. docker compose logs mariadb
# 2. docker exec -it microblog_mariadb mysql -u root -prootpassword
# 3. Check tables and data
# 4. Restart if needed: docker compose restart mariadb

# =============================================================================
# NOTES
# =============================================================================

# - Your website runs on http://localhost:5001
# - Database runs on localhost:3306 (accessible from host)
# - Database data persists between container restarts (unless you use -v flag)
# - The database reinitializes completely when you use 'docker compose down -v'
# - Flask runs in development mode with debug info in logs
# - Wait script ensures database is ready before Flask starts
