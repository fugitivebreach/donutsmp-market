# Railway Deployment Guide

## 🚀 Deploy DonutMarket Store to Railway

### Prerequisites
- Railway account (https://railway.app)
- Discord application with OAuth2 configured
- Discord bot token

### Step 1: Prepare Your Repository
1. Push your code to GitHub/GitLab
2. Ensure all files are committed including:
   - `railway.json` (Docker configuration)
   - `Dockerfile` (Multi-language build)
   - `Procfile` (Fallback process definition)
   - `.env.example` (Environment template)
   - `.dockerignore` (Build optimization)

### Step 2: Create Railway Project
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### Step 3: Configure Environment Variables
In Railway dashboard, add these environment variables:

```env
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=https://your-app-name.railway.app/auth/callback
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_BOT_WEBHOOK_URL=https://your-app-name.railway.app:8080/webhook/purchase
SESSION_SECRET=your_random_session_secret
RAILWAY_ENVIRONMENT=production
```

### Step 4: Update Discord Application
1. Go to Discord Developer Portal
2. Update OAuth2 redirect URI to: `https://your-app-name.railway.app/auth/callback`
3. Update bot webhook URL if needed

### Step 5: Deploy
1. Railway will automatically deploy when you push to main branch
2. Both Node.js server and Python Discord bot will start together
3. Check logs for any errors

### Features Included
✅ **Multi-Store System** - Browse different Minecraft stores
✅ **Discord OAuth** - Login with Discord
✅ **Payment Methods** - Configurable payment options
✅ **Shopping Cart** - Multi-store cart system
✅ **Discord Bot** - Automatic ticket creation
✅ **Responsive Design** - Works on all devices

### Troubleshooting
- Check Railway logs if deployment fails
- Ensure all environment variables are set
- Verify Discord OAuth redirect URI matches exactly
- Make sure bot has proper permissions in Discord server

### Local Development
```bash
npm install
pip install -r bot/requirements.txt
npm run dev
```

### Production Commands
- `npm start` - Starts both server and bot
- `npm run start:server` - Server only
- `npm run start:bot` - Bot only
