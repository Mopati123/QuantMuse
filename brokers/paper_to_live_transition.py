#!/usr/bin/env python3
"""
Paper Trading to Live Trading Transition System for QuantMuse
Gradual transition from paper trading to live trading with A/B testing
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import json

from .deriv_broker import DerivBroker
from .mt5_broker import MT5Broker
from .multi_broker_router import MultiBrokerOrderRouter
from .unified_risk_manager import UnifiedRiskManager

class TradingMode(Enum):
    """Trading modes"""
    PAPER = "paper"
    LIVE = "live"
    HYBRID = "hybrid"  # Both paper and live for A/B testing

class TransitionPhase(Enum):
    """Transition phases"""
    PAPER_ONLY = "paper_only"
    PAPER_VALIDATION = "paper_validation"
    SMALL_LIVE_TEST = "small_live_test"
    INCREASED_LIVE = "increased_live"
    FULL_LIVE = "full_live"

@dataclass
class TransitionConfig:
    """Configuration for transition phases"""
    phase: TransitionPhase
    paper_percentage: float  # Percentage of trades in paper mode
    live_percentage: float    # Percentage of trades in live mode
    max_live_capital: float   # Maximum capital for live trading
    min_performance_score: float  # Minimum performance score to advance
    duration_days: int        # Duration of this phase in days
    requirements: Dict[str, Any]  # Additional requirements for this phase

@dataclass
class PerformanceMetrics:
    """Performance metrics for transition evaluation"""
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    avg_trade_duration: float
    volatility: float
    risk_adjusted_return: float
    last_updated: datetime

@dataclass
class TransitionState:
    """Current transition state"""
    current_phase: TransitionPhase
    phase_start_date: datetime
    phase_end_date: datetime
    paper_performance: PerformanceMetrics
    live_performance: PerformanceMetrics
    transition_score: float
    last_evaluation: datetime
    ready_for_next_phase: bool

class PaperToLiveTransition:
    """Manages transition from paper to live trading"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.paper_brokers = {}
        self.live_brokers = {}
        self.transition_state = None
        self.performance_history = []
        self.transition_history = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize transition phases
        self.transition_phases = self._initialize_transition_phases()
        
        # Performance evaluation criteria
        self.evaluation_criteria = {
            'min_return': 0.05,  # 5% minimum return
            'min_sharpe': 1.0,   # Minimum Sharpe ratio
            'max_drawdown': 0.10,  # Maximum 10% drawdown
            'min_win_rate': 0.55,  # Minimum 55% win rate
            'min_profit_factor': 1.2,  # Minimum profit factor
            'min_trades': 50,   # Minimum number of trades
            'evaluation_period': 7  # Days of evaluation
        }
        
        # Capital allocation strategy
        self.capital_allocation = {
            'initial_live_capital': 1000,  # Start with $1K
            'max_live_capital': 10000,     # Maximum $10K
            'increment_factor': 2.0,      # Double capital each phase
            'risk_percentage': 0.02,      # 2% risk per trade
            'max_loss_threshold': 0.05    # Stop if losing more than 5%
        }
    
    def add_paper_broker(self, name: str, broker_instance: Any) -> bool:
        """Add paper trading broker"""
        try:
            self.paper_brokers[name] = broker_instance
            self.logger.info(f"Added paper broker: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add paper broker {name}: {e}")
            return False
    
    def add_live_broker(self, name: str, broker_instance: Any) -> bool:
        """Add live trading broker"""
        try:
            self.live_brokers[name] = broker_instance
            self.logger.info(f"Added live broker: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add live broker {name}: {e}")
            return False
    
    def start_transition(self) -> Dict[str, Any]:
        """Start the transition process"""
        try:
            self.logger.info("Starting paper to live trading transition")
            
            # Initialize transition state
            self.transition_state = TransitionState(
                current_phase=TransitionPhase.PAPER_ONLY,
                phase_start_date=datetime.now(),
                phase_end_date=datetime.now() + timedelta(days=self.transition_phases[0].duration_days),
                paper_performance=PerformanceMetrics(0, 0, 0, 0, 0, 0, 0, 0, datetime.now()),
                live_performance=PerformanceMetrics(0, 0, 0, 0, 0, 0, 0, 0, datetime.now()),
                transition_score=0.0,
                last_evaluation=datetime.now(),
                ready_for_next_phase=False
            )
            
            return {
                'success': True,
                'current_phase': self.transition_state.current_phase.value,
                'phase_duration': self.transition_phases[0].duration_days,
                'message': 'Transition started in paper-only mode'
            }
            
        except Exception as e:
            self.logger.error(f"Error starting transition: {e}")
            return {'success': False, 'error': str(e)}
    
    async def execute_trade(self, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade based on current transition phase"""
        try:
            if not self.transition_state:
                return {'success': False, 'error': 'Transition not started'}
            
            # Determine execution mode based on current phase
            phase_config = self._get_current_phase_config()
            
            if self.transition_state.current_phase == TransitionPhase.PAPER_ONLY:
                return await self._execute_paper_trade(order_request)
            
            elif self.transition_state.current_phase == TransitionPhase.HYBRID:
                return await self._execute_hybrid_trade(order_request, phase_config)
            
            else:  # Live phases
                return await self._execute_live_trade(order_request, phase_config)
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_paper_trade(self, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute paper trade"""
        try:
            # Simulate paper trade execution
            paper_result = {
                'success': True,
                'mode': 'paper',
                'execution_time': 0.1,
                'price': order_request.get('price', 1.0),
                'volume': order_request.get('volume', 0.01),
                'timestamp': datetime.now().isoformat(),
                'simulated': True
            }
            
            # Record paper trade
            self._record_trade(order_request, paper_result, 'paper')
            
            return paper_result
            
        except Exception as e:
            self.logger.error(f"Error executing paper trade: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_hybrid_trade(self, order_request: Dict[str, Any], phase_config: TransitionConfig) -> Dict[str, Any]:
        """Execute hybrid trade (both paper and live)"""
        try:
            results = {}
            
            # Determine if this trade should be live
            should_be_live = np.random.random() < phase_config.live_percentage
            
            if should_be_live:
                # Execute live trade
                live_result = await self._execute_actual_live_trade(order_request)
                results['live'] = live_result
                
                # Also simulate paper trade for comparison
                paper_result = await self._execute_paper_trade(order_request)
                results['paper'] = paper_result
                
                # Record both trades
                self._record_trade(order_request, live_result, 'live')
                self._record_trade(order_request, paper_result, 'paper')
                
            else:
                # Execute only paper trade
                paper_result = await self._execute_paper_trade(order_request)
                results['paper'] = paper_result
                self._record_trade(order_request, paper_result, 'paper')
            
            results['mode'] = 'hybrid'
            results['live_percentage'] = phase_config.live_percentage
            results['paper_percentage'] = phase_config.paper_percentage
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error executing hybrid trade: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_live_trade(self, order_request: Dict[str, Any], phase_config: TransitionConfig) -> Dict[str, Any]:
        """Execute live trade"""
        try:
            # Check if we have live brokers
            if not self.live_brokers:
                return {'success': False, 'error': 'No live brokers available'}
            
            # Check capital limits
            if not self._check_capital_limits(order_request):
                return {'success': False, 'error': 'Capital limits exceeded'}
            
            # Execute on live broker
            broker_name = list(self.live_brokers.keys())[0]  # Use first live broker
            broker = self.live_brokers[broker_name]
            
            if broker_name == 'deriv':
                live_result = await broker.place_order(order_request)
            else:  # MT5
                live_result = broker.place_order(order_request)
            
            # Record live trade
            self._record_trade(order_request, live_result, 'live')
            
            live_result['mode'] = 'live'
            live_result['broker'] = broker_name
            
            return live_result
            
        except Exception as e:
            self.logger.error(f"Error executing live trade: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_actual_live_trade(self, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute actual live trade (small size for testing)"""
        try:
            # Reduce order size for live testing
            reduced_order = order_request.copy()
            reduced_order['volume'] = min(order_request.get('volume', 0.01), 0.01)  # Max 0.01 for testing
            
            # Execute on live broker
            broker_name = list(self.live_brokers.keys())[0]
            broker = self.live_brokers[broker_name]
            
            if broker_name == 'deriv':
                result = await broker.place_order(reduced_order)
            else:  # MT5
                result = broker.place_order(reduced_order)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing actual live trade: {e}")
            return {'success': False, 'error': str(e)}
    
    def _record_trade(self, order_request: Dict[str, Any], result: Dict[str, Any], mode: str):
        """Record trade for performance tracking"""
        try:
            trade_record = {
                'order_request': order_request,
                'execution_result': result,
                'mode': mode,
                'timestamp': datetime.now(),
                'phase': self.transition_state.current_phase.value if self.transition_state else 'unknown'
            }
            
            self.performance_history.append(trade_record)
            
            # Keep only recent trades
            if len(self.performance_history) > 1000:
                self.performance_history = self.performance_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error recording trade: {e}")
    
    def _check_capital_limits(self, order_request: Dict[str, Any]) -> bool:
        """Check if trade exceeds capital limits"""
        try:
            # Get current live capital usage
            current_live_capital = self._get_current_live_capital()
            max_live_capital = self.capital_allocation['max_live_capital']
            
            # Calculate trade value
            trade_value = order_request.get('volume', 0) * order_request.get('price', 1)
            
            # Check if adding this trade exceeds limits
            if current_live_capital + trade_value > max_live_capital:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking capital limits: {e}")
            return False
    
    def _get_current_live_capital(self) -> float:
        """Get current live capital usage"""
        try:
            # Calculate from recent live trades
            live_trades = [t for t in self.performance_history if t.get('mode') == 'live']
            
            if not live_trades:
                return 0.0
            
            # Sum up current positions (simplified)
            current_capital = sum(
                t['execution_result'].get('volume', 0) * t['execution_result'].get('price', 1)
                for t in live_trades[-100:]  # Last 100 trades
            )
            
            return current_capital
            
        except Exception as e:
            self.logger.error(f"Error getting current live capital: {e}")
            return 0.0
    
    def evaluate_transition_progress(self) -> Dict[str, Any]:
        """Evaluate progress and determine if ready for next phase"""
        try:
            if not self.transition_state:
                return {'ready': False, 'reason': 'No active transition'}
            
            # Check if phase duration is complete
            if datetime.now() < self.transition_state.phase_end_date:
                return {
                    'ready': False,
                    'reason': 'Phase duration not complete',
                    'days_remaining': (self.transition_state.phase_end_date - datetime.now()).days
                }
            
            # Calculate performance metrics
            paper_metrics = self._calculate_performance_metrics('paper')
            live_metrics = self._calculate_performance_metrics('live')
            
            # Update transition state
            self.transition_state.paper_performance = paper_metrics
            self.transition_state.live_performance = live_metrics
            self.transition_state.last_evaluation = datetime.now()
            
            # Evaluate readiness for next phase
            phase_config = self._get_current_phase_config()
            ready = self._evaluate_phase_requirements(paper_metrics, live_metrics, phase_config)
            
            self.transition_state.ready_for_next_phase = ready
            self.transition_state.transition_score = self._calculate_transition_score(paper_metrics, live_metrics)
            
            return {
                'ready': ready,
                'current_phase': self.transition_state.current_phase.value,
                'paper_performance': paper_metrics.__dict__,
                'live_performance': live_metrics.__dict__,
                'transition_score': self.transition_state.transition_score,
                'requirements_met': self._check_requirements_met(phase_config, paper_metrics, live_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating transition progress: {e}")
            return {'ready': False, 'error': str(e)}
    
    def advance_to_next_phase(self) -> Dict[str, Any]:
        """Advance to the next transition phase"""
        try:
            if not self.transition_state:
                return {'success': False, 'error': 'No active transition'}
            
            # Get current phase index
            current_phase_index = self._get_phase_index(self.transition_state.current_phase)
            
            if current_phase_index >= len(self.transition_phases) - 1:
                return {'success': False, 'error': 'Already in final phase'}
            
            # Move to next phase
            next_phase_index = current_phase_index + 1
            next_phase = self.transition_phases[next_phase_index]
            
            # Update transition state
            old_phase = self.transition_state.current_phase
            self.transition_state.current_phase = next_phase.phase
            self.transition_state.phase_start_date = datetime.now()
            self.transition_state.phase_end_date = datetime.now() + timedelta(days=next_phase.duration_days)
            self.transition_state.ready_for_next_phase = False
            
            # Record transition
            transition_record = {
                'from_phase': old_phase.value,
                'to_phase': next_phase.phase.value,
                'timestamp': datetime.now(),
                'transition_score': self.transition_state.transition_score
            }
            self.transition_history.append(transition_record)
            
            self.logger.info(f"Advanced from {old_phase.value} to {next_phase.phase.value}")
            
            return {
                'success': True,
                'previous_phase': old_phase.value,
                'new_phase': next_phase.phase.value,
                'new_duration': next_phase.duration_days,
                'paper_percentage': next_phase.paper_percentage,
                'live_percentage': next_phase.live_percentage,
                'max_live_capital': next_phase.max_live_capital
            }
            
        except Exception as e:
            self.logger.error(f"Error advancing to next phase: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_performance_metrics(self, mode: str) -> PerformanceMetrics:
        """Calculate performance metrics for paper or live trades"""
        try:
            # Filter trades by mode
            mode_trades = [t for t in self.performance_history if t.get('mode') == mode]
            
            if not mode_trades:
                return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0, 0, datetime.now())
            
            # Calculate metrics (simplified implementation)
            total_trades = len(mode_trades)
            successful_trades = sum(1 for t in mode_trades if t['execution_result'].get('success', False))
            
            win_rate = successful_trades / total_trades if total_trades > 0 else 0
            
            # Mock performance calculations (in production, you'd use actual trade results)
            total_return = np.random.normal(0.05, 0.02)  # 5% average return with 2% std
            sharpe_ratio = total_return / 0.02 if 0.02 > 0 else 0
            max_drawdown = abs(np.random.normal(0.05, 0.01))  # 5% average drawdown
            profit_factor = np.random.uniform(1.1, 1.5)
            avg_trade_duration = np.random.uniform(1, 24)  # 1-24 hours
            volatility = np.random.uniform(0.1, 0.3)
            risk_adjusted_return = total_return / volatility if volatility > 0 else 0
            
            return PerformanceMetrics(
                total_return=total_return,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                avg_trade_duration=avg_trade_duration,
                volatility=volatility,
                risk_adjusted_return=risk_adjusted_return,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0, 0, datetime.now())
    
    def _evaluate_phase_requirements(self, paper_metrics: PerformanceMetrics, 
                                   live_metrics: PerformanceMetrics, 
                                   phase_config: TransitionConfig) -> bool:
        """Evaluate if requirements for current phase are met"""
        try:
            requirements = phase_config.requirements
            
            # Check paper performance requirements
            if 'min_paper_return' in requirements:
                if paper_metrics.total_return < requirements['min_paper_return']:
                    return False
            
            if 'min_paper_sharpe' in requirements:
                if paper_metrics.sharpe_ratio < requirements['min_paper_sharpe']:
                    return False
            
            # Check live performance requirements (if applicable)
            if phase_config.live_percentage > 0:
                if 'min_live_return' in requirements:
                    if live_metrics.total_return < requirements['min_live_return']:
                        return False
                
                if 'min_live_trades' in requirements:
                    live_trades = len([t for t in self.performance_history if t.get('mode') == 'live'])
                    if live_trades < requirements['min_live_trades']:
                        return False
            
            # Check drawdown limits
            if 'max_drawdown' in requirements:
                if paper_metrics.max_drawdown > requirements['max_drawdown']:
                    return False
                if phase_config.live_percentage > 0 and live_metrics.max_drawdown > requirements['max_drawdown']:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating phase requirements: {e}")
            return False
    
    def _calculate_transition_score(self, paper_metrics: PerformanceMetrics, 
                                  live_metrics: PerformanceMetrics) -> float:
        """Calculate overall transition score"""
        try:
            # Weight different metrics
            paper_weight = 0.4
            live_weight = 0.6
            
            # Calculate paper score
            paper_score = (
                min(paper_metrics.total_return * 10, 1.0) * 0.3 +  # Return (max 10%)
                min(paper_metrics.sharpe_ratio / 2, 1.0) * 0.3 +     # Sharpe (max 2.0)
                min(paper_metrics.win_rate, 1.0) * 0.2 +             # Win rate
                min(paper_metrics.profit_factor / 2, 1.0) * 0.2      # Profit factor (max 2.0)
            )
            
            # Calculate live score
            live_score = (
                min(live_metrics.total_return * 10, 1.0) * 0.3 +
                min(live_metrics.sharpe_ratio / 2, 1.0) * 0.3 +
                min(live_metrics.win_rate, 1.0) * 0.2 +
                min(live_metrics.profit_factor / 2, 1.0) * 0.2
            )
            
            # Combined score
            overall_score = paper_score * paper_weight + live_score * live_weight
            
            return overall_score
            
        except Exception as e:
            self.logger.error(f"Error calculating transition score: {e}")
            return 0.0
    
    def _get_current_phase_config(self) -> TransitionConfig:
        """Get configuration for current phase"""
        try:
            if not self.transition_state:
                return self.transition_phases[0]
            
            phase_index = self._get_phase_index(self.transition_state.current_phase)
            return self.transition_phases[phase_index]
            
        except Exception as e:
            self.logger.error(f"Error getting current phase config: {e}")
            return self.transition_phases[0]
    
    def _get_phase_index(self, phase: TransitionPhase) -> int:
        """Get index of phase in transition phases"""
        for i, phase_config in enumerate(self.transition_phases):
            if phase_config.phase == phase:
                return i
        return 0
    
    def _initialize_transition_phases(self) -> List[TransitionConfig]:
        """Initialize transition phases"""
        return [
            TransitionConfig(
                phase=TransitionPhase.PAPER_ONLY,
                paper_percentage=1.0,
                live_percentage=0.0,
                max_live_capital=0,
                min_performance_score=0.0,
                duration_days=7,
                requirements={'min_paper_return': 0.02, 'min_paper_trades': 20}
            ),
            TransitionConfig(
                phase=TransitionPhase.PAPER_VALIDATION,
                paper_percentage=1.0,
                live_percentage=0.0,
                max_live_capital=0,
                min_performance_score=0.5,
                duration_days=7,
                requirements={'min_paper_return': 0.05, 'min_paper_sharpe': 1.0, 'min_paper_trades': 50}
            ),
            TransitionConfig(
                phase=TransitionPhase.SMALL_LIVE_TEST,
                paper_percentage=0.8,
                live_percentage=0.2,
                max_live_capital=1000,
                min_performance_score=0.6,
                duration_days=7,
                requirements={'min_paper_return': 0.05, 'min_live_trades': 10, 'max_drawdown': 0.05}
            ),
            TransitionConfig(
                phase=TransitionPhase.INCREASED_LIVE,
                paper_percentage=0.5,
                live_percentage=0.5,
                max_live_capital=5000,
                min_performance_score=0.7,
                duration_days=14,
                requirements={'min_live_return': 0.03, 'min_live_trades': 25, 'max_drawdown': 0.08}
            ),
            TransitionConfig(
                phase=TransitionPhase.FULL_LIVE,
                paper_percentage=0.0,
                live_percentage=1.0,
                max_live_capital=10000,
                min_performance_score=0.8,
                duration_days=30,
                requirements={'min_live_return': 0.05, 'min_live_sharpe': 1.2, 'min_live_trades': 50}
            )
        ]
    
    def _check_requirements_met(self, phase_config: TransitionConfig, 
                              paper_metrics: PerformanceMetrics, 
                              live_metrics: PerformanceMetrics) -> Dict[str, bool]:
        """Check if specific requirements are met"""
        try:
            requirements_met = {}
            
            for requirement, value in phase_config.requirements.items():
                if requirement == 'min_paper_return':
                    requirements_met[requirement] = paper_metrics.total_return >= value
                elif requirement == 'min_paper_sharpe':
                    requirements_met[requirement] = paper_metrics.sharpe_ratio >= value
                elif requirement == 'min_paper_trades':
                    paper_trades = len([t for t in self.performance_history if t.get('mode') == 'paper'])
                    requirements_met[requirement] = paper_trades >= value
                elif requirement == 'min_live_return':
                    requirements_met[requirement] = live_metrics.total_return >= value
                elif requirement == 'min_live_sharpe':
                    requirements_met[requirement] = live_metrics.sharpe_ratio >= value
                elif requirement == 'min_live_trades':
                    live_trades = len([t for t in self.performance_history if t.get('mode') == 'live'])
                    requirements_met[requirement] = live_trades >= value
                elif requirement == 'max_drawdown':
                    requirements_met[requirement] = (paper_metrics.max_drawdown <= value and 
                                                  live_metrics.max_drawdown <= value)
            
            return requirements_met
            
        except Exception as e:
            self.logger.error(f"Error checking requirements met: {e}")
            return {}
    
    def get_transition_status(self) -> Dict[str, Any]:
        """Get current transition status"""
        try:
            if not self.transition_state:
                return {
                    'active': False,
                    'message': 'No active transition'
                }
            
            # Get evaluation
            evaluation = self.evaluate_transition_progress()
            
            return {
                'active': True,
                'current_phase': self.transition_state.current_phase.value,
                'phase_start_date': self.transition_state.phase_start_date.isoformat(),
                'phase_end_date': self.transition_state.phase_end_date.isoformat(),
                'days_in_phase': (datetime.now() - self.transition_state.phase_start_date).days,
                'days_remaining': max(0, (self.transition_state.phase_end_date - datetime.now()).days),
                'transition_score': self.transition_state.transition_score,
                'ready_for_next_phase': evaluation.get('ready', False),
                'total_trades': len(self.performance_history),
                'paper_trades': len([t for t in self.performance_history if t.get('mode') == 'paper']),
                'live_trades': len([t for t in self.performance_history if t.get('mode') == 'live']),
                'current_live_capital': self._get_current_live_capital(),
                'max_live_capital': self._get_current_phase_config().max_live_capital,
                'transition_history': [
                    {
                        'from_phase': t['from_phase'],
                        'to_phase': t['to_phase'],
                        'timestamp': t['timestamp'].isoformat()
                    }
                    for t in self.transition_history
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting transition status: {e}")
            return {'active': False, 'error': str(e)}
    
    async def emergency_stop(self) -> Dict[str, Any]:
        """Emergency stop - halt all live trading"""
        try:
            self.logger.warning("Emergency stop activated - halting all live trading")
            
            # Close all live positions
            for broker_name, broker in self.live_brokers.items():
                try:
                    if broker_name == 'deriv':
                        positions = await broker.get_positions()
                        for position in positions:
                            await broker.close_position(position['contract_id'])
                    else:  # MT5
                        positions = broker.get_positions()
                        for position in positions:
                            broker.close_position(position['position_id'])
                except Exception as e:
                    self.logger.error(f"Error closing positions for {broker_name}: {e}")
            
            # Reset transition to paper-only
            if self.transition_state:
                self.transition_state.current_phase = TransitionPhase.PAPER_ONLY
                self.transition_state.ready_for_next_phase = False
            
            return {
                'success': True,
                'message': 'Emergency stop completed - all live trading halted',
                'current_phase': TransitionPhase.PAPER_ONLY.value
            }
            
        except Exception as e:
            self.logger.error(f"Error during emergency stop: {e}")
            return {'success': False, 'error': str(e)}

# Utility functions
def create_transition_config() -> Dict[str, Any]:
    """Create default transition configuration"""
    return {
        'initial_capital': 10000,
        'max_live_capital': 10000,
        'risk_per_trade': 0.02,
        'emergency_stop_loss': 0.10,
        'evaluation_frequency': 24,  # Hours
        'performance_window': 30,  # Days
        'auto_advance': True  # Automatically advance phases when ready
    }

# Example usage
async def test_paper_to_live_transition():
    """Test paper to live transition"""
    # Create transition system
    config = create_transition_config()
    transition = PaperToLiveTransition(config)
    
    # Add brokers (mock instances for testing)
    # deriv_paper = DerivBroker("your_api_token", demo_mode=True)
    # deriv_live = DerivBroker("your_api_token", demo_mode=False)
    # mt5_paper = MT5Broker(12345678, "password", "demo_server", demo_mode=True)
    # mt5_live = MT5Broker(87654321, "password", "live_server", demo_mode=False)
    
    # transition.add_paper_broker("deriv", deriv_paper)
    # transition.add_paper_broker("mt5", mt5_paper)
    # transition.add_live_broker("deriv", deriv_live)
    # transition.add_live_broker("mt5", mt5_live)
    
    # Start transition
    # result = transition.start_transition()
    # print(f"Transition started: {result}")
    
    # Get status
    status = transition.get_transition_status()
    print(f"Transition Status: {status}")

if __name__ == "__main__":
    asyncio.run(test_paper_to_live_transition())
