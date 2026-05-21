# Vercel Deployment Guide for QuantMuse Interactive Dashboard

## Overview

This guide provides step-by-step instructions for deploying the QuantMuse Interactive Dashboard on Vercel using serverless functions.

## Prerequisites

- **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
- **GitHub Account**: For version control and deployment
- **Node.js 16+**: For local development
- **Python 3.9+**: For serverless functions

## Deployment Architecture

### Vercel Serverless Setup

```
QuantMuse Dashboard (Vercel)
├── Static Files (HTML/CSS/JS)
│   ├── vercel_dashboard.html
│   ├── vercel_dashboard_config.js
│   └── Chart.js, Axios (CDN)
├── Serverless API
│   └── api/index.py (Python)
├── Configuration
│   ├── vercel.json
│   └── requirements.txt
└── Mock Data System
    └── Built-in mock trading system
```

## Step-by-Step Deployment

### 1. Prepare Your Project

#### Create Vercel Project Structure

```bash
# Navigate to your project directory
cd c:\Users\Dataentry\Project_X\QuantMuse

# Ensure you have the required files
ls -la
```

Required files:
- `vercel.json` - Vercel configuration
- `api/index.py` - Serverless API functions
- `vercel_dashboard.html` - Main dashboard
- `vercel_dashboard_config.js` - Dashboard configuration
- `requirements.txt` - Python dependencies

#### Update Vercel Configuration

Open `vercel.json` and verify the configuration:

```json
{
  "version": 2,
  "name": "quantmuse-interactive-dashboard",
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/vercel_dashboard.html"
    }
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  },
  "env": {
    "PYTHON_VERSION": "3.9"
  },
  "installCommand": "pip install -r requirements.txt",
  "framework": null
}
```

### 2. Install Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Verify installation
vercel --version
```

### 3. Login to Vercel

```bash
# Login to your Vercel account
vercel login

# Follow the instructions to authenticate
```

### 4. Initialize Vercel Project

```bash
# Initialize Vercel in your project directory
vercel init

# Answer the prompts:
# - Set up and deploy "QuantMuse Interactive Dashboard"? Yes
# - Which scope do you want to deploy to? (Your account)
# - Link to existing project? No
# - What's your project's name? quantmuse-interactive-dashboard
# - In which directory is your code located? ./
# - Want to override the settings? No
```

### 5. Configure Environment Variables

```bash
# Set environment variables (optional)
vercel env add PYTHON_VERSION

# Set to: 3.9
# Select: Production
```

### 6. Deploy to Vercel

```bash
# Deploy your project
vercel --prod

# Wait for deployment to complete
# You'll get a URL like: https://quantmuse-interactive-dashboard.vercel.app
```

### 7. Verify Deployment

1. **Open the deployed URL** in your browser
2. **Check the dashboard** loads correctly
3. **Test API endpoints**:
   - System status: `https://your-url.vercel.app/api/system/status`
   - Portfolio state: `https://your-url.vercel.app/api/portfolio/state`
   - Broker status: `https://your-url.vercel.app/api/brokers/status`

## Configuration Options

### 1. Custom Domain

```bash
# Add custom domain
vercel domains add your-domain.com

# Verify DNS settings
vercel domains ls
```

### 2. Environment Variables

```bash
# Add custom environment variables
vercel env add API_KEY
vercel env add BROKER_CONFIG
vercel env add RISK_LIMITS
```

### 3. Build Configuration

Update `vercel.json` for custom build settings:

```json
{
  "build": {
    "env": {
      "PYTHON_VERSION": "3.9"
    },
    "command": "echo 'Build complete'"
  }
}
```

## Features Available on Vercel

### ✅ **Fully Functional Features**

1. **Real-Time Monitoring**
   - Portfolio tracking with live updates
   - Interactive charts and visualizations
   - Broker status monitoring
   - Position management

2. **Manual Trading Controls**
   - Order placement with validation
   - Risk calculation and preview
   - Order management
   - Position closing

3. **Strategy Management**
   - Strategy start/stop controls
   - Performance monitoring
   - Parameter adjustment
   - A/B testing interface

4. **Risk Management**
   - Adjustable risk limits
   - Real-time exposure tracking
   - Risk alerts and warnings
   - Emergency stop functionality

5. **Testing Tools**
   - Scenario testing
   - Load testing
   - Test suite execution
   - Performance monitoring

6. **Transition Control**
   - Paper-to-live transition management
   - Phase configuration
   - Progress tracking
   - Analytics dashboard

### ⚠️ **Limitations on Vercel**

1. **WebSocket Not Supported**
   - Real-time updates use polling instead
   - 5-second refresh intervals
   - Slightly delayed data updates

2. **No Persistent Storage**
   - Data resets on function restart
   - Mock data system for demonstration
   - Session-based state management

3. **Function Duration Limits**
   - 30-second maximum execution time
   - Timeout handling implemented
   - Optimized for quick responses

4. **No File System Access**
   - Cannot write to disk
   - All data handled in memory
   - Mock data generation

## Mock Data System

The Vercel deployment includes a comprehensive mock data system that simulates:

### 1. **Portfolio Simulation**
```python
portfolio = {
    'total_value': 25000,
    'cash': 20000,
    'positions_count': 5,
    'pnl': 0,
    'win_rate': 0.65,
    'sharpe_ratio': 1.5
}
```

### 2. **Broker Simulation**
```python
brokers = {
    'deriv': {
        'connected': True,
        'status': 'Connected',
        'balance': 10000,
        'positions': 2,
        'performance': 0.05
    },
    'mt5': {
        'connected': True,
        'status': 'Connected',
        'balance': 15000,
        'positions': 3,
        'performance': 0.08
    }
}
```

