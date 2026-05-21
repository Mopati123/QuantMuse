#!/usr/bin/env python3
"""
Unified Risk Manager for QuantMuse
Cross-platform risk management across Deriv and MT5
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np

from .deriv_broker import DerivBroker
from .mt5_broker import MT5Broker

class RiskLevel(Enum):
    """Risk severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    """Risk alert types"""
    POSITION_LIMIT = "position_limit"
    EXPOSURE_LIMIT = "exposure_limit"
    CORRELATION_RISK = "correlation_risk"
    MARGIN_CALL = "margin_call"
    DRAWDOWN_LIMIT = "drawdown_limit"
    VOLATILITY_SPIKE = "volatility_spike"

@dataclass
class RiskLimit:
    """Risk limit configuration"""
    name: str
    limit_type: str
    max_value: float
    current_value: float
    alert_threshold: float
    action_threshold: float
    enabled: bool = True
    last_updated: datetime = datetime.now()

@dataclass
class RiskAlert:
    """Risk alert information"""
    alert_type: AlertType
    severity: RiskLevel
    message: str
    broker: str
    asset: str
    current_value: float
    limit_value: float
    timestamp: datetime
    resolved: bool = False
    action_taken: Optional[str] = None

@dataclass
class PortfolioRisk:
    """Portfolio risk metrics"""
    total_exposure: float
    total_positions: int
    correlated_exposure: float
    sector_exposure: Dict[str, float]
    currency_exposure: Dict[str, float]
    var_95: float  # Value at Risk 95%
    max_drawdown: float
    sharpe_ratio: float
    last_updated: datetime

class UnifiedRiskManager:
    """Unified risk management across all brokers"""
    
    def __init__(self, risk_config: Dict[str, Any]):
        self.risk_config = risk_config
        self.brokers = {}
        self.risk_limits = {}
        self.active_alerts = []
        self.alert_history = []
        self.portfolio_risk = PortfolioRisk(
            total_exposure=0.0,
            total_positions=0,
            correlated_exposure=0.0,
            sector_exposure={},
            currency_exposure={},
            var_95=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            last_updated=datetime.now()
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize risk limits
        self._initialize_risk_limits()
        
        # Asset correlation matrix (simplified)
        self.asset_correlations = {
            'EUR/USD': {'GBP/USD': 0.7, 'AUD/USD': 0.6, 'USD/CHF': -0.8},
            'GBP/USD': {'EUR/USD': 0.7, 'EUR/GBP': 0.8, 'USD/JPY': 0.5},
            'USD/JPY': {'GBP/USD': 0.5, 'EUR/JPY': 0.8, 'USD/CHF': 0.4},
            'Gold': {'Silver': 0.8, 'USD/CHF': 0.6, 'EUR/USD': 0.3},
            'Oil': {'Natural Gas': 0.7, 'USD/CAD': 0.6}
        }
        
        # Asset sector mapping
        self.asset_sectors = {
            'EUR/USD': 'forex',
            'GBP/USD': 'forex',
            'USD/JPY': 'forex',
            'AUD/USD': 'forex',
            'Gold': 'commodities',
            'Silver': 'commodities',
            'Oil': 'commodities',
            'Natural Gas': 'commodities',
            'US 30': 'indices',
            'US 500': 'indices',
            'US Tech 100': 'indices'
        }
        
        # Asset currency mapping
        self.asset_currencies = {
            'EUR/USD': 'USD',
            'GBP/USD': 'USD',
            'USD/JPY': 'USD',
            'AUD/USD': 'USD',
            'Gold': 'USD',
            'Silver': 'USD',
            'Oil': 'USD',
            'Natural Gas': 'USD',
            'US 30': 'USD',
            'US 500': 'USD',
            'US Tech 100': 'USD'
        }
    
    def add_broker(self, name: str, broker_instance: Any) -> bool:
        """Add broker to risk management system"""
        try:
            self.brokers[name] = broker_instance
            self.logger.info(f"Added broker to risk management: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add broker {name}: {e}")
            return False
    
    async def check_order_risk(self, order_request: Dict[str, Any], broker_name: str) -> Dict[str, Any]:
        """Check if order meets unified risk criteria"""
        try:
            self.logger.info(f"Checking order risk for {broker_name}: {order_request}")
            
            risk_checks = {
                'passed': True,
                'warnings': [],
                'errors': [],
                'risk_score': 0.0,
                'recommendations': []
            }
            
            # Get current portfolio state
            await self._update_portfolio_risk()
            
            # Check position limits
            position_check = await self._check_position_limits(order_request, broker_name)
            if not position_check['passed']:
                risk_checks['passed'] = False
                risk_checks['errors'].extend(position_check['errors'])
            else:
                risk_checks['warnings'].extend(position_check['warnings'])
            
            # Check exposure limits
            exposure_check = self._check_exposure_limits(order_request, broker_name)
            if not exposure_check['passed']:
                risk_checks['passed'] = False
                risk_checks['errors'].extend(exposure_check['errors'])
            else:
                risk_checks['warnings'].extend(exposure_check['warnings'])
            
            # Check correlation risk
            correlation_check = await self._check_correlation_risk(order_request, broker_name)
            if not correlation_check['passed']:
                risk_checks['passed'] = False
                risk_checks['errors'].extend(correlation_check['errors'])
            else:
                risk_checks['warnings'].extend(correlation_check['warnings'])
            
            # Check sector concentration
            sector_check = self._check_sector_concentration(order_request, broker_name)
            if not sector_check['passed']:
                risk_checks['passed'] = False
                risk_checks['errors'].extend(sector_check['errors'])
            else:
                risk_checks['warnings'].extend(sector_check['warnings'])
            
            # Calculate overall risk score
            risk_checks['risk_score'] = self._calculate_risk_score(risk_checks)
            
            # Generate recommendations
            risk_checks['recommendations'] = self._generate_recommendations(risk_checks)
            
            return risk_checks
            
        except Exception as e:
            self.logger.error(f"Error checking order risk: {e}")
            return {
                'passed': False,
                'errors': [f"Risk check failed: {e}"],
                'risk_score': 1.0
            }
    
    async def _update_portfolio_risk(self):
        """Update portfolio risk metrics"""
        try:
            total_exposure = 0.0
            total_positions = 0
            sector_exposure = {}
            currency_exposure = {}
            all_positions = []
            
            # Get positions from all brokers
            for broker_name, broker in self.brokers.items():
                try:
                    if broker_name == 'deriv':
                        positions = await broker.get_positions()
                    else:  # MT5
                        positions = broker.get_positions()
                    
                    for position in positions:
                        # Calculate position value
                        position_value = self._calculate_position_value(position, broker_name)
                        total_exposure += abs(position_value)
                        total_positions += 1
                        all_positions.append(position)
                        
                        # Update sector exposure
                        symbol = position.get('symbol', '')
                        sector = self.asset_sectors.get(symbol, 'other')
                        sector_exposure[sector] = sector_exposure.get(sector, 0) + abs(position_value)
                        
                        # Update currency exposure
                        currency = self.asset_currencies.get(symbol, 'USD')
                        currency_exposure[currency] = currency_exposure.get(currency, 0) + abs(position_value)
                
                except Exception as e:
                    self.logger.error(f"Error getting positions from {broker_name}: {e}")
            
            # Calculate correlated exposure
            correlated_exposure = self._calculate_correlated_exposure(all_positions)
            
            # Calculate VaR (simplified)
            var_95 = self._calculate_var(all_positions)
            
            # Calculate max drawdown (simplified)
            max_drawdown = self._calculate_max_drawdown(all_positions)
            
            # Calculate Sharpe ratio (simplified)
            sharpe_ratio = self._calculate_sharpe_ratio(all_positions)
            
            # Update portfolio risk
            self.portfolio_risk = PortfolioRisk(
                total_exposure=total_exposure,
                total_positions=total_positions,
                correlated_exposure=correlated_exposure,
                sector_exposure=sector_exposure,
                currency_exposure=currency_exposure,
                var_95=var_95,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error updating portfolio risk: {e}")
    
    def _calculate_position_value(self, position: Dict[str, Any], broker_name: str) -> float:
        """Calculate position value"""
        try:
            if broker_name == 'deriv':
                # For Deriv binary options
                return position.get('payout', 0)
            else:  # MT5
                # For MT5 positions
                volume = position.get('volume', 0)
                current_price = position.get('current_price', 0)
                return volume * current_price
                
        except Exception as e:
            self.logger.error(f"Error calculating position value: {e}")
            return 0.0
    
    def _calculate_correlated_exposure(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate correlated exposure"""
        try:
            correlated_exposure = 0.0
            processed_symbols = set()
            
            for position in positions:
                symbol = position.get('symbol', '')
                if symbol in processed_symbols:
                    continue
                
                processed_symbols.add(symbol)
                
                # Find correlated positions
                for other_position in positions:
                    other_symbol = other_position.get('symbol', '')
                    if other_symbol == symbol:
                        continue
                    
                    # Check correlation
                    correlation = self._get_correlation(symbol, other_symbol)
                    if correlation > 0.7:  # High correlation threshold
                        position_value = self._calculate_position_value(position, 'mt5')  # Simplified
                        other_value = self._calculate_position_value(other_position, 'mt5')
                        correlated_exposure += (position_value + other_value) * correlation
            
            return correlated_exposure
            
        except Exception as e:
            self.logger.error(f"Error calculating correlated exposure: {e}")
            return 0.0
    
    def _get_correlation(self, symbol1: str, symbol2: str) -> float:
        """Get correlation between two symbols"""
        try:
            return self.asset_correlations.get(symbol1, {}).get(symbol2, 0.0)
        except:
            return 0.0
    
    def _calculate_var(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate Value at Risk (simplified)"""
        try:
            if not positions:
                return 0.0
            
            # Simplified VaR calculation
            # In production, you'd use historical returns and statistical methods
            total_value = sum(self._calculate_position_value(pos, 'mt5') for pos in positions)
            return total_value * 0.05  # Assume 5% VaR
            
        except Exception as e:
            self.logger.error(f"Error calculating VaR: {e}")
            return 0.0
    
    def _calculate_max_drawdown(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate maximum drawdown (simplified)"""
        try:
            # This is a simplified implementation
            # In production, you'd use historical portfolio values
            return 0.02  # Assume 2% max drawdown
            
        except Exception as e:
            self.logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
    
    def _calculate_sharpe_ratio(self, positions: List[Dict[str, Any]]) -> float:
        """Calculate Sharpe ratio (simplified)"""
        try:
            # This is a simplified implementation
            # In production, you'd use historical returns
            return 1.5  # Assume 1.5 Sharpe ratio
            
        except Exception as e:
            self.logger.error(f"Error calculating Sharpe ratio: {e}")
            return 0.0
    
    async def _check_position_limits(self, order_request: Dict[str, Any], broker_name: str) -> Dict[str, Any]:
        """Check position limits"""
        try:
            result = {'passed': True, 'warnings': [], 'errors': []}
            
            # Get current positions for this broker
            broker = self.brokers[broker_name]
            
            if broker_name == 'deriv':
                positions = await broker.get_positions()
            else:  # MT5
                positions = broker.get_positions()
            
            current_positions = len(positions)
            max_positions = self.risk_limits['max_positions_per_broker'].max_value
            
            if current_positions >= max_positions:
                result['passed'] = False
                result['errors'].append(f"Maximum positions ({max_positions}) reached for {broker_name}")
            elif current_positions >= max_positions * 0.8:
                result['warnings'].append(f"Approaching position limit ({current_positions}/{max_positions})")
            
            # Check position size
            order_volume = order_request.get('volume', 0)
            max_position_size = self.risk_limits['max_position_size'].max_value
            
            if order_volume > max_position_size:
                result['passed'] = False
                result['errors'].append(f"Order size ({order_volume}) exceeds maximum ({max_position_size})")
            elif order_volume > max_position_size * 0.8:
                result['warnings'].append(f"Large order size ({order_volume}) approaching limit ({max_position_size})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking position limits: {e}")
            return {'passed': False, 'errors': [f"Position limit check failed: {e}"]}
    
    def _check_exposure_limits(self, order_request: Dict[str, Any], broker_name: str) -> Dict[str, Any]:
        """Check exposure limits"""
        try:
            result = {'passed': True, 'warnings': [], 'errors': []}
            
            # Calculate new total exposure
            order_value = order_request.get('volume', 0) * order_request.get('price', 1)
            new_total_exposure = self.portfolio_risk.total_exposure + order_value
            
            max_total_exposure = self.risk_limits['max_total_exposure'].max_value
            
            if new_total_exposure > max_total_exposure:
                result['passed'] = False
                result['errors'].append(f"Total exposure ({new_total_exposure}) exceeds maximum ({max_total_exposure})")
            elif new_total_exposure > max_total_exposure * 0.8:
                result['warnings'].append(f"High total exposure ({new_total_exposure}/{max_total_exposure})")
            
            # Check broker-specific exposure
            max_broker_exposure = self.risk_limits['max_broker_exposure'].max_value
            current_broker_exposure = self._get_broker_exposure(broker_name)
            new_broker_exposure = current_broker_exposure + order_value
            
            if new_broker_exposure > max_broker_exposure:
                result['passed'] = False
                result['errors'].append(f"Broker exposure ({new_broker_exposure}) exceeds maximum ({max_broker_exposure})")
            elif new_broker_exposure > max_broker_exposure * 0.8:
                result['warnings'].append(f"High broker exposure ({new_broker_exposure}/{max_broker_exposure})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking exposure limits: {e}")
            return {'passed': False, 'errors': [f"Exposure limit check failed: {e}"]}
    
    async def _check_correlation_risk(self, order_request: Dict[str, Any], broker_name: str) -> Dict[str, Any]:
        """Check correlation risk"""
        try:
            result = {'passed': True, 'warnings': [], 'errors': []}
            
            order_symbol = order_request.get('symbol', '')
            
            # Get current positions
            all_positions = []
            for broker in self.brokers.values():
                try:
                    if isinstance(broker, DerivBroker):
                        positions = await broker.get_positions()
                    else:  # MT5
                        positions = broker.get_positions()
                    all_positions.extend(positions)
                except:
                    continue
            
            # Check correlations
            correlated_exposure = 0.0
            for position in all_positions:
                position_symbol = position.get('symbol', '')
                correlation = self._get_correlation(order_symbol, position_symbol)
                
                if correlation > 0.7:
                    position_value = self._calculate_position_value(position, 'mt5')
                    correlated_exposure += position_value * correlation
            
            max_correlated_exposure = self.risk_limits['max_correlated_exposure'].max_value
            
            if correlated_exposure > max_correlated_exposure:
                result['passed'] = False
                result['errors'].append(f"Correlated exposure ({correlated_exposure}) exceeds maximum ({max_correlated_exposure})")
            elif correlated_exposure > max_correlated_exposure * 0.8:
                result['warnings'].append(f"High correlated exposure ({correlated_exposure}/{max_correlated_exposure})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking correlation risk: {e}")
            return {'passed': False, 'errors': [f"Correlation risk check failed: {e}"]}
    
    def _check_sector_concentration(self, order_request: Dict[str, Any], broker_name: str) -> Dict[str, Any]:
        """Check sector concentration"""
        try:
            result = {'passed': True, 'warnings': [], 'errors': []}
            
            order_symbol = order_request.get('symbol', '')
            order_sector = self.asset_sectors.get(order_symbol, 'other')
            order_value = order_request.get('volume', 0) * order_request.get('price', 1)
            
            # Calculate new sector exposure
            current_sector_exposure = self.portfolio_risk.sector_exposure.get(order_sector, 0)
            new_sector_exposure = current_sector_exposure + order_value
            
            max_sector_exposure = self.risk_limits['max_sector_exposure'].max_value
            
            if new_sector_exposure > max_sector_exposure:
                result['passed'] = False
                result['errors'].append(f"Sector exposure ({new_sector_exposure}) exceeds maximum ({max_sector_exposure})")
            elif new_sector_exposure > max_sector_exposure * 0.8:
                result['warnings'].append(f"High sector exposure ({new_sector_exposure}/{max_sector_exposure})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking sector concentration: {e}")
            return {'passed': False, 'errors': [f"Sector concentration check failed: {e}"]}
    
    def _calculate_risk_score(self, risk_checks: Dict[str, Any]) -> float:
        """Calculate overall risk score"""
        try:
            risk_score = 0.0
            
            # Base score from warnings and errors
            risk_score += len(risk_checks['errors']) * 0.5
            risk_score += len(risk_checks['warnings']) * 0.2
            
            # Add portfolio risk factors
            risk_score += self.portfolio_risk.total_exposure / 1000000  # Normalize by $1M
            risk_score += self.portfolio_risk.correlated_exposure / 500000  # Normalize by $500K
            risk_score += self.portfolio_risk.max_drawdown * 2  # Weight drawdown
            
            # Cap at 1.0
            return min(risk_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating risk score: {e}")
            return 1.0
    
    def _generate_recommendations(self, risk_checks: Dict[str, Any]) -> List[str]:
        """Generate risk recommendations"""
        try:
            recommendations = []
            
            if risk_checks['risk_score'] > 0.7:
                recommendations.append("Consider reducing position size")
            
            if len(risk_checks['warnings']) > 2:
                recommendations.append("Monitor risk levels closely")
            
            if self.portfolio_risk.total_exposure > 800000:
                recommendations.append("Consider taking some profits")
            
            if self.portfolio_risk.correlated_exposure > 300000:
                recommendations.append("Diversify across uncorrelated assets")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _get_broker_exposure(self, broker_name: str) -> float:
        """Get current exposure for a broker"""
        try:
            broker = self.brokers[broker_name]
            
            if isinstance(broker, DerivBroker):
                positions = asyncio.create_task(broker.get_positions())
            else:  # MT5
                positions = broker.get_positions()
            
            exposure = 0.0
            for position in positions:
                exposure += self._calculate_position_value(position, broker_name)
            
            return exposure
            
        except Exception as e:
            self.logger.error(f"Error getting broker exposure: {e}")
            return 0.0
    
    def _initialize_risk_limits(self):
        """Initialize default risk limits"""
        self.risk_limits = {
            'max_total_exposure': RiskLimit(
                name='max_total_exposure',
                limit_type='total_exposure',
                max_value=self.risk_config.get('unified_limits', {}).get('max_total_exposure', 200000),
                current_value=0.0,
                alert_threshold=0.8,
                action_threshold=1.0
            ),
            'max_broker_exposure': RiskLimit(
                name='max_broker_exposure',
                limit_type='broker_exposure',
                max_value=self.risk_config.get('unified_limits', {}).get('max_per_broker', 100000),
                current_value=0.0,
                alert_threshold=0.8,
                action_threshold=1.0
            ),
            'max_position_size': RiskLimit(
                name='max_position_size',
                limit_type='position_size',
                max_value=self.risk_config.get('unified_limits', {}).get('max_per_asset', 50000),
                current_value=0.0,
                alert_threshold=0.8,
                action_threshold=1.0
            ),
            'max_positions_per_broker': RiskLimit(
                name='max_positions_per_broker',
                limit_type='position_count',
                max_value=20,
                current_value=0.0,
                alert_threshold=0.8,
                action_threshold=1.0
            ),
            'max_correlated_exposure': RiskLimit(
                name='max_correlated_exposure',
                limit_type='correlated_exposure',
                max_value=self.risk_config.get('correlation_limits', {}).get('max_correlated_exposure', 150000),
                current_value=0.0,
                alert_threshold=0.8,
                action_threshold=1.0
            ),
            'max_sector_exposure': RiskLimit(
                name='max_sector_exposure',
                limit_type='sector_exposure',
                max_value=100000,
                current_value=0.0,
                alert_threshold=0.8,
                action_threshold=1.0
            )
        }
    
    async def enforce_risk_limits(self) -> List[Dict[str, Any]]:
        """Enforce risk limits across all positions"""
        try:
            enforcement_actions = []
            
            # Update portfolio risk
            await self._update_portfolio_risk()
            
            # Check for limit violations
            for limit_name, limit in self.risk_limits.items():
                if limit.current_value > limit.action_threshold:
                    # Take enforcement action
                    action = await self._take_enforcement_action(limit_name, limit)
                    enforcement_actions.append(action)
            
            return enforcement_actions
            
        except Exception as e:
            self.logger.error(f"Error enforcing risk limits: {e}")
            return []
    
    async def _take_enforcement_action(self, limit_name: str, limit: RiskLimit) -> Dict[str, Any]:
        """Take enforcement action for limit violation"""
        try:
            action = {
                'limit_name': limit_name,
                'action_taken': 'none',
                'timestamp': datetime.now(),
                'success': False
            }
            
            if limit_name == 'max_total_exposure':
                # Close most risky positions
                action = await self._close_risky_positions()
            elif limit_name == 'max_correlated_exposure':
                # Close correlated positions
                action = await self._close_correlated_positions()
            elif limit_name == 'max_position_size':
                # Reduce position size
                action = await self._reduce_large_positions()
            
            return action
            
        except Exception as e:
            self.logger.error(f"Error taking enforcement action: {e}")
            return {'action_taken': 'error', 'error': str(e)}
    
    async def _close_risky_positions(self) -> Dict[str, Any]:
        """Close most risky positions"""
        try:
            # This is a simplified implementation
            # In production, you'd identify and close the riskiest positions
            return {
                'action_taken': 'close_risky_positions',
                'positions_closed': 0,
                'success': True
            }
        except Exception as e:
            return {'action_taken': 'error', 'error': str(e)}
    
    async def _close_correlated_positions(self) -> Dict[str, Any]:
        """Close correlated positions"""
        try:
            # This is a simplified implementation
            return {
                'action_taken': 'close_correlated_positions',
                'positions_closed': 0,
                'success': True
            }
        except Exception as e:
            return {'action_taken': 'error', 'error': str(e)}
    
    async def _reduce_large_positions(self) -> Dict[str, Any]:
        """Reduce large positions"""
        try:
            # This is a simplified implementation
            return {
                'action_taken': 'reduce_large_positions',
                'positions_reduced': 0,
                'success': True
            }
        except Exception as e:
            return {'action_taken': 'error', 'error': str(e)}
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get comprehensive risk summary"""
        try:
            return {
                'portfolio_risk': {
                    'total_exposure': self.portfolio_risk.total_exposure,
                    'total_positions': self.portfolio_risk.total_positions,
                    'correlated_exposure': self.portfolio_risk.correlated_exposure,
                    'sector_exposure': self.portfolio_risk.sector_exposure,
                    'currency_exposure': self.portfolio_risk.currency_exposure,
                    'var_95': self.portfolio_risk.var_95,
                    'max_drawdown': self.portfolio_risk.max_drawdown,
                    'sharpe_ratio': self.portfolio_risk.sharpe_ratio,
                    'last_updated': self.portfolio_risk.last_updated.isoformat()
                },
                'risk_limits': {
                    name: {
                        'current_value': limit.current_value,
                        'max_value': limit.max_value,
                        'utilization': limit.current_value / limit.max_value,
                        'alert_threshold': limit.alert_threshold,
                        'enabled': limit.enabled
                    }
                    for name, limit in self.risk_limits.items()
                },
                'active_alerts': len(self.active_alerts),
                'alert_history': len(self.alert_history),
                'risk_score': self._calculate_overall_risk_score(),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting risk summary: {e}")
            return {}
    
    def _calculate_overall_risk_score(self) -> float:
        """Calculate overall risk score"""
        try:
            # Combine various risk factors
            exposure_score = min(self.portfolio_risk.total_exposure / 200000, 1.0)
            correlation_score = min(self.portfolio_risk.correlated_exposure / 150000, 1.0)
            drawdown_score = min(self.portfolio_risk.max_drawdown / 0.1, 1.0)
            
            # Weighted average
            overall_score = (exposure_score * 0.4 + correlation_score * 0.3 + drawdown_score * 0.3)
            
            return overall_score
            
        except Exception as e:
            self.logger.error(f"Error calculating overall risk score: {e}")
            return 1.0
    
    def update_risk_limits(self, new_limits: Dict[str, Any]):
        """Update risk limits"""
        try:
            for limit_name, new_limit in new_limits.items():
                if limit_name in self.risk_limits:
                    self.risk_limits[limit_name].max_value = new_limit
                    self.risk_limits[limit_name].last_updated = datetime.now()
                    self.logger.info(f"Updated risk limit {limit_name} to {new_limit}")
            
        except Exception as e:
            self.logger.error(f"Error updating risk limits: {e}")

# Utility functions
def create_risk_config() -> Dict[str, Any]:
    """Create default risk configuration"""
    return {
        'unified_limits': {
            'max_total_exposure': 200000,  # $200K
            'max_per_broker': 100000,      # $100K per broker
            'max_per_asset': 50000,        # $50K per asset
        },
        'correlation_limits': {
            'max_correlated_exposure': 150000,  # $150K
            'correlation_threshold': 0.7
        },
        'position_limits': {
            'max_positions_per_broker': 20,
            'max_open_positions': 50
        },
        'alert_thresholds': {
            'risk_score_warning': 0.6,
            'risk_score_critical': 0.8,
            'drawdown_warning': 0.05,
            'drawdown_critical': 0.10
        }
    }

# Example usage
async def test_unified_risk_manager():
    """Test unified risk manager"""
    # Create risk manager
    risk_config = create_risk_config()
    risk_manager = UnifiedRiskManager(risk_config)
    
    # Add brokers (mock instances for testing)
    # deriv_broker = DerivBroker("your_api_token", demo_mode=True)
    # mt5_broker = MT5Broker(12345678, "password", "demo_server", demo_mode=True)
    
    # risk_manager.add_broker("deriv", deriv_broker)
    # risk_manager.add_broker("mt5", mt5_broker)
    
    # Test order risk check
    order_request = {
        'symbol': 'EUR/USD',
        'volume': 0.1,
        'price': 1.1000,
        'type': 'BUY'
    }
    
    # risk_check = await risk_manager.check_order_risk(order_request, 'deriv')
    # print(f"Risk Check: {risk_check}")
    
    # Get risk summary
    risk_summary = risk_manager.get_risk_summary()
    print(f"Risk Summary: {risk_summary}")

if __name__ == "__main__":
    asyncio.run(test_unified_risk_manager())
