# QuantMuse Interactive Control Dashboard Deployment Guide

## Overview

The QuantMuse Interactive Control Dashboard provides comprehensive control and testing capabilities for the multi-broker trading system. This guide covers deployment, configuration, and usage of the complete interactive dashboard system.

## System Architecture

### Components

1. **Interactive Dashboard HTML** (`interactive_control_dashboard.html`)
   - Modern web-based interface with real-time updates
   - 7 main control tabs with full system control
   - WebSocket integration for live data streaming
   - Responsive design with dark/light themes

2. **Enhanced Trading API** (`enhanced_trading_api.py`)
   - Flask-based REST API with SocketIO support
   - Comprehensive endpoints for all dashboard functions
   - Real-time event broadcasting via WebSocket
   - Integration with all system components

3. **WebSocket Server** (`websocket_server.py`)
   - Real-time data streaming server
   - Live price updates, position changes, system status
   - Client subscription management
   - Mock data generation for testing

4. **Testing Framework** (`testing/test_interactive_dashboard.py`)
   - Comprehensive test suite for dashboard functionality
   - API endpoint testing
   - WebSocket functionality testing
   - Performance and load testing

## Prerequisites

### System Requirements

- **Python 3.8+**
- **Node.js 16+** (for WebSocket dependencies)
- **4GB RAM minimum**
- **2GB disk space**
- **Network connection** for broker APIs

### Python Dependencies

```bash
pip install flask flask-cors flask-socketio
pip install websockets
pip install pandas numpy
pip install requests
pip install asyncio
pip install python-socketio
```

### Broker Requirements

- **Deriv Account**: API token (demo or live)
- **MetaTrader 5**: Terminal installation with login credentials
- **Network access**: For broker API connections

## Installation Guide

### 1. Clone/Download the Project

```bash
# Navigate to your project directory
cd c:\Users\Dataentry\Project_X\QuantMuse

# Verify all files are present
ls -la
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Or install individually
pip install flask flask-cors flask-socketio websockets pandas numpy requests asyncio python-socketio
```

### 3. Verify File Structure

Ensure you have the following key files:

```
QuantMuse/
├── interactive_control_dashboard.html
├── enhanced_trading_api.py
├── websocket_server.py
├── testing/
│   └── test_interactive_dashboard.py
├── brokers/
│   ├── deriv_broker.py
│   ├── mt5_broker.py
│   ├── multi_broker_router.py
│   ├── unified_risk_manager.py
│   ├── paper_to_live_transition.py
│   └── asset_mapper.py
└── production_strategies.py
```

## Configuration

### 1. Broker Configuration

#### Deriv Configuration

```python
# In enhanced_trading_api.py or via dashboard
deriv_config = {
    'api_token': 'your_deriv_api_token',
    'app_id': '3089',  # Demo app ID
    'demo_mode': True  # Set to False for live trading
}
```

#### MetaTrader 5 Configuration

```python
# In enhanced_trading_api.py or via dashboard
mt5_config = {
    'login': 12345678,
    'password': 'your_mt5_password',
    'server': 'Demo_Server',  # or your live server
    'terminal_path': 'C:/Program Files/MetaTrader 5/terminal64.exe'
}
```

### 2. API Configuration

```python
# enhanced_trading_api.py configuration
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False  # Set to False for production
}

# websocket_server.py configuration
WS_CONFIG = {
    'host': 'localhost',
    'port': 8765
}
```

### 3. Risk Management Configuration

```python
# Default risk limits (adjustable via dashboard)
RISK_LIMITS = {
    'max_total_exposure': 200000,
    'max_per_broker': 100000,
    'max_per_asset': 20000,
    'max_correlated_exposure': 50000
}
```

## Deployment Steps

### 1. Start WebSocket Server

```bash
# Terminal 1: Start WebSocket server
python websocket_server.py
```

The WebSocket server will start on `ws://localhost:8765` and provide real-time data updates.

### 2. Start Enhanced Trading API

