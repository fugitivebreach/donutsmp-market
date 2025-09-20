const express = require('express');
const cors = require('cors');
const axios = require('axios');
const session = require('express-session');
const path = require('path');
const fs = require('fs');
require('dotenv').config({ path: path.join(__dirname, '../config/.env') });

const app = express();
const PORT = process.env.PORT || 3000;

// Discord OAuth configuration
const DISCORD_CLIENT_ID = process.env.DISCORD_CLIENT_ID || 'YOUR_DISCORD_CLIENT_ID';
const DISCORD_CLIENT_SECRET = process.env.DISCORD_CLIENT_SECRET || 'YOUR_DISCORD_CLIENT_SECRET';
const DISCORD_REDIRECT_URI = process.env.DISCORD_REDIRECT_URI || 'http://localhost:3000/auth/callback';
const DISCORD_BOT_WEBHOOK_URL = process.env.DISCORD_BOT_WEBHOOK_URL || 
    (process.env.RAILWAY_ENVIRONMENT === 'production' 
        ? `https://${process.env.RAILWAY_PUBLIC_DOMAIN || 'donutmarket.up.railway.app'}/webhook/purchase`
        : 'http://localhost:8080/webhook/purchase');

// Middleware
const allowedOrigins = process.env.RAILWAY_ENVIRONMENT === 'production' 
    ? [process.env.RAILWAY_PUBLIC_DOMAIN || 'https://your-app.railway.app']
    : ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5500'];

app.use(cors({
    origin: allowedOrigins,
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging middleware
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
    next();
});

// Middleware to ensure proper content type for HTML files
app.use((req, res, next) => {
    if (req.path.endsWith('.html') || req.path === '/') {
        res.setHeader('Content-Type', 'text/html; charset=utf-8');
    }
    next();
});

// Session configuration
app.use(session({
    secret: process.env.SESSION_SECRET || 'your-secret-key-here',
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: false, // Set to true in production with HTTPS
        maxAge: 24 * 60 * 60 * 1000 // 24 hours
    }
}));

// Serve static files with proper MIME types
app.use(express.static(path.join(__dirname, '../public'), {
    setHeaders: (res, path) => {
        if (path.endsWith('.html')) {
            res.setHeader('Content-Type', 'text/html; charset=utf-8');
        } else if (path.endsWith('.css')) {
            res.setHeader('Content-Type', 'text/css');
        } else if (path.endsWith('.js')) {
            res.setHeader('Content-Type', 'application/javascript');
        }
    }
}));

// Routes

// Home route - serve the main page
app.get('/', (req, res) => {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.sendFile(path.join(__dirname, '../public/replica.html'));
});

// Login route - redirect to Discord OAuth
app.get('/login', (req, res) => {
    const discordAuthUrl = `https://discord.com/api/oauth2/authorize?client_id=${DISCORD_CLIENT_ID}&redirect_uri=${encodeURIComponent(DISCORD_REDIRECT_URI)}&response_type=code&scope=identify%20email%20guilds.join`;
    res.redirect(discordAuthUrl);
});

// Discord OAuth callback
app.get('/auth/callback', async (req, res) => {
    const { code } = req.query;
    
    if (!code) {
        return res.redirect('/login.html?error=no_code');
    }
    
    try {
        // Exchange code for access token
        const tokenResponse = await axios.post('https://discord.com/api/oauth2/token', new URLSearchParams({
            client_id: DISCORD_CLIENT_ID,
            client_secret: DISCORD_CLIENT_SECRET,
            grant_type: 'authorization_code',
            code: code,
            redirect_uri: DISCORD_REDIRECT_URI,
            scope: 'identify email guilds.join'
        }), {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });
        
        const { access_token, token_type } = tokenResponse.data;
        
        // Get user information
        const userResponse = await axios.get('https://discord.com/api/users/@me', {
            headers: {
                Authorization: `${token_type} ${access_token}`
            }
        });
        
        const userData = userResponse.data;
        
        // Store user data in session
        req.session.user = {
            id: userData.id,
            username: `${userData.username}#${userData.discriminator}`,
            avatar: userData.avatar ? `https://cdn.discordapp.com/avatars/${userData.id}/${userData.avatar}.png` : null,
            email: userData.email,
            access_token: access_token
        };
        
        // Redirect to success page with user data
        const userDataEncoded = encodeURIComponent(JSON.stringify({
            id: userData.id,
            username: `${userData.username}#${userData.discriminator}`,
            avatar: userData.avatar ? `https://cdn.discordapp.com/avatars/${userData.id}/${userData.avatar}.png` : 'https://cdn.discordapp.com/embed/avatars/0.png'
        }));
        
        res.redirect(`/auth/success?user=${userDataEncoded}`);
        
    } catch (error) {
        console.error('Discord OAuth error:', error.response?.data || error.message);
        res.redirect('/login.html?error=oauth_failed');
    }
});

