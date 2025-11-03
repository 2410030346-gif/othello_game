# 🎮 Othello Game Server - Quick Deployment

## ⚡ Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

### 1️⃣ One-Click Deploy

1. Click the button above or go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect this GitHub repository
4. Render will auto-detect `render.yaml` configuration
5. Click **"Create Web Service"**
6. Wait 2-5 minutes for deployment ✅

### 2️⃣ Your Server URL

After deployment, you'll get a URL like:
```
https://othello-game-server-xxxx.onrender.com
```

### 3️⃣ Connect Players

Players run the desktop game locally and connect to your server:

**In the game:**
- Click **"Play Online"**
- Enter your Render URL (without https://)
- Enter port: `10000` (default Render port)

---

## 📦 What's Deployed

- **Server Type**: TCP Socket Server for multiplayer matchmaking
- **Port**: Auto-assigned by Render (check dashboard)
- **Files**: Only `server.py` and `network.py` (no game client)
- **Dependencies**: None (pure Python sockets)

## ⚠️ Important: Render Free Tier Limitations

### The Problem:
Render's free tier is designed for HTTP web services, not TCP game servers.

### What This Means:
- ✅ Server will deploy successfully
- ✅ Will appear "Live" in dashboard
- ❌ TCP connections may not work on free tier
- ❌ Free tier spins down after 15 minutes

### Solutions:

#### Option A: Use Railway (Recommended for Game Servers)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```
Railway supports TCP sockets and is better for game servers!

#### Option B: Upgrade Render Plan
- Render Paid Plan: $7/month
- Full TCP socket support
- Always-on server

#### Option C: Run Locally
```bash
python server.py
# Share your IP with friends
```

---

## 🔧 Configuration Files

### `render.yaml`
Defines Render service configuration:
- Build command
- Start command
- Environment variables

### `requirements-server.txt`
Server-only dependencies (minimal, no Pygame or PyTorch)

### `Procfile`
Process definition for Render

### `.renderignore`
Excludes unnecessary files from deployment

---

## 📊 Monitoring

### Check Server Status
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click your service name
3. View **Logs** tab for real-time output

### Expected Logs
```
Othello Online Game Server
==================================================
Starting server on port 10000...
Environment: Render
Server started on port 10000
Server running! Players can connect to:
...
```

---

## 🐛 Troubleshooting

### Server Shows "Live" But Players Can't Connect
**Cause**: Render free tier doesn't support TCP sockets  
**Solution**: Use Railway.app or upgrade to paid plan

### Server Spins Down
**Cause**: Free tier sleeps after 15 min inactivity  
**Solution**: Upgrade or use a keep-alive service

### "Port Already in Use"
**Cause**: Multiple instances running  
**Solution**: Use `PORT` environment variable (already configured)

---

## 💰 Cost Comparison

| Platform | Free Tier | TCP Support | Best For |
|----------|-----------|-------------|----------|
| **Railway** | ✅ $5 credit | ✅ Yes | Game servers ⭐ |
| **Render** | ✅ Yes | ❌ Paid only | Web apps |
| **Fly.io** | ✅ Yes | ✅ Yes | Real-time apps |
| **Heroku** | ❌ No | ✅ Yes ($7/mo) | Legacy apps |

---

## 🚀 Alternative: Deploy to Railway

Railway is better for game servers:

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Deploy
railway up

# 5. Get your URL
railway domain
```

Railway will give you a URL with TCP support included!

---

## 📝 Summary

✅ **Deployment files created**:
- `render.yaml` - Render config
- `requirements-server.txt` - Dependencies
- `Procfile` - Process definition
- `runtime.txt` - Python version
- `.renderignore` - Exclude files
- `DEPLOYMENT.md` - Full guide

✅ **Server updated**:
- Uses `PORT` environment variable
- Logs environment info
- Ready for cloud deployment

⚠️ **Recommendation**:
Use **Railway.app** for game servers instead of Render's free tier!

---

**Ready to deploy?** Push to GitHub and follow Step 1 above! 🚀
