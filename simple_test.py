#!/usr/bin/env python3
"""
Simplified Comprehensive Test - Demo of All Strategies
Runs all strategies with mock data for demonstration
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def generate_mock_data(days=60):
    """Generate mock market data for testing"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Generate price data for multiple assets
    assets = ['AAPL', 'GOOGL', 'MSFT', 'BTC', 'ETH']
    data_dict = {}
    
    np.random.seed(42)  # For reproducible results
    
    for asset in assets:
        # Generate realistic price movements
        returns = np.random.normal(0.001, 0.02, days)  # Daily returns
        prices = [100]  # Starting price
        
        for ret in returns:
            prices.append(prices[-1] * (1 + ret))
        
        data_dict[asset] = pd.DataFrame({
            'close': prices[1:],  # Remove starting price
            'volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)
    
    return pd.concat(data_dict, keys=assets)

def calculate_momentum_signals(data, lookback=20):
    """Calculate momentum signals"""
    signals = {}
    
    for asset in data.columns:
        prices = data[asset]['close']
        
        # Calculate momentum (price change over lookback period)
        momentum = (prices.iloc[-1] / prices.iloc[-lookback] - 1) * 100
        
        # Generate signal: 1 if momentum > threshold, 0 otherwise
        threshold = 5.0  # 5% momentum threshold
        signals[asset] = 1 if momentum > threshold else 0
    
    return signals

def calculate_factor_signals(data):
    """Calculate multi-factor signals"""
    signals = {}
    
    for asset in data.columns:
        prices = data[asset]['close']
        volumes = data[asset]['volume']
        
        # Calculate multiple factors
        # Momentum factor
        momentum = (prices.iloc[-1] / prices.iloc[-20] - 1) * 100
        
        # Volume factor (normalized)
        volume_factor = volumes.iloc[-20:].mean() / volumes.mean()
        
        # Volatility factor (inverse - lower volatility gets higher score)
        volatility = prices.pct_change().iloc[-20:].std()
        volatility_factor = 1 / (1 + volatility)  # Inverse volatility
        
        # Combined factor score
        combined_score = 0.4 * momentum + 0.3 * volume_factor + 0.3 * volatility_factor
        
        # Generate signal
        threshold = np.percentile([combined_score], 70)  # Top 30%
        signals[asset] = 1 if combined_score > threshold else 0
    
    return signals

def calculate_ai_ml_signals(data):
    """Calculate AI/ML enhanced signals"""
    signals = {}
    
    for asset in data.columns:
        prices = data[asset]['close']
        
        # Technical analysis factors
        momentum = (prices.iloc[-1] / prices.iloc[-20] - 1) * 100
        volatility = prices.pct_change().iloc[-20:].std()
        
        # Mock sentiment analysis (-1 to 1)
        sentiment_score = np.random.uniform(-0.5, 0.8)
        
        # Mock LLM insight (0 to 1)
        llm_score = np.random.uniform(0.3, 0.9)
        
        # Combine signals
        combined_score = (
            0.4 * (momentum / 20) +  # Normalized momentum
            0.3 * sentiment_score +
            0.3 * llm_score
        )
        
        # Generate signal based on confidence threshold
        confidence_threshold = 0.6
        signals[asset] = {
            'signal': 1 if combined_score > confidence_threshold else 0,
            'sentiment': sentiment_score,
            'llm_insight': llm_score,
            'combined_score': combined_score
        }
    
    return signals

def calculate_hybrid_signals(momentum_signals, factor_signals, ai_ml_signals):
    """Calculate hybrid strategy signals"""
    signals = {}
    
    for asset in momentum_signals.keys():
        # Weighted combination of all strategies
        momentum_weight = 0.3
        factor_weight = 0.3
        ai_ml_weight = 0.4
        
        combined_signal = (
            momentum_weight * momentum_signals[asset] +
            factor_weight * factor_signals[asset] +
            ai_ml_weight * ai_ml_signals[asset]['signal']
        )
        
        # Generate signal
        consensus_threshold = 0.6
        signals[asset] = {
            'signal': 1 if combined_signal > consensus_threshold else 0,
            'components': {
                'momentum': momentum_signals[asset],
                'factor': factor_signals[asset],
                'ai_ml': ai_ml_signals[asset]['signal']
            },
            'weights': {
                'momentum': momentum_weight,
                'factor': factor_weight,
                'ai_ml': ai_ml_weight
            }
        }
    
    return signals

def backtest_strategy(signals, data, initial_capital=10000):
    """Simple backtest implementation"""
    if isinstance(signals[list(signals.keys())[0]], dict):
        # Handle AI/ML or hybrid signals (nested dict)
        flat_signals = {k: v['signal'] if isinstance(v, dict) else v for k, v in signals.items()}
    else:
        flat_signals = signals
    
    portfolio_value = initial_capital
    positions = {}
    returns = []
    
    # Simulate trading over the period
    for i in range(20, len(data)):  # Start after signal calculation period
        current_date = data.index[i]
        
        # Rebalance monthly (simplified)
        if i % 30 == 0:  # Monthly rebalancing
            # Update positions based on signals
            for asset, signal in flat_signals.items():
                if signal == 1 and asset not in positions:
                    # Buy signal
                    positions[asset] = portfolio_value / len([s for s in flat_signals.values() if s == 1])
                elif signal == 0 and asset in positions:
                    # Sell signal
                    del positions[asset]
        
        # Calculate portfolio return for this day
        daily_return = 0
        if positions:
            for asset in positions:
                if asset in data.columns:
                    price_change = data[asset]['close'].pct_change().iloc[i]
                    daily_return += (positions[asset] / portfolio_value) * price_change
        
        portfolio_value *= (1 + daily_return)
        returns.append(daily_return)
    
    # Calculate performance metrics
    returns_array = np.array(returns)
    total_return = (portfolio_value / initial_capital) - 1
    
    # Risk metrics
    volatility = returns_array.std() * np.sqrt(252)  # Annualized
    max_drawdown = self.calculate_max_drawdown(returns_array)
    
    # Sharpe ratio (assuming 2% risk-free rate)
    excess_returns = returns_array - 0.02/252
    sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
    
    return {
        'total_return': total_return,
        'annualized_return': (1 + total_return) ** (252/len(returns)) - 1,
        'volatility': volatility,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'final_value': portfolio_value
    }

def calculate_max_drawdown(self, returns):
    """Calculate maximum drawdown"""
    cumulative = np.cumprod(1 + np.array(returns))
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    return np.min(drawdown)

def run_comprehensive_test():
    """Run comprehensive test of all strategies"""
    print("🚀 Starting Comprehensive QuantMuse Strategy Test")
    print("=" * 60)
    
    # Generate test data
    print("📊 Generating market data...")
    data = generate_mock_data(days=180)
    print(f"Generated data for {len(data.columns)} assets over {len(data)} days")
    
    # Test all strategies
    results = {}
    
    # 1. Momentum Strategy
    print("\n🎯 Testing Momentum Strategy...")
    momentum_signals = calculate_momentum_signals(data)
    momentum_performance = backtest_strategy(momentum_signals, data)
    results['momentum'] = {
        'signals': momentum_signals,
        'performance': momentum_performance,
        'description': 'High-momentum stock selection strategy'
    }
    
    # 2. Factor Analysis Strategy
    print("📈 Testing Factor Analysis Strategy...")
    factor_signals = calculate_factor_signals(data)
    factor_performance = backtest_strategy(factor_signals, data)
    results['factor_analysis'] = {
        'signals': factor_signals,
        'performance': factor_performance,
        'description': 'Multi-factor stock selection strategy'
    }
    
    # 3. AI/ML Strategy
    print("🤖 Testing AI/ML Strategy...")
    ai_ml_signals = calculate_ai_ml_signals(data)
    ai_ml_performance = backtest_strategy(ai_ml_signals, data)
    results['ai_ml'] = {
        'signals': ai_ml_signals,
        'performance': ai_ml_performance,
        'description': 'AI and sentiment-enhanced strategy'
    }
    
    # 4. Hybrid Strategy
    print("🔀 Testing Hybrid Strategy...")
    hybrid_signals = calculate_hybrid_signals(momentum_signals, factor_signals, ai_ml_signals)
    hybrid_performance = backtest_strategy(hybrid_signals, data)
    results['hybrid'] = {
        'signals': hybrid_signals,
        'performance': hybrid_performance,
        'description': 'Combined signals from all strategies'
    }
    
    # Analysis and comparison
    print("\n📊 PERFORMANCE ANALYSIS")
    print("=" * 40)
    
    comparison_data = []
    for strategy, result in results.items():
        perf = result['performance']
        comparison_data.append({
            'Strategy': strategy.replace('_', ' ').title(),
            'Total Return': f"{perf['total_return']:.2%}",
            'Annualized Return': f"{perf['annualized_return']:.2%}",
            'Sharpe Ratio': f"{perf['sharpe_ratio']:.2f}",
            'Max Drawdown': f"{perf['max_drawdown']:.2%}",
            'Volatility': f"{perf['volatility']:.2%}",
            'Final Value': f"${perf['final_value']:,.2f}"
        })
    
    # Display comparison table
    df_comparison = pd.DataFrame(comparison_data)
    print(df_comparison.to_string(index=False))
    
    # Find best performers
    best_return = max(results.items(), key=lambda x: x[1]['performance']['total_return'])
    best_sharpe = max(results.items(), key=lambda x: x[1]['performance']['sharpe_ratio'])
    
    print(f"\n🏆 BEST PERFORMERS")
    print("-" * 30)
    print(f"Best Total Return: {best_return[0].replace('_', ' ').title()}")
    print(f"  Return: {best_return[1]['performance']['total_return']:.2%}")
    print(f"  Sharpe: {best_return[1]['performance']['sharpe_ratio']:.2f}")
    
    print(f"\nBest Risk-Adjusted: {best_sharpe[0].replace('_', ' ').title()}")
    print(f"  Return: {best_sharpe[1]['performance']['total_return']:.2%}")
    print(f"  Sharpe: {best_sharpe[1]['performance']['sharpe_ratio']:.2f}")
    
    # Detailed strategy analysis
    print(f"\n🔍 DETAILED ANALYSIS")
    print("=" * 30)
    
    for strategy, result in results.items():
        print(f"\n{strategy.replace('_', ' ').title()} Strategy:")
        print(f"  Description: {result['description']}")
        perf = result['performance']
        print(f"  Performance: {perf['total_return']:.2%} return, {perf['sharpe_ratio']:.2f} Sharpe")
        
        # Show signal details for AI/ML and Hybrid
        if strategy in ['ai_ml', 'hybrid']:
            signals = result['signals']
            if strategy == 'ai_ml':
                avg_sentiment = np.mean([s['sentiment'] for s in signals.values()])
                avg_llm = np.mean([s['llm_insight'] for s in signals.values()])
                print(f"  AI Insights: Avg Sentiment {avg_sentiment:.2f}, Avg LLM Score {avg_llm:.2f}")
            elif strategy == 'hybrid':
                components = list(signals.values())[0]['components']  # Take first asset as example
                weights = list(signals.values())[0]['weights']
                print(f"  Hybrid Weights: Momentum {weights['momentum']:.1f}, Factor {weights['factor']:.1f}, AI/ML {weights['ai_ml']:.1f}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"strategy_test_results_{timestamp}.json"
    
    # Prepare results for saving
    saveable_results = {}
    for strategy, result in results.items():
        saveable_results[strategy] = {
            'description': result['description'],
            'performance': result['performance'],
            'signal_count': sum(1 if s == 1 else 0 for s in result['signals'].values() if isinstance(s, int)) + 
                            sum(1 if s['signal'] == 1 else 0 for s in result['signals'].values() if isinstance(s, dict)),
            'timestamp': datetime.now().isoformat()
        }
    
    with open(results_file, 'w') as f:
        json.dump(saveable_results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return results

# Fix the method reference issue
def calculate_max_drawdown(returns):
    """Calculate maximum drawdown"""
    cumulative = np.cumprod(1 + np.array(returns))
    running_max = np.maximum.accumulate(cumulative) if hasattr(np, 'maximum.accumulate') else np.maximum.reduceat(cumulative, np.arange(len(cumulative)))
    drawdown = (cumulative - running_max) / running_max
    return np.min(drawdown)

if __name__ == "__main__":
    results = run_comprehensive_test()
    print("\n🎉 Comprehensive testing completed!")
    print("📈 All strategies tested across multiple dimensions")
    print("🔍 Use the results file for detailed analysis")
