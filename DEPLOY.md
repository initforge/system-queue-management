# 🚀 Deploy QStream to DigitalOcean Droplet ($6/mo setup)

This guide uses a single **Droplet (VPS)** with Docker Compose to run everything (Backend, Frontend, and Database) for the lowest possible cost.

## 1. Create a Droplet
1. Log in to [DigitalOcean](https://cloud.digitalocean.com/).
2. Click **Create** → **Droplets**.
3. **Choose Region**: Pick one close to you (e.g., Singapore).
4. **Choose Image**: Select **Marketplace** tab and search for **"Docker"** (on Ubuntu 22.04). This saves time installing Docker.
5. **Choose Size**: 
   - Basic Plan
   - CPU Option: **Regular**
   - Select the **$6/month** (1 GB RAM / 1 CPU / 25 GB SSD) - *Must scroll left/click "See all plans" to find it.*
6. **Authentication**: Choose **SSH Key** (safer) or **Password**.
7. **Create Droplet**.

## 2. Server Setup (via SSH)
Once the Droplet is "Running", copy its **IP Address**. Open your terminal (PowerShell or Bash) and run:

```bash
ssh root@your_droplet_ip
```

### Clone the Repository
Inside the server:
```bash
git clone https://github.com/initforge/system-queue-management.git
cd system-queue-management
```

## 3. Configuration
Create the production environment file:
```bash
cp .env.example .env
nano .env
```

**Key values to set in `.env`:**
- `DATABASE_URL`: `postgresql://admin:YOUR_PASSWORD@db:5432/queue_management`
- `POSTGRES_PASSWORD`: `YOUR_PASSWORD`
- `JWT_SECRET_KEY`: `run-openssl-rand-hex-32-locally-and-paste-here`
- `REACT_APP_API_URL`: `http://your_droplet_ip:8000/api/v1`
- `REACT_APP_WS_URL`: `ws://your_droplet_ip:8000/ws`
- `CORS_ORIGINS`: `http://your_droplet_ip,http://your_droplet_ip:3000`

*(Press `Ctrl+O`, `Enter`, then `Ctrl+X` to save and exit nano)*

## 4. Run the Application
Use Docker Compose to build and start everything in the background:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### To check logs:
```bash
docker compose -f docker-compose.prod.yml logs -f
```

## 5. Firewall Setup (Crucial)
Ensure the ports are open on the Droplet:
1. In DigitalOcean Dashboard, go to **Networking** → **Firewalls**.
2. Create Firewall named `qstream-firewall`.
3. Add **Inbound Rules**:
   - **HTTP**: Port 80
   - **Custom**: Port 8000 (Backend API)
   - **SSH**: Port 22 (Already there)
4. Apply the firewall to your Droplet.

## 6. Access the App
- **Frontend**: `http://your_droplet_ip`
- **Backend API**: `http://your_droplet_ip:8000/api/v1`
- **API Docs**: `http://your_droplet_ip:8000/docs`

---

## Pros & Cons (Droplet vs App Platform)
| Feature | Droplet ($6) | App Platform ($17+) |
|---------|-------------|-------------------|
| **Cost** | 🤑 Very Low | 💸 Higher |
| **Setup** | Manual SSH | Automated |
| **Scaling** | Manual | One-click |
| **Database** | Self-managed (Free) | Managed (Paid) |
| **SSL (HTTPS)** | Manual (Certbot) | Automatic |

---

### Optional: Adding SSL (HTTPS)
If you have a domain, you can install **Nginx Proxy Manager** or use **Certbot** to get free SSL. Ask me for a separate guide if you reach this step!
