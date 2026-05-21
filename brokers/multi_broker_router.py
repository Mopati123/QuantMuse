#!/usr/bin/env python3
"""
Multi-Broker Order Router for QuantMuse
Intelligent order routing across Deriv and MT5
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np

from .deriv_broker import DerivBroker
from .mt5_broker import MT5Broker

class RoutingStrategy(Enum):
    """Order routing strategies"""
    COST_OPTIMIZED = "cost_optimized"
    LIQUIDITY_BASED = "liquidity_based"
    RISK_BALANCED = "risk_balanced"
    PERFORMANCE_BASED = "performance_based"
    ROUND_ROBIN = "round_robin"

@dataclass
class BrokerPerformance:
    """Broker performance metrics"""
    name: str
    success_rate: float
    avg_execution_time: float
    avg_spread: float
    total_orders: int
    recent_orders: List[Dict[str, Any]]
    last_updated: datetime

@dataclass
class OrderRequest:
    """Standardized order request"""
    symbol: str
    asset_type: str
    order_type: str
    volume: float
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy: str = RoutingStrategy.COST_OPTIMIZED
    split_allowed: bool = True
    max_brokers: int = 2
    urgency: str = "normal"  # normal, high, low
    created_at: datetime = datetime.now()

@dataclass
class BrokerOrder:
    """Order routed to specific broker"""
    broker_name: str
    original_request: OrderRequest
    modified_request: Dict[str, Any]
    status: str  # pending, submitted, filled, failed
    order_id: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    filled_price: Optional[float] = None
    filled_volume: Optional[float] = None
    created_at: datetime = datetime.now()

class MultiBrokerOrderRouter:
    """Intelligent order routing across multiple brokers"""
    
    def __init__(self):
        self.brokers = {}
        self.performance_tracker = {}
        self.routing_rules = {}
        self.active_orders = {}
        self.order_history = []
        self.logger = logging.getLogger(__name__)
        
        # Default routing configuration
        self.config = {
            'strategy': RoutingStrategy.COST_OPTIMIZED,
            'split_orders': True,
            'max_brokers_per_order': 2,
            'min_order_size': 0.01,
            'performance_window': 100,  # Number of recent orders to track
            'cost_threshold': 0.001,  # Cost difference threshold for routing
            'liquidity_threshold': 100000,  # Minimum liquidity for large orders
            'risk_threshold': 0.15  # Risk threshold for balanced routing
        }
        
        # Asset compatibility matrix
        self.asset_compatibility = {
            'deriv': {
                'forex': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CHF'],
                'commodities': ['Gold', 'Silver', 'Oil', 'Natural Gas'],
                'indices': ['US 30', 'US 500', 'US Tech 100'],
                'binary_options': ['Rise/Fall', 'Higher/Lower', 'Touch/No Touch']
            },
            'mt5': {
                'forex': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CHF', 'EUR/GBP', 'EUR/JPY'],
                'commodities': ['Gold', 'Silver', 'Oil', 'Brent Oil', 'Natural Gas'],
                'indices': ['US 30', 'US 500', 'US Tech 100', 'Germany 40', 'UK 100'],
                'stocks': ['Apple', 'Microsoft', 'Google', 'Amazon', 'Tesla']
            }
        }
        
        # Initialize performance tracking
        self._initialize_performance_tracking()
    
    def add_broker(self, name: str, broker_instance: Any) -> bool:
        """Add broker to routing system"""
        try:
            self.brokers[name] = broker_instance
            
            # Initialize performance tracking for new broker
            self.performance_tracker[name] = BrokerPerformance(
                name=name,
                success_rate=1.0,
                avg_execution_time=0.1,
                avg_spread=0.0001,
                total_orders=0,
                recent_orders=[],
                last_updated=datetime.now()
            )
            
            self.logger.info(f"Added broker: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add broker {name}: {e}")
            return False
    
    def remove_broker(self, name: str) -> bool:
        """Remove broker from routing system"""
        try:
            if name in self.brokers:
                del self.brokers[name]
                del self.performance_tracker[name]
                self.logger.info(f"Removed broker: {name}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove broker {name}: {e}")
            return False
    
    async def route_order(self, order_request: OrderRequest) -> List[BrokerOrder]:
        """Route order to best broker(s)"""
        try:
            self.logger.info(f"Routing order: {order_request.symbol} {order_request.volume}")
            
            # Get compatible brokers
            compatible_brokers = self._get_compatible_brokers(order_request)
            
            if not compatible_brokers:
                raise ValueError(f"No compatible brokers for {order_request.symbol}")
            
            # Select best broker(s) based on strategy
            selected_brokers = await self._select_best_brokers(order_request, compatible_brokers)
            
            # Create broker orders
            broker_orders = []
            
            if len(selected_brokers) == 1 or not order_request.split_allowed:
                # Single broker execution
                broker_name = selected_brokers[0]
                broker_order = await self._create_broker_order(broker_name, order_request)
                broker_orders.append(broker_order)
                
            else:
                # Split order across multiple brokers
                broker_orders = await self._split_order(order_request, selected_brokers)
            
            # Execute orders
            for broker_order in broker_orders:
                await self._execute_broker_order(broker_order)
            
            # Track order
            self.active_orders[order_request.created_at] = broker_orders
            
            return broker_orders
            
        except Exception as e:
            self.logger.error(f"Error routing order: {e}")
            return []
    
    async def _create_broker_order(self, broker_name: str, order_request: OrderRequest) -> BrokerOrder:
        """Create order for specific broker"""
        try:
            # Map order to broker format
            broker_format = self._map_order_to_broker(broker_name, order_request)
            
            broker_order = BrokerOrder(
                broker_name=broker_name,
                original_request=order_request,
                modified_request=broker_format,
                status='pending'
            )
            
            return broker_order
            
        except Exception as e:
            self.logger.error(f"Error creating broker order for {broker_name}: {e}")
            raise
    
    async def _execute_broker_order(self, broker_order: BrokerOrder) -> bool:
        """Execute order on specific broker"""
        try:
            start_time = datetime.now()
            broker = self.brokers[broker_order.broker_name]
            
            # Execute order based on broker type
            if broker_order.broker_name == 'deriv':
                result = await broker.place_order(broker_order.modified_request)
            else:  # MT5
                result = broker.place_order(broker_order.modified_request)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update broker order
            if result['success']:
                broker_order.status = 'filled'
                broker_order.order_id = result.get('order_id')
                broker_order.filled_price = result.get('price')
                broker_order.filled_volume = broker_order.modified_request.get('volume')
                broker_order.execution_time = execution_time
                
                # Update performance tracking
                self._update_performance_tracking(broker_order.broker_name, True, execution_time)
                
            else:
                broker_order.status = 'failed'
                broker_order.error = result.get('error')
                
                # Update performance tracking
                self._update_performance_tracking(broker_order.broker_name, False, execution_time)
            
            return result['success']
            
        except Exception as e:
            self.logger.error(f"Error executing broker order: {e}")
            broker_order.status = 'failed'
            broker_order.error = str(e)
            return False
    
    async def _split_order(self, order_request: OrderRequest, brokers: List[str]) -> List[BrokerOrder]:
        """Split order across multiple brokers"""
        try:
            broker_orders = []
            
            # Calculate split ratios based on broker performance
            split_ratios = self._calculate_split_ratios(brokers)
            
            for i, broker_name in enumerate(brokers):
                # Calculate volume for this broker
                volume_ratio = split_ratios[i]
                broker_volume = order_request.volume * volume_ratio
                
                # Create modified order request
                modified_request = OrderRequest(
                    symbol=order_request.symbol,
                    asset_type=order_request.asset_type,
                    order_type=order_request.order_type,
                    volume=broker_volume,
                    price=order_request.price,
                    stop_loss=order_request.stop_loss,
                    take_profit=order_request.take_profit,
                    strategy=order_request.strategy,
                    split_allowed=False,  # Prevent further splitting
                    max_brokers=1,
                    urgency=order_request.urgency,
                    created_at=order_request.created_at
                )
                
                # Create broker order
                broker_order = await self._create_broker_order(broker_name, modified_request)
                broker_orders.append(broker_order)
            
            return broker_orders
            
        except Exception as e:
            self.logger.error(f"Error splitting order: {e}")
            return []
    
    def _get_compatible_brokers(self, order_request: OrderRequest) -> List[str]:
        """Get brokers that support the requested asset"""
        try:
            compatible_brokers = []
            
            for broker_name, broker in self.brokers.items():
                if self._is_asset_supported(broker_name, order_request.symbol, order_request.asset_type):
                    compatible_brokers.append(broker_name)
            
            return compatible_brokers
            
        except Exception as e:
            self.logger.error(f"Error getting compatible brokers: {e}")
            return []
    
    def _is_asset_supported(self, broker_name: str, symbol: str, asset_type: str) -> bool:
        """Check if broker supports the asset"""
        try:
            supported_assets = self.asset_compatibility.get(broker_name, {}).get(asset_type, [])
            return symbol in supported_assets
            
        except Exception as e:
            self.logger.error(f"Error checking asset support: {e}")
            return False
    
    async def _select_best_brokers(self, order_request: OrderRequest, compatible_brokers: List[str]) -> List[str]:
        """Select best broker(s) based on routing strategy"""
        try:
            strategy = order_request.strategy or self.config['strategy']
            
            if strategy == RoutingStrategy.COST_OPTIMIZED:
                return self._select_by_cost(compatible_brokers, order_request)
            elif strategy == RoutingStrategy.LIQUIDITY_BASED:
                return self._select_by_liquidity(compatible_brokers, order_request)
            elif strategy == RoutingStrategy.RISK_BALANCED:
                return await self._select_by_risk(compatible_brokers, order_request)
            elif strategy == RoutingStrategy.PERFORMANCE_BASED:
                return self._select_by_performance(compatible_brokers, order_request)
            elif strategy == RoutingStrategy.ROUND_ROBIN:
                return self._select_round_robin(compatible_brokers, order_request)
            else:
                return compatible_brokers[:1]  # Default to first broker
                
        except Exception as e:
            self.logger.error(f"Error selecting best brokers: {e}")
            return compatible_brokers[:1]
    
    def _select_by_cost(self, brokers: List[str], order_request: OrderRequest) -> List[str]:
        """Select broker with lowest cost"""
        try:
            broker_costs = {}
            
            for broker_name in brokers:
                broker = self.brokers[broker_name]
                
                # Get current spread/cost
                if broker_name == 'deriv':
                    # For Deriv, check binary options cost or spread
                    cost = self._get_deriv_cost(order_request)
                else:  # MT5
                    # For MT5, get current spread
                    cost = self._get_mt5_spread(order_request.symbol)
                
                broker_costs[broker_name] = cost
            
            # Sort by cost (lowest first)
            sorted_brokers = sorted(broker_costs.items(), key=lambda x: x[1])
            
            # Return top brokers
            max_brokers = min(order_request.max_brokers, len(sorted_brokers))
            return [broker for broker, cost in sorted_brokers[:max_brokers]]
            
        except Exception as e:
            self.logger.error(f"Error selecting by cost: {e}")
            return brokers[:1]
    
    def _select_by_performance(self, brokers: List[str], order_request: OrderRequest) -> List[str]:
        """Select broker with best performance"""
        try:
            broker_scores = {}
            
            for broker_name in brokers:
                performance = self.performance_tracker[broker_name]
                
                # Calculate performance score
                score = (performance.success_rate * 0.4 + 
                        (1 / performance.avg_execution_time) * 0.3 + 
                        (1 / performance.avg_spread) * 0.3)
                
                broker_scores[broker_name] = score
            
            # Sort by score (highest first)
            sorted_brokers = sorted(broker_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Return top brokers
            max_brokers = min(order_request.max_brokers, len(sorted_brokers))
            return [broker for broker, score in sorted_brokers[:max_brokers]]
            
        except Exception as e:
            self.logger.error(f"Error selecting by performance: {e}")
            return brokers[:1]
    
    def _select_by_liquidity(self, brokers: List[str], order_request: OrderRequest) -> List[str]:
        """Select broker with best liquidity for large orders"""
        try:
            if order_request.volume < self.config['liquidity_threshold']:
                # For small orders, use cost optimization
                return self._select_by_cost(brokers, order_request)
            
            # For large orders, prefer brokers with better liquidity
            # This is a simplified implementation
            # In production, you'd use actual liquidity data
            liquidity_scores = {
                'mt5': 0.8,  # MT5 generally has better liquidity for forex
                'deriv': 0.6   # Deriv is good for binary options
            }
            
            # Filter by compatible brokers
            filtered_scores = {k: v for k, v in liquidity_scores.items() if k in brokers}
            
            # Sort by liquidity score
            sorted_brokers = sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True)
            
            max_brokers = min(order_request.max_brokers, len(sorted_brokers))
            return [broker for broker, score in sorted_brokers[:max_brokers]]
            
        except Exception as e:
            self.logger.error(f"Error selecting by liquidity: {e}")
            return brokers[:1]
    
    async def _select_by_risk(self, brokers: List[str], order_request: OrderRequest) -> List[str]:
        """Select broker for balanced risk distribution"""
        try:
            # Calculate current risk exposure per broker
            broker_exposure = {}
            
            for broker_name in brokers:
                # Get current positions for this broker
                broker = self.brokers[broker_name]
                
                if broker_name == 'deriv':
                    positions = await broker.get_positions()
                else:  # MT5
                    positions = broker.get_positions()
                
                # Calculate exposure (simplified)
                exposure = sum(pos.get('volume', 0) for pos in positions)
                broker_exposure[broker_name] = exposure
            
            # Sort by exposure (lowest first)
            sorted_brokers = sorted(broker_exposure.items(), key=lambda x: x[1])
            
            max_brokers = min(order_request.max_brokers, len(sorted_brokers))
            return [broker for broker, exposure in sorted_brokers[:max_brokers]]
            
        except Exception as e:
            self.logger.error(f"Error selecting by risk: {e}")
            return brokers[:1]
    
    def _select_round_robin(self, brokers: List[str], order_request: OrderRequest) -> List[str]:
        """Select broker using round-robin"""
        try:
            # Simple round-robin implementation
            # In production, you'd maintain a proper round-robin counter
            import random
            selected = random.choice(brokers)
            return [selected]
            
        except Exception as e:
            self.logger.error(f"Error selecting round-robin: {e}")
            return brokers[:1]
    
    def _calculate_split_ratios(self, brokers: List[str]) -> List[float]:
        """Calculate order split ratios based on broker performance"""
        try:
            # Calculate performance weights
            weights = []
            
            for broker_name in brokers:
                performance = self.performance_tracker[broker_name]
                
                # Weight based on success rate and execution speed
                weight = performance.success_rate * (1 / max(performance.avg_execution_time, 0.01))
                weights.append(weight)
            
            # Normalize weights
            total_weight = sum(weights)
            if total_weight > 0:
                ratios = [w / total_weight for w in weights]
            else:
                ratios = [1.0 / len(brokers)] * len(brokers)
            
            return ratios
            
        except Exception as e:
            self.logger.error(f"Error calculating split ratios: {e}")
            return [1.0 / len(brokers)] * len(brokers)
    
    def _map_order_to_broker(self, broker_name: str, order_request: OrderRequest) -> Dict[str, Any]:
        """Map order to broker-specific format"""
        try:
            if broker_name == 'deriv':
                return self._map_to_deriv(order_request)
            else:  # MT5
                return self._map_to_mt5(order_request)
                
        except Exception as e:
            self.logger.error(f"Error mapping order to {broker_name}: {e}")
            raise
    
    def _map_to_deriv(self, order_request: OrderRequest) -> Dict[str, Any]:
        """Map order to Deriv format"""
        # Map symbol to Deriv format
        deriv_symbol = self._map_symbol_to_deriv(order_request.symbol, order_request.asset_type)
        
        # Create Deriv order
        deriv_order = {
            'symbol': deriv_symbol,
            'type': 'CALL' if order_request.order_type.upper() == 'BUY' else 'PUT',
            'amount': order_request.volume * 1000,  # Convert to Deriv amount
            'duration': 60,  # Default 60 seconds
            'duration_unit': 's'
        }
        
        return deriv_order
    
    def _map_to_mt5(self, order_request: OrderRequest) -> Dict[str, Any]:
        """Map order to MT5 format"""
        # Map symbol to MT5 format
        mt5_symbol = self._map_symbol_to_mt5(order_request.symbol, order_request.asset_type)
        
        # Create MT5 order
        mt5_order = {
            'symbol': mt5_symbol,
            'type': f'market_{order_request.order_type.lower()}',
            'volume': order_request.volume,
            'price': order_request.price or 0.0,
            'stop_loss': order_request.stop_loss or 0.0,
            'take_profit': order_request.take_profit or 0.0
        }
        
        return mt5_order
    
    def _map_symbol_to_deriv(self, symbol: str, asset_type: str) -> str:
        """Map symbol to Deriv format"""
        from .deriv_broker import map_asset_to_deriv
        return map_asset_to_deriv(symbol, asset_type)
    
    def _map_symbol_to_mt5(self, symbol: str, asset_type: str) -> str:
        """Map symbol to MT5 format"""
        from .mt5_broker import map_asset_to_mt5
        return map_asset_to_mt5(symbol, asset_type)
    
    def _get_deriv_cost(self, order_request: OrderRequest) -> float:
        """Get cost for Deriv order (simplified)"""
        # This is a simplified cost calculation
        # In production, you'd get actual costs from Deriv API
        return 0.001  # Default cost
    
    def _get_mt5_spread(self, symbol: str) -> float:
        """Get spread for MT5 symbol"""
        try:
            broker = self.brokers.get('mt5')
            if broker and broker.connected:
                symbol_info = broker.get_symbol_info(symbol)
                return symbol_info.get('spread', 0.0001) / 10000  # Convert to pips
            return 0.0001
        except Exception as e:
            self.logger.error(f"Error getting MT5 spread: {e}")
            return 0.0001
    
    def _initialize_performance_tracking(self):
        """Initialize performance tracking for all brokers"""
        # This will be populated when brokers are added
        pass
    
    def _update_performance_tracking(self, broker_name: str, success: bool, execution_time: float):
        """Update performance tracking for broker"""
        try:
            performance = self.performance_tracker[broker_name]
            
            # Update recent orders
            performance.recent_orders.append({
                'success': success,
                'execution_time': execution_time,
                'timestamp': datetime.now()
            })
            
            # Keep only recent orders
            if len(performance.recent_orders) > self.config['performance_window']:
                performance.recent_orders = performance.recent_orders[-self.config['performance_window']:]
            
            # Update metrics
            performance.total_orders += 1
            performance.last_updated = datetime.now()
            
            # Calculate success rate
            recent_orders = performance.recent_orders[-50:]  # Last 50 orders
            if recent_orders:
                success_count = sum(1 for order in recent_orders if order['success'])
                performance.success_rate = success_count / len(recent_orders)
            
            # Calculate average execution time
            if recent_orders:
                execution_times = [order['execution_time'] for order in recent_orders]
                performance.avg_execution_time = np.mean(execution_times)
            
        except Exception as e:
            self.logger.error(f"Error updating performance tracking: {e}")
    
    def get_routing_status(self) -> Dict[str, Any]:
        """Get current routing status and performance"""
        try:
            return {
                'connected_brokers': list(self.brokers.keys()),
                'performance_metrics': {
                    name: {
                        'success_rate': perf.success_rate,
                        'avg_execution_time': perf.avg_execution_time,
                        'total_orders': perf.total_orders,
                        'last_updated': perf.last_updated.isoformat()
                    }
                    for name, perf in self.performance_tracker.items()
                },
                'active_orders': len(self.active_orders),
                'total_orders_routed': len(self.order_history),
                'routing_config': self.config,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting routing status: {e}")
            return {}
    
    def update_routing_config(self, new_config: Dict[str, Any]):
        """Update routing configuration"""
        try:
            self.config.update(new_config)
            self.logger.info(f"Updated routing config: {new_config}")
            
        except Exception as e:
            self.logger.error(f"Error updating routing config: {e}")

# Utility functions
def create_order_request(symbol: str, asset_type: str, order_type: str, volume: float,
                        strategy: RoutingStrategy = RoutingStrategy.COST_OPTIMIZED,
                        **kwargs) -> OrderRequest:
    """Create standardized order request"""
    return OrderRequest(
        symbol=symbol,
        asset_type=asset_type,
        order_type=order_type,
        volume=volume,
        strategy=strategy,
        **kwargs
    )

# Example usage
async def test_multi_broker_routing():
    """Test multi-broker routing"""
    # Create router
    router = MultiBrokerOrderRouter()
    
    # Add brokers (mock instances for testing)
    # deriv_broker = DerivBroker("your_api_token", demo_mode=True)
    # mt5_broker = MT5Broker(12345678, "password", "demo_server", demo_mode=True)
    
    # router.add_broker("deriv", deriv_broker)
    # router.add_broker("mt5", mt5_broker)
    
    # Create test order
    order_request = create_order_request(
        symbol="EUR/USD",
        asset_type="forex",
        order_type="BUY",
        volume=0.1,
        strategy=RoutingStrategy.COST_OPTIMIZED
    )
    
    # Route order
    # broker_orders = await router.route_order(order_request)
    
    # Get routing status
    status = router.get_routing_status()
    print(f"Routing Status: {status}")

if __name__ == "__main__":
    asyncio.run(test_multi_broker_routing())
