# 🌈 FemboyWorld - Inclusive Social Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://femboyworld.online)

**FemboyWorld** is a modern, inclusive social media platform built with Flask that celebrates diversity, creativity, and community. Built for the modern web with a beautiful dark theme and comprehensive social features.

## ✨ Features

### 🌟 Core Social Features
- **User Authentication** - Secure login/registration with session management
- **Content Sharing** - Upload images, videos, and text posts
- **Social Interactions** - Like, comment, and follow other users
- **Real-time Notifications** - Stay updated with user activity
- **Advanced Search** - Find users, posts, and hashtags easily

### 🎨 Content Discovery
- **Personalized Feeds** - "For You", "Following", and "Trending" sections
- **Hashtag System** - Organize and discover content by topics
- **User Mentions** - Tag friends with @username functionality
- **Content Categories** - Fashion, style, and creative expression

### 🛡️ Community & Safety
- **Content Moderation** - Report inappropriate content
- **Support System** - Get help with tickets and issues
- **Community Guidelines** - Clear rules for inclusive participation
- **User Verification** - Secure account management

### 🚀 Technical Excellence
- **Responsive Design** - Works perfectly on all devices
- **Dark Theme** - Beautiful, modern interface
- **Performance Optimized** - Fast loading and smooth interactions
- **Security Focused** - HTTPS, CSRF protection, secure headers

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/femboyworld.git
   cd femboyworld
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**
   ```bash
   python migrate_db.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 🌐 Production Deployment

### GitHub Pages (Static)
For static hosting on GitHub Pages, the platform is ready with:
- ✅ Responsive design
- ✅ Modern CSS framework
- ✅ Optimized assets
- ✅ SEO-friendly structure

### Cloud Deployment
For full-stack deployment, see our detailed guides:
- [🚀 Heroku Deployment](HEROKU_DEPLOYMENT.md)
- [☁️ Oracle Cloud Deployment](ORACLE_CLOUD_DEPLOYMENT.md)
- [📚 Complete Deployment Guide](DEPLOYMENT_GUIDE.md)

## 🏗️ Project Structure

```
femboyworld/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── migrate_db.py         # Database migration script
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── home.html        # Home page
│   ├── login.html       # Login form
│   ├── register.html    # Registration form
│   ├── upload.html      # Content upload
│   ├── profile.html     # User profiles
│   ├── contact.html     # Contact & FAQ
│   ├── support.html     # Support tickets
│   └── report.html      # Content reporting
├── static/               # Static assets (CSS, JS, images)
└── instance/            # Database files (gitignored)
```

## 🎯 Platform Values

- **Inclusivity** - Welcome to all identities and expressions
- **Creativity** - Celebrate artistic and fashion content
- **Community** - Build meaningful connections
- **Safety** - Maintain a respectful environment
- **Innovation** - Modern web technologies and UX

## 🔧 Technology Stack

- **Backend**: Flask, SQLAlchemy, SQLite/PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Flask-Login, Werkzeug security
- **File Handling**: Secure uploads with validation
- **Styling**: Custom dark theme with CSS variables

## 📱 Features Overview

| Feature | Status | Description |
|---------|--------|-------------|
| User Authentication | ✅ Complete | Login, registration, session management |
| Content Upload | ✅ Complete | Images, videos, text posts |
| Social Features | ✅ Complete | Likes, comments, follows |
| Notifications | ✅ Complete | Real-time user activity |
| Search System | ✅ Complete | Advanced content discovery |
| Hashtags | ✅ Complete | Content organization |
| User Mentions | ✅ Complete | @username functionality |
| Support System | ✅ Complete | Help tickets and FAQ |
| Content Reporting | ✅ Complete | Community moderation |
| Responsive Design | ✅ Complete | Mobile-first approach |

## 🌟 Getting Started

### For Users
1. **Register** an account
2. **Complete** your profile
3. **Upload** your first post
4. **Connect** with other users
5. **Explore** trending content

### For Developers
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

## 📚 Documentation

- [📖 Setup Guide](SETUP_GUIDE.md) - Complete installation instructions
- [🚀 Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment
- [🔧 Configuration](config.py) - Environment and app settings
- [💾 Database Schema](migrate_db.py) - Database structure and migrations

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone and setup
git clone https://github.com/yourusername/femboyworld.git
cd femboyworld
pip install -r requirements.txt

# Run development server
python app.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check our [Setup Guide](SETUP_GUIDE.md)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/femboyworld/issues)
- **Community**: Join our discussions
- **Email**: Contact us through the platform

## 🎉 Acknowledgments

- **Flask Community** - Amazing web framework
- **Bootstrap Team** - Beautiful UI components
- **Font Awesome** - Icon library
- **Our Users** - For feedback and support

---

**Built with ❤️ for an inclusive community**

*FemboyWorld - Where creativity meets community*