```bash
# Terminal 2: Start trading API
python enhanced_trading_api.py
```

The API server will start on `http://localhost:5000` with SocketIO support.

### 3. Open Interactive Dashboard

```bash
# Open the dashboard in your browser
# Navigate to: http://localhost:5000
# Or open the HTML file directly:
# double-click interactive_control_dashboard.html
```

### 4. Verify System Status

Check the dashboard header for system status indicators:
- **System Status**: Overall system health
- **API Status**: API connection status
- **WebSocket Status**: Real-time connection status

## Usage Guide

### 1. Real-Time Monitoring Tab

**Features:**
- Live portfolio tracking with P&L
- Broker status monitoring
- Real-time price charts
- Order book visualization
- Active positions management

**Controls:**
- Connect/disconnect all brokers
- Refresh broker status
- Close individual positions

### 2. Manual Trading Tab

**Features:**
- Quick order entry
- Advanced order types
- Order management
- Risk calculation

**Controls:**
- Select broker (Deriv, MT5, or Auto-Route)
- Choose asset and order type
- Set volume and price
- Add stop loss/take profit

### 3. Strategy Management Tab

**Features:**
- Strategy selection and control
- Performance comparison
- A/B testing results
- Parameter adjustment

**Controls:**
- Start/stop/pause strategies
- Adjust risk levels
- Set position sizing
- Configure rebalance frequency

### 4. Broker Management Tab

**Features:**
- Broker connection management
- Asset mapping configuration
- Performance metrics
- Connection testing

**Controls:**
- Enter broker credentials
- Test connections
- Manage asset mappings
- View broker statistics

### 5. Risk Management Tab

**Features:**
- Real-time risk exposure
- Adjustable risk limits
- Risk alerts
- Emergency controls

**Controls:**
- Update risk limits
- Run risk analysis
- Enable alerts
- Emergency stop all

### 6. Testing Tools Tab

**Features:**
- Scenario testing
- Load testing
- Test suite execution
- Performance metrics

**Controls:**
- Select test scenarios
- Configure load tests
- Run test suites
- Generate reports

### 7. Transition Control Tab

**Features:**
- Paper-to-live transition management
- Phase configuration
- Progress visualization
- Analytics dashboard

**Controls:**
- Start/advance transitions
- Configure phases
- Monitor progress
- Emergency revert

## Testing

### 1. Run Comprehensive Tests

```bash
# Run the interactive dashboard test suite
python testing/test_interactive_dashboard.py
```

### 2. Test Individual Components

```bash
# Test API endpoints
curl -X GET http://localhost:5000/api/system/status

# Test WebSocket connection
python -c "import websockets; asyncio.run(websockets.connect('ws://localhost:8765'))"

# Test dashboard functionality
# Open browser and navigate through all tabs
```

### 3. Performance Testing

The dashboard includes built-in performance testing:
- Load testing with configurable orders/second
- API response time monitoring
- Concurrent connection testing
- WebSocket performance metrics

## Security Considerations

### 1. API Security

- Use HTTPS in production (`https://your-domain.com`)
- Implement API key authentication
- Rate limiting for API endpoints
- Input validation and sanitization

### 2. WebSocket Security

- Use WSS (WebSocket Secure) in production
- Implement client authentication
- Validate subscription requests
- Monitor for unusual activity

### 3. Broker Credentials

- Store credentials securely (environment variables)
- Use read-only API keys where possible
- Rotate credentials regularly
- Monitor for unauthorized access

## Monitoring and Maintenance

### 1. System Monitoring

Monitor these key metrics:
- API response times
- WebSocket connection health
- Broker connection status
- System resource usage

### 2. Log Management

Key log files:
- `enhanced_trading_api.log`
- `websocket_server.log`
- `interactive_dashboard_test_results.json`

### 3. Performance Optimization

- Regular performance testing
- Database optimization (if using persistent storage)
- Cache frequently accessed data
- Monitor memory usage

