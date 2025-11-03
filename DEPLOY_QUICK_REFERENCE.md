# 🚀 QUICK DEPLOYMENT REFERENCE

## ⚡ 3-Minute Deploy to Railway (Recommended)

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Deploy!
railway up
```

**Done!** Your server is live with TCP support! 🎉

---

## 🌐 Alternative: Deploy to Render

### Online (No CLI):
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect `othello_game` repo
4. Click "Create Web Service"

### With CLI:
```bash
# 1. Install Render CLI
npm i -g render-cli

# 2. Login
render login

# 3. Deploy
render deploy
```

**Note:** Render free tier may not support TCP sockets!

---

## 📁 Files You Need (All Created ✅)

- `render.yaml` - Render configuration
- `railway.json` - Railway configuration
- `Procfile` - Process command
- `runtime.txt` - Python version
- `requirements-server.txt` - Dependencies
- `.renderignore` - Exclude files

---

## 🎯 What Gets Deployed

**Server Only:**
- `server.py` (matchmaking server)
- `network.py` (networking logic)
- Minimal dependencies (no Pygame)

**Not Deployed (runs locally):**
- `main.py` (game client)
- Game assets, sounds, graphics
- AI models

---

## 🔗 How Players Connect

1. Player runs game locally: `python main.py`
2. Clicks "Play Online"
3. Enters server URL from Railway/Render
4. Gets matched with opponent
5. Plays online!

---

## ⚠️ Important

| Platform | TCP Support | Free Tier | Best For |
|----------|-------------|-----------|----------|
| **Railway** | ✅ Yes | $5 credit | Games ⭐ |
| **Render** | ❌ Paid only | ✅ Yes | Web apps |

**Recommendation:** Use Railway for game servers!

---

## 🐛 Quick Troubleshooting

**Can't connect?**
→ Use Railway instead of Render free tier

**Server sleeping?**
→ Free tier behavior, upgrade or use keep-alive

**Deployment failed?**
→ Check logs in dashboard

---

## 📞 Get Help

- Full Guide: `DEPLOYMENT.md`
- Quick Start: `DEPLOY_QUICK_START.md`
- Checklist: `DEPLOYMENT_CHECKLIST.md`
- Summary: `README_RENDER.md`

---

**Ready? Just run: `railway up` 🚀**
