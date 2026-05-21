#!/usr/bin/env python3
"""
Enhanced Trading API for QuantMuse Interactive Dashboard
Provides comprehensive control endpoints for manual trading, strategy management,
broker management, risk controls, and testing tools
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import asyncio
import threading
from typing import Dict, List, Any, Optional
import uuid

# Import existing components
from production_strategies import StrategyManager, ProductionMomentumStrategy, AdaptiveHybridStrategy
from brokers.multi_broker_router import MultiBrokerOrderRouter, RoutingStrategy, OrderRequest
from brokers.unified_risk_manager import UnifiedRiskManager, create_risk_config
from brokers.paper_to_live_transition import PaperToLiveTransition, create_transition_config
from brokers.deriv_broker import DerivBroker
from brokers.mt5_broker import MT5Broker
from brokers.asset_mapper import AssetMapper

# Initialize Flask app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_trading_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedTradingSystem:
    """Enhanced trading system with full dashboard control"""
    
    def __init__(self):
        self.portfolio_manager = PortfolioManager()
        self.strategy_manager = StrategyManager()
        self.order_router = MultiBrokerOrderRouter()
        self.risk_manager = UnifiedRiskManager(create_risk_config())
        self.transition_system = PaperToLiveTransition(create_transition_config())
        self.asset_mapper = AssetMapper()
        
        # Broker instances
        self.brokers = {}
        
        # System state
        self.system_status = {
            'running': False,
            'mode': 'paper',  # paper, live, hybrid
            'active_strategies': [],
            'connected_brokers': [],
            'risk_alerts': [],
            'last_update': datetime.now().isoformat()
        }
        
        # Initialize brokers
        self._initialize_brokers()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_brokers(self):
        """Initialize broker instances"""
        try:
            # Initialize Deriv broker (demo mode by default)
            self.brokers['deriv'] = DerivBroker('demo_token', demo_mode=True)
            self.order_router.add_broker('deriv', self.brokers['deriv'])
            self.risk_manager.add_broker('deriv', self.brokers['deriv'])
            
            # Initialize MT5 broker (demo mode by default)
            self.brokers['mt5'] = MT5Broker(12345678, 'demo_password', 'Demo_Server', demo_mode=True)
            self.order_router.add_broker('mt5', self.brokers['mt5'])
            self.risk_manager.add_broker('mt5', self.brokers['mt5'])
            
            logger.info("Brokers initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing brokers: {e}")
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        def monitor_system():
            while True:
                try:
                    self._update_system_status()
                    asyncio.run(self._check_risk_alerts())
                    asyncio.run(self._update_portfolio_metrics())
                    time.sleep(5)  # Update every 5 seconds
                except Exception as e:
                    logger.error(f"Error in system monitoring: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
        
        logger.info("Background monitoring started")
    
    def _update_system_status(self):
        """Update system status"""
        self.system_status['last_update'] = datetime.now().isoformat()
        self.system_status['connected_brokers'] = [
            name for name, broker in self.brokers.items() 
            if hasattr(broker, 'connected') and broker.connected
        ]
    
    async def _check_risk_alerts(self):
        """Check for risk alerts"""
        try:
            # Get current risk assessment
            risk_assessment = await self.risk_manager.get_risk_summary()
            
            # Check for alerts
            if risk_assessment['risk_score'] > 0.8:
                alert = {
                    'type': 'high_risk',
                    'message': f"High risk score: {risk_assessment['risk_score']:.2f}",
                    'severity': 'critical',
                    'timestamp': datetime.now().isoformat()
                }
                self.system_status['risk_alerts'].append(alert)
                
                # Emit via WebSocket
                socketio.emit('risk_alert', alert)
                
        except Exception as e:
            logger.error(f"Error checking risk alerts: {e}")
    
    async def _update_portfolio_metrics(self):
        """Update portfolio metrics"""
        try:
            # Get portfolio state
            portfolio_state = self.portfolio_manager.get_portfolio_state()
            
            # Emit portfolio update
            socketio.emit('portfolio_update', {
                'portfolio': portfolio_state,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error updating portfolio metrics: {e}")

class PortfolioManager:
    """Enhanced portfolio manager for dashboard control"""
    
    def __init__(self):
        self.positions = {}
        self.orders = {}
        self.cash = 100000.0
        self.portfolio_value = self.cash
        self.trades = []
        self.performance_history = []
        self.metrics = {
            'total_return': 0.0,
            'win_rate': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'volatility': 0.0
        }
    
    def get_portfolio_state(self) -> Dict[str, Any]:
        """Get current portfolio state"""
        return {
            'total_value': self.portfolio_value,
            'cash': self.cash,
            'positions_count': len(self.positions),
            'orders_count': len(self.orders),
            'metrics': self.metrics,
            'positions': list(self.positions.values()),
            'orders': list(self.orders.values())
        }
    
    def add_position(self, position_data: Dict[str, Any]) -> str:
        """Add a new position"""
        position_id = str(uuid.uuid4())
        position_data['id'] = position_id
        position_data['timestamp'] = datetime.now().isoformat()
        position_data['pnl'] = 0.0
        
        self.positions[position_id] = position_data
        self._update_portfolio_value()
        
        return position_id
    
    def close_position(self, position_id: str) -> Dict[str, Any]:
        """Close a position"""
        if position_id not in self.positions:
            raise ValueError(f"Position {position_id} not found")
        
        position = self.positions.pop(position_id)
        self.cash += position.get('pnl', 0) + position.get('cost_basis', 0)
        self._update_portfolio_value()
        
        return position
    
    def add_order(self, order_data: Dict[str, Any]) -> str:
        """Add a new order"""
        order_id = str(uuid.uuid4())
        order_data['id'] = order_id
        order_data['timestamp'] = datetime.now().isoformat()
        order_data['status'] = 'pending'
        
        self.orders[order_id] = order_data
        return order_id
    
    def update_order(self, order_id: str, updates: Dict[str, Any]):
        """Update order status"""
        if order_id in self.orders:
            self.orders[order_id].update(updates)
            
            # If order is filled, create position
            if updates.get('status') == 'filled':
                self._create_position_from_order(self.orders[order_id])
    
    def _create_position_from_order(self, order: Dict[str, Any]):
        """Create position from filled order"""
        position_data = {
            'broker': order['broker'],
            'asset': order['asset'],
            'type': order['direction'],
            'volume': order['volume'],
            'entry_price': order['fill_price'],
            'current_price': order['fill_price'],
            'cost_basis': order['volume'] * order['fill_price'],
            'order_id': order['id']
        }
        
        self.add_position(position_data)
    
    def _update_portfolio_value(self):
        """Update portfolio value"""
        total_position_value = sum(
            pos.get('volume', 0) * pos.get('current_price', 0) 
            for pos in self.positions.values()
        )
        
        self.portfolio_value = self.cash + total_position_value
        
        # Update metrics
        if len(self.trades) > 0:
            self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate portfolio metrics"""
        if not self.trades:
            return
        
        # Calculate returns
        returns = [trade.get('pnl', 0) for trade in self.trades]
        total_return = sum(returns) / self.cash
        
        # Calculate win rate
        winning_trades = len([r for r in returns if r > 0])
        win_rate = winning_trades / len(returns) if returns else 0
        
        # Calculate Sharpe ratio (simplified)
        if len(returns) > 1:
            returns_df = pd.Series(returns)
            sharpe_ratio = returns_df.mean() / returns_df.std() if returns_df.std() > 0 else 0
        else:
            sharpe_ratio = 0
        
        self.metrics.update({
            'total_return': total_return,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe_ratio
        })

