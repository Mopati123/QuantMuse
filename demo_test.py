#!/usr/bin/env python3
"""
Quick Demo of QuantMuse Trading Strategies
Simple demonstration of all strategy types
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

def generate_simple_data():
    """Generate simple test data"""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    
    # Create price data for 5 assets
    assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    np.random.seed(42)
    
    all_data = []
    for asset in assets:
        prices = 100 + np.cumsum(np.random.normal(0.001, 0.02, len(dates)))
        volumes = np.random.randint(1000000, 5000000, len(dates))
        
        for i, date in enumerate(dates):
            all_data.append({
                'date': date,
                'asset': asset,
                'close': prices[i],
                'volume': volumes[i]
            })
    
    return pd.DataFrame(all_data)

def test_momentum_strategy(data):
    """Test momentum strategy"""
    print("🎯 Testing Momentum Strategy...")
    
    # Calculate momentum for each asset
    results = []
    for asset in data['asset'].unique():
        asset_data = data[data['asset'] == asset].sort_values('date')
        prices = asset_data['close'].values
        
        # Simple momentum: last 20 days return
        if len(prices) >= 20:
            momentum = (prices[-1] / prices[-20] - 1) * 100
            signal = 1 if momentum > 5 else 0  # 5% threshold
            
            results.append({
                'asset': asset,
                'strategy': 'momentum',
                'momentum': momentum,
                'signal': signal,
                'final_price': prices[-1]
            })
    
    return pd.DataFrame(results)

def test_factor_strategy(data):
    """Test multi-factor strategy"""
    print("📊 Testing Factor Analysis Strategy...")
    
    results = []
    for asset in data['asset'].unique():
        asset_data = data[data['asset'] == asset].sort_values('date')
        prices = asset_data['close'].values
        volumes = asset_data['volume'].values
        
        if len(prices) >= 20:
            # Multiple factors
            momentum = (prices[-1] / prices[-20] - 1) * 100
            avg_volume = volumes[-20:].mean() / volumes.mean()
            price_series = pd.Series(prices)
            volatility = price_series.pct_change().iloc[-20:].std()
            
            # Combined score
            score = 0.4 * momentum + 0.3 * avg_volume + 0.3 * (1 / (1 + volatility))
            signal = 1 if score > np.percentile([score], 70) else 0
            
            results.append({
                'asset': asset,
                'strategy': 'factor_analysis',
                'score': score,
                'signal': signal,
                'final_price': prices[-1]
            })
    
    return pd.DataFrame(results)

def test_ai_ml_strategy(data):
    """Test AI/ML enhanced strategy"""
    print("🤖 Testing AI/ML Strategy...")
    
    results = []
    for asset in data['asset'].unique():
        asset_data = data[data['asset'] == asset].sort_values('date')
        prices = asset_data['close'].values
        
        if len(prices) >= 20:
            # Technical factors
            momentum = (prices[-1] / prices[-20] - 1) * 100
            price_series = pd.Series(prices)
            volatility = price_series.pct_change().iloc[-20:].std()
            
            # Mock AI signals
            sentiment = np.random.uniform(-0.5, 0.8)  # News sentiment
            llm_insight = np.random.uniform(0.3, 0.9)  # LLM analysis
            
            # Combined AI signal
            ai_score = 0.4 * (momentum / 20) + 0.3 * sentiment + 0.3 * llm_insight
            signal = 1 if ai_score > 0.6 else 0
            
            results.append({
                'asset': asset,
                'strategy': 'ai_ml',
                'ai_score': ai_score,
                'sentiment': sentiment,
                'llm_insight': llm_insight,
                'signal': signal,
                'final_price': prices[-1]
            })
    
    return pd.DataFrame(results)

def test_hybrid_strategy(momentum_results, factor_results, ai_ml_results):
    """Test hybrid strategy combining all approaches"""
    print("🔀 Testing Hybrid Strategy...")
    
    results = []
    for asset in momentum_results['asset']:
        # Get signals from all strategies
        momentum_signal = momentum_results[momentum_results['asset'] == asset]['signal'].iloc[0]
        factor_signal = factor_results[factor_results['asset'] == asset]['signal'].iloc[0]
        ai_ml_signal = ai_ml_results[ai_ml_results['asset'] == asset]['signal'].iloc[0]
        
        # Weighted combination
        combined = 0.3 * momentum_signal + 0.3 * factor_signal + 0.4 * ai_ml_signal
        signal = 1 if combined > 0.6 else 0
        
        results.append({
            'asset': asset,
            'strategy': 'hybrid',
            'combined_score': combined,
            'signal': signal,
            'momentum_signal': momentum_signal,
            'factor_signal': factor_signal,
            'ai_ml_signal': ai_ml_signal
        })
    
    return pd.DataFrame(results)

def calculate_performance(signals_df, data):
    """Calculate simple performance metrics"""
    selected_assets = signals_df[signals_df['signal'] == 1]['asset'].tolist()
    
    if not selected_assets:
        return {
            'total_return': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'selected_assets': 0
        }
    
    # Get final prices for selected assets
    final_prices = []
    initial_prices = []
    
    for asset in selected_assets:
        asset_data = data[data['asset'] == asset].sort_values('date')
        prices = asset_data['close'].values
        if len(prices) >= 20:
            initial_prices.append(prices[0])
            final_prices.append(prices[-1])
    
    if not initial_prices:
        return {
            'total_return': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'selected_assets': 0
        }
    
    # Calculate returns
    returns = np.array(final_prices) / np.array(initial_prices) - 1
    avg_return = np.mean(returns)
    
    # Simple risk metrics
    volatility = np.std(returns) if len(returns) > 1 else 0
    sharpe_ratio = avg_return / volatility if volatility > 0 else 0
    max_drawdown = np.min(np.cumprod(1 + returns) / np.maximum.accumulate(np.cumprod(1 + returns))) if len(returns) > 1 else 0
    
    return {
        'total_return': avg_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': abs(max_drawdown),
        'selected_assets': len(selected_assets),
        'avg_return': avg_return
    }

def run_demo():
    """Run the complete demo"""
    print("🚀 QuantMuse Trading Strategy Demo")
    print("=" * 50)
    
    # Generate test data
    print("📈 Generating market data...")
    data = generate_simple_data()
    print(f"Generated {len(data['asset'].unique())} assets over {len(data)} days")
    
    # Test all strategies
    momentum_results = test_momentum_strategy(data)
    factor_results = test_factor_strategy(data)
    ai_ml_results = test_ai_ml_strategy(data)
    hybrid_results = test_hybrid_strategy(momentum_results, factor_results, ai_ml_results)
    
    # Calculate performance
    print("\n📊 Calculating Performance...")
    momentum_perf = calculate_performance(momentum_results, data)
    factor_perf = calculate_performance(factor_results, data)
    ai_ml_perf = calculate_performance(ai_ml_results, data)
    hybrid_perf = calculate_performance(hybrid_results, data)
    
    # Results summary
    results_summary = {
        'momentum': {**momentum_perf, 'strategy': 'Momentum'},
        'factor_analysis': {**factor_perf, 'strategy': 'Factor Analysis'},
        'ai_ml': {**ai_ml_perf, 'strategy': 'AI/ML'},
        'hybrid': {**hybrid_perf, 'strategy': 'Hybrid'}
    }
    
    # Display results
    print("\n📋 PERFORMANCE RESULTS")
    print("=" * 40)
    
    for strategy_key, result in results_summary.items():
        print(f"\n{result['strategy']} Strategy:")
        print(f"  Selected Assets: {result['selected_assets']}")
        print(f"  Total Return: {result['total_return']:.2%}")
        print(f"  Sharpe Ratio: {result['sharpe_ratio']:.2f}")
        print(f"  Max Drawdown: {result['max_drawdown']:.2%}")
    
    # Find best performer
    best_strategy = max(results_summary.items(), key=lambda x: x[1]['total_return'])
    best_sharpe = max(results_summary.items(), key=lambda x: x[1]['sharpe_ratio'])
    
    print(f"\n🏆 BEST PERFORMERS")
    print("-" * 25)
    print(f"Best Return: {best_strategy[1]['strategy']} ({best_strategy[1]['total_return']:.2%})")
    print(f"Best Sharpe: {best_sharpe[1]['strategy']} ({best_sharpe[1]['sharpe_ratio']:.2f})")
    
    # Strategy insights
    print(f"\n💡 STRATEGY INSIGHTS")
    print("-" * 25)
    
    # Asset selection analysis
    all_selections = {}
    for strategy_key, result in results_summary.items():
        all_selections[result['strategy']] = result['selected_assets']
    
    print("Asset Selection by Strategy:")
    for strategy, count in all_selections.items():
        print(f"  {strategy}: {count} assets")
    
    # Performance comparison
    print(f"\n📈 Performance Comparison:")
    comparison_data = []
    for strategy_key, result in results_summary.items():
        comparison_data.append({
            'Strategy': result['strategy'],
            'Return': f"{result['total_return']:.2%}",
            'Sharpe': f"{result['sharpe_ratio']:.2f}",
            'Risk': f"{result['max_drawdown']:.2%}"
        })
    
    for row in comparison_data:
        print(f"  {row['Strategy']:<12} | {row['Return']:<8} | {row['Sharpe']:<6} | {row['Risk']:<8}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"demo_strategy_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results_summary, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    print("\n🎉 Demo completed!")
    
    return results_summary

if __name__ == "__main__":
    results = run_demo()
