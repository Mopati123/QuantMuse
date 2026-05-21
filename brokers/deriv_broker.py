#!/usr/bin/env python3
"""
Deriv Broker Integration for QuantMuse
Supports all asset types: binary options, forex, commodities
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

class DerivBroker:
    """Deriv API integration for trading"""
    
    def __init__(self, api_token: str, app_id: str = None, demo_mode: bool = True):
        self.api_token = api_token
        self.app_id = app_id or "3089"  # Deriv demo app ID
        self.demo_mode = demo_mode
        self.websocket = None
        self.connected = False
        self.account_info = {}
        self.positions = {}
        self.logger = logging.getLogger(__name__)
        
        # WebSocket endpoints
        self.ws_url = "wss://ws.binaryws.com/websockets/v3"
        
        # Asset mappings for Deriv
        self.asset_mappings = {
            'forex': {
                'EUR/USD': 'frxEURUSD',
                'GBP/USD': 'frxGBPUSD', 
                'USD/JPY': 'frxUSDJPY',
                'AUD/USD': 'frxAUDUSD',
                'USD/CHF': 'frxUSDCHF',
                'EUR/GBP': 'frxEURGBP',
                'EUR/JPY': 'frxEURJPY',
                'GBP/JPY': 'frxGBPJPY'
            },
            'commodities': {
                'Gold': 'frxXAUUSD',
                'Silver': 'frxXAGUSD',
                'Oil': 'frxUSOIL',
                'Natural Gas': 'frxNGAS'
            },
            'indices': {
                'US 30': 'frxUS30',
                'US 500': 'frxUS500',
                'US Tech 100': 'frxUSTECH',
                'Germany 40': 'frxDEU30',
                'UK 100': 'frxUK100'
            },
            'binary_options': {
                'Rise/Fall': 'rise_fall',
                'Higher/Lower': 'higher_lower',
                'Touch/No Touch': 'touch_no_touch',
                'In/Out': 'in_out'
            }
        }
        
        # Request counter for message IDs
        self.request_counter = 0
        
    async def connect(self) -> bool:
        """Establish WebSocket connection to Deriv"""
        try:
            self.logger.info(f"Connecting to Deriv (demo_mode={self.demo_mode})...")
            
            self.websocket = await websockets.connect(self.ws_url)
            self.connected = True
            
            # Authorize connection
            await self.authorize()
            
            # Get account info
            await self.get_account_info()
            
            self.logger.info("Successfully connected to Deriv")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Deriv: {e}")
            self.connected = False
            return False
    
    async def authorize(self) -> bool:
        """Authorize with Deriv API"""
        try:
            auth_request = {
                "authorize": self.api_token
            }
            
            response = await self.send_request(auth_request)
            
            if response.get('error'):
                self.logger.error(f"Authorization failed: {response['error']}")
                return False
            
            self.logger.info("Successfully authorized with Deriv")
            return True
            
        except Exception as e:
            self.logger.error(f"Authorization error: {e}")
            return False
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account balance and information"""
        try:
            request = {"balance": 1}
            response = await self.send_request(request)
            
            if response.get('error'):
                self.logger.error(f"Failed to get account info: {response['error']}")
                return {}
            
            self.account_info = {
                'balance': response.get('balance', {}).get('balance', 0),
                'currency': response.get('balance', {}).get('currency', 'USD'),
                'demo_account': self.demo_mode,
                'loginid': response.get('balance', {}).get('loginid', ''),
                'account_type': 'demo' if self.demo_mode else 'real'
            }
            
            return self.account_info
            
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}")
            return {}
    
    async def get_asset_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for an asset"""
        try:
            request = {"ticks": symbol}
            response = await self.send_request(request)
            
            if response.get('error'):
                self.logger.error(f"Failed to get price for {symbol}: {response['error']}")
                return {}
            
            tick_data = response.get('tick', {})
            return {
                'symbol': symbol,
                'price': tick_data.get('quote', 0),
                'timestamp': tick_data.get('epoch', 0),
                'pip_size': tick_data.get('pip_size', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            return {}
    
    async def place_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """Place order on Deriv"""
        try:
            # Map order parameters to Deriv format
            deriv_order = self._map_order_to_deriv(order_params)
            
            response = await self.send_request(deriv_order)
            
            if response.get('error'):
                self.logger.error(f"Order failed: {response['error']}")
                return {
                    'success': False,
                    'error': response['error'],
                    'order_id': None
                }
            
            # Return success response
            return {
                'success': True,
                'order_id': response.get('buy', {}).get('contract_id'),
                'contract_info': response.get('buy', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return {
                'success': False,
                'error': str(e),
                'order_id': None
            }
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get open positions"""
        try:
            request = {"portfolio": 1}
            response = await self.send_request(request)
            
            if response.get('error'):
                self.logger.error(f"Failed to get positions: {response['error']}")
                return []
            
            positions = response.get('portfolio', {}).get('contracts', [])
            
            # Format positions
            formatted_positions = []
            for pos in positions:
                if pos.get('status') == 'open':
                    formatted_positions.append({
                        'contract_id': pos.get('contract_id'),
                        'symbol': pos.get('underlying_symbol'),
                        'type': pos.get('contract_type'),
                        'entry_price': pos.get('entry_tick'),
                        'current_price': pos.get('current_spot'),
                        'payout': pos.get('payout'),
                        'profit': pos.get('profit'),
                        'purchase_time': pos.get('purchase_time'),
                        'expiry_time': pos.get('expiry_time'),
                        'status': pos.get('status')
                    })
            
            self.positions = {pos['contract_id']: pos for pos in formatted_positions}
            return formatted_positions
            
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []
    
    async def close_position(self, contract_id: str) -> Dict[str, Any]:
        """Close a position"""
        try:
            request = {"sell": contract_id, "price": 100}
            response = await self.send_request(request)
            
            if response.get('error'):
                self.logger.error(f"Failed to close position {contract_id}: {response['error']}")
                return {
                    'success': False,
                    'error': response['error']
                }
            
            return {
                'success': True,
                'sell_info': response.get('sell', {}),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error closing position {contract_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_transaction_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get transaction history"""
        try:
            request = {"transaction_history": 1, "limit": limit}
            response = await self.send_request(request)
            
            if response.get('error'):
                self.logger.error(f"Failed to get transaction history: {response['error']}")
                return []
            
            transactions = response.get('transaction_history', {}).get('transactions', [])
            
            # Format transactions
            formatted_transactions = []
            for tx in transactions:
                formatted_transactions.append({
                    'transaction_id': tx.get('transaction_id'),
                    'type': tx.get('action_type'),
                    'amount': tx.get('amount'),
                    'balance': tx.get('balance_after'),
                    'timestamp': tx.get('transaction_time'),
                    'description': tx.get('longcode', '')
                })
            
            return formatted_transactions
            
        except Exception as e:
            self.logger.error(f"Error getting transaction history: {e}")
            return []
    
    def _map_order_to_deriv(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """Map order parameters to Deriv API format"""
        
        # Basic order parameters
        symbol = order_params.get('symbol', 'EUR/USD')
        order_type = order_params.get('type', 'CALL')  # CALL or PUT
        amount = order_params.get('amount', 10)
        duration = order_params.get('duration', 60)  # in seconds
        duration_unit = order_params.get('duration_unit', 's')
        
        # Map symbol to Deriv format
        deriv_symbol = self.asset_mappings.get('forex', {}).get(symbol, symbol)
        if deriv_symbol == symbol:
            # Try other asset types
            for asset_type, mappings in self.asset_mappings.items():
                if symbol in mappings:
                    deriv_symbol = mappings[symbol]
                    break
        
        # Create Deriv order
        deriv_order = {
            "buy": 1,
            "parameters": {
                "amount": amount,
                "basis": "payout",  # or "stake"
                "contract_type": order_type,
                "currency": "USD",
                "duration": duration,
                "duration_unit": duration_unit,
                "symbol": deriv_symbol
            }
        }
        
        # Add optional parameters
        if 'barrier' in order_params:
            deriv_order["parameters"]["barrier"] = order_params['barrier']
        
        if 'prediction' in order_params:
            deriv_order["parameters"]["prediction"] = order_params['prediction']
        
        return deriv_order
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to Deriv WebSocket API"""
        try:
            if not self.websocket or not self.connected:
                raise ConnectionError("Not connected to Deriv")
            
            # Add message ID
            self.request_counter += 1
            request["req_id"] = self.request_counter
            
            # Send request
            message = json.dumps(request)
            await self.websocket.send(message)
            
            # Wait for response
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Error sending request: {e}")
            return {"error": str(e)}
    
    async def subscribe_to_ticks(self, symbols: List[str]):
        """Subscribe to real-time tick data"""
        try:
            for symbol in symbols:
                request = {"ticks": symbol, "subscribe": 1}
                await self.send_request(request)
            
            self.logger.info(f"Subscribed to ticks for {len(symbols)} symbols")
            
        except Exception as e:
            self.logger.error(f"Error subscribing to ticks: {e}")
    
    async def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary"""
        try:
            # Get current positions
            positions = await self.get_positions()
            
            # Calculate total P&L
            total_pnl = sum(pos.get('profit', 0) for pos in positions)
            
            # Get recent transactions
            transactions = await self.get_transaction_history(10)
            
            return {
                'account_info': self.account_info,
                'positions': positions,
                'total_positions': len(positions),
                'total_pnl': total_pnl,
                'recent_transactions': transactions,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return {}
    
    async def disconnect(self):
        """Disconnect from Deriv"""
        try:
            if self.websocket:
                await self.websocket.close()
                self.connected = False
                self.logger.info("Disconnected from Deriv")
        except Exception as e:
            self.logger.error(f"Error disconnecting: {e}")

# Utility functions for Deriv integration
def map_asset_to_deriv(asset_name: str, asset_type: str = 'forex') -> str:
    """Map asset name to Deriv symbol"""
    asset_mappings = {
        'forex': {
            'EUR/USD': 'frxEURUSD',
            'GBP/USD': 'frxGBPUSD',
            'USD/JPY': 'frxUSDJPY',
            'AUD/USD': 'frxAUDUSD',
            'USD/CHF': 'frxUSDCHF',
            'EUR/GBP': 'frxEURGBP',
            'EUR/JPY': 'frxEURJPY',
            'GBP/JPY': 'frxGBPJPY'
        },
        'commodities': {
            'Gold': 'frxXAUUSD',
            'Silver': 'frxXAGUSD',
            'Oil': 'frxUSOIL',
            'Natural Gas': 'frxNGAS'
        },
        'indices': {
            'US 30': 'frxUS30',
            'US 500': 'frxUS500',
            'US Tech 100': 'frxUSTECH',
            'Germany 40': 'frxDEU30',
            'UK 100': 'frxUK100'
        }
    }
    
    return asset_mappings.get(asset_type, {}).get(asset_name, asset_name)

def create_deriv_order_params(symbol: str, order_type: str, amount: float, 
                            duration: int = 60, **kwargs) -> Dict[str, Any]:
    """Create standardized order parameters for Deriv"""
    return {
        'symbol': symbol,
        'type': order_type.upper(),  # CALL or PUT
        'amount': amount,
        'duration': duration,
        'duration_unit': 's',
        **kwargs
    }

# Example usage
async def test_deriv_connection():
    """Test Deriv connection"""
    # Note: Replace with actual API token for testing
    api_token = "your_deriv_api_token_here"
    
    broker = DerivBroker(api_token, demo_mode=True)
    
    try:
        # Connect
        connected = await broker.connect()
        if not connected:
            print("Failed to connect to Deriv")
            return
        
        # Get account info
        account_info = await broker.get_account_info()
        print(f"Account Info: {account_info}")
        
        # Get asset price
        price_data = await broker.get_asset_price('frxEURUSD')
        print(f"EUR/USD Price: {price_data}")
        
        # Get positions
        positions = await broker.get_positions()
        print(f"Open Positions: {len(positions)}")
        
        # Get portfolio summary
        portfolio = await broker.get_portfolio_summary()
        print(f"Portfolio Summary: {portfolio}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await broker.disconnect()

if __name__ == "__main__":
    asyncio.run(test_deriv_connection())