### 3. **Real-Time Updates**
- Price fluctuations
- Position P&L changes
- Broker status updates
- Strategy performance tracking

## API Endpoints

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/system/status` | Get system status |
| GET | `/api/portfolio/state` | Get portfolio information |
| GET | `/api/brokers/status` | Get broker status |

### Trading Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/orders/place` | Place a new order |
| POST | `/api/positions/close/{id}` | Close a position |

### Strategy Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/strategies/start` | Start a strategy |
| POST | `/api/strategies/stop` | Stop a strategy |
| GET | `/api/strategies/performance` | Get performance data |

### Risk Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/risk/limits` | Get risk limits |
| POST | `/api/risk/limits` | Update risk limits |
| POST | `/api/risk/emergency_stop` | Emergency stop all trading |

### Testing Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/testing/run_scenario` | Run scenario test |
| POST | `/api/testing/run_load_test` | Run load test |

### Transition Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/transition/status` | Get transition status |
| POST | `/api/transition/start` | Start transition |
| POST | `/api/transition/advance` | Advance phase |

## Monitoring and Debugging

### 1. Vercel Dashboard

- Access at [vercel.com](https://vercel.com)
- Monitor function logs
- Check performance metrics
- View error reports

### 2. Local Development

```bash
# Test locally before deployment
vercel dev

# Access at http://localhost:3000
```

### 3. Debug Mode

Enable debug logging in `api/index.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 4. Error Handling

The dashboard includes comprehensive error handling:
- Network error detection
- Fallback to mock data
- User-friendly error messages
- Automatic retry functionality

## Performance Optimization

### 1. Caching

- Browser caching for static assets
- API response caching (30 seconds)
- Chart data optimization

### 2. Bundle Optimization

- Minified HTML/CSS/JS
- CDN for external libraries
- Optimized image loading

### 3. Function Optimization

- Fast response times (< 1 second)
- Efficient data processing
- Memory usage optimization

## Security Considerations

### 1. API Security

- CORS configuration
- Input validation
- Rate limiting (built-in)
- Error message sanitization

### 2. Data Protection

- No sensitive data in logs
- Mock data for demonstration
- No persistent storage

### 3. Access Control

- Public read access
- No authentication required
- Safe for demonstration

## Troubleshooting

### Common Issues

#### 1. Deployment Failed

**Problem**: Build or deployment fails

**Solutions**:
- Check `vercel.json` syntax
- Verify `requirements.txt` format
- Check Python version compatibility
- Review Vercel logs

#### 2. API Not Responding

**Problem**: API endpoints return errors

**Solutions**:
- Check function logs in Vercel dashboard
- Verify import statements
- Test with `vercel dev` locally
- Check timeout settings

#### 3. Dashboard Not Loading

**Problem**: Dashboard shows blank page

**Solutions**:
- Check browser console for errors
- Verify static file paths
- Check network requests
- Clear browser cache

#### 4. Real-Time Updates Not Working

**Problem**: Data not updating automatically

**Solutions**:
- Check polling status indicator
- Verify API responses
- Check browser network tab
- Ensure JavaScript is enabled

### Debug Mode

Enable detailed logging:

```python
# In api/index.py
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add logging to functions
logger.info(f"Processing request: {path}")
```

### Performance Monitoring

Monitor key metrics:
- Function response time
- Error rate
- Memory usage
- Request frequency

## Advanced Configuration

### 1. Custom Domains

```bash
# Add custom domain
vercel domains add your-domain.com

# Configure DNS records
# A record: 76.76.19.19
# CNAME: cname.vercel-dns.com
```

### 2. Environment Variables

```bash
# Add production variables
vercel env add NODE_ENV production
vercel env add API_URL https://api.example.com
vercel env add DEBUG false
```

### 3. Edge Functions

For better performance, consider edge functions:

```json
{
  "functions": {
    "api/index.py": {
      "maxDuration": 30,
      "runtime": "python3.9"
    }
  }
}
```

## Maintenance

### 1. Regular Updates

- Update dependencies in `requirements.txt`
- Review Vercel platform updates
- Monitor security advisories
- Update dashboard features

### 2. Performance Monitoring

- Check Vercel analytics
- Monitor function performance
- Review error logs
- Optimize slow endpoints

### 3. Backup and Recovery

- Version control with Git
- Environment variable backup
- Configuration backup
- Deployment rollback capability

## Next Steps

### 1. Production Deployment

1. **Deploy to Vercel** using this guide
2. **Test all functionality** in production
3. **Monitor performance** and errors
4. **Set up custom domain** (optional)

### 2. Feature Enhancements

1. **Add real broker integration** (requires external services)
2. **Implement user authentication**
3. **Add persistent storage** (database integration)
4. **Enhance real-time features** (WebSocket alternative)

### 3. Scaling Considerations

1. **Monitor usage metrics**
2. **Optimize function performance**
3. **Consider edge functions**
4. **Implement caching strategies**

## Support

### Vercel Documentation
- [Vercel Docs](https://vercel.com/docs)
- [Python Functions](https://vercel.com/docs/concepts/functions/serverless-functions)
- [Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)

### Common Issues
- Check [Vercel Status](https://www.vercel-status.com/)
- Review [GitHub Issues](https://github.com/vercel/vercel/issues)
- Contact Vercel Support

---

## Conclusion

The QuantMuse Interactive Dashboard is now ready for deployment on Vercel! This serverless deployment provides:

- ✅ **Full dashboard functionality** with mock data
- ✅ **Real-time updates** via polling
- ✅ **Complete trading controls** and testing tools
- ✅ **Risk management** and strategy controls
- ✅ **Professional deployment** with automatic scaling

The dashboard demonstrates all the features of the QuantMuse system in a production-ready environment, perfect for demonstrations, testing, and development purposes.

**Ready to deploy! 🚀**
