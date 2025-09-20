# DonutMarket Store - Complete E-commerce Solution

A modern e-commerce website replica for DonutSMP with Discord integration, shopping cart functionality, secure authentication, and automated ticket system.

## 🚀 Features

### Frontend
- **Responsive Design**: Modern, mobile-friendly interface
- **Discord Authentication**: Secure OAuth2 login system
- **Shopping Cart**: Add items, calculate prices, and manage orders
- **Real-time Pricing**: Dynamic price calculation for custom amounts
- **Animated UI**: Smooth animations and interactive elements
- **Product Categories**: Organized tabs for different item types

### Backend
- **Node.js Server**: Express.js backend with session management
- **Discord OAuth**: Complete OAuth2 flow with user data storage
- **API Endpoints**: RESTful API for cart and order management
- **Ticket Integration**: Automated Discord ticket creation

### Discord Bot
- **Ticket System**: Automated support ticket creation
- **Permission Control**: Role and user-based access control
- **Purchase Notifications**: Formatted embeds for new purchases
- **Interactive UI**: Discord buttons for ticket management
- **Mobile Menu** - Responsive navigation

### Interactive Elements
- Product "Buy Now" buttons open purchase modals
- Referral codes automatically apply 10% discount
- Quantity selector updates pricing in real-time
- Review form submission with validation
- Smooth scroll navigation between sections

## 🛠️ Technologies Used

- **HTML5** - Semantic markup structure
- **CSS3** - Modern styling with flexbox/grid
- **Vanilla JavaScript** - No external dependencies
- **Font Awesome** - Icon library
- **Google Fonts** - Typography (Inter font family)

## 📱 Responsive Breakpoints

- **Desktop**: 1200px and above
- **Tablet**: 768px - 1199px
- **Mobile**: Below 768px
- **Small Mobile**: Below 480px

## 🚀 Getting Started

1. **Download/Clone** the project files
2. **Open** `index.html` in your web browser
3. **Explore** the fully functional website

### Local Development
```bash
# If you have Python installed, you can run a local server:
python -m http.server 8000

# Or with Node.js:
npx http-server

# Then visit: http://localhost:8000
```

## 🎯 Key Sections

### 1. Hero Section
- Main branding and navigation
- Call-to-action buttons
- Gradient background design

### 2. How It Works
- 3-step process explanation
- Icon-based visual design
- Clear, concise descriptions

### 3. Popular Products
- DonutSMP Coins ($0.18/M)
- Elytra ($30.99)
- Netherite Armor ($19.99)
- Skeleton Spawner ($0.23)
- Mystery Box ($5.99)

### 4. Referral System
- Detailed explanation of how referrals work
- Benefits for both buyers and referrers
- Example calculations
- Call-to-action buttons

### 5. Customer Reviews
- Dynamic loading simulation
- Policy links
- Social proof elements

### 6. About & Contact
- Company information
- Feature highlights
- Review submission form

## 💡 Customization

### Colors
Edit the CSS custom properties in `styles.css`:
```css
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --accent-color: #ffd700;
  --text-color: #2d3748;
  --background-color: #f8fafc;
}
```

### Products
Update the products object in `script.js`:
```javascript
const products = {
    'Product Name': { price: 10.99, unit: '' },
    // Add more products here
};
```

### Content
Modify the HTML content in `index.html` to match your needs.

## 🔧 Browser Support

- **Chrome** 60+
- **Firefox** 60+
- **Safari** 12+
- **Edge** 79+

## 📄 License

This is a frontend recreation for educational/demonstration purposes. The original DonutMarket website and branding belong to their respective owners.

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

## 📞 Support

If you encounter any issues or have questions about the code, please create an issue in the repository.

---

**Note**: This is a static frontend copy. For full functionality, you would need to implement backend services for payment processing, user authentication, and database management.
