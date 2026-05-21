#!/usr/bin/env python3
"""
MetaTrader 5 Broker Integration for QuantMuse
Supports forex, stocks, commodities, indices
"""

import MetaTrader5 as mt5
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import time

class MT5Broker:
    """MetaTrader 5 integration for trading"""
    
    def __init__(self, login: int, password: str, server: str, demo_mode: bool = True, 
                 mt5_path: str = None):
        self.login = login
        self.password = password
        self.server = server
        self.demo_mode = demo_mode
        self.mt5_path = mt5_path or "C:/Program Files/MetaTrader 5/terminal64.exe"
        self.connected = False
        self.account_info = {}
        self.positions = {}
        self.logger = logging.getLogger(__name__)
        
        # Asset mappings for MT5
        self.asset_mappings = {
            'forex': {
                'EUR/USD': 'EURUSD',
                'GBP/USD': 'GBPUSD',
                'USD/JPY': 'USDJPY',
                'AUD/USD': 'AUDUSD',
                'USD/CHF': 'USDCHF',
                'EUR/GBP': 'EURGBP',
                'EUR/JPY': 'EURJPY',
                'GBP/JPY': 'GBPJPY',
                'USD/CAD': 'USDCAD',
                'NZD/USD': 'NZDUSD'
            },
            'commodities': {
                'Gold': 'XAUUSD',
                'XAUUSD': 'XAUUSD',  # Add direct mapping
                'Silver': 'XAGUSD',
                'XAGUSD': 'XAGUSD',  # Add direct mapping
                'Oil': 'USOIL',
                'Brent Oil': 'UKOIL',
                'Natural Gas': 'NGAS',
                'Copper': 'COPPER',
                'Platinum': 'XPTUSD'
            },
            'indices': {
                'US 30': 'US30',
                'US 500': 'US500',
                'US Tech 100': 'USTECH',
                'Germany 40': 'DEU30',
                'UK 100': 'UK100',
                'Japan 225': 'JP225',
                'China 50': 'CHINA50',
                'Australia 200': 'AUS200'
            },
            'stocks': {
                'Apple': 'AAPL',
                'Microsoft': 'MSFT',
                'Google': 'GOOGL',
                'Amazon': 'AMZN',
                'Tesla': 'TSLA',
                'Facebook': 'META',
                'Netflix': 'NFLX',
                'NVIDIA': 'NVDA'
            }
        }
        
        # Order type mappings
        self.order_types = {
            'market_buy': mt5.ORDER_TYPE_BUY,
            'market_sell': mt5.ORDER_TYPE_SELL,
            'limit_buy': mt5.ORDER_TYPE_BUY_LIMIT,
            'limit_sell': mt5.ORDER_TYPE_SELL_LIMIT,
            'stop_buy': mt5.ORDER_TYPE_BUY_STOP,
            'stop_sell': mt5.ORDER_TYPE_SELL_STOP
        }
        
        # Timeframe mappings
        self.timeframes = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1,
            'W1': mt5.TIMEFRAME_W1,
            'MN1': mt5.TIMEFRAME_MN1
        }
    
    def connect(self) -> bool:
        """Connect to MT5 terminal"""
        try:
            self.logger.info(f"Connecting to MT5 (demo_mode={self.demo_mode})...")
            
            # Initialize MT5
            if not mt5.initialize():
                self.logger.error("MT5.initialize() failed")
                return False
            
            # Login to account
            authorized = mt5.login(self.login, password=self.password, server=self.server)
            
            if not authorized:
                self.logger.error(f"Failed to login to MT5: {mt5.last_error()}")
                mt5.shutdown()
                return False
            
            self.connected = True
            
            # Get account info
            self.get_account_info()
            
            self.logger.info("Successfully connected to MT5")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MT5: {e}")
            self.connected = False
            if mt5.initialized():
                mt5.shutdown()
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account balance and information"""
        try:
            if not self.connected:
                return {}
            
            account_info = mt5.account_info()
            
            if account_info is None:
                self.logger.error("Failed to get account info")
                return {}
            
            self.account_info = {
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'profit': account_info.profit,
                'leverage': account_info.leverage,
                'currency': account_info.currency,
                'login': account_info.login,
                'server': account_info.server,
                'demo_account': self.demo_mode,
                'account_type': 'demo' if self.demo_mode else 'real'
            }
            
            return self.account_info
            
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}")
            return {}
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get symbol information"""
        try:
            if not self.connected:
                return {}
            
            symbol_info = mt5.symbol_info(symbol)
            
            if symbol_info is None:
                self.logger.error(f"Symbol {symbol} not found")
                return {}
            
            return {
                'symbol': symbol_info.name,
                'bid': symbol_info.bid,
                'ask': symbol_info.ask,
                'spread': symbol_info.spread,
                'digits': symbol_info.digits,
                'point': symbol_info.point,
                'trade_contract_size': symbol_info.trade_contract_size,
                'volume_min': symbol_info.volume_min,
                'volume_max': symbol_info.volume_max,
                'volume_step': symbol_info.volume_step,
                'swap_long': symbol_info.swap_long,
                'swap_short': symbol_info.swap_short,
                'starting_time': symbol_info.starting_time,
                'expiration_time': symbol_info.expiration_time
            }
            
        except Exception as e:
            self.logger.error(f"Error getting symbol info for {symbol}: {e}")
            return {}
    
    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for a symbol"""
        try:
            if not self.connected:
                return {}
            
            tick = mt5.symbol_info_tick(symbol)
            
            if tick is None:
                self.logger.error(f"Failed to get tick for {symbol}")
                return {}
            
            return {
                'symbol': symbol,
                'bid': tick.bid,
                'ask': tick.ask,
                'last': tick.last,
                'volume': tick.volume,
                'time': datetime.fromtimestamp(tick.time),
                'spread': tick.ask - tick.bid
            }
            
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            return {}
    
    def place_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """Place order on MT5"""
        try:
            if not self.connected:
                return {
                    'success': False,
                    'error': 'Not connected to MT5',
                    'order_id': None
                }
            
            # Map order parameters to MT5 format
            mt5_order = self._map_order_to_mt5(order_params)
            
            # Send order request
            result = mt5.order_send(mt5_order)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Order failed: {result.retcode} - {result.comment}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'order_id': None
                }
            
            # Return success response
            return {
                'success': True,
                'order_id': result.order,
                'deal_id': result.deal,
                'volume': result.volume,
                'price': result.price,
                'bid': result.bid,
                'ask': result.ask,
                'type': result.type,
                'magic': result.magic,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return {
                'success': False,
                'error': str(e),
                'order_id': None
            }
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get open positions"""
        try:
            if not self.connected:
                return []
            
            positions = mt5.positions_get()
            
            if positions is None:
                self.logger.error("Failed to get positions")
                return []
            
            # Format positions
            formatted_positions = []
            for pos in positions:
                formatted_positions.append({
                    'position_id': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == mt5.POSITION_TYPE_BUY else 'SELL',
                    'volume': pos.volume,
                    'open_price': pos.price_open,
                    'current_price': pos.price_current,
                    'profit': pos.profit,
                    'swap': pos.swap,
                    'commission': pos.commission,
                    'open_time': datetime.fromtimestamp(pos.time),
                    'magic': pos.magic,
                    'comment': pos.comment,
                    'stop_loss': pos.sl,
                    'take_profit': pos.tp
                })
            
            self.positions = {pos['position_id']: pos for pos in formatted_positions}
            return formatted_positions
            
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []
    
    def close_position(self, position_id: int, volume: float = None) -> Dict[str, Any]:
        """Close a position"""
        try:
            if not self.connected:
                return {
                    'success': False,
                    'error': 'Not connected to MT5'
                }
            
            # Get position details
            position = mt5.positions_get(ticket=position_id)
            
            if not position:
                return {
                    'success': False,
                    'error': f'Position {position_id} not found'
                }
            
            position = position[0]
            
            # Determine close volume
            close_volume = volume if volume else position.volume
            
            # Create close request
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": close_volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position_id,
                "price": mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask,
                "deviation": 20,
                "magic": position.magic,
                "comment": "Close position",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send close request
            result = mt5.order_send(close_request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Close failed: {result.retcode} - {result.comment}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
            
            return {
                'success': True,
                'close_info': {
                    'order_id': result.order,
                    'deal_id': result.deal,
                    'volume': result.volume,
                    'price': result.price,
                    'profit': position.profit
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error closing position {position_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def modify_position(self, position_id: int, stop_loss: float = None, 
                       take_profit: float = None) -> Dict[str, Any]:
        """Modify position stop loss and take profit"""
        try:
            if not self.connected:
                return {
                    'success': False,
                    'error': 'Not connected to MT5'
                }
            
            # Get position details
            position = mt5.positions_get(ticket=position_id)
            
            if not position:
                return {
                    'success': False,
                    'error': f'Position {position_id} not found'
                }
            
            position = position[0]
            
            # Create modify request
            modify_request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "sl": stop_loss if stop_loss is not None else position.sl,
                "tp": take_profit if take_profit is not None else position.tp,
                "position": position_id,
                "magic": position.magic,
                "comment": "Modify SL/TP",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send modify request
            result = mt5.order_send(modify_request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Modify failed: {result.retcode} - {result.comment}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
            
            return {
                'success': True,
                'modify_info': {
                    'order_id': result.order,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error modifying position {position_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_historical_data(self, symbol: str, timeframe: str, count: int = 100) -> pd.DataFrame:
        """Get historical data for a symbol"""
        try:
            if not self.connected:
                return pd.DataFrame()
            
            mt5_timeframe = self.timeframes.get(timeframe, mt5.TIMEFRAME_H1)
            
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            
            if rates is None:
                self.logger.error(f"Failed to get historical data for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error getting historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_order_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get order history"""
        try:
            if not self.connected:
                return []
            
            # Calculate date range
            from_date = datetime.now() - timedelta(days=days)
            to_date = datetime.now()
            
            # Get deals
            deals = mt5.history_deals_get(from_date, to_date)
            
            if deals is None:
                self.logger.error("Failed to get order history")
                return []
            
            # Format deals
            formatted_deals = []
            for deal in deals:
                formatted_deals.append({
                    'deal_id': deal.ticket,
                    'order_id': deal.order,
                    'symbol': deal.symbol,
                    'type': 'BUY' if deal.type == mt5.DEAL_TYPE_BUY else 'SELL',
                    'volume': deal.volume,
                    'price': deal.price,
                    'profit': deal.profit,
                    'commission': deal.commission,
                    'swap': deal.swap,
                    'time': datetime.fromtimestamp(deal.time),
                    'magic': deal.magic,
                    'comment': deal.comment
                })
            
            return formatted_deals
            
        except Exception as e:
            self.logger.error(f"Error getting order history: {e}")
            return []
    
    def _map_order_to_mt5(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """Map order parameters to MT5 format"""
        
        # Basic order parameters
        symbol = order_params.get('symbol', 'EURUSD')
        order_type = order_params.get('type', 'market_buy')
        volume = order_params.get('volume', 0.01)
        price = order_params.get('price', 0.0)
        stop_loss = order_params.get('stop_loss', 0.0)
        take_profit = order_params.get('take_profit', 0.0)
        deviation = order_params.get('deviation', 20)
        magic = order_params.get('magic', 123456)
        comment = order_params.get('comment', 'QuantMuse Order')
        
        # Get current price if not provided
        if price == 0.0 and 'market' in order_type:
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                price = tick.ask if 'buy' in order_type else tick.bid
        
        # Create MT5 order
        mt5_order = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": self.order_types.get(order_type, mt5.ORDER_TYPE_BUY),
            "price": price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": deviation,
            "magic": magic,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        return mt5_order
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary"""
        try:
            # Get current positions
            positions = self.get_positions()
            
            # Calculate total P&L
            total_pnl = sum(pos.get('profit', 0) for pos in positions)
            
            # Get recent deals
            deals = self.get_order_history(7)
            
            return {
                'account_info': self.account_info,
                'positions': positions,
                'total_positions': len(positions),
                'total_pnl': total_pnl,
                'recent_deals': deals,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return {}
    
    def disconnect(self):
        """Disconnect from MT5"""
        try:
            if mt5.initialized():
                mt5.shutdown()
                self.connected = False
                self.logger.info("Disconnected from MT5")
        except Exception as e:
            self.logger.error(f"Error disconnecting: {e}")

# Utility functions for MT5 integration
def map_asset_to_mt5(asset_name: str, asset_type: str = 'forex') -> str:
    """Map asset name to MT5 symbol"""
    asset_mappings = {
        'forex': {
            'EUR/USD': 'EURUSD',
            'GBP/USD': 'GBPUSD',
            'USD/JPY': 'USDJPY',
            'AUD/USD': 'AUDUSD',
            'USD/CHF': 'USDCHF',
            'EUR/GBP': 'EURGBP',
            'EUR/JPY': 'EURJPY',
            'GBP/JPY': 'GBPJPY',
            'USD/CAD': 'USDCAD',
            'NZD/USD': 'NZDUSD'
        },
        'commodities': {
            'Gold': 'XAUUSD',
            'Silver': 'XAGUSD',
            'Oil': 'USOIL',
            'Brent Oil': 'UKOIL',
            'Natural Gas': 'NGAS',
            'Copper': 'COPPER',
            'Platinum': 'XPTUSD'
        },
        'indices': {
            'US 30': 'US30',
            'US 500': 'US500',
            'US Tech 100': 'USTECH',
            'Germany 40': 'DEU30',
            'UK 100': 'UK100',
            'Japan 225': 'JP225',
            'China 50': 'CHINA50',
            'Australia 200': 'AUS200'
        },
        'stocks': {
            'Apple': 'AAPL',
            'Microsoft': 'MSFT',
            'Google': 'GOOGL',
            'Amazon': 'AMZN',
            'Tesla': 'TSLA',
            'Facebook': 'META',
            'Netflix': 'NFLX',
            'NVIDIA': 'NVDA'
        }
    }
    
    return asset_mappings.get(asset_type, {}).get(asset_name, asset_name)

def create_mt5_order_params(symbol: str, order_type: str, volume: float, 
                           price: float = 0.0, stop_loss: float = 0.0, 
                           take_profit: float = 0.0, **kwargs) -> Dict[str, Any]:
    """Create standardized order parameters for MT5"""
    return {
        'symbol': symbol,
        'type': order_type.lower(),
        'volume': volume,
        'price': price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'magic': kwargs.get('magic', 123456),
        'comment': kwargs.get('comment', 'QuantMuse Order'),
        'deviation': kwargs.get('deviation', 20)
    }

# Example usage
def test_mt5_connection():
    """Test MT5 connection"""
    # Note: Replace with actual credentials for testing
    login = 12345678  # Your MT5 login
    password = "your_password"  # Your MT5 password
    server = "Demo_Server"  # Your MT5 server
    
    broker = MT5Broker(login, password, server, demo_mode=True)
    
    try:
        # Connect
        connected = broker.connect()
        if not connected:
            print("Failed to connect to MT5")
            return
        
        # Get account info
        account_info = broker.get_account_info()
        print(f"Account Info: {account_info}")
        
        # Get symbol info
        symbol_info = broker.get_symbol_info('EURUSD')
        print(f"EURUSD Info: {symbol_info}")
        
        # Get current price
        price_data = broker.get_current_price('EURUSD')
        print(f"EURUSD Price: {price_data}")
        
        # Get positions
        positions = broker.get_positions()
        print(f"Open Positions: {len(positions)}")
        
        # Get portfolio summary
        portfolio = broker.get_portfolio_summary()
        print(f"Portfolio Summary: {portfolio}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        broker.disconnect()

if __name__ == "__main__":
    test_mt5_connection()
