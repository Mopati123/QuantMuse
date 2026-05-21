#!/usr/bin/env python3
"""
Comprehensive QuantMuse Trading Algorithm Testing Framework
Tests all strategies across all data sources, timeframes, and metrics
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_service.factors import FactorCalculator, FactorScreener, StockSelector
from data_service.backtest import FactorBacktest, PerformanceAnalyzer
from data_service.strategies import MomentumStrategy, StrategyRegistry
from data_service.fetchers import BinanceFetcher, YahooFetcher, AlphaVantageFetcher
from data_service.ai import SentimentAnalyzer, LLMIntegration
from data_service.storage import DatabaseManager

class ComprehensiveTestFramework:
    """Comprehensive testing framework for all QuantMuse strategies"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.results = {}
        self.test_configs = self._generate_test_configs()
        
    def _setup_logger(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('comprehensive_test.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _generate_test_configs(self) -> List[Dict[str, Any]]:
        """Generate all test configurations for superposition testing"""
        configs = []
        
        # Strategies
        strategies = ['momentum', 'factor_analysis', 'ai_ml', 'hybrid']
        
        # Data sources
        data_sources = ['binance', 'yahoo', 'mixed']
        
        # Timeframes
        timeframes = [
            {'name': 'short_term', 'days': 60},
            {'name': 'medium_term', 'days': 180},
            {'name': 'long_term', 'days': 730}
        ]
        
        # Generate all combinations
        for strategy in strategies:
            for source in data_sources:
                for timeframe in timeframes:
                    config = {
                        'strategy': strategy,
                        'data_source': source,
                        'timeframe': timeframe,
                        'test_id': f"{strategy}_{source}_{timeframe['name']}"
                    }
                    configs.append(config)
        
        self.logger.info(f"Generated {len(configs)} test configurations")
        return configs
    
    def fetch_data(self, source: str, days: int) -> pd.DataFrame:
        """Fetch market data from specified source"""
        try:
            if source == 'binance':
                fetcher = BinanceFetcher()
                # Get BTC and ETH data
                btc_data = fetcher.fetch_historical_data("BTCUSD", interval="1d", limit=days)
                eth_data = fetcher.fetch_historical_data("ETHUSD", interval="1d", limit=days)
                # Combine crypto data
                data = pd.concat([btc_data, eth_data], keys=['BTC', 'ETH'])
                
            elif source == 'yahoo':
                fetcher = YahooFetcher()
                # Get major tech stocks
                symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
                data_dict = {}
                for symbol in symbols:
                    data_dict[symbol] = fetcher.fetch_historical_data(symbol, period=f"{days}d")
                data = pd.concat(data_dict, keys=symbols)
                
            elif source == 'mixed':
                # Combine both crypto and stocks
                crypto_data = self.fetch_data('binance', days)
                stock_data = self.fetch_data('yahoo', days)
                data = pd.concat([crypto_data, stock_data], keys=['Crypto', 'Stocks'])
            
            self.logger.info(f"Fetched {len(data)} data points from {source}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data from {source}: {e}")
            return pd.DataFrame()
    
    def calculate_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive factors for all assets"""
        try:
            factor_calculator = FactorCalculator()
            factor_data = {}
            
            # Calculate factors for each asset
            if isinstance(data.index, pd.MultiIndex):
                # MultiIndex case (multiple assets)
                for asset in data.index.get_level_values(0).unique():
                    asset_data = data.loc[asset]
                    factor_data[asset] = factor_calculator.calculate_all_factors(asset_data)
            else:
                # Single asset case
                factor_data['default'] = factor_calculator.calculate_all_factors(data)
            
            # Combine all factor data
            combined_factors = pd.concat(factor_data, axis=1)
            self.logger.info(f"Calculated {len(combined_factors.columns)} factors")
            return combined_factors
            
        except Exception as e:
            self.logger.error(f"Error calculating factors: {e}")
            return pd.DataFrame()
    
    def run_momentum_strategy(self, factor_data: pd.DataFrame, price_data: pd.DataFrame, 
                          params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run momentum strategy with specified parameters"""
        try:
            strategy = MomentumStrategy()
            
            # Set parameters
            default_params = {
                'lookback_period': 60,
                'top_n': 20,
                'min_momentum': 5.0,
                'rebalance_frequency': 'monthly'
            }
            if params:
                default_params.update(params)
            strategy.parameters = default_params
            
            # Generate signals
            result = strategy.generate_signals(factor_data, price_data)
            
            self.logger.info(f"Momentum strategy completed with {len(result.signals)} signals")
            return {
                'strategy': 'momentum',
                'signals': result.signals,
                'performance': result.performance,
                'parameters': default_params
            }
            
        except Exception as e:
            self.logger.error(f"Error in momentum strategy: {e}")
            return {'error': str(e)}
    
    def run_factor_analysis_strategy(self, factor_data: pd.DataFrame, price_data: pd.DataFrame,
                                params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run multi-factor analysis strategy"""
        try:
            screener = FactorScreener()
            selector = StockSelector()
            
            # Default parameters
            default_params = {
                'momentum_weight': 0.3,
                'value_weight': 0.3,
                'quality_weight': 0.2,
                'volatility_weight': 0.2,
                'top_n': 15
            }
            if params:
                default_params.update(params)
            
            # Create multi-factor screener
            multi_factor_screener = screener.create_multi_factor_screener(
                momentum_weight=default_params['momentum_weight'],
                value_weight=default_params['value_weight'],
                quality_weight=default_params['quality_weight'],
                volatility_weight=default_params['volatility_weight']
            )
            
            # Screen stocks
            screening_results = multi_factor_screener.screen_stocks(factor_data)
            
            # Select top stocks
            selection_result = selector.select_stocks(
                factor_data, price_data,
                selection_method='top_n',
                n=default_params['top_n']
            )
            
            # Generate simple signals (1 for selected, 0 for others)
            signals = {}
            for asset in factor_data.index:
                signals[asset] = 1 if asset in selection_result['selected_assets'] else 0
            
            self.logger.info(f"Factor analysis selected {len(selection_result['selected_assets'])} assets")
            return {
                'strategy': 'factor_analysis',
                'signals': signals,
                'performance': selection_result,
                'parameters': default_params
            }
            
        except Exception as e:
            self.logger.error(f"Error in factor analysis strategy: {e}")
            return {'error': str(e)}
    
    def run_ai_ml_strategy(self, factor_data: pd.DataFrame, price_data: pd.DataFrame,
                         params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run AI/ML enhanced strategy"""
        try:
            sentiment_analyzer = SentimentAnalyzer()
            llm_integration = LLMIntegration()
            
            # Default parameters
            default_params = {
                'sentiment_weight': 0.4,
                'factor_weight': 0.4,
                'llm_weight': 0.2,
                'confidence_threshold': 0.6
            }
            if params:
                default_params.update(params)
            
            # Get sentiment analysis (mock for now)
            sentiment_scores = {}
            for asset in factor_data.index:
                # In real implementation, this would analyze news/social media
                sentiment_scores[asset] = np.random.uniform(-1, 1)  # Mock sentiment
            
            # Get LLM insights (mock for now)
            llm_insights = {}
            for asset in factor_data.index:
                # In real implementation, this would call LLM API
                llm_insights[asset] = np.random.uniform(0, 1)  # Mock LLM score
            
            # Combine signals
            signals = {}
            for asset in factor_data.index:
                # Normalize factors to 0-1 range
                factor_score = (factor_data.loc[asset].mean() - factor_data.min().min()) / (factor_data.max().max() - factor_data.min().min())
                
                # Combine all signals
                combined_score = (
                    default_params['sentiment_weight'] * sentiment_scores.get(asset, 0) +
                    default_params['factor_weight'] * factor_score +
                    default_params['llm_weight'] * llm_insights.get(asset, 0)
                )
                
                # Generate signal based on threshold
                signals[asset] = 1 if combined_score > default_params['confidence_threshold'] else 0
            
            self.logger.info(f"AI/ML strategy generated {sum(signals.values())} buy signals")
            return {
                'strategy': 'ai_ml',
                'signals': signals,
                'sentiment_scores': sentiment_scores,
                'llm_insights': llm_insights,
                'parameters': default_params
            }
            
        except Exception as e:
            self.logger.error(f"Error in AI/ML strategy: {e}")
            return {'error': str(e)}
    
    def run_hybrid_strategy(self, factor_data: pd.DataFrame, price_data: pd.DataFrame,
                          params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run hybrid strategy combining all approaches"""
        try:
            # Get results from all strategies
            momentum_result = self.run_momentum_strategy(factor_data, price_data)
            factor_result = self.run_factor_analysis_strategy(factor_data, price_data)
            ai_ml_result = self.run_ai_ml_strategy(factor_data, price_data)
            
            # Default parameters for hybrid
            default_params = {
                'momentum_weight': 0.3,
                'factor_weight': 0.3,
                'ai_ml_weight': 0.4,
                'consensus_threshold': 0.6
            }
            if params:
                default_params.update(params)
            
            # Combine signals
            signals = {}
            for asset in factor_data.index:
                momentum_signal = momentum_result.get('signals', {}).get(asset, 0)
                factor_signal = factor_result.get('signals', {}).get(asset, 0)
                ai_ml_signal = ai_ml_result.get('signals', {}).get(asset, 0)
                
                # Weighted combination
                combined_signal = (
                    default_params['momentum_weight'] * momentum_signal +
                    default_params['factor_weight'] * factor_signal +
                    default_params['ai_ml_weight'] * ai_ml_signal
                )
                
                # Generate signal based on consensus
                signals[asset] = 1 if combined_signal > default_params['consensus_threshold'] else 0
            
            self.logger.info(f"Hybrid strategy generated {sum(signals.values())} buy signals")
            return {
                'strategy': 'hybrid',
                'signals': signals,
                'components': {
                    'momentum': momentum_result,
                    'factor_analysis': factor_result,
                    'ai_ml': ai_ml_result
                },
                'parameters': default_params
            }
            
        except Exception as e:
            self.logger.error(f"Error in hybrid strategy: {e}")
            return {'error': str(e)}
    
    def backtest_strategy(self, strategy_result: Dict[str, Any], price_data: pd.DataFrame) -> Dict[str, Any]:
        """Backtest strategy results with comprehensive metrics"""
        try:
            backtest_engine = FactorBacktest()
            performance_analyzer = PerformanceAnalyzer()
            
            # Convert signals to backtest format
            signals = strategy_result.get('signals', {})
            if not signals:
                return {'error': 'No signals generated'}
            
            # Create positions DataFrame
            positions = pd.DataFrame(index=price_data.index, columns=price_data.columns)
            for asset, signal in signals.items():
                if asset in positions.columns:
                    positions[asset] = signal
            
            # Run backtest
            backtest_result = backtest_engine.run_backtest(
                positions=positions,
                price_data=price_data,
                rebalance_frequency='monthly'
            )
            
            # Calculate comprehensive performance metrics
            performance = performance_analyzer.calculate_all_metrics(
                backtest_result['returns'],
                benchmark_returns=price_data.pct_change().mean(axis=1)  # Simple benchmark
            )
            
            self.logger.info(f"Backtest completed: {performance.get('total_return', 0):.2%} total return")
            return {
                'backtest_result': backtest_result,
                'performance_metrics': performance,
                'strategy_name': strategy_result.get('strategy')
            }
            
        except Exception as e:
            self.logger.error(f"Error in backtesting: {e}")
            return {'error': str(e)}
    
    def run_single_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test configuration"""
        test_id = config['test_id']
        self.logger.info(f"Running test: {test_id}")
        
        try:
            # Fetch data
            data = self.fetch_data(config['data_source'], config['timeframe']['days'])
            if data.empty:
                return {'test_id': test_id, 'error': 'Failed to fetch data'}
            
            # Calculate factors
            factor_data = self.calculate_factors(data)
            if factor_data.empty:
                return {'test_id': test_id, 'error': 'Failed to calculate factors'}
            
            # Run strategy
            strategy_name = config['strategy']
            if strategy_name == 'momentum':
                strategy_result = self.run_momentum_strategy(factor_data, data)
            elif strategy_name == 'factor_analysis':
                strategy_result = self.run_factor_analysis_strategy(factor_data, data)
            elif strategy_name == 'ai_ml':
                strategy_result = self.run_ai_ml_strategy(factor_data, data)
            elif strategy_name == 'hybrid':
                strategy_result = self.run_hybrid_strategy(factor_data, data)
            else:
                return {'test_id': test_id, 'error': f'Unknown strategy: {strategy_name}'}
            
            if 'error' in strategy_result:
                return {'test_id': test_id, 'error': strategy_result['error']}
            
            # Backtest results
            backtest_result = self.backtest_strategy(strategy_result, data)
            if 'error' in backtest_result:
                return {'test_id': test_id, 'error': backtest_result['error']}
            
            # Combine results
            test_result = {
                'test_id': test_id,
                'config': config,
                'strategy_result': strategy_result,
                'backtest_result': backtest_result,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Test {test_id} completed successfully")
            return test_result
            
        except Exception as e:
            self.logger.error(f"Error in test {test_id}: {e}")
            return {'test_id': test_id, 'error': str(e)}
    
    def run_all_tests(self, parallel: bool = True) -> Dict[str, Any]:
        """Run all test configurations"""
        self.logger.info(f"Starting comprehensive test with {len(self.test_configs)} configurations")
        
        results = {}
        
        if parallel:
            # Run tests in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_config = {
                    executor.submit(self.run_single_test, config): config 
                    for config in self.test_configs
                }
                
                for future in as_completed(future_to_config):
                    config = future_to_config[future]
                    try:
                        result = future.result(timeout=300)  # 5 minute timeout
                        results[result['test_id']] = result
                    except Exception as e:
                        results[config['test_id']] = {
                            'test_id': config['test_id'], 
                            'error': f'Timeout or error: {str(e)}'
                        }
        else:
            # Run tests sequentially
            for config in self.test_configs:
                result = self.run_single_test(config)
                results[result['test_id']] = result
        
        self.results = results
        self.logger.info(f"Completed {len(results)} tests")
        return results
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze all test results and generate insights"""
        if not self.results:
            return {'error': 'No results to analyze'}
        
        analysis = {
            'summary': {},
            'strategy_comparison': {},
            'data_source_comparison': {},
            'timeframe_comparison': {},
            'best_performers': {},
            'risk_analysis': {}
        }
        
        # Separate successful tests
        successful_tests = {
            k: v for k, v in self.results.items() 
            if 'error' not in v and 'backtest_result' in v
        }
        
        if not successful_tests:
            return {'error': 'No successful tests to analyze'}
        
        # Aggregate by strategy
        strategy_performance = {}
        for test_id, result in successful_tests.items():
            strategy = result['config']['strategy']
            performance = result['backtest_result']['performance_metrics']
            
            if strategy not in strategy_performance:
                strategy_performance[strategy] = []
            strategy_performance[strategy].append(performance)
        
        # Calculate average performance by strategy
        for strategy, performances in strategy_performance.items():
            avg_metrics = {}
            for metric in performances[0].keys():
                values = [p[metric] for p in performances if metric in p]
                avg_metrics[metric] = np.mean(values) if values else 0
            analysis['strategy_comparison'][strategy] = avg_metrics
        
        # Similar analysis for data sources and timeframes
        # (Implementation would follow same pattern as strategy analysis)
        
        # Find best performers
        all_performances = []
        for test_id, result in successful_tests.items():
            performance = result['backtest_result']['performance_metrics']
            total_return = performance.get('total_return', 0)
            sharpe_ratio = performance.get('sharpe_ratio', 0)
            
            all_performances.append({
                'test_id': test_id,
                'config': result['config'],
                'total_return': total_return,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': performance.get('max_drawdown', 0)
            })
        
        # Sort by different metrics
        best_by_return = sorted(all_performances, key=lambda x: x['total_return'], reverse=True)[:5]
        best_by_sharpe = sorted(all_performances, key=lambda x: x['sharpe_ratio'], reverse=True)[:5]
        
        analysis['best_performers'] = {
            'by_total_return': best_by_return,
            'by_sharpe_ratio': best_by_sharpe
        }
        
        # Summary statistics
        analysis['summary'] = {
            'total_tests': len(self.results),
            'successful_tests': len(successful_tests),
            'success_rate': len(successful_tests) / len(self.results) * 100,
            'strategies_tested': len(set(r['config']['strategy'] for r in successful_tests.values())),
            'data_sources_tested': len(set(r['config']['data_source'] for r in successful_tests.values())),
            'timeframes_tested': len(set(r['config']['timeframe']['name'] for r in successful_tests.values()))
        }
        
        return analysis
    
    def save_results(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Save comprehensive test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw results
        results_file = f"comprehensive_test_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save analysis
        analysis_file = f"comprehensive_test_analysis_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        self.logger.info(f"Results saved to {results_file}")
        self.logger.info(f"Analysis saved to {analysis_file}")
        
        return results_file, analysis_file

def main():
    """Main execution function"""
    print("🚀 Starting Comprehensive QuantMuse Trading Algorithm Test")
    print("=" * 60)
    
    # Initialize framework
    framework = ComprehensiveTestFramework()
    
    # Run all tests
    print("📊 Running all test configurations...")
    results = framework.run_all_tests(parallel=True)
    
    # Analyze results
    print("📈 Analyzing results...")
    analysis = framework.analyze_results()
    
    # Save results
    print("💾 Saving results...")
    results_file, analysis_file = framework.save_results(results, analysis)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    if 'summary' in analysis:
        summary = analysis['summary']
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful Tests: {summary['successful_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Strategies Tested: {summary['strategies_tested']}")
        print(f"Data Sources Tested: {summary['data_sources_tested']}")
        print(f"Timeframes Tested: {summary['timeframes_tested']}")
    
    if 'best_performers' in analysis:
        print("\n🏆 TOP PERFORMERS")
        print("-" * 30)
        
        best_return = analysis['best_performers']['by_total_return'][0]
        best_sharpe = analysis['best_performers']['by_sharpe_ratio'][0]
        
        print(f"Best Total Return: {best_return['test_id']}")
        print(f"  Return: {best_return['total_return']:.2%}")
        print(f"  Sharpe: {best_return['sharpe_ratio']:.2f}")
        print(f"  Config: {best_return['config']}")
        
        print(f"\nBest Sharpe Ratio: {best_sharpe['test_id']}")
        print(f"  Return: {best_sharpe['total_return']:.2%}")
        print(f"  Sharpe: {best_sharpe['sharpe_ratio']:.2f}")
        print(f"  Config: {best_sharpe['config']}")
    
    print(f"\n📄 Detailed Results: {results_file}")
    print(f"📊 Analysis Report: {analysis_file}")
    print("\n🎉 Comprehensive testing completed!")

if __name__ == "__main__":
    main()
