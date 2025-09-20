# DonutMarket Store - Complete E-commerce Solution

A modern e-commerce website replica for DonutSMP with Discord integration, shopping cart functionality, secure authentication, and automated ticket system.

## 📁 Project Structure

```
donutmarket-store/
├── 📂 backend/                 # Express.js server
│   └── server.js              # Main server file
├── 📂 bot/                    # Discord bot
│   ├── discord_bot.py         # Bot implementation
│   └── requirements.txt       # Python dependencies
├── 📂 public/                 # Frontend files
│   ├── replica.html           # Main store page
│   ├── login.html             # Discord authentication
│   ├── checkout.html          # Shopping cart & checkout
│   ├── success.html           # Order confirmation
│   ├── policy.html            # Terms & refund policy
│   ├── index.html             # Alternative layout
│   └── original_source.html   # Original website source
├── 📂 config/                 # Configuration files
│   └── .env.example           # Environment variables template
├── 📂 docs/                   # Documentation
├── 📂 static/                 # Static assets (images, etc.)
├── 📂 assets/                 # Additional assets
├── package.json               # Node.js dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm run setup
```

### 2. Configure Environment
```bash
# Copy and edit the environment file
copy config\.env.example .env
# Edit .env with your Discord credentials
```

### 3. Start the Application
```bash
# Start the backend server
npm start

# In another terminal, start the Discord bot
npm run bot
```

### 4. Access the Application
Open `http://localhost:3000` in your browser

## 🛠️ Available Scripts

- `npm start` - Start the production server
- `npm run dev` - Start development server with auto-reload
- `npm run bot` - Start the Discord bot
- `npm run setup` - Install all dependencies (Node.js + Python)
- `npm run clean` - Clean and reinstall dependencies
- `npm run build` - Build the project (static files)
- `npm run lint` - Run linting (placeholder)

## 🔧 Configuration

### Discord Application Setup
1. Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Get your Client ID and Client Secret
3. Create a bot and get the bot token
4. Set up OAuth2 redirect URI: `http://localhost:3000/auth/callback`

### Environment Variables
Copy `config/.env.example` to `.env` and fill in:

```env
# Discord OAuth
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=http://localhost:3000/auth/callback

# Discord Bot
BOT_TOKEN=your_bot_token
GUILD_ID=your_server_id
TICKET_CATEGORY_ID=your_category_id
SERVER_OWNER_ID=your_user_id
ALLOWED_USER_IDS=user1,user2
ALLOWED_ROLE_IDS=role1,role2

# Server
PORT=3000
SESSION_SECRET=your_session_secret
```

## 🌟 Features

### Frontend (`public/`)
- **Modern UI**: Responsive design with animations
- **Shopping Cart**: Real-time price calculation
- **Authentication**: Discord OAuth2 integration
- **Multiple Pages**: Store, login, checkout, success, policy

### Backend (`backend/`)
- **Express Server**: RESTful API with session management
- **Discord OAuth**: Complete authentication flow
- **API Endpoints**: Cart, orders, user management
- **Static Serving**: Proper MIME types and headers

### Discord Bot (`bot/`)
- **Ticket System**: Automated support ticket creation
- **Permissions**: Role and user-based access control
- **Slash Commands**: Interactive bot commands
- **Purchase Integration**: Webhook for order processing

## 🔗 API Endpoints

### Authentication
- `GET /` → Main store page
- `GET /login` → Discord OAuth redirect
- `GET /auth/callback` → OAuth callback handler
- `POST /api/logout` → Logout user

### Orders
- `POST /api/create-ticket` → Create purchase ticket
- `GET /api/order/:id` → Get order status
- `GET /api/user` → Get current user info

### Pages
- `GET /replica.html` → Main store
- `GET /login.html` → Login page
- `GET /checkout.html` → Checkout page
- `GET /success.html` → Success page
- `GET /policy.html` → Policy page

## 🤖 Discord Bot Commands

- `/create_ticket [reason]` - Create support ticket
- `/test_purchase` - Test purchase ticket system
- `/close_ticket` - Close current ticket

## 🔒 Security Features

- **Session Management**: Secure Express sessions
- **CORS Protection**: Configured for specific origins
- **Input Validation**: Server-side validation
- **Permission Control**: Role-based Discord access
- **OAuth2 Security**: Secure Discord authentication

## 🐛 Troubleshooting

### Common Issues

1. **HTML showing as plain text**
   - Server now properly sets MIME types
   - Check console for request logs

2. **Bot not responding**
   - Verify bot token and permissions
   - Check guild and category IDs

3. **OAuth errors**
   - Verify client credentials
   - Check redirect URI matches exactly

### Debug Information
- Server logs all requests with timestamps
- Bot logs ticket creation attempts
- Check browser console for frontend errors

## 📝 Development

### File Organization
- **Frontend**: All HTML/CSS/JS in `public/`
- **Backend**: Server logic in `backend/`
- **Bot**: Discord bot in `bot/`
- **Config**: Environment and settings in `config/`
- **Docs**: Documentation in `docs/`

### Adding New Features
1. Frontend changes go in `public/`
2. API endpoints added to `backend/server.js`
3. Bot features added to `bot/discord_bot.py`
4. Update this README for new features

## 📄 License

This project is for educational purposes. Please respect the original DonutMarket branding and content.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

- Check the troubleshooting section
- Review server and bot logs
- Create an issue in the repository
- Contact the development team

---

**Note**: This is a replica/educational project. Ensure you have permission before using any branding or content from the original DonutMarket.
