#!/usr/bin/env python3
"""
Vercel Serverless API for QuantMuse Interactive Dashboard
Adapted for serverless deployment on Vercel
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock data for serverless deployment
class MockTradingSystem:
    """Mock trading system for Vercel deployment"""
    
    def __init__(self):
        self.portfolio = {
            'total_value': 25000,
            'cash': 20000,
            'positions_count': 5,
            'pnl': 0,
            'win_rate': 0.65,
            'sharpe_ratio': 1.5
        }
        
        self.brokers = {
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
        
        self.system_status = {
            'running': True,
            'mode': 'paper',
            'active_strategies': ['momentum'],
            'connected_brokers': ['deriv', 'mt5'],
            'risk_alerts': [],
            'last_update': datetime.now().isoformat()
        }
        
        self.positions = [
            {
                'id': 'pos_001',
                'broker': 'deriv',
                'asset': 'EUR/USD',
                'type': 'CALL',
                'volume': 0.1,
                'entry_price': 1.0980,
                'current_price': 1.1000,
                'pnl': 20.00,
                'timestamp': datetime.now().isoformat()
            },
            {
                'id': 'pos_002',
                'broker': 'mt5',
                'asset': 'EUR/USD',
                'type': 'BUY',
                'volume': 0.05,
                'entry_price': 1.0990,
                'current_price': 1.1000,
                'pnl': 5.00,
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        self.strategies = {
            'active': 'hybrid',
            'mode': 'paper',
            'performance': {
                'momentum': 0.03,
                'factor_analysis': 0.05,
                'ai_ml': 0.07,
                'hybrid': 0.06
            }
        }
        
        self.risk = {
            'total_exposure': 5000,
            'risk_score': 0.35,
            'alerts_count': 0,
            'limits': {
                'max_total_exposure': 200000,
                'max_per_broker': 100000,
                'max_per_asset': 20000,
                'max_correlated_exposure': 50000
            }
        }
        
        self.transition = {
            'current_phase': 'small_live_test',
            'score': 72,
            'days_in_phase': 3,
            'paper_return': 0.06,
            'live_return': 0.04
        }
    
    def get_portfolio_state(self) -> Dict[str, Any]:
        """Get portfolio state"""
        return {
            'total_value': self.portfolio['total_value'],
            'cash': self.portfolio['cash'],
            'positions_count': self.portfolio['positions_count'],
            'orders_count': 0,
            'metrics': {
                'total_return': self.portfolio['pnl'] / self.portfolio['cash'],
                'win_rate': self.portfolio['win_rate'],
                'sharpe_ratio': self.portfolio['sharpe_ratio'],
                'max_drawdown': 0.02,
                'volatility': 0.15
            },
            'positions': self.positions,
            'orders': []
        }
    
    def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Place an order"""
        order_id = f"ORD_{int(datetime.now().timestamp())}"
        
        # Simulate order placement
        new_position = {
            'id': f"pos_{order_id.split('_')[1]}",
            'broker': order_data.get('broker', 'deriv'),
            'asset': order_data.get('asset', 'EUR/USD'),
            'type': order_data.get('direction', 'BUY'),
            'volume': order_data.get('volume', 0.01),
            'entry_price': 1.1000,
            'current_price': 1.1000,
            'pnl': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        self.positions.append(new_position)
        self.portfolio['positions_count'] += 1
        
        return {
            'status': 'success',
            'order_id': order_id,
            'position': new_position
        }
    
    def close_position(self, position_id: str) -> Dict[str, Any]:
        """Close a position"""
        for i, position in enumerate(self.positions):
            if position['id'] == position_id:
                closed_position = self.positions.pop(i)
                self.portfolio['positions_count'] -= 1
                return {
                    'status': 'success',
                    'position': closed_position
                }
        
        return {
            'status': 'error',
            'message': 'Position not found'
        }
    
    def start_strategy(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a strategy"""
        strategy_name = strategy_data.get('strategy', 'momentum')
        mode = strategy_data.get('mode', 'paper')
        
        self.strategies['active'] = strategy_name
        self.strategies['mode'] = mode
        self.system_status['active_strategies'] = [strategy_name]
        
        return {
            'status': 'success',
            'message': f'Strategy {strategy_name} started in {mode} mode'
        }
    
    def stop_strategy(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stop a strategy"""
        self.strategies['active'] = None
        self.system_status['active_strategies'] = []
        
        return {
            'status': 'success',
            'message': 'All strategies stopped'
        }
    
    def update_risk_limits(self, limits_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update risk limits"""
        self.risk['limits'].update(limits_data)
        
        return {
            'status': 'success',
            'message': 'Risk limits updated successfully'
        }
    
    def emergency_stop(self) -> Dict[str, Any]:
        """Emergency stop all trading"""
        self.positions = []
        self.portfolio['positions_count'] = 0
        self.strategies['active'] = None
        self.system_status['active_strategies'] = []
        
        return {
            'status': 'success',
            'message': 'Emergency stop executed successfully'
        }
    
    def start_transition(self) -> Dict[str, Any]:
        """Start paper-to-live transition"""
        self.transition['current_phase'] = 'paper_only'
        self.transition['score'] = 0
        self.transition['days_in_phase'] = 0
        
        return {
            'status': 'success',
            'message': 'Transition started successfully',
            'data': self.transition
        }
    
    def advance_transition_phase(self) -> Dict[str, Any]:
        """Advance transition phase"""
        phases = ['paper_only', 'small_live_test', 'mixed_trading', 'majority_live', 'full_live']
        current_index = phases.index(self.transition['current_phase'])
        
        if current_index < len(phases) - 1:
            self.transition['current_phase'] = phases[current_index + 1]
            self.transition['score'] = 0
            self.transition['days_in_phase'] = 0
            
            return {
                'status': 'success',
                'message': f'Advanced to {self.transition["current_phase"]} phase',
                'data': self.transition
            }
        else:
            return {
                'status': 'warning',
                'message': 'Already in final phase'
            }

# Initialize mock trading system
trading_system = MockTradingSystem()

def handler(request):
    """Main Vercel serverless function handler"""
    
    # Parse request
    method = request.method
    path = request.path
    headers = dict(request.headers)
    
    # Handle CORS
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            },
            'body': ''
        }
    
    # Parse JSON body for POST requests
    body = {}
    if method == 'POST' and hasattr(request, 'body'):
        try:
            body = json.loads(request.body) if request.body else {}
        except:
            body = {}
    
    # Route handling
    try:
        # System status
        if path == '/api/system/status':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'status': 'success',
                    'data': trading_system.system_status
                })
            }
        
        # Portfolio state
        elif path == '/api/portfolio/state':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'status': 'success',
                    'data': trading_system.get_portfolio_state()
                })
            }
        
        # Brokers status
        elif path == '/api/brokers/status':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'status': 'success',
                    'data': trading_system.brokers
                })
            }
        
        # Place order
        elif path == '/api/orders/place' and method == 'POST':
            result = trading_system.place_order(body)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps(result)
            }
        
        # Close position
        elif path.startswith('/api/positions/close/') and method == 'POST':
            position_id = path.split('/')[-1]
            result = trading_system.close_position(position_id)
            return {
                'statusCode': 200 if result['status'] == 'success' else 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps(result)
            }
        
        # Start strategy
        elif path == '/api/strategies/start' and method == 'POST':
            result = trading_system.start_strategy(body)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps(result)
            }
        
        # Stop strategy
        elif path == '/api/strategies/stop' and method == 'POST':
            result = trading_system.stop_strategy(body)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps(result)
            }
        
        # Strategy performance
        elif path == '/api/strategies/performance':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'status': 'success',
                    'data': trading_system.strategies
                })
            }
        
        # Risk limits
        elif path == '/api/risk/limits':
            if method == 'GET':
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'body': json.dumps({
                        'status': 'success',
                        'data': trading_system.risk['limits']
                    })
                }
            elif method == 'POST':
                result = trading_system.update_risk_limits(body)
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'body': json.dumps(result)
                }
        
        # Emergency stop
        elif path == '/api/risk/emergency_stop' and method == 'POST':
            result = trading_system.emergency_stop()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps(result)
            }
        
        # Transition status
        elif path == '/api/transition/status':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'status': 'success',
                    'data': trading_system.transition
                })
            }
        
        # Start transition
        elif path == '/api/transition/start' and method == 'POST':
            result = trading_system.start_transition()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps(result)
            }
        
        # Advance transition
        elif path == '/api/transition/advance' and method == 'POST':
            result = trading_system.advance_transition_phase()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps(result)
            }
        
        # Run scenario test
        elif path == '/api/testing/run_scenario' and method == 'POST':
            scenario = body.get('scenario', 'market_crash')
            duration = body.get('duration', 60)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'status': 'success',
                    'message': f'Scenario test {scenario} started',
                    'data': {
                        'scenario': scenario,
                        'duration': duration,
                        'start_time': datetime.now().isoformat(),
                        'status': 'running'
                    }
                })
            }
        
        # Run load test
        elif path == '/api/testing/run_load_test' and method == 'POST':
            orders_per_second = body.get('orders_per_second', 10)
            duration = body.get('duration', 300)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'status': 'success',
                    'message': f'Load test started: {orders_per_second} orders/sec for {duration}s',
                    'data': {
                        'orders_per_second': orders_per_second,
                        'duration': duration,
                        'start_time': datetime.now().isoformat(),
                        'status': 'running'
                    }
                })
            }
        
        # Default response
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'status': 'error',
                    'message': f'Endpoint not found: {path}'
                })
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            })
        }