// Auth success page
app.get('/auth/success', (req, res) => {
    const userDataEncoded = req.query.user;
    
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Successful</title>
            <style>
                body {
                    font-family: 'Inter', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    color: white;
                }
                .container {
                    text-align: center;
                    background: rgba(255, 255, 255, 0.1);
                    padding: 2rem;
                    border-radius: 12px;
                    backdrop-filter: blur(10px);
                }
                .success-icon {
                    font-size: 3rem;
                    color: #48bb78;
                    margin-bottom: 1rem;
                }
            </style>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css">
        </head>
        <body>
            <div class="container">
                <div class="success-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h1>Login Successful!</h1>
                <p>You have been successfully logged in with Discord.</p>
                <p>Redirecting you back to the store...</p>
            </div>
            
            <script>
                // Store user data in localStorage
                const userData = decodeURIComponent('${userDataEncoded}');
                localStorage.setItem('discord_logged_in', 'true');
                localStorage.setItem('discord_user', userData);
                
                // Redirect after 2 seconds
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            </script>
        </body>
        </html>
    `);
});

// API Routes

// Get current user
app.get('/api/user', (req, res) => {
    if (req.session.user) {
        res.json({
            success: true,
            user: req.session.user
        });
    } else {
        res.status(401).json({
            success: false,
            error: 'Not authenticated'
        });
    }
});

// Logout
app.post('/api/logout', (req, res) => {
    req.session.destroy((err) => {
        if (err) {
            return res.status(500).json({
                success: false,
                error: 'Failed to logout'
            });
        }
        res.json({
            success: true,
            message: 'Logged out successfully'
        });
    });
});

// Create ticket (purchase)
app.post('/api/create-ticket', async (req, res) => {
    try {
        const { buyer, discord, transactionId, totalAmount, items } = req.body;
        
        // Validate required fields
        if (!buyer || !discord || !transactionId || !totalAmount || !items) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields'
            });
        }
        
        // Send to Discord bot webhook
        const webhookData = {
            buyer,
            discord,
            transactionId,
            totalAmount,
            items
        };
        
        console.log('🔔 Sending webhook to Discord bot:', DISCORD_BOT_WEBHOOK_URL);
        console.log('📋 Webhook data:', JSON.stringify(webhookData, null, 2));
        
        try {
            let ticketResponse;
            
            if (process.env.RAILWAY_ENVIRONMENT === 'production') {
                // Use internal ticket creation for Railway
                ticketResponse = await createDiscordTicketInternal(webhookData);
                if (ticketResponse) {
                    console.log('✅ Discord ticket created internally:', ticketResponse);
                } else {
                    throw new Error('Failed to create internal ticket');
                }
            } else {
                // Use webhook for local development
                const healthCheck = await axios.get('http://localhost:8080/health', { timeout: 2000 }).catch(() => null);
                
                if (!healthCheck) {
                    console.log('⚠️  Discord bot webhook server is not running');
                    throw new Error('Discord bot webhook server is offline');
                }
                
                const response = await axios.post(DISCORD_BOT_WEBHOOK_URL, webhookData, {
                    timeout: 10000,
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                ticketResponse = response.data;
                console.log('✅ Discord webhook response:', ticketResponse);
            }
            
            res.json({
                success: true,
                message: 'Ticket created successfully',
                transactionId: transactionId,
                ticketData: ticketResponse
            });
            
        } catch (error) {
            console.error('❌ Discord webhook error:', error.message);
            console.error('🔗 Webhook URL:', DISCORD_BOT_WEBHOOK_URL);
            console.error('💡 Make sure the Discord bot is running: python bot/discord_bot.py');
            
            // Still return success - order was received, just ticket creation failed
            res.json({
                success: true,
                message: 'Order received successfully',
                note: 'Discord bot is offline - ticket will be created manually',
                error: 'Discord bot webhook unavailable',
                instructions: 'Please start the Discord bot to enable automatic ticket creation'
            });
        }
        
    } catch (error) {
        console.error('Create ticket error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// Get order status
app.get('/api/order/:transactionId', (req, res) => {
    const { transactionId } = req.params;
    
    // In a real implementation, you would check a database
    // For now, return a mock response
    res.json({
        success: true,
        order: {
            transactionId,
            status: 'processing',
            items: [
                { name: 'DonutSMP Money', amount: '200M' }
            ],
            totalAmount: '32.00',
            createdAt: new Date().toISOString()
        }
    });
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Store configuration endpoint
app.get('/api/store-config', (req, res) => {
    try {
        const configPath = path.join(__dirname, '../stores/config.json');
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        res.json(config);
    } catch (error) {
        console.error('Error loading store config:', error);
        res.status(500).json({ error: 'Failed to load store configuration' });
    }
});

// All stores endpoint
app.get('/api/all-stores', (req, res) => {
    try {
        const storesDir = path.join(__dirname, '../stores');
        const files = fs.readdirSync(storesDir).filter(file => file.endsWith('.json'));
        
        const stores = files.map(file => {
            try {
                const filePath = path.join(storesDir, file);
                const storeData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                
                // Add storeId if not present
                if (!storeData.storeId) {
                    storeData.storeId = file.replace('.json', '');
                }
                
                return storeData;
            } catch (error) {
                console.error(`Error loading store ${file}:`, error);
                return null;
            }
        }).filter(store => store !== null);
        
        res.json(stores);
    } catch (error) {
        console.error('Error loading stores:', error);
        res.status(500).json({ error: 'Failed to load stores' });
    }
});

// Discord bot webhook endpoint (for Railway deployment)
app.post('/webhook/purchase', (req, res) => {
    console.log('🔔 Received webhook from Discord bot:', req.body);
    res.json({ success: true, message: 'Webhook received' });
});

// Internal function to create Discord tickets (for Railway)
async function createDiscordTicketInternal(ticketData) {
    if (process.env.RAILWAY_ENVIRONMENT !== 'production') {
        return null; // Only use this in Railway production
    }
    
    try {
        // In Railway, we'll store ticket data in a simple queue/file system
        // The Discord bot will periodically check for new tickets
        const ticketsDir = path.join(__dirname, '../tickets');
        if (!fs.existsSync(ticketsDir)) {
            fs.mkdirSync(ticketsDir, { recursive: true });
        }
        
        const ticketFile = path.join(ticketsDir, `ticket_${ticketData.transactionId}.json`);
        fs.writeFileSync(ticketFile, JSON.stringify(ticketData, null, 2));
        
        console.log('✅ Ticket data saved for Discord bot processing:', ticketFile);
        return { success: true, ticket_id: ticketData.transactionId };
    } catch (error) {
        console.error('❌ Error saving ticket data:', error);
        return null;
    }
}

// Test ticket creation endpoint
app.post('/api/test-ticket', async (req, res) => {
    try {
        const testData = {
            buyer: 'TestUser',
            discord: 'TestUser#1234',
            transactionId: 'TEST_' + Date.now(),
            totalAmount: '25.00',
            items: [
                { name: 'DonutSMP Money', amount: '200M' },
                { name: 'Test Item', amount: '1x' }
            ]
        };
        
        console.log('🧪 Testing ticket creation with data:', testData);
        
        const response = await axios.post(DISCORD_BOT_WEBHOOK_URL, testData, {
            timeout: 10000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        res.json({
            success: true,
            message: 'Test ticket created successfully',
            botResponse: response.data
        });
        
    } catch (error) {
        console.error('Test ticket error:', error.message);
        res.status(500).json({
            success: false,
            error: error.message,
            webhookUrl: DISCORD_BOT_WEBHOOK_URL
        });
    }
});

// Serve static files
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/replica.html'));
});

app.get('/stores', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/stores.html'));
});

app.get('/replica.html', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/replica.html'));
});

app.get('/login.html', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/login.html'));
});

app.get('/checkout.html', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/checkout.html'));
});

app.get('/success.html', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/success.html'));
});

app.get('/policy.html', (req, res) => {
});

app.get('/policy', (req, res) => {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.sendFile(path.join(__dirname, '../public/policy.html'));
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Server error:', error);
    res.status(500).json({
        success: false,
        error: 'Internal server error'
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        success: false,
        error: 'Route not found'
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
    console.log(`📁 Serving files from: ${path.join(__dirname, '../public')}`);
    console.log(`📱 Discord OAuth redirect URI: ${DISCORD_REDIRECT_URI}`);
    console.log(`🤖 Discord bot webhook URL: ${DISCORD_BOT_WEBHOOK_URL}`);
    
    // Configuration warnings
    if (DISCORD_CLIENT_ID === 'YOUR_DISCORD_CLIENT_ID') {
        console.log('⚠️  Please set DISCORD_CLIENT_ID in your .env file');
    }
    if (DISCORD_CLIENT_SECRET === 'YOUR_DISCORD_CLIENT_SECRET') {
        console.log('⚠️  Please set DISCORD_CLIENT_SECRET in your .env file');
    }
    
    console.log('\n📄 Available routes:');
    console.log('  GET  /                  → replica.html');
    console.log('  GET  /replica.html      → replica.html');
    console.log('  GET  /login.html        → login.html');
    console.log('  GET  /checkout.html     → checkout.html');
    console.log('  GET  /success.html      → success.html');
    console.log('  GET  /policy.html       → policy.html');
    console.log('  GET  /health            → health check');
});

module.exports = app;
