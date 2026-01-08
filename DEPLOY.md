# 🚀 QStream Production Deployment - DigitalOcean VPS
**IP: 178.128.55.142**

## Quick Deploy (5 Minutes)

### Step 1: SSH into VPS
```bash
ssh root@178.128.55.142
```

### Step 2: Clone & Deploy
```bash
git clone <YOUR_REPO_URL> /opt/qstream
cd /opt/qstream
chmod +x deploy.sh
sudo bash deploy.sh
```

### Step 3: Access
- Frontend: http://178.128.55.142:3000
- Backend: http://178.128.55.142:8000/docs

---

## 🔐 Default Credentials
- **Admin:** admin@qstream.vn / admin123
- **Manager:** manager.01@qstream.vn / manager123  
- **Staff:** staff.01@qstream.vn / staff123

⚠️ Change passwords after first login!

---

## 📋 Manual Steps

```bash
# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose

# Deploy
cd /opt/qstream
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# Check status
docker ps
```

---

## 🛠️ Useful Commands

```bash
# Logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart
docker-compose -f docker-compose.prod.yml restart

# Stop
docker-compose -f docker-compose.prod.yml down

# Database access
docker exec -it queue_db_prod psql -U qstream_admin -d queue_management
```

---

## ✅ Success Checklist
- [ ] 4 containers running
- [ ] Frontend loads at :3000
- [ ] API docs at :8000/docs
- [ ] Can login
- [ ] WebSocket works
- [ ] Firewall configured (ports 22, 80, 3000, 8000)
