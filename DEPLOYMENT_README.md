# CashMatters Deployment Guide

## VPS Server Setup (Ubuntu 22.04/20.04)

### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx curl git ufw certbot python3-certbot-nginx
```

### 2. PostgreSQL Database Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
```

In PostgreSQL shell:
```sql
CREATE DATABASE cashmatters_db;
CREATE USER cashmatters_user WITH PASSWORD 'your_secure_password_here';
ALTER ROLE cashmatters_user SET client_encoding TO 'utf8';
ALTER ROLE cashmatters_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE cashmatters_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE cashmatters_db TO cashmatters_user;
\q
```

### 3. Application Setup

```bash
# Create application user
sudo useradd --create-home --shell /bin/bash django
sudo usermod -a -G www-data django

# Create application directory
sudo mkdir -p /home/django/apps
sudo chown django:django /home/django/apps

# Upload your project files to /home/django/apps/cashmatters/
# You can use scp, rsync, or git clone
```

### 4. Python Environment Setup

```bash
# Setup virtual environment
sudo -u django bash -c "cd /home/django/apps/cashmatters && python3 -m venv venv"
sudo -u django bash -c "cd /home/django/apps/cashmatters && source venv/bin/activate && pip install --upgrade pip"
sudo -u django bash -c "cd /home/django/apps/cashmatters && source venv/bin/activate && pip install -r requirements.txt"
```

### 5. Django Configuration

```bash
# Create logs directory
sudo mkdir -p /home/django/apps/cashmatters/logs
sudo chown django:django /home/django/apps/cashmatters/logs

# Collect static files
sudo -u django bash -c "cd /home/django/apps/cashmatters && source venv/bin/activate && python manage.py collectstatic --noinput"

# Run migrations
sudo -u django bash -c "cd /home/django/apps/cashmatters && source venv/bin/activate && DJANGO_SETTINGS_MODULE=cashmatters.settings.production python manage.py migrate"

# Create superuser
sudo -u django bash -c "cd /home/django/apps/cashmatters && source venv/bin/activate && DJANGO_SETTINGS_MODULE=cashmatters.settings.production python manage.py createsuperuser"
```

### 6. Gunicorn Setup

```bash
# Copy gunicorn service file
sudo cp /home/django/apps/cashmatters/gunicorn.service /etc/systemd/system/

# Start and enable gunicorn
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### 7. Nginx Setup

```bash
# Copy nginx configuration
sudo cp /home/django/apps/cashmatters/nginx.conf /etc/nginx/sites-available/cashmatters

# Enable site
sudo ln -sf /etc/nginx/sites-available/cashmatters /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 8. Firewall Setup

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

### 9. SSL Setup (Let's Encrypt)

```bash
# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test renewal
sudo certbot renew --dry-run
```

### 10. Production Settings Configuration

Update `/home/django/apps/cashmatters/cashmatters/settings/production.py`:

1. Change `SECRET_KEY` to a secure random key
2. Update `ALLOWED_HOSTS` with your domain
3. Update database password
4. Configure email settings if needed

### 11. Monitoring and Maintenance

```bash
# Check service status
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql

# View logs
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### 12. Backup Strategy

```bash
# Database backup
sudo -u postgres pg_dump cashmatters_db > cashmatters_backup_$(date +%Y%m%d).sql

# File backup
tar -czf cashmatters_files_$(date +%Y%m%d).tar.gz /home/django/apps/cashmatters/
```

## Docker Deployment with GitHub Actions

### Prerequisites

1. **Server Setup**: Ensure Docker and Docker Compose are installed on your server
2. **SSH Access**: Ensure SSH password authentication is enabled for deployment
3. **Project Directory**: Ensure your project is cloned at `/home/django/apps/cashmatters/`

### Initial Server Setup for Docker

Run the automated setup script on your server:

```bash
# Upload the setup script to your server
scp setup-docker-deploy.sh user@72.62.147.13:~/

# Run it on the server
ssh user@72.62.147.13
chmod +x setup-docker-deploy.sh
./setup-docker-deploy.sh
```

This script will:
- Create the application directory structure
- Clone your repository
- Set up basic permissions
- Create the .env file from the example

### GitHub Actions Setup

1. **Create GitHub Secrets** in your repository settings:
   - `SERVER_HOST`: Your server IP (72.62.147.13)
   - `SERVER_USER`: SSH username (root)
   - `SERVER_PASSWORD`: Your SSH password
   - `SERVER_PORT`: SSH port (usually `22`)

2. **Password Authentication**: Since you're using password authentication, simply ensure your root password is set and accessible for the deployment.

### Deployment Workflow

The GitHub Actions workflow (`.github/workflows/deploy.yml`) will:
- Trigger on pushes to the `main` branch
- SSH into your server
- Pull latest code changes
- Run `docker compose down`
- Build with `docker compose build --no-cache`
- Start services with `docker compose up -d`

### Manual Docker Deployment

If you need to deploy manually:

```bash
# On your server
cd /home/django/apps/cashmatters

# Pull latest changes
git pull origin main

# Deploy with Docker Compose
docker compose down
docker compose build --no-cache
docker compose up -d

# Check logs
docker compose logs -f
```

### Environment Variables

Create a `.env` file in your project root with production settings:

```bash
# Copy the example file
cp .env.example .env

# Edit with your production values
nano .env
```

The `.env.example` file contains all the required environment variables for production.

## Quick Deployment Script

Run the automated deployment script:

```bash
chmod +x deploy-server.sh
sudo ./deploy-server.sh
```

## Troubleshooting

### Common Issues:

1. **Permission denied**: Check file ownership with `sudo chown -R django:www-data /home/django/apps/cashmatters/`

2. **502 Bad Gateway**: Check if Gunicorn is running: `sudo systemctl status gunicorn`

3. **Database connection failed**: Verify PostgreSQL credentials and ensure database exists

4. **Static files not loading**: Run `python manage.py collectstatic --noinput`

5. **Port 80 already in use**: Check what's using port 80: `sudo netstat -tulpn | grep :80`

## Security Checklist

- [ ] Change default PostgreSQL password
- [ ] Update Django SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable SSL/HTTPS
- [ ] Set up firewall (UFW)
- [ ] Keep system updated
- [ ] Regular backups
- [ ] Monitor logs
- [ ] Use strong passwords
- [ ] Disable DEBUG in production</content>
<parameter name="filePath">/Users/avialdosolution/Desktop/cashmatters/DEPLOYMENT_README.md