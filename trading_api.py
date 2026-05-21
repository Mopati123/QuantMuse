#!/usr/bin/env python3
"""
Production Trading API for QuantMuse
RESTful endpoints for strategy execution and monitoring
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
from production_strategies import StrategyManager, ProductionMomentumStrategy, AdaptiveHybridStrategy

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PortfolioManager:
    """Manages portfolio state and positions"""
    
    def __init__(self):
        self.positions = {}
        self.cash = 100000.0  # Starting cash
        self.portfolio_value = self.cash
        self.trades = []
        self.performance_history = []
        
    def add_position(self, asset: str, quantity: float, price: float, trade_id: str):
        """Add a new position"""
        if asset in self.positions:
            # Update existing position
            current_qty = self.positions[asset]['quantity']
            current_cost = self.positions[asset]['cost_basis']
            new_cost = current_qty * current_cost + quantity * price
            new_qty = current_qty + quantity
            avg_cost = new_cost / new_qty if new_qty != 0 else 0
            
            self.positions[asset] = {
                'quantity': new_qty,
                'cost_basis': avg_cost,
                'last_price': price,
                'trade_ids': self.positions[asset]['trade_ids'] + [trade_id],
                'last_updated': datetime.now()
            }
        else:
            # New position
            self.positions[asset] = {
                'quantity': quantity,
                'cost_basis': price,
                'last_price': price,
                'trade_ids': [trade_id],
                'last_updated': datetime.now()
            }
        
        # Update cash
        self.cash -= quantity * price
        self._update_portfolio_value()
        
    def close_position(self, asset: str, quantity: float, price: float, trade_id: str):
        """Close a position"""
        if asset not in self.positions:
            return False
            
        current_qty = self.positions[asset]['quantity']
        if quantity > current_qty:
            quantity = current_qty  # Can't sell more than we have
        
        # Calculate P&L
        cost_basis = self.positions[asset]['cost_basis']
        realized_pnl = (price - cost_basis) * quantity
        
        # Update position
        new_qty = current_qty - quantity
        if new_qty == 0:
            del self.positions[asset]
        else:
            self.positions[asset]['quantity'] = new_qty
            self.positions[asset]['last_price'] = price
            self.positions[asset]['trade_ids'].append(trade_id)
        
        # Update cash
        self.cash += quantity * price
        self._update_portfolio_value()
        
        # Record trade
        self.trades.append({
            'trade_id': trade_id,
            'asset': asset,
            'action': 'sell',
            'quantity': quantity,
            'price': price,
            'cost_basis': cost_basis,
            'realized_pnl': realized_pnl,
            'timestamp': datetime.now()
        })
        
        return True
    
    def _update_portfolio_value(self):
        """Update total portfolio value"""
        total_value = self.cash
        for asset, position in self.positions.items():
            total_value += position['quantity'] * position['last_price']
        
        self.portfolio_value = total_value
        
        # Record performance
        self.performance_history.append({
            'timestamp': datetime.now(),
            'portfolio_value': total_value,
            'cash': self.cash,
            'positions_count': len(self.positions)
        })
    
    def get_portfolio_summary(self):
        """Get current portfolio summary"""
        return {
            'portfolio_value': self.portfolio_value,
            'cash': self.cash,
            'positions': self.positions,
            'total_positions': len(self.positions),
            'total_trades': len(self.trades),
            'last_updated': datetime.now().isoformat()
        }

class RiskManager:
    """Manages risk limits and monitoring"""
    
    def __init__(self):
        self.risk_limits = {
            'max_portfolio_risk': 0.15,  # 15% max portfolio risk
            'max_position_size': 0.10,   # 10% max per position
            'max_drawdown': 0.10,        # 10% max drawdown
            'stop_loss': 0.05,           # 5% stop loss
            'take_profit': 0.10          # 10% take profit
        }
        self.alerts = []
        self.risk_metrics = {}
        
    def check_trade_risk(self, asset: str, quantity: float, price: float, portfolio_value: float) -> dict:
        """Check if trade meets risk criteria"""
        trade_value = quantity * price
        position_size = trade_value / portfolio_value
        
        checks = {
            'passed': True,
            'warnings': [],
            'errors': []
        }
        
        # Position size check
        if position_size > self.risk_limits['max_position_size']:
            checks['passed'] = False
            checks['errors'].append(f"Position size {position_size:.2%} exceeds limit {self.risk_limits['max_position_size']:.2%}")
        
        # Portfolio risk check
        total_risk = position_size / portfolio_value
        if total_risk > self.risk_limits['max_portfolio_risk']:
            checks['passed'] = False
            checks['errors'].append(f"Portfolio risk {total_risk:.2%} exceeds limit {self.risk_limits['max_portfolio_risk']:.2%}")
        
        # Warning for large positions
        if position_size > self.risk_limits['max_position_size'] * 0.8:
            checks['warnings'].append(f"Large position: {position_size:.2%}")
        
        return checks
    
    def update_risk_metrics(self, portfolio_manager):
        """Update risk metrics based on current portfolio"""
        portfolio_value = portfolio_manager.portfolio_value
        
        # Calculate current risk
        total_position_value = sum(
            pos['quantity'] * pos['last_price'] 
            for pos in portfolio_manager.positions.values()
        )
        
        current_risk = total_position_value / portfolio_value if portfolio_value > 0 else 0
        
        # Calculate drawdown
        if len(portfolio_manager.performance_history) > 1:
            peak_value = max(h['portfolio_value'] for h in portfolio_manager.performance_history)
            current_value = portfolio_manager.portfolio_value
            drawdown = (current_value - peak_value) / peak_value if peak_value > 0 else 0
        else:
            drawdown = 0
        
        self.risk_metrics = {
            'current_risk': current_risk,
            'max_risk_limit': self.risk_limits['max_portfolio_risk'],
            'current_drawdown': drawdown,
            'max_drawdown_limit': self.risk_limits['max_drawdown'],
            'position_count': len(portfolio_manager.positions),
            'last_updated': datetime.now().isoformat()
        }
        
        # Check for alerts
        self._check_alerts()
        
        return self.risk_metrics
    
    def _check_alerts(self):
        """Check for risk alerts"""
        if self.risk_metrics['current_risk'] > self.risk_limits['max_portfolio_risk'] * 0.9:
            self.alerts.append({
                'type': 'risk_limit_warning',
                'message': f"Portfolio risk {self.risk_metrics['current_risk']:.2%} approaching limit",
                'timestamp': datetime.now()
            })
        
        if abs(self.risk_metrics['current_drawdown']) > self.risk_limits['max_drawdown'] * 0.8:
            self.alerts.append({
                'type': 'drawdown_warning',
                'message': f"Drawdown {abs(self.risk_metrics['current_drawdown']):.2%} approaching limit",
                'timestamp': datetime.now()
            })

# Sample data generation for testing
def generate_sample_market_data():
    """Generate sample market data for API testing"""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    market_data = []
    
    for date in dates:
        for asset in assets:
            # Simulate realistic price movements
            base_return = np.random.normal(0.0005, 0.02, 1)
            price = 100 * (1 + np.random.normal(0, 0.015))
            
            market_data.append({
                'date': date,
                'asset': asset,
                'close': price,
                'volume': np.random.randint(100000, 1000000)
            })
    
    return pd.DataFrame(market_data)

# API Endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'components': {
            'strategy_manager': 'active',
            'portfolio_manager': 'active',
            'risk_manager': 'active'
        }
    })

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get available strategies"""
    return jsonify({
        'strategies': list(strategy_manager.strategies.keys()),
        'active_strategy': strategy_manager.active_strategy,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/strategies/<strategy_name>', methods=['GET'])
def get_strategy_details(strategy_name):
    """Get detailed strategy information"""
    if strategy_name not in strategy_manager.strategies:
        return jsonify({'error': 'Strategy not found'}), 404
    
    strategy = strategy_manager.strategies[strategy_name]
    return jsonify({
        'name': strategy.name,
        'description': strategy.description,
        'parameters': getattr(strategy, 'parameters', {}),
        'performance_metrics': getattr(strategy, 'performance_metrics', {}),
        'positions': strategy.positions,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/strategies/execute', methods=['POST'])
def execute_strategy():
    """Execute trading strategy"""
    data = request.get_json()
    
    # Validate request
    if not data or 'strategy' not in data:
        return jsonify({'error': 'Strategy name required'}), 400
    
    strategy_name = data['strategy']
    if strategy_name not in strategy_manager.strategies:
        return jsonify({'error': 'Strategy not found'}), 404
    
    try:
        # Set active strategy
        strategy_manager.set_active_strategy(strategy_name)
        
        # Generate sample market data (in production, this would be real data)
        market_data = generate_sample_market_data()
        
        # Execute strategy
        result = strategy_manager.execute_active_strategy(market_data)
        
        # Process trades
        executed_trades = []
        for trade in result.get('trades', []):
            # Check risk
            risk_check = risk_manager.check_trade_risk(
                trade['asset'], 
                trade['position_size'], 
                trade['price'], 
                portfolio_manager.portfolio_value
            )
            
            if risk_check['passed']:
                # Execute trade
                portfolio_manager.add_position(
                    trade['asset'],
                    trade['position_size'] / trade['price'],  # Convert to shares
                    trade['price'],
                    trade['trade_id']
                )
                executed_trades.append(trade)
            else:
                logger.warning(f"Trade rejected by risk manager: {risk_check['errors']}")
        
        # Update risk metrics
        risk_metrics = risk_manager.update_risk_metrics(portfolio_manager)
        
        return jsonify({
            'success': True,
            'strategy': strategy_name,
            'execution_summary': result['execution_summary'],
            'trades_executed': executed_trades,
            'risk_metrics': risk_metrics,
            'portfolio_summary': portfolio_manager.get_portfolio_summary(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error executing strategy: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/current', methods=['GET'])
def get_current_portfolio():
    """Get current portfolio status"""
    return jsonify(portfolio_manager.get_portfolio_summary())

@app.route('/api/portfolio/performance', methods=['GET'])
def get_portfolio_performance():
    """Get portfolio performance history"""
    return jsonify({
        'performance_history': portfolio_manager.performance_history,
        'total_trades': len(portfolio_manager.trades),
        'current_value': portfolio_manager.portfolio_value,
        'initial_value': 100000.0,  # Starting value
        'total_return': (portfolio_manager.portfolio_value - 100000.0) / 100000.0,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/risk/current', methods=['GET'])
def get_current_risk():
    """Get current risk metrics"""
    risk_metrics = risk_manager.update_risk_metrics(portfolio_manager)
    return jsonify({
        'risk_metrics': risk_metrics,
        'risk_limits': risk_manager.risk_limits,
        'active_alerts': risk_manager.alerts[-5:],  # Last 5 alerts
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/risk/limits', methods=['POST'])
def update_risk_limits():
    """Update risk management limits"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Risk limits data required'}), 400
    
    try:
        # Validate and update risk limits
        for key, value in data.items():
            if key in risk_manager.risk_limits:
                if isinstance(value, (int, float)) and 0 <= value <= 1:
                    risk_manager.risk_limits[key] = value
                else:
                    return jsonify({'error': f'Invalid value for {key}: {value}'}), 400
            else:
                return jsonify({'error': f'Unknown risk limit: {key}'}), 400
        
        return jsonify({
            'success': True,
            'updated_limits': risk_manager.risk_limits,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error updating risk limits: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/active', methods=['GET'])
def get_active_alerts():
    """Get active alerts"""
    return jsonify({
        'alerts': risk_manager.alerts[-10:],  # Last 10 alerts
        'alert_count': len(risk_manager.alerts),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/market/data', methods=['GET'])
def get_market_data():
    """Get current market data (sample for testing)"""
    try:
        # Generate sample data
        market_data = generate_sample_market_data()
        
        # Get latest prices
        latest_data = market_data.groupby('asset').last().reset_index()
        
        return jsonify({
            'market_data': latest_data.to_dict('records'),
            'data_points': len(market_data),
            'assets': latest_data['asset'].tolist(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """Get comprehensive dashboard summary"""
    return jsonify({
        'portfolio': portfolio_manager.get_portfolio_summary(),
        'risk': risk_manager.update_risk_metrics(portfolio_manager),
        'strategies': {
            'available': list(strategy_manager.strategies.keys()),
            'active': strategy_manager.active_strategy,
            'performance': strategy_manager.performance_tracker
        },
        'alerts': risk_manager.alerts[-5:],
        'market': {
            'status': 'active',
            'last_update': datetime.now().isoformat()
        },
        'system': {
            'status': 'healthy',
            'uptime': '24h 15m',  # Mock uptime
            'api_version': '1.0.0'
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Global instances
strategy_manager = StrategyManager()
portfolio_manager = PortfolioManager()
risk_manager = RiskManager()

# Main execution
if __name__ == '__main__':
    print("🚀 Starting QuantMuse Trading API Server")
    print("=" * 50)
    
    # Initialize with momentum strategy
    strategy_manager.set_active_strategy('momentum')
    
    print("📋 Available Endpoints:")
    print("  GET  /api/health - Health check")
    print("  GET  /api/strategies - List strategies")
    print("  POST /api/strategies/execute - Execute strategy")
    print("  GET  /api/portfolio/current - Current portfolio")
    print("  GET  /api/risk/current - Current risk metrics")
    print("  GET  /api/dashboard/summary - Dashboard summary")
    print("\n🌐 Server starting on http://localhost:5000")
    print("📊 API documentation available at http://localhost:5000/api/health")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
