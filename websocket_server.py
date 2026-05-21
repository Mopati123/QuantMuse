#!/usr/bin/env python3
"""
WebSocket Server for QuantMuse Interactive Dashboard
Provides real-time updates for portfolio, positions, prices, and system status
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime, timedelta
import random
from typing import Dict, List, Any, Set
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('websocket_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QuantMuseWebSocketServer:
    """WebSocket server for real-time dashboard updates"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.running = False
        self.update_task = None
        
        # Mock data for demonstration
        self.mock_data = {
            'portfolio': {
                'total_value': 25000,
                'cash': 20000,
                'positions_count': 5,
                'pnl': 0,
                'win_rate': 0.65,
                'sharpe_ratio': 1.5
            },
            'brokers': {
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
            },
            'positions': [
                {
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
                    'broker': 'mt5',
                    'asset': 'EUR/USD',
                    'type': 'BUY',
                    'volume': 0.05,
                    'entry_price': 1.0990,
                    'current_price': 1.1000,
                    'pnl': 5.00,
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'prices': {
                'EUR/USD': 1.1000,
                'GBP/USD': 1.2500,
                'XAUUSD': 1850.00,
                'US30': 35000
            },
            'risk': {
                'total_exposure': 5000,
                'risk_score': 0.35,
                'alerts_count': 0,
                'sector_exposure': {
                    'forex': 3000,
                    'commodities': 1500,
                    'indices': 500
                }
            },
            'strategies': {
                'active': 'hybrid',
                'mode': 'paper',
                'performance': {
                    'momentum': 0.03,
                    'factor_analysis': 0.05,
                    'ai_ml': 0.07,
                    'hybrid': 0.06
                }
            },
            'transition': {
                'current_phase': 'small_live_test',
                'score': 72,
                'days_in_phase': 3,
                'paper_return': 0.06,
                'live_return': 0.04
            }
        }
    
    async def register_client(self, websocket):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        # Send initial data
        await self.send_initial_data(websocket)
    
    async def unregister_client(self, websocket):
        """Unregister a WebSocket client"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def send_initial_data(self, websocket):
        """Send initial data to newly connected client"""
        try:
            initial_data = {
                'type': 'initial_data',
                'data': self.mock_data,
                'timestamp': datetime.now().isoformat()
            }
            await websocket.send(json.dumps(initial_data))
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return
        
        message_str = json.dumps(message)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.clients.discard(client)
    
    async def update_portfolio_data(self):
        """Update and broadcast portfolio data"""
        # Simulate portfolio changes
        base_value = 25000
        variation = random.uniform(-500, 500)
        self.mock_data['portfolio']['total_value'] = base_value + variation
        self.mock_data['portfolio']['pnl'] = variation
        self.mock_data['portfolio']['cash'] = self.mock_data['portfolio']['total_value'] * 0.8
        
        message = {
            'type': 'portfolio_update',
            'data': self.mock_data['portfolio'],
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast_message(message)
    
    async def update_price_data(self):
        """Update and broadcast price data"""
        # Simulate price movements
        for symbol in self.mock_data['prices']:
            base_price = self.mock_data['prices'][symbol]
            change = random.uniform(-0.001, 0.001)
            self.mock_data['prices'][symbol] = base_price * (1 + change)
            
            message = {
                'type': 'price_update',
                'data': {
                    'symbol': symbol,
                    'price': self.mock_data['prices'][symbol],
                    'change': change,
                    'timestamp': datetime.now().isoformat()
                },
                'timestamp': datetime.now().isoformat()
            }
            
            await self.broadcast_message(message)
    
    async def update_positions(self):
        """Update and broadcast position data"""
        # Simulate position changes
        for position in self.mock_data['positions']:
            # Update current price
            if position['asset'] in self.mock_data['prices']:
                position['current_price'] = self.mock_data['prices'][position['asset']]
                
                # Calculate P&L
                if position['type'] in ['BUY', 'CALL']:
                    position['pnl'] = (position['current_price'] - position['entry_price']) * position['volume'] * 1000
                else:
                    position['pnl'] = (position['entry_price'] - position['current_price']) * position['volume'] * 1000
                
                position['timestamp'] = datetime.now().isoformat()
        
        message = {
            'type': 'position_update',
            'data': self.mock_data['positions'],
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast_message(message)
    
    async def update_broker_status(self):
        """Update and broadcast broker status"""
        # Simulate broker status changes
        for broker_name, broker_data in self.mock_data['brokers'].items():
            # Randomly simulate connection issues
            if random.random() < 0.05:  # 5% chance of disconnection
                broker_data['connected'] = False
                broker_data['status'] = 'Disconnected'
            elif not broker_data['connected'] and random.random() < 0.5:  # 50% chance of reconnection
                broker_data['connected'] = True
                broker_data['status'] = 'Connected'
            
            # Update performance
            if broker_data['connected']:
                broker_data['performance'] += random.uniform(-0.001, 0.002)
                broker_data['balance'] += random.uniform(-100, 100)
        
        message = {
            'type': 'broker_update',
            'data': self.mock_data['brokers'],
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast_message(message)
    
    async def update_risk_data(self):
        """Update and broadcast risk data"""
        # Simulate risk changes
        max_exposure = 200000
        self.mock_data['risk']['total_exposure'] = random.uniform(0, max_exposure * 0.8)
        self.mock_data['risk']['risk_score'] = self.mock_data['risk']['total_exposure'] / max_exposure
        
        # Randomly generate alerts
        if random.random() < 0.1:  # 10% chance of new alert
            self.mock_data['risk']['alerts_count'] += 1
            alert_message = {
                'type': 'risk_alert',
                'data': {
                    'message': 'High exposure warning',
                    'severity': 'warning',
                    'exposure': self.mock_data['risk']['total_exposure'],
                    'timestamp': datetime.now().isoformat()
                },
                'timestamp': datetime.now().isoformat()
            }
            await self.broadcast_message(alert_message)
        
        message = {
            'type': 'risk_update',
            'data': self.mock_data['risk'],
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast_message(message)
    
    async def update_strategy_data(self):
        """Update and broadcast strategy data"""
        # Simulate strategy performance changes
        for strategy in self.mock_data['strategies']['performance']:
            self.mock_data['strategies']['performance'][strategy] += random.uniform(-0.001, 0.002)
        
        message = {
            'type': 'strategy_update',
            'data': self.mock_data['strategies'],
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast_message(message)
    
    async def update_transition_data(self):
        """Update and broadcast transition data"""
        # Simulate transition progress
        if self.mock_data['transition']['current_phase'] != 'full_live':
            self.mock_data['transition']['score'] = min(100, self.mock_data['transition']['score'] + random.uniform(0, 2))
            self.mock_data['transition']['days_in_phase'] += random.uniform(0, 0.1)
            
            # Check for phase advancement
            if self.mock_data['transition']['score'] >= 100:
                phases = ['paper_only', 'small_live_test', 'mixed_trading', 'majority_live', 'full_live']
                current_index = phases.index(self.mock_data['transition']['current_phase'])
                if current_index < len(phases) - 1:
                    self.mock_data['transition']['current_phase'] = phases[current_index + 1]
                    self.mock_data['transition']['score'] = 0
                    self.mock_data['transition']['days_in_phase'] = 0
        
        message = {
            'type': 'transition_update',
            'data': self.mock_data['transition'],
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast_message(message)
    
    async def periodic_updates(self):
        """Run periodic updates for all data types"""
        while self.running:
            try:
                # Update different data types at different intervals
                await asyncio.gather(
                    self.update_price_data(),
                    self.update_positions(),
                    self.update_portfolio_data()
                )
                
                # Update less frequently
                if random.random() < 0.3:  # 30% chance
                    await asyncio.gather(
                        self.update_broker_status(),
                        self.update_risk_data(),
                        self.update_strategy_data(),
                        self.update_transition_data()
                    )
                
                await asyncio.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in periodic updates: {e}")
                await asyncio.sleep(5)
    
    async def handle_client_message(self, websocket, message: str):
        """Handle messages from clients"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # Handle subscription requests
                await self.handle_subscription(websocket, data)
            elif message_type == 'action':
                # Handle action requests
                await self.handle_action(websocket, data)
            elif message_type == 'get_data':
                # Handle data requests
                await self.handle_data_request(websocket, data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
    
    async def handle_subscription(self, websocket, data: Dict[str, Any]):
        """Handle subscription requests"""
        subscription_type = data.get('subscription_type')
        logger.info(f"Client subscribed to: {subscription_type}")
        
        # Send current data for the subscription
        if subscription_type == 'portfolio':
            await websocket.send(json.dumps({
                'type': 'portfolio_update',
                'data': self.mock_data['portfolio'],
                'timestamp': datetime.now().isoformat()
            }))
        elif subscription_type == 'prices':
            await websocket.send(json.dumps({
                'type': 'price_update',
                'data': self.mock_data['prices'],
                'timestamp': datetime.now().isoformat()
            }))
    
    async def handle_action(self, websocket, data: Dict[str, Any]):
        """Handle action requests from clients"""
        action = data.get('action')
        logger.info(f"Received action: {action}")
        
        if action == 'place_order':
            # Simulate order placement
            order_data = data.get('order_data', {})
            
            # Add to positions
            new_position = {
                'broker': order_data.get('broker', 'deriv'),
                'asset': order_data.get('asset', 'EUR/USD'),
                'type': order_data.get('type', 'BUY'),
                'volume': order_data.get('volume', 0.01),
                'entry_price': self.mock_data['prices'].get(order_data.get('asset', 'EUR/USD'), 1.1000),
                'current_price': self.mock_data['prices'].get(order_data.get('asset', 'EUR/USD'), 1.1000),
                'pnl': 0.0,
                'timestamp': datetime.now().isoformat()
            }
            
            self.mock_data['positions'].append(new_position)
            self.mock_data['portfolio']['positions_count'] += 1
            
            # Broadcast position update
            await self.update_positions()
            
            # Send confirmation
            await websocket.send(json.dumps({
                'type': 'order_confirmation',
                'data': {
                    'success': True,
                    'order_id': f'ORD_{int(time.time())}',
                    'position': new_position
                },
                'timestamp': datetime.now().isoformat()
            }))
            
        elif action == 'close_position':
            # Simulate position closing
            position_id = data.get('position_id')
            
            if position_id < len(self.mock_data['positions']):
                closed_position = self.mock_data['positions'].pop(position_id)
                self.mock_data['portfolio']['positions_count'] -= 1
                
                # Broadcast position update
                await self.update_positions()
                
                # Send confirmation
                await websocket.send(json.dumps({
                    'type': 'position_closed',
                    'data': {
                        'success': True,
                        'position': closed_position
                    },
                    'timestamp': datetime.now().isoformat()
                }))
        
        elif action == 'emergency_stop':
            # Simulate emergency stop
            logger.warning("Emergency stop triggered!")
            
            # Close all positions
            self.mock_data['positions'] = []
            self.mock_data['portfolio']['positions_count'] = 0
            
            # Stop strategies
            self.mock_data['strategies']['active'] = None
            
            # Broadcast emergency stop
            await self.broadcast_message({
                'type': 'emergency_stop',
                'data': {
                    'message': 'Emergency stop executed',
                    'timestamp': datetime.now().isoformat()
                },
                'timestamp': datetime.now().isoformat()
            })
    
    async def handle_data_request(self, websocket, data: Dict[str, Any]):
        """Handle data requests from clients"""
        data_type = data.get('data_type')
        
        if data_type == 'full_state':
            await websocket.send(json.dumps({
                'type': 'full_state',
                'data': self.mock_data,
                'timestamp': datetime.now().isoformat()
            }))
        elif data_type in self.mock_data:
            await websocket.send(json.dumps({
                'type': f'{data_type}_data',
                'data': self.mock_data[data_type],
                'timestamp': datetime.now().isoformat()
            }))
    
    async def handle_client(self, websocket, path):
        """Handle a WebSocket client connection"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start the WebSocket server"""
        self.running = True
        
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        # Start periodic updates
        self.update_task = asyncio.create_task(self.periodic_updates())
        
        # Start WebSocket server
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever
    
    async def stop_server(self):
        """Stop the WebSocket server"""
        self.running = False
        
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        
        logger.info("WebSocket server stopped")

def run_server():
    """Run the WebSocket server"""
    server = QuantMuseWebSocketServer()
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        asyncio.run(server.stop_server())

if __name__ == "__main__":
    run_server()
