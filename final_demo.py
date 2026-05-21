#!/usr/bin/env python3
"""
Final Working Demo - QuantMuse Trading Strategies
Demonstrates all strategies with realistic parameters
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

def generate_realistic_data():
    """Generate realistic market data"""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    
    # Create price data with different trends
    assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    np.random.seed(42)
    
    all_data = []
    trends = [0.15, 0.08, 0.12, -0.05, 0.20]  # Different performance trends
    
    for i, asset in enumerate(assets):
        # Base trend + random walk
        base_return = trends[i] / 252  # Daily trend
        returns = np.random.normal(base_return, 0.025, len(dates))  # Add volatility
        
        prices = 100 * np.cumprod(1 + returns)
        volumes = np.random.randint(500000, 2000000, len(dates))
        
        for j, date in enumerate(dates):
            all_data.append({
                'date': date,
                'asset': asset,
                'close': prices[j],
                'volume': volumes[j]
            })
    
    return pd.DataFrame(all_data)

def test_strategy_performance(data, strategy_name, signals):
    """Test strategy performance"""
    selected_assets = signals[signals['signal'] == 1]['asset'].unique()
    
    if len(selected_assets) == 0:
        return {
            'strategy': strategy_name,
            'selected_count': 0,
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0
        }
    
    # Calculate returns for selected assets
    returns = []
    for asset in selected_assets:
        asset_data = data[data['asset'] == asset].sort_values('date')
        prices = asset_data['close'].values
        
        if len(prices) >= 40:  # Use 40-day holding period
            initial_price = prices[-40]
            final_price = prices[-1]
            asset_return = (final_price / initial_price) - 1
            returns.append(asset_return)
    
    if not returns:
        return {
            'strategy': strategy_name,
            'selected_count': len(selected_assets),
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0
        }
    
    # Performance metrics
    avg_return = np.mean(returns)
    volatility = np.std(returns) if len(returns) > 1 else 0.01
    sharpe_ratio = avg_return / volatility if volatility > 0 else 0
    
    # Simple max drawdown
    cumulative_returns = np.cumprod(1 + np.array(returns))
    running_max = np.maximum.accumulate(cumulative_returns) if hasattr(np, 'maximum.accumulate') else np.maximum.reduceat(cumulative_returns, np.arange(len(cumulative_returns)))
    drawdowns = (cumulative_returns - running_max) / running_max
    max_drawdown = np.min(drawdowns) if len(drawdowns) > 0 else 0
    
    return {
        'strategy': strategy_name,
        'selected_count': len(selected_assets),
        'selected_assets': list(selected_assets),
        'total_return': avg_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': abs(max_drawdown),
        'volatility': volatility
    }

def run_momentum_test(data):
    """Run momentum strategy test"""
    print("🎯 Testing Momentum Strategy...")
    
    results = []
    for asset in data['asset'].unique():
        asset_data = data[data['asset'] == asset].sort_values('date')
        prices = asset_data['close'].values
        
        if len(prices) >= 20:
            momentum = (prices[-1] / prices[-20] - 1) * 100
            signal = 1 if momentum > 2 else 0  # Lower threshold
            
            results.append({
                'asset': asset,
                'momentum': momentum,
                'signal': signal
            })
    
    signals_df = pd.DataFrame(results)
    return test_strategy_performance(data, "Momentum", signals_df)

def run_factor_test(data):
    """Run factor analysis test"""
    print("📊 Testing Factor Analysis Strategy...")
    
    results = []
    for asset in data['asset'].unique():
        asset_data = data[data['asset'] == asset].sort_values('date')
        prices = asset_data['close'].values
        volumes = asset_data['volume'].values
        
        if len(prices) >= 20:
            momentum = (prices[-1] / prices[-20] - 1) * 100
            volume_factor = volumes[-20:].mean() / volumes.mean()
            price_series = pd.Series(prices)
            volatility = price_series.pct_change().iloc[-20:].std()
            
            # Combined score
            score = 0.4 * momentum + 0.3 * volume_factor + 0.3 * (1 / (1 + volatility))
            signal = 1 if score > np.percentile([score], 60) else 0  # Top 40%
            
            results.append({
                'asset': asset,
                'score': score,
                'signal': signal
            })
    
    signals_df = pd.DataFrame(results)
    return test_strategy_performance(data, "Factor Analysis", signals_df)

def run_ai_ml_test(data):
    """Run AI/ML strategy test"""
    print("🤖 Testing AI/ML Strategy...")
    
    results = []
    for asset in data['asset'].unique():
        asset_data = data[data['asset'] == asset].sort_values('date')
        prices = asset_data['close'].values
        
        if len(prices) >= 20:
            momentum = (prices[-1] / prices[-20] - 1) * 100
            price_series = pd.Series(prices)
            volatility = price_series.pct_change().iloc[-20:].std()
            
            # Mock AI signals with some bias
            sentiment = np.random.uniform(-0.3, 0.9)
            llm_insight = np.random.uniform(0.4, 0.95)
            
            # Combined AI signal
            ai_score = 0.4 * (momentum / 20) + 0.3 * sentiment + 0.3 * llm_insight
            signal = 1 if ai_score > 0.5 else 0  # Lower threshold
            
            results.append({
                'asset': asset,
                'ai_score': ai_score,
                'sentiment': sentiment,
                'llm_insight': llm_insight,
                'signal': signal
            })
    
    signals_df = pd.DataFrame(results)
    return test_strategy_performance(data, "AI/ML", signals_df)

def run_hybrid_test(data, momentum_perf, factor_perf, ai_ml_perf):
    """Run hybrid strategy test"""
    print("🔀 Testing Hybrid Strategy...")
    
    # Create hybrid signals based on individual strategy performance
    results = []
    all_assets = data['asset'].unique()
    
    for asset in all_assets:
        # Get individual signals
        momentum_signal = 1 if asset in momentum_perf.get('selected_assets', []) else 0
        factor_signal = 1 if asset in factor_perf.get('selected_assets', []) else 0
        ai_ml_signal = 1 if asset in ai_ml_perf.get('selected_assets', []) else 0
        
        # Weight based on past performance (dynamic weighting)
        momentum_weight = max(momentum_perf['total_return'], 0) / 0.15  # Normalize
        factor_weight = max(factor_perf['total_return'], 0) / 0.15
        ai_ml_weight = max(ai_ml_perf['total_return'], 0) / 0.15
        
        total_weight = momentum_weight + factor_weight + ai_ml_weight
        if total_weight > 0:
            momentum_weight /= total_weight
            factor_weight /= total_weight
            ai_ml_weight /= total_weight
        
        # Combined signal
        combined = (momentum_weight * momentum_signal + 
                    factor_weight * factor_signal + 
                    ai_ml_weight * ai_ml_signal)
        
        signal = 1 if combined > 0.5 else 0
        
        results.append({
            'asset': asset,
            'combined_score': combined,
            'signal': signal,
            'weights': {
                'momentum': momentum_weight,
                'factor': factor_weight,
                'ai_ml': ai_ml_weight
            }
        })
    
    signals_df = pd.DataFrame(results)
    return test_strategy_performance(data, "Hybrid", signals_df)

def run_comprehensive_demo():
    """Run the complete comprehensive demo"""
    print("🚀 QuantMuse Comprehensive Trading Strategy Demo")
    print("=" * 60)
    
    # Generate realistic data
    print("📈 Generating realistic market data...")
    data = generate_realistic_data()
    print(f"Generated {len(data['asset'].unique())} assets over {len(data)} days")
    
    # Run all strategies
    momentum_perf = run_momentum_test(data)
    factor_perf = run_factor_test(data)
    ai_ml_perf = run_ai_ml_test(data)
    hybrid_perf = run_hybrid_test(data, momentum_perf, factor_perf, ai_ml_perf)
    
    # Results summary
    results = {
        'momentum': momentum_perf,
        'factor_analysis': factor_perf,
        'ai_ml': ai_ml_perf,
        'hybrid': hybrid_perf
    }
    
    # Display results
    print("\n📊 STRATEGY PERFORMANCE RESULTS")
    print("=" * 50)
    
    for strategy_key, perf in results.items():
        print(f"\n{perf['strategy']} Strategy:")
        print(f"  Assets Selected: {perf['selected_count']}")
        if perf.get('selected_assets'):
            selected_list = perf['selected_assets']
            print(f"  Selected: {', '.join(selected_list[:3])}" + 
                           ("..." if len(selected_list) > 3 else ""))
        print(f"  Total Return: {perf['total_return']:.2%}")
        print(f"  Sharpe Ratio: {perf['sharpe_ratio']:.2f}")
        print(f"  Max Drawdown: {perf['max_drawdown']:.2%}")
        if 'volatility' in perf:
            print(f"  Volatility: {perf['volatility']:.2%}")
    
    # Performance comparison table
    print(f"\n📈 PERFORMANCE COMPARISON")
    print("-" * 50)
    print(f"{'Strategy':<15} | {'Return':<8} | {'Sharpe':<7} | {'Drawdown':<10} | {'Selected':<9}")
    print("-" * 50)
    
    for strategy_key, perf in results.items():
        print(f"{perf['strategy']:<15} | {perf['total_return']:>7.2%} | {perf['sharpe_ratio']:>7.2f} | {perf['max_drawdown']:>9.2%} | {perf['selected_count']:>9}")
    
    # Best performers
    print(f"\n🏆 TOP PERFORMERS")
    print("-" * 30)
    
    # Sort by different metrics
    by_return = sorted(results.items(), key=lambda x: x[1]['total_return'], reverse=True)
    by_sharpe = sorted(results.items(), key=lambda x: x[1]['sharpe_ratio'], reverse=True)
    by_selection = sorted(results.items(), key=lambda x: x[1]['selected_count'], reverse=True)
    
    print(f"Best Total Return: {by_return[0][1]['strategy']} ({by_return[0][1]['total_return']:.2%})")
    print(f"Best Sharpe Ratio: {by_sharpe[0][1]['strategy']} ({by_sharpe[0][1]['sharpe_ratio']:.2f})")
    print(f"Most Selective: {by_selection[0][1]['strategy']} ({by_selection[0][1]['selected_count']} assets)")
    
    # Strategy insights
    print(f"\n💡 KEY INSIGHTS")
    print("-" * 25)
    
    avg_return = np.mean([perf['total_return'] for perf in results.values()])
    avg_sharpe = np.mean([perf['sharpe_ratio'] for perf in results.values()])
    
    print(f"Average Return Across All Strategies: {avg_return:.2%}")
    print(f"Average Sharpe Ratio: {avg_sharpe:.2f}")
    
    # Hybrid vs individual comparison
    if hybrid_perf['total_return'] > avg_return:
        print(f"✅ Hybrid Strategy Outperforms Average (+{(hybrid_perf['total_return'] - avg_return):.2%})")
    else:
        print(f"⚠️  Hybrid Strategy Underperforms Average ({(hybrid_perf['total_return'] - avg_return):.2%})")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"comprehensive_demo_results_{timestamp}.json"
    
    # Prepare saveable results
    saveable_results = {}
    for strategy_key, perf in results.items():
        saveable_results[strategy_key] = {
            **perf,
            'timestamp': datetime.now().isoformat()
        }
    
    with open(results_file, 'w') as f:
        json.dump(saveable_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed Results saved to: {results_file}")
    
    # Recommendations
    print(f"\n📋 RECOMMENDATIONS")
    print("-" * 25)
    
    if hybrid_perf['sharpe_ratio'] > avg_sharpe:
        print("✅ Consider deploying Hybrid Strategy for production")
        print("✅ Dynamic weighting based on performance shows promise")
    else:
        print("⚠️  Refine individual strategy parameters before deployment")
        print("⚠️  Consider market regime analysis for better timing")
    
    print("\n🎉 Comprehensive Demo Completed!")
    return results

if __name__ == "__main__":
    results = run_comprehensive_demo()