# Initialize enhanced trading system
trading_system = EnhancedTradingSystem()

# API Routes
@app.route('/')
def index():
    """Serve the interactive dashboard"""
    return render_template('interactive_control_dashboard.html')

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Get system status"""
    return jsonify({
        'status': 'success',
        'data': trading_system.system_status
    })

@app.route('/api/portfolio/state', methods=['GET'])
def get_portfolio_state():
    """Get portfolio state"""
    return jsonify({
        'status': 'success',
        'data': trading_system.portfolio_manager.get_portfolio_state()
    })

@app.route('/api/brokers/status', methods=['GET'])
def get_brokers_status():
    """Get brokers status"""
    brokers_status = {}
    for name, broker in trading_system.brokers.items():
        brokers_status[name] = {
            'connected': getattr(broker, 'connected', False),
            'status': getattr(broker, 'status', 'Unknown'),
            'balance': getattr(broker, 'balance', 0),
            'positions': len(getattr(broker, 'positions', {}))
        }
    
    return jsonify({
        'status': 'success',
        'data': brokers_status
    })

@app.route('/api/orders/place', methods=['POST'])
def place_order():
    """Place a manual order"""
    try:
        order_data = request.json
        
        # Validate order data
        required_fields = ['broker', 'asset', 'type', 'direction', 'volume']
        for field in required_fields:
            if field not in order_data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Check risk limits
        risk_check = asyncio.run(trading_system.risk_manager.check_order_risk(
            order_data, order_data['broker']
        ))
        
        if not risk_check['passed']:
            return jsonify({
                'status': 'error',
                'message': 'Order blocked by risk limits',
                'risk_check': risk_check
            }), 400
        
        # Create order
        order_id = trading_system.portfolio_manager.add_order(order_data)
        
        # Route order through broker
        order_request = OrderRequest(
            symbol=order_data['asset'],
            asset_type='forex',  # Determine based on asset
            order_type=order_data['direction'].upper(),
            volume=order_data['volume']
        )
        
        # Route order
        routed_orders = asyncio.run(trading_system.order_router.route_order(order_request))
        
        # Update order status
        if routed_orders:
            trading_system.portfolio_manager.update_order(order_id, {
                'status': 'filled',
                'fill_price': order_data.get('price', 1.1000),
                'routed_orders': [order.__dict__ for order in routed_orders]
            })
            
            return jsonify({
                'status': 'success',
                'message': 'Order placed successfully',
                'order_id': order_id,
                'routed_orders': len(routed_orders)
            })
        else:
            trading_system.portfolio_manager.update_order(order_id, {
                'status': 'failed',
                'error': 'No suitable broker found'
            })
            
            return jsonify({
                'status': 'error',
                'message': 'Order failed - no suitable broker'
            }), 400
            
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/orders/cancel/<order_id>', methods=['POST'])
def cancel_order(order_id):
    """Cancel an order"""
    try:
        if order_id not in trading_system.portfolio_manager.orders:
            return jsonify({
                'status': 'error',
                'message': 'Order not found'
            }), 404
        
        order = trading_system.portfolio_manager.orders[order_id]
        
        if order['status'] != 'pending':
            return jsonify({
                'status': 'error',
                'message': 'Order cannot be cancelled'
            }), 400
        
        # Update order status
        trading_system.portfolio_manager.update_order(order_id, {
            'status': 'cancelled'
        })
        
        return jsonify({
            'status': 'success',
            'message': 'Order cancelled successfully'
        })
        
    except Exception as e:
        logger.error(f"Error cancelling order: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/positions/close/<position_id>', methods=['POST'])
def close_position(position_id):
    """Close a position"""
    try:
        closed_position = trading_system.portfolio_manager.close_position(position_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Position closed successfully',
            'position': closed_position
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error closing position: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/strategies/start', methods=['POST'])
def start_strategy():
    """Start a trading strategy"""
    try:
        strategy_data = request.json
        strategy_name = strategy_data.get('strategy')
        mode = strategy_data.get('mode', 'paper')
        
        if not strategy_name:
            return jsonify({
                'status': 'error',
                'message': 'Strategy name is required'
            }), 400
        
        # Initialize strategy
        if strategy_name == 'momentum':
            strategy = ProductionMomentumStrategy()
        elif strategy_name == 'hybrid':
            strategy = AdaptiveHybridStrategy()
        else:
            return jsonify({
                'status': 'error',
                'message': f'Unknown strategy: {strategy_name}'
            }), 400
        
        # Start strategy
        trading_system.strategy_manager.add_strategy(strategy_name, strategy)
        trading_system.system_status['active_strategies'].append(strategy_name)
        trading_system.system_status['mode'] = mode
        
        return jsonify({
            'status': 'success',
            'message': f'Strategy {strategy_name} started in {mode} mode'
        })
        
    except Exception as e:
        logger.error(f"Error starting strategy: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/strategies/stop', methods=['POST'])
def stop_strategy():
    """Stop a trading strategy"""
    try:
        strategy_name = request.json.get('strategy')
        
        if strategy_name:
            # Stop specific strategy
            trading_system.strategy_manager.remove_strategy(strategy_name)
            if strategy_name in trading_system.system_status['active_strategies']:
                trading_system.system_status['active_strategies'].remove(strategy_name)
            
            message = f'Strategy {strategy_name} stopped'
        else:
            # Stop all strategies
            trading_system.strategy_manager.clear_strategies()
            trading_system.system_status['active_strategies'] = []
            
            message = 'All strategies stopped'
        
        return jsonify({
            'status': 'success',
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Error stopping strategy: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/strategies/performance', methods=['GET'])
def get_strategy_performance():
    """Get strategy performance metrics"""
    try:
        performance = trading_system.strategy_manager.get_performance_metrics()
        
        return jsonify({
            'status': 'success',
            'data': performance
        })
        
    except Exception as e:
        logger.error(f"Error getting strategy performance: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/brokers/connect', methods=['POST'])
def connect_broker():
    """Connect to a broker"""
    try:
        broker_data = request.json
        broker_name = broker_data.get('broker')
        
        if broker_name not in trading_system.brokers:
            return jsonify({
                'status': 'error',
                'message': f'Unknown broker: {broker_name}'
            }), 400
        
        broker = trading_system.brokers[broker_name]
        
        # Connect to broker
        if broker_name == 'deriv':
            token = broker_data.get('token')
            if not token:
                return jsonify({
                    'status': 'error',
                    'message': 'API token is required for Deriv'
                }), 400
            
            # Update token and connect
            broker.api_token = token
            asyncio.run(broker.connect())
            
        elif broker_name == 'mt5':
            login = broker_data.get('login')
            password = broker_data.get('password')
            server = broker_data.get('server')
            
            if not all([login, password, server]):
                return jsonify({
                    'status': 'error',
                    'message': 'Login, password, and server are required for MT5'
                }), 400
            
            # Update credentials and connect
            broker.login = login
            broker.password = password
            broker.server = server
            asyncio.run(broker.connect())
        
        return jsonify({
            'status': 'success',
            'message': f'{broker_name} connected successfully'
        })
        
    except Exception as e:
        logger.error(f"Error connecting to broker: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/brokers/disconnect/<broker_name>', methods=['POST'])
def disconnect_broker(broker_name):
    """Disconnect from a broker"""
    try:
        if broker_name not in trading_system.brokers:
            return jsonify({
                'status': 'error',
                'message': f'Unknown broker: {broker_name}'
            }), 400
        
        broker = trading_system.brokers[broker_name]
        asyncio.run(broker.disconnect())
        
        return jsonify({
            'status': 'success',
            'message': f'{broker_name} disconnected successfully'
        })
        
    except Exception as e:
        logger.error(f"Error disconnecting from broker: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/risk/limits', methods=['GET'])
def get_risk_limits():
    """Get current risk limits"""
    try:
        risk_limits = trading_system.risk_manager.get_risk_limits()
        
        return jsonify({
            'status': 'success',
            'data': risk_limits
        })
        
    except Exception as e:
        logger.error(f"Error getting risk limits: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/risk/limits', methods=['POST'])
def update_risk_limits():
    """Update risk limits"""
    try:
        limits_data = request.json
        
        # Update risk limits
        for limit_name, limit_value in limits_data.items():
            if hasattr(trading_system.risk_manager, f'{limit_name}_limit'):
                setattr(trading_system.risk_manager, f'{limit_name}_limit', limit_value)
        
        return jsonify({
            'status': 'success',
            'message': 'Risk limits updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating risk limits: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/risk/emergency_stop', methods=['POST'])
def emergency_stop():
    """Emergency stop all trading"""
    try:
        # Stop all strategies
        trading_system.strategy_manager.clear_strategies()
        trading_system.system_status['active_strategies'] = []
        
        # Close all positions
        position_ids = list(trading_system.portfolio_manager.positions.keys())
        for position_id in position_ids:
            trading_system.portfolio_manager.close_position(position_id)
        
        # Cancel all orders
        order_ids = list(trading_system.portfolio_manager.orders.keys())
        for order_id in order_ids:
            if trading_system.portfolio_manager.orders[order_id]['status'] == 'pending':
                trading_system.portfolio_manager.update_order(order_id, {'status': 'cancelled'})
        
        return jsonify({
            'status': 'success',
            'message': 'Emergency stop executed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error executing emergency stop: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/transition/start', methods=['POST'])
def start_transition():
    """Start paper-to-live transition"""
    try:
        result = trading_system.transition_system.start_transition()
        
        return jsonify({
            'status': 'success',
            'message': 'Transition started successfully',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error starting transition: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/transition/status', methods=['GET'])
def get_transition_status():
    """Get transition status"""
    try:
        status = trading_system.transition_system.get_transition_status()
        
        return jsonify({
            'status': 'success',
            'data': status
        })
        
    except Exception as e:
        logger.error(f"Error getting transition status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/transition/advance', methods=['POST'])
def advance_transition_phase():
    """Advance to next transition phase"""
    try:
        result = trading_system.transition_system.advance_phase()
        
        return jsonify({
            'status': 'success',
            'message': 'Transition phase advanced',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error advancing transition: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/testing/run_scenario', methods=['POST'])
def run_scenario_test():
    """Run a scenario test"""
    try:
        scenario_data = request.json
        scenario = scenario_data.get('scenario')
        duration = scenario_data.get('duration', 60)
        
        # Simulate scenario test
        test_results = {
            'scenario': scenario,
            'duration': duration,
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        return jsonify({
            'status': 'success',
            'message': f'Scenario test {scenario} started',
            'data': test_results
        })
        
    except Exception as e:
        logger.error(f"Error running scenario test: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/testing/run_load_test', methods=['POST'])
def run_load_test():
    """Run a load test"""
    try:
        load_test_data = request.json
        orders_per_second = load_test_data.get('orders_per_second', 10)
        duration = load_test_data.get('duration', 300)
        
        # Simulate load test
        test_results = {
            'orders_per_second': orders_per_second,
            'duration': duration,
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        return jsonify({
            'status': 'success',
            'message': f'Load test started: {orders_per_second} orders/sec for {duration}s',
            'data': test_results
        })
        
    except Exception as e:
        logger.error(f"Error running load test: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info("Client connected via WebSocket")
    emit('connected', {'message': 'Connected to QuantMuse Trading System'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info("Client disconnected from WebSocket")

@socketio.on('subscribe')
def handle_subscribe(data):
    """Handle subscription requests"""
    subscription_type = data.get('type')
    logger.info(f"Client subscribed to: {subscription_type}")
    
    # Send initial data for subscription
    if subscription_type == 'portfolio':
        emit('portfolio_update', trading_system.portfolio_manager.get_portfolio_state())
    elif subscription_type == 'system':
        emit('system_status', trading_system.system_status)

@socketio.on('action')
def handle_action(data):
    """Handle action requests"""
    action = data.get('action')
    logger.info(f"Received action: {action}")
    
    try:
        if action == 'place_order':
            # Handle order placement
            order_data = data.get('order_data')
            order_id = trading_system.portfolio_manager.add_order(order_data)
            
            emit('action_response', {
                'action': action,
                'status': 'success',
                'order_id': order_id
            })
            
        elif action == 'emergency_stop':
            # Handle emergency stop
            emergency_stop()
            
            emit('action_response', {
                'action': action,
                'status': 'success',
                'message': 'Emergency stop executed'
            })
            
        else:
            emit('action_response', {
                'action': action,
                'status': 'error',
                'message': f'Unknown action: {action}'
            })
            
    except Exception as e:
        logger.error(f"Error handling action {action}: {e}")
        emit('action_response', {
            'action': action,
            'status': 'error',
            'message': str(e)
        })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    logger.info("Starting Enhanced QuantMuse Trading API")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
