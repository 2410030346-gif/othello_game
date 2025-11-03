# 🚀 Othello Game - Render Deployment Guide

## 📋 What Gets Deployed

This deployment sets up the **multiplayer game server** on Render. Players will:
- Download and run the game on their computers (Windows, Mac, Linux)
- Connect to your Render server for online multiplayer matches
- Get automatically matched with other online players

## 🔧 Deployment Steps

### Step 1: Push to GitHub

Make sure all files are committed and pushed:
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Create Render Account

1. Go to [https://render.com](https://render.com)
2. Sign up with your GitHub account (free)

### Step 3: Deploy from GitHub

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `othello_game`
3. Configure the service:
   - **Name**: `othello-game-server`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements-server.txt`
   - **Start Command**: `python server.py`
   - **Plan**: Free

4. Click **"Create Web Service"**

### Step 4: Wait for Deployment

- First deployment takes 2-5 minutes
- You'll get a URL like: `https://othello-game-server.onrender.com`
- **IMPORTANT**: Note down this URL!

### Step 5: Get Connection Details

Since Render doesn't provide direct TCP socket access for free tier, you have two options:

#### Option A: Use Render for Testing Only
- The server will deploy successfully
- Use for learning about deployment
- For actual gameplay, host locally or use paid Render plan

#### Option B: Alternative Free Hosting
Consider these alternatives that support TCP sockets:
- **Railway.app** - Better for game servers
- **Fly.io** - Supports TCP/UDP
- **Local Network** - Host on your computer

## 🎮 How Players Connect

Once deployed, players need to:

1. **Download the game** from your GitHub:
   ```bash
   git clone https://github.com/2410030346-gif/othello_game.git
   cd othello_game
   pip install -r requirements.txt
   ```

2. **Run the game**:
   ```bash
   python main.py
   ```

3. **Click "Play Online"** and enter:
   - Host: `your-server-url.onrender.com`
   - Port: `443` (or the port Render assigns)

## ⚠️ Important Notes

### Render Free Tier Limitations:
- **Spins down after 15 minutes** of inactivity
- **Cold start** takes 30-60 seconds when waking up
- **TCP sockets** may not work on free tier (HTTP/WebSocket only)

### For Production Use:
- Upgrade to Render's paid plan ($7/month)
- Or use Railway.app (better for game servers)
- Or host on a VPS (DigitalOcean, Linode, etc.)

## 🔍 Monitoring Your Server

1. **View Logs**: 
   - Go to your Render dashboard
   - Click on your service
   - Click "Logs" tab

2. **Check Status**:
   - "Live" = Server is running
   - "Deploying" = Being updated
   - "Failed" = Check logs for errors

## 🐛 Troubleshooting

### "Connection Failed" Error
- Server may be sleeping (free tier)
- TCP sockets not supported on free tier
- Try Railway.app instead

### Server Won't Start
- Check logs in Render dashboard
- Verify `requirements-server.txt` has no errors
- Ensure Python version is compatible

### Players Can't Connect
- Verify server is "Live" in Render
- Check firewall settings
- Ensure using correct URL and port

## 💡 Better Alternatives for Game Servers

Since this is a game server using TCP sockets, consider:

1. **Railway.app** (Recommended)
   - Better for game servers
   - Supports TCP/UDP
   - Free tier includes hours
   - Easy deployment: `railway up`

2. **Fly.io**
   - Excellent for real-time apps
   - Global edge network
   - Free tier available

3. **Self-Hosted**
   - Run on your PC when playing
   - Free and full control
   - Share your IP with friends

## 📝 Files Created for Deployment

- `render.yaml` - Render configuration
- `requirements-server.txt` - Server-only dependencies (no Pygame)
- `Procfile` - Process configuration
- `DEPLOYMENT.md` - This guide
- Updated `server.py` - Uses PORT environment variable

## 🎯 Next Steps

1. ✅ Push changes to GitHub
2. ✅ Create Render account
3. ✅ Deploy service
4. ⚠️ Test connection (may not work on free tier)
5. 🔄 Consider Railway.app if Render doesn't work

---

**Need Help?** Check the logs in Render dashboard or contact support.