## Troubleshooting

### Common Issues

#### 1. WebSocket Connection Failed

**Problem**: Dashboard shows "WS: Disconnected"

**Solutions**:
- Ensure WebSocket server is running on port 8765
- Check firewall settings
- Verify browser WebSocket support
- Restart WebSocket server

#### 2. API Connection Failed

**Problem**: Dashboard shows "API: Disconnected"

**Solutions**:
- Ensure API server is running on port 5000
- Check for port conflicts
- Verify Flask server startup
- Check API logs for errors

#### 3. Broker Connection Failed

**Problem**: Cannot connect to Deriv or MT5

**Solutions**:
- Verify broker credentials
- Check network connectivity
- Ensure broker servers are accessible
- Test with demo accounts first

#### 4. Real-Time Updates Not Working

**Problem**: Charts and data not updating

**Solutions**:
- Check WebSocket connection
- Verify data generation in WebSocket server
- Check browser console for JavaScript errors
- Refresh dashboard

#### 5. Order Placement Failed

**Problem**: Orders not executing

**Solutions**:
- Check broker connection status
- Verify risk limits
- Check order parameters
- Review API error messages

### Debug Mode

Enable debug mode for detailed logging:

```python
# In enhanced_trading_api.py
app.run(debug=True)

# In websocket_server.py
logging.basicConfig(level=logging.DEBUG)
```

## Production Deployment

### 1. Production Server Setup

```bash
# Use production WSGI server
pip install gunicorn

# Start API server
gunicorn -w 4 -b 0.0.0.0:5000 enhanced_trading_api:app

# Use reverse proxy (nginx) for SSL termination
```

### 2. SSL Configuration

```nginx
# Nginx configuration example
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /socket.io/ {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. Environment Variables

```bash
# Set environment variables
export QUANTMUSE_ENV=production
export DERIV_API_TOKEN=your_token
export MT5_LOGIN=your_login
export MT5_PASSWORD=your_password
export MT5_SERVER=your_server
```

## Advanced Features

### 1. Custom Strategies

Add custom strategies to the dashboard:

```python
# In production_strategies.py
class CustomStrategy(ProductionStrategy):
    def generate_signals(self, data):
        # Your custom logic
        pass

# Register in API
trading_system.strategy_manager.add_strategy('custom', CustomStrategy())
```

### 2. Additional Brokers

Add new broker integrations:

```python
# Create new broker class
class NewBroker:
    def __init__(self, config):
        # Initialize broker
        pass
    
    def place_order(self, order):
        # Place order logic
        pass

# Add to system
trading_system.brokers['new_broker'] = NewBroker(config)
```

### 3. Custom Risk Rules

Add custom risk management rules:

```python
# In unified_risk_manager.py
def custom_risk_check(order_request, broker_name):
    # Your custom risk logic
    return {'passed': True, 'warnings': [], 'errors': []}

# Add to risk manager
risk_manager.custom_checks.append(custom_risk_check)
```

## Support and Maintenance

### 1. Regular Updates

- Update broker API connections
- Review and update risk limits
- Monitor performance metrics
- Update dependencies

### 2. Backups

- Backup configuration files
- Export trading history
- Backup system logs
- Document custom configurations

### 3. Scaling

- Horizontal scaling with load balancers
- Database clustering for persistence
- CDN for static assets
- Multiple WebSocket servers

## Conclusion

The QuantMuse Interactive Control Dashboard provides a comprehensive solution for managing and testing your multi-broker trading system. With real-time monitoring, manual trading controls, strategy management, and advanced testing tools, you have complete control over your trading operations.

For support and updates, refer to the system logs and test results. The dashboard is designed to be extensible and can be customized to meet your specific trading requirements.

---

**Next Steps:**
1. Deploy the system using this guide
2. Configure your broker credentials
3. Test all functionality with the test suite
4. Start with paper trading before going live
5. Monitor system performance and optimize as needed

**Happy Trading!** 🚀
