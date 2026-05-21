#!/usr/bin/env python3
"""
Asset Mapping and Normalization System for QuantMuse
Maps assets between Deriv and MT5 formats with normalization
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np

class AssetType(Enum):
    """Asset types"""
    FOREX = "forex"
    COMMODITIES = "commodities"
    INDICES = "indices"
    STOCKS = "stocks"
    BINARY_OPTIONS = "binary_options"

@dataclass
class AssetMapping:
    """Asset mapping between brokers"""
    standard_name: str
    asset_type: AssetType
    deriv_symbol: Optional[str]
    mt5_symbol: Optional[str]
    description: str
    trading_hours: Dict[str, str]
    min_lot_size: float
    max_lot_size: float
    lot_step: float
    tick_size: float
    contract_size: float

@dataclass
class NormalizedPrice:
    """Normalized price data"""
    symbol: str
    broker: str
    bid: float
    ask: float
    spread: float
    timestamp: str
    volume: Optional[float] = None
    mid_price: Optional[float] = None

class AssetMapper:
    """Maps and normalizes assets between different broker formats"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.asset_mappings = {}
        self.reverse_mappings = {}
        self.price_normalizers = {}
        
        # Initialize asset mappings
        self._initialize_asset_mappings()
        self._initialize_reverse_mappings()
        self._initialize_price_normalizers()
    
    def _initialize_asset_mappings(self):
        """Initialize comprehensive asset mappings"""
        
        # Forex mappings
        forex_assets = [
            AssetMapping(
                standard_name="EUR/USD",
                asset_type=AssetType.FOREX,
                deriv_symbol="frxEURUSD",
                mt5_symbol="EURUSD",
                description="Euro vs US Dollar",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.00001,
                contract_size=100000
            ),
            AssetMapping(
                standard_name="GBP/USD",
                asset_type=AssetType.FOREX,
                deriv_symbol="frxGBPUSD",
                mt5_symbol="GBPUSD",
                description="British Pound vs US Dollar",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.00001,
                contract_size=100000
            ),
            AssetMapping(
                standard_name="USD/JPY",
                asset_type=AssetType.FOREX,
                deriv_symbol="frxUSDJPY",
                mt5_symbol="USDJPY",
                description="US Dollar vs Japanese Yen",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.001,
                contract_size=100000
            ),
            AssetMapping(
                standard_name="AUD/USD",
                asset_type=AssetType.FOREX,
                deriv_symbol="frxAUDUSD",
                mt5_symbol="AUDUSD",
                description="Australian Dollar vs US Dollar",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.00001,
                contract_size=100000
            ),
            AssetMapping(
                standard_name="USD/CHF",
                asset_type=AssetType.FOREX,
                deriv_symbol="frxUSDCHF",
                mt5_symbol="USDCHF",
                description="US Dollar vs Swiss Franc",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.00001,
                contract_size=100000
            ),
            AssetMapping(
                standard_name="EUR/GBP",
                asset_type=AssetType.FOREX,
                deriv_symbol="frxEURGBP",
                mt5_symbol="EURGBP",
                description="Euro vs British Pound",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.00001,
                contract_size=100000
            ),
            AssetMapping(
                standard_name="EUR/JPY",
                asset_type=AssetType.FOREX,
                deriv_symbol="frxEURJPY",
                mt5_symbol="EURJPY",
                description="Euro vs Japanese Yen",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.001,
                contract_size=100000
            ),
            AssetMapping(
                standard_name="GBP/JPY",
                asset_type=AssetType.FOREX,
                deriv_symbol="frxGBPJPY",
                mt5_symbol="GBPJPY",
                description="British Pound vs Japanese Yen",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.001,
                contract_size=100000
            ),
            AssetMapping(
                standard_name="USD/CAD",
                asset_type=AssetType.FOREX,
                deriv_symbol="frxUSDCAD",
                mt5_symbol="USDCAD",
                description="US Dollar vs Canadian Dollar",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.00001,
                contract_size=100000
            ),
            AssetMapping(
                standard_name="NZD/USD",
                asset_type=AssetType.FOREX,
                deriv_symbol="frxNZDUSD",
                mt5_symbol="NZDUSD",
                description="New Zealand Dollar vs US Dollar",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.00001,
                contract_size=100000
            )
        ]
        
        # Commodities mappings
        commodity_assets = [
            AssetMapping(
                standard_name="Gold",
                asset_type=AssetType.COMMODITIES,
                deriv_symbol="frxXAUUSD",
                mt5_symbol="XAUUSD",
                description="Gold Spot",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.01,
                contract_size=100
            ),
            AssetMapping(
                standard_name="Silver",
                asset_type=AssetType.COMMODITIES,
                deriv_symbol="frxXAGUSD",
                mt5_symbol="XAGUSD",
                description="Silver Spot",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.001,
                contract_size=5000
            ),
            AssetMapping(
                standard_name="Oil",
                asset_type=AssetType.COMMODITIES,
                deriv_symbol="frxUSOIL",
                mt5_symbol="USOIL",
                description="Crude Oil WTI",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.01,
                contract_size=1000
            ),
            AssetMapping(
                standard_name="Brent Oil",
                asset_type=AssetType.COMMODITIES,
                deriv_symbol="frxUKOIL",
                mt5_symbol="UKOIL",
                description="Brent Crude Oil",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.01,
                contract_size=1000
            ),
            AssetMapping(
                standard_name="Natural Gas",
                asset_type=AssetType.COMMODITIES,
                deriv_symbol="frxNGAS",
                mt5_symbol="NGAS",
                description="Natural Gas",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.001,
                contract_size=10000
            ),
            AssetMapping(
                standard_name="Copper",
                asset_type=AssetType.COMMODITIES,
                deriv_symbol="frxCOPPER",
                mt5_symbol="COPPER",
                description="Copper",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.0005,
                contract_size=25000
            ),
            AssetMapping(
                standard_name="Platinum",
                asset_type=AssetType.COMMODITIES,
                deriv_symbol="frxXPTUSD",
                mt5_symbol="XPTUSD",
                description="Platinum",
                trading_hours={"market": "24/5", "break": "Weekends"},
                min_lot_size=0.01,
                max_lot_size=100.0,
                lot_step=0.01,
                tick_size=0.01,
                contract_size=50
            )
        ]
        
        # Indices mappings
        index_assets = [
            AssetMapping(
                standard_name="US 30",
                asset_type=AssetType.INDICES,
                deriv_symbol="frxUS30",
                mt5_symbol="US30",
                description="Dow Jones Industrial Average",
                trading_hours={"market": "09:30-16:00 EST", "break": "Weekends"},
                min_lot_size=0.1,
                max_lot_size=1000.0,
                lot_step=0.1,
                tick_size=1.0,
                contract_size=1
            ),
            AssetMapping(
                standard_name="US 500",
                asset_type=AssetType.INDICES,
                deriv_symbol="frxUS500",
                mt5_symbol="US500",
                description="S&P 500 Index",
                trading_hours={"market": "09:30-16:00 EST", "break": "Weekends"},
                min_lot_size=0.1,
                max_lot_size=1000.0,
                lot_step=0.1,
                tick_size=0.25,
                contract_size=1
            ),
            AssetMapping(
                standard_name="US Tech 100",
                asset_type=AssetType.INDICES,
                deriv_symbol="frxUSTECH",
                mt5_symbol="USTECH",
                description="NASDAQ 100 Index",
                trading_hours={"market": "09:30-16:00 EST", "break": "Weekends"},
                min_lot_size=0.1,
                max_lot_size=1000.0,
                lot_step=0.1,
                tick_size=0.25,
                contract_size=1
            ),
            AssetMapping(
                standard_name="Germany 40",
                asset_type=AssetType.INDICES,
                deriv_symbol="frxDEU30",
                mt5_symbol="DEU30",
                description="DAX Index",
                trading_hours={"market": "09:00-17:30 CET", "break": "Weekends"},
                min_lot_size=0.1,
                max_lot_size=1000.0,
                lot_step=0.1,
                tick_size=1.0,
                contract_size=1
            ),
            AssetMapping(
                standard_name="UK 100",
                asset_type=AssetType.INDICES,
                deriv_symbol="frxUK100",
                mt5_symbol="UK100",
                description="FTSE 100 Index",
                trading_hours={"market": "08:00-16:30 GMT", "break": "Weekends"},
                min_lot_size=0.1,
                max_lot_size=1000.0,
                lot_step=0.1,
                tick_size=1.0,
                contract_size=1
            ),
            AssetMapping(
                standard_name="Japan 225",
                asset_type=AssetType.INDICES,
                deriv_symbol="frxJP225",
                mt5_symbol="JP225",
                description="Nikkei 225 Index",
                trading_hours={"market": "09:00-15:00 JST", "break": "Weekends"},
                min_lot_size=0.1,
                max_lot_size=1000.0,
                lot_step=0.1,
                tick_size=1.0,
                contract_size=1
            ),
            AssetMapping(
                standard_name="China 50",
                asset_type=AssetType.INDICES,
                deriv_symbol="frxCHINA50",
                mt5_symbol="CHINA50",
                description="China A50 Index",
                trading_hours={"market": "09:30-15:00 CST", "break": "Weekends"},
                min_lot_size=0.1,
                max_lot_size=1000.0,
                lot_step=0.1,
                tick_size=1.0,
                contract_size=1
            ),
            AssetMapping(
                standard_name="Australia 200",
                asset_type=AssetType.INDICES,
                deriv_symbol="frxAUS200",
                mt5_symbol="AUS200",
                description="ASX 200 Index",
                trading_hours={"market": "10:00-16:00 AEST", "break": "Weekends"},
                min_lot_size=0.1,
                max_lot_size=1000.0,
                lot_step=0.1,
                tick_size=1.0,
                contract_size=1
            )
        ]
        
        # Stocks mappings (MT5 only)
        stock_assets = [
            AssetMapping(
                standard_name="Apple",
                asset_type=AssetType.STOCKS,
                deriv_symbol=None,
                mt5_symbol="AAPL",
                description="Apple Inc.",
                trading_hours={"market": "09:30-16:00 EST", "break": "Weekends"},
                min_lot_size=1,
                max_lot_size=10000,
                lot_step=1,
                tick_size=0.01,
                contract_size=1
            ),
            AssetMapping(
                standard_name="Microsoft",
                asset_type=AssetType.STOCKS,
                deriv_symbol=None,
                mt5_symbol="MSFT",
                description="Microsoft Corporation",
                trading_hours={"market": "09:30-16:00 EST", "break": "Weekends"},
                min_lot_size=1,
                max_lot_size=10000,
                lot_step=1,
                tick_size=0.01,
                contract_size=1
            ),
            AssetMapping(
                standard_name="Google",
                asset_type=AssetType.STOCKS,
                deriv_symbol=None,
                mt5_symbol="GOOGL",
                description="Alphabet Inc.",
                trading_hours={"market": "09:30-16:00 EST", "break": "Weekends"},
                min_lot_size=1,
                max_lot_size=10000,
                lot_step=1,
                tick_size=0.01,
                contract_size=1
            ),
            AssetMapping(
                standard_name="Amazon",
                asset_type=AssetType.STOCKS,
                deriv_symbol=None,
                mt5_symbol="AMZN",
                description="Amazon.com Inc.",
                trading_hours={"market": "09:30-16:00 EST", "break": "Weekends"},
                min_lot_size=1,
                max_lot_size=10000,
                lot_step=1,
                tick_size=0.01,
                contract_size=1
            ),
            AssetMapping(
                standard_name="Tesla",
                asset_type=AssetType.STOCKS,
                deriv_symbol=None,
                mt5_symbol="TSLA",
                description="Tesla Inc.",
                trading_hours={"market": "09:30-16:00 EST", "break": "Weekends"},
                min_lot_size=1,
                max_lot_size=10000,
                lot_step=1,
                tick_size=0.01,
                contract_size=1
            ),
            AssetMapping(
                standard_name="Facebook",
                asset_type=AssetType.STOCKS,
                deriv_symbol=None,
                mt5_symbol="META",
                description="Meta Platforms Inc.",
                trading_hours={"market": "09:30-16:00 EST", "break": "Weekends"},
                min_lot_size=1,
                max_lot_size=10000,
                lot_step=1,
                tick_size=0.01,
                contract_size=1
            ),
            AssetMapping(
                standard_name="Netflix",
                asset_type=AssetType.STOCKS,
                deriv_symbol=None,
                mt5_symbol="NFLX",
                description="Netflix Inc.",
                trading_hours={"market": "09:30-16:00 EST", "break": "Weekends"},
                min_lot_size=1,
                max_lot_size=10000,
                lot_step=1,
                tick_size=0.01,
                contract_size=1
            ),
            AssetMapping(
                standard_name="NVIDIA",
                asset_type=AssetType.STOCKS,
                deriv_symbol=None,
                mt5_symbol="NVDA",
                description="NVIDIA Corporation",
                trading_hours={"market": "09:30-16:00 EST", "break": "Weekends"},
                min_lot_size=1,
                max_lot_size=10000,
                lot_step=1,
                tick_size=0.01,
                contract_size=1
            )
        ]
        
        # Binary options mappings (Deriv only)
        binary_assets = [
            AssetMapping(
                standard_name="Rise/Fall",
                asset_type=AssetType.BINARY_OPTIONS,
                deriv_symbol="rise_fall",
                mt5_symbol=None,
                description="Predict if price will rise or fall",
                trading_hours={"market": "Varies by underlying", "break": "Weekends"},
                min_lot_size=1,
                max_lot_size=10000,
                lot_step=1,
                tick_size=0.01,
                contract_size=1
            ),
            AssetMapping(
                standard_name="Higher/Lower",
                asset_type=AssetType.BINARY_OPTIONS,
                deriv_symbol="higher_lower",
                mt5_symbol=None,
                description="Predict if price will be higher or lower",
                trading_hours={"market": "Varies by underlying", "break": "Weekends"},
                min_lot_size=1,
                max_lot_size=10000,
                lot_step=1,
                tick_size=0.01,
                contract_size=1
            ),
            AssetMapping(
                standard_name="Touch/No Touch",
                asset_type=AssetType.BINARY_OPTIONS,
                deriv_symbol="touch_no_touch",
                mt5_symbol=None,
                description="Predict if price will touch a barrier",
                trading_hours={"market": "Varies by underlying", "break": "Weekends"},
                min_lot_size=1,
                max_lot_size=10000,
                lot_step=1,
                tick_size=0.01,
                contract_size=1
            ),
            AssetMapping(
                standard_name="In/Out",
                asset_type=AssetType.BINARY_OPTIONS,
                deriv_symbol="in_out",
                mt5_symbol=None,
                description="Predict if price will stay in or exit range",
                trading_hours={"market": "Varies by underlying", "break": "Weekends"},
                min_lot_size=1,
                max_lot_size=10000,
                lot_step=1,
                tick_size=0.01,
                contract_size=1
            )
        ]
        
        # Add all mappings to dictionary
        for asset in forex_assets + commodity_assets + index_assets + stock_assets + binary_assets:
            self.asset_mappings[asset.standard_name] = asset
    
    def _initialize_reverse_mappings(self):
        """Initialize reverse mappings for broker symbols"""
        for standard_name, mapping in self.asset_mappings.items():
            # Deriv reverse mapping
            if mapping.deriv_symbol:
                self.reverse_mappings[f"deriv_{mapping.deriv_symbol}"] = standard_name
            
            # MT5 reverse mapping
            if mapping.mt5_symbol:
                self.reverse_mappings[f"mt5_{mapping.mt5_symbol}"] = standard_name
    
    def _initialize_price_normalizers(self):
        """Initialize price normalizers for different asset types"""
        self.price_normalizers = {
            AssetType.FOREX: {
                'precision': 5,
                'pip_multiplier': 10000,
                'lot_multiplier': 100000
            },
            AssetType.COMMODITIES: {
                'precision': 2,
                'pip_multiplier': 100,
                'lot_multiplier': 100
            },
            AssetType.INDICES: {
                'precision': 2,
                'pip_multiplier': 1,
                'lot_multiplier': 1
            },
            AssetType.STOCKS: {
                'precision': 2,
                'pip_multiplier': 1,
                'lot_multiplier': 1
            },
            AssetType.BINARY_OPTIONS: {
                'precision': 2,
                'pip_multiplier': 1,
                'lot_multiplier': 1
            }
        }
    
    def map_to_broker(self, standard_name: str, broker: str) -> Optional[str]:
        """Map standard asset name to broker-specific symbol"""
        try:
            mapping = self.asset_mappings.get(standard_name)
            if not mapping:
                self.logger.warning(f"No mapping found for asset: {standard_name}")
                return None
            
            if broker.lower() == 'deriv':
                return mapping.deriv_symbol
            elif broker.lower() == 'mt5':
                return mapping.mt5_symbol
            else:
                self.logger.error(f"Unknown broker: {broker}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error mapping {standard_name} to {broker}: {e}")
            return None
    
    def map_from_broker(self, broker_symbol: str, broker: str) -> Optional[str]:
        """Map broker-specific symbol to standard name"""
        try:
            key = f"{broker.lower()}_{broker_symbol}"
            return self.reverse_mappings.get(key)
            
        except Exception as e:
            self.logger.error(f"Error mapping {broker_symbol} from {broker}: {e}")
            return None
    
    def normalize_price(self, price_data: Dict[str, Any], broker: str) -> NormalizedPrice:
        """Normalize price data to standard format"""
        try:
            # Get standard name
            broker_symbol = price_data.get('symbol', '')
            standard_name = self.map_from_broker(broker_symbol, broker)
            
            if not standard_name:
                # If no mapping found, use broker symbol as standard
                standard_name = broker_symbol
            
            # Get asset type and normalizer
            mapping = self.asset_mappings.get(standard_name)
            if not mapping:
                # Default to forex if no mapping found
                asset_type = AssetType.FOREX
            else:
                asset_type = mapping.asset_type
            
            normalizer = self.price_normalizers.get(asset_type, self.price_normalizers[AssetType.FOREX])
            
            # Extract and normalize prices
            bid = float(price_data.get('bid', 0))
            ask = float(price_data.get('ask', 0))
            spread = ask - bid
            mid_price = (bid + ask) / 2
            
            # Apply precision
            precision = normalizer['precision']
            bid = round(bid, precision)
            ask = round(ask, precision)
            spread = round(spread, precision)
            mid_price = round(mid_price, precision)
            
            return NormalizedPrice(
                symbol=standard_name,
                broker=broker,
                bid=bid,
                ask=ask,
                spread=spread,
                timestamp=price_data.get('timestamp', ''),
                volume=price_data.get('volume'),
                mid_price=mid_price
            )
            
        except Exception as e:
            self.logger.error(f"Error normalizing price data: {e}")
            raise
    
    def normalize_volume(self, volume: float, standard_name: str, broker: str) -> float:
        """Normalize volume to standard units"""
        try:
            mapping = self.asset_mappings.get(standard_name)
            if not mapping:
                return volume
            
            # Get normalizer for asset type
            normalizer = self.price_normalizers.get(mapping.asset_type, {})
            lot_multiplier = normalizer.get('lot_multiplier', 1)
            
            # Normalize volume
            normalized_volume = volume * lot_multiplier
            
            return round(normalized_volume, 2)
            
        except Exception as e:
            self.logger.error(f"Error normalizing volume: {e}")
            return volume
    
    def normalize_spread(self, spread: float, standard_name: str, broker: str) -> float:
        """Normalize spread to pips"""
        try:
            mapping = self.asset_mappings.get(standard_name)
            if not mapping:
                return spread
            
            # Get normalizer for asset type
            normalizer = self.price_normalizers.get(mapping.asset_type, {})
            pip_multiplier = normalizer.get('pip_multiplier', 1)
            
            # Convert to pips
            spread_pips = spread * pip_multiplier
            
            return round(spread_pips, 2)
            
        except Exception as e:
            self.logger.error(f"Error normalizing spread: {e}")
            return spread
    
    def get_asset_info(self, standard_name: str) -> Optional[AssetMapping]:
        """Get comprehensive asset information"""
        return self.asset_mappings.get(standard_name)
    
    def get_assets_by_type(self, asset_type: AssetType) -> List[str]:
        """Get all assets of a specific type"""
        return [
            name for name, mapping in self.asset_mappings.items()
            if mapping.asset_type == asset_type
        ]
    
    def get_assets_by_broker(self, broker: str) -> List[str]:
        """Get all assets available on a specific broker"""
        available_assets = []
        
        for standard_name, mapping in self.asset_mappings.items():
            if broker.lower() == 'deriv' and mapping.deriv_symbol:
                available_assets.append(standard_name)
            elif broker.lower() == 'mt5' and mapping.mt5_symbol:
                available_assets.append(standard_name)
        
        return available_assets
    
    def get_compatible_assets(self, brokers: List[str]) -> List[str]:
        """Get assets available on all specified brokers"""
        if not brokers:
            return []
        
        compatible_assets = []
        
        for standard_name, mapping in self.asset_mappings.items():
            available_on_all = True
            
            for broker in brokers:
                broker_lower = broker.lower()
                if broker_lower == 'deriv' and not mapping.deriv_symbol:
                    available_on_all = False
                    break
                elif broker_lower == 'mt5' and not mapping.mt5_symbol:
                    available_on_all = False
                    break
            
            if available_on_all:
                compatible_assets.append(standard_name)
        
        return compatible_assets
    
    def validate_order_parameters(self, order_params: Dict[str, Any], broker: str) -> Dict[str, Any]:
        """Validate and normalize order parameters"""
        try:
            standard_name = order_params.get('symbol', '')
            mapping = self.asset_mappings.get(standard_name)
            
            if not mapping:
                return {
                    'valid': False,
                    'error': f'Unknown asset: {standard_name}'
                }
            
            # Check if asset is available on broker
            broker_symbol = self.map_to_broker(standard_name, broker)
            if not broker_symbol:
                return {
                    'valid': False,
                    'error': f'Asset {standard_name} not available on {broker}'
                }
            
            # Validate volume
            volume = float(order_params.get('volume', 0))
            if volume < mapping.min_lot_size or volume > mapping.max_lot_size:
                return {
                    'valid': False,
                    'error': f'Volume {volume} outside range [{mapping.min_lot_size}, {mapping.max_lot_size}]'
                }
            
            # Validate volume step
            volume_step = mapping.lot_step
            if (volume / volume_step) % 1 != 0:
                return {
                    'valid': False,
                    'error': f'Volume {volume} not a multiple of step {volume_step}'
                }
            
            # Normalize order parameters
            normalized_params = order_params.copy()
            normalized_params['symbol'] = broker_symbol
            normalized_params['volume'] = volume
            normalized_params['min_lot_size'] = mapping.min_lot_size
            normalized_params['max_lot_size'] = mapping.max_lot_size
            normalized_params['tick_size'] = mapping.tick_size
            normalized_params['contract_size'] = mapping.contract_size
            
            return {
                'valid': True,
                'normalized_params': normalized_params,
                'asset_info': mapping
            }
            
        except Exception as e:
            self.logger.error(f"Error validating order parameters: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def get_trading_hours(self, standard_name: str) -> Dict[str, str]:
        """Get trading hours for an asset"""
        mapping = self.asset_mappings.get(standard_name)
        return mapping.trading_hours if mapping else {}
    
    def is_market_open(self, standard_name: str) -> bool:
        """Check if market is open for an asset (simplified)"""
        # This is a simplified implementation
        # In production, you'd check actual market hours based on timezone
        import datetime
        
        now = datetime.datetime.now()
        weekday = now.weekday()  # 0 = Monday, 6 = Sunday
        hour = now.hour
        
        # Forex markets are open 24/5
        if weekday < 5:  # Monday to Friday
            return True
        
        return False
    
    def calculate_position_value(self, standard_name: str, volume: float, price: float) -> float:
        """Calculate position value in base currency"""
        try:
            mapping = self.asset_mappings.get(standard_name)
            if not mapping:
                return volume * price
            
            # Use contract size for calculation
            position_value = volume * price * mapping.contract_size
            
            return round(position_value, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating position value: {e}")
            return volume * price
    
    def get_asset_summary(self) -> Dict[str, Any]:
        """Get summary of all available assets"""
        try:
            summary = {
                'total_assets': len(self.asset_mappings),
                'assets_by_type': {},
                'assets_by_broker': {
                    'deriv': len(self.get_assets_by_broker('deriv')),
                    'mt5': len(self.get_assets_by_broker('mt5')),
                    'both': len(self.get_compatible_assets(['deriv', 'mt5']))
                },
                'asset_types': list(AssetType),
                'last_updated': datetime.datetime.now().isoformat()
            }
            
            # Count assets by type
            for asset_type in AssetType:
                summary['assets_by_type'][asset_type.value] = len(self.get_assets_by_type(asset_type))
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting asset summary: {e}")
            return {}

# Utility functions
def create_asset_mapper() -> AssetMapper:
    """Create and return asset mapper instance"""
    return AssetMapper()

def map_asset_to_broker(standard_name: str, broker: str) -> Optional[str]:
    """Convenience function to map asset to broker"""
    mapper = AssetMapper()
    return mapper.map_to_broker(standard_name, broker)

def normalize_price_data(price_data: Dict[str, Any], broker: str) -> NormalizedPrice:
    """Convenience function to normalize price data"""
    mapper = AssetMapper()
    return mapper.normalize_price(price_data, broker)

# Example usage
def test_asset_mapper():
    """Test asset mapper functionality"""
    mapper = AssetMapper()
    
    # Test mapping
    print("Testing asset mappings:")
    print(f"EUR/USD -> Deriv: {mapper.map_to_broker('EUR/USD', 'deriv')}")
    print(f"EUR/USD -> MT5: {mapper.map_to_broker('EUR/USD', 'mt5')}")
    
    # Test reverse mapping
    print(f"frxEURUSD -> Standard: {mapper.map_from_broker('frxEURUSD', 'deriv')}")
    print(f"EURUSD -> Standard: {mapper.map_from_broker('EURUSD', 'mt5')}")
    
    # Test compatible assets
    compatible = mapper.get_compatible_assets(['deriv', 'mt5'])
    print(f"Compatible assets: {len(compatible)}")
    
    # Test asset summary
    summary = mapper.get_asset_summary()
    print(f"Asset summary: {summary}")

if __name__ == "__main__":
    test_asset_mapper()
