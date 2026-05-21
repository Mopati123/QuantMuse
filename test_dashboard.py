#!/usr/bin/env python3
"""
Interactive Dashboard for Comprehensive Trading Test Results
Real-time visualization and analysis of all strategy performance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
import glob

class TestResultsDashboard:
    """Interactive dashboard for comprehensive test results"""
    
    def __init__(self):
        self.load_results()
    
    def load_results(self):
        """Load latest test results"""
        # Find latest results file
        result_files = glob.glob("comprehensive_test_results_*.json")
        analysis_files = glob.glob("comprehensive_test_analysis_*.json")
        
        if result_files:
            latest_result = max(result_files)
            with open(latest_result, 'r') as f:
                self.results = json.load(f)
        else:
            self.results = {}
        
        if analysis_files:
            latest_analysis = max(analysis_files)
            with open(latest_analysis, 'r') as f:
                self.analysis = json.load(f)
        else:
            self.analysis = {}
    
    def render_sidebar(self):
        """Render sidebar with filters and controls"""
        st.sidebar.title("🎛️ Test Controls")
        
        # Test configuration filters
        st.sidebar.subheader("Filters")
        
        # Strategy filter
        if self.results:
            all_strategies = list(set(r['config']['strategy'] for r in self.results.values() if 'config' in r))
            selected_strategies = st.sidebar.multiselect(
                "Strategies", all_strategies, default=all_strategies
            )
        else:
            selected_strategies = []
        
        # Data source filter
        if self.results:
            all_sources = list(set(r['config']['data_source'] for r in self.results.values() if 'config' in r))
            selected_sources = st.sidebar.multiselect(
                "Data Sources", all_sources, default=all_sources
            )
        else:
            selected_sources = []
        
        # Timeframe filter
        if self.results:
            all_timeframes = list(set(r['config']['timeframe']['name'] for r in self.results.values() if 'config' in r))
            selected_timeframes = st.sidebar.multiselect(
                "Timeframes", all_timeframes, default=all_timeframes
            )
        else:
            selected_timeframes = []
        
        # Performance metrics
        st.sidebar.subheader("Display Options")
        show_returns = st.sidebar.checkbox("Show Returns", True)
        show_risk = st.sidebar.checkbox("Show Risk Metrics", True)
        show_comparison = st.sidebar.checkbox("Show Comparisons", True)
        
        return {
            'strategies': selected_strategies,
            'sources': selected_sources,
            'timeframes': selected_timeframes,
            'show_returns': show_returns,
            'show_risk': show_risk,
            'show_comparison': show_comparison
        }
    
    def filter_results(self, filters):
        """Filter results based on sidebar selections"""
        filtered_results = {}
        
        for test_id, result in self.results.items():
            if 'config' not in result or 'backtest_result' not in result:
                continue
            
            config = result['config']
            
            # Apply filters
            if (filters['strategies'] and config['strategy'] not in filters['strategies']):
                continue
            if (filters['sources'] and config['data_source'] not in filters['sources']):
                continue
            if (filters['timeframes'] and config['timeframe']['name'] not in filters['timeframes']):
                continue
            
            filtered_results[test_id] = result
        
        return filtered_results
    
    def render_performance_overview(self, filters):
        """Render performance overview section"""
        st.header("📊 Performance Overview")
        
        filtered_results = self.filter_results(filters)
        
        if not filtered_results:
            st.warning("No results match the selected filters.")
            return
        
        # Create performance DataFrame
        performance_data = []
        for test_id, result in filtered_results.items():
            if 'backtest_result' not in result:
                continue
            
            performance = result['backtest_result'].get('performance_metrics', {})
            config = result['config']
            
            performance_data.append({
                'Test ID': test_id,
                'Strategy': config['strategy'],
                'Data Source': config['data_source'],
                'Timeframe': config['timeframe']['name'],
                'Total Return': performance.get('total_return', 0),
                'Sharpe Ratio': performance.get('sharpe_ratio', 0),
                'Max Drawdown': performance.get('max_drawdown', 0),
                'Win Rate': performance.get('win_rate', 0),
                'Volatility': performance.get('volatility', 0)
            })
        
        if performance_data:
            df = pd.DataFrame(performance_data)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Tests", len(df))
            with col2:
                st.metric("Avg Return", f"{df['Total Return'].mean():.2%}")
            with col3:
                st.metric("Avg Sharpe", f"{df['Sharpe Ratio'].mean():.2f}")
            with col4:
                st.metric("Best Return", f"{df['Total Return'].max():.2%}")
            
            # Performance table
            if filters['show_returns']:
                st.subheader("📈 Performance Table")
                st.dataframe(df, use_container_width=True)
    
    def render_strategy_comparison(self, filters):
        """Render strategy comparison charts"""
        if not filters['show_comparison']:
            return
        
        st.header("🔍 Strategy Comparison")
        
        filtered_results = self.filter_results(filters)
        
        if not filtered_results:
            return
        
        # Group by strategy
        strategy_data = {}
        for test_id, result in filtered_results.items():
            if 'backtest_result' not in result:
                continue
            
            strategy = result['config']['strategy']
            performance = result['backtest_result'].get('performance_metrics', {})
            
            if strategy not in strategy_data:
                strategy_data[strategy] = []
            strategy_data[strategy].append(performance)
        
        if not strategy_data:
            return
        
        # Create comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Returns Comparison")
            
            returns_data = []
            for strategy, performances in strategy_data.items():
                for perf in performances:
                    returns_data.append({
                        'Strategy': strategy,
                        'Total Return': perf.get('total_return', 0),
                        'Metric': 'Total Return'
                    })
            
            if returns_data:
                df_returns = pd.DataFrame(returns_data)
                fig_returns = px.box(
                    df_returns, x='Strategy', y='Total Return',
                    title="Total Return Distribution by Strategy"
                )
                st.plotly_chart(fig_returns, use_container_width=True)
        
        with col2:
            st.subheader("Risk-Adjusted Performance")
            
            sharpe_data = []
            for strategy, performances in strategy_data.items():
                for perf in performances:
                    sharpe_data.append({
                        'Strategy': strategy,
                        'Sharpe Ratio': perf.get('sharpe_ratio', 0),
                        'Metric': 'Sharpe Ratio'
                    })
            
            if sharpe_data:
                df_sharpe = pd.DataFrame(sharpe_data)
                fig_sharpe = px.box(
                    df_sharpe, x='Strategy', y='Sharpe Ratio',
                    title="Sharpe Ratio Distribution by Strategy"
                )
                st.plotly_chart(fig_sharpe, use_container_width=True)
    
    def render_risk_analysis(self, filters):
        """Render risk analysis section"""
        if not filters['show_risk']:
            return
        
        st.header("⚠️ Risk Analysis")
        
        filtered_results = self.filter_results(filters)
        
        if not filtered_results:
            return
        
        # Risk metrics scatter plot
        risk_data = []
        for test_id, result in filtered_results.items():
            if 'backtest_result' not in result:
                continue
            
            performance = result['backtest_result'].get('performance_metrics', {})
            config = result['config']
            
            risk_data.append({
                'Test ID': test_id,
                'Strategy': config['strategy'],
                'Data Source': config['data_source'],
                'Total Return': performance.get('total_return', 0),
                'Max Drawdown': performance.get('max_drawdown', 0),
                'Volatility': performance.get('volatility', 0),
                'Sharpe Ratio': performance.get('sharpe_ratio', 0)
            })
        
        if risk_data:
            df_risk = pd.DataFrame(risk_data)
            
            # Risk vs Return scatter
            fig_risk_return = px.scatter(
                df_risk, x='Max Drawdown', y='Total Return',
                color='Strategy', size='Sharpe Ratio',
                title="Risk vs Return Profile",
                labels={'Max Drawdown': 'Max Drawdown', 'Total Return': 'Total Return'}
            )
            st.plotly_chart(fig_risk_return, use_container_width=True)
            
            # Risk metrics table
            st.subheader("Risk Metrics Summary")
            risk_summary = df_risk.groupby('Strategy').agg({
                'Max Drawdown': ['mean', 'std'],
                'Volatility': ['mean', 'std'],
                'Sharpe Ratio': 'mean'
            }).round(4)
            st.dataframe(risk_summary)
    
    def render_best_performers(self):
        """Render best performers section"""
        if 'best_performers' not in self.analysis:
            return
        
        st.header("🏆 Best Performers")
        
        best_by_return = self.analysis['best_performers'].get('by_total_return', [])
        best_by_sharpe = self.analysis['best_performers'].get('by_sharpe_ratio', [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🥇 Highest Returns")
            
            if best_by_return:
                for i, performer in enumerate(best_by_return[:5], 1):
                    config = performer['config']
                    st.write(f"**{i}. {performer['test_id']}**")
                    st.write(f"Return: `{performer['total_return']:.2%}`")
                    st.write(f"Sharpe: `{performer['sharpe_ratio']:.2f}`")
                    st.write(f"Strategy: `{config['strategy']}`")
                    st.write(f"Data: `{config['data_source']}`")
                    st.write("---")
        
        with col2:
            st.subheader("⭐ Best Risk-Adjusted")
            
            if best_by_sharpe:
                for i, performer in enumerate(best_by_sharpe[:5], 1):
                    config = performer['config']
                    st.write(f"**{i}. {performer['test_id']}**")
                    st.write(f"Sharpe: `{performer['sharpe_ratio']:.2f}`")
                    st.write(f"Return: `{performer['total_return']:.2%}`")
                    st.write(f"Max DD: `{performer['max_drawdown']:.2%}`")
                    st.write(f"Strategy: `{config['strategy']}`")
                    st.write("---")
    
    def render_detailed_analysis(self):
        """Render detailed analysis section"""
        st.header("🔬 Detailed Analysis")
        
        # Test selection
        if self.results:
            test_ids = list(self.results.keys())
            selected_test = st.selectbox("Select Test for Detailed Analysis", test_ids)
            
            if selected_test and selected_test in self.results:
                result = self.results[selected_test]
                
                # Configuration details
                st.subheader("Configuration")
                config = result['config']
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Strategy:**", config['strategy'])
                    st.write("**Data Source:**", config['data_source'])
                    st.write("**Timeframe:**", f"{config['timeframe']['name']} ({config['timeframe']['days']} days)")
                
                with col2:
                    if 'strategy_result' in result and 'parameters' in result['strategy_result']:
                        params = result['strategy_result']['parameters']
                        st.write("**Parameters:**")
                        for param, value in params.items():
                            st.write(f"• {param}: {value}")
                
                # Performance metrics
                if 'backtest_result' in result:
                    st.subheader("Performance Metrics")
                    performance = result['backtest_result'].get('performance_metrics', {})
                    
                    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                    
                    with metrics_col1:
                        st.metric("Total Return", f"{performance.get('total_return', 0):.2%}")
                        st.metric("Annualized Return", f"{performance.get('annualized_return', 0):.2%}")
                        st.metric("Sharpe Ratio", f"{performance.get('sharpe_ratio', 0):.2f}")
                    
                    with metrics_col2:
                        st.metric("Max Drawdown", f"{performance.get('max_drawdown', 0):.2%}")
                        st.metric("Volatility", f"{performance.get('volatility', 0):.2%}")
                        st.metric("Win Rate", f"{performance.get('win_rate', 0):.2%}")
                    
                    with metrics_col3:
                        st.metric("Profit Factor", f"{performance.get('profit_factor', 0):.2f}")
                        st.metric("Sortino Ratio", f"{performance.get('sortino_ratio', 0):.2f}")
                        st.metric("Calmar Ratio", f"{performance.get('calmar_ratio', 0):.2f}")
    
    def run(self):
        """Run the dashboard"""
        st.set_page_config(
            page_title="QuantMuse Test Results",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("🚀 QuantMuse Comprehensive Test Results")
        st.markdown("Interactive dashboard for analyzing trading strategy performance across all configurations")
        
        # Sidebar controls
        filters = self.render_sidebar()
        
        # Main content
        if not self.results:
            st.error("No test results found. Please run comprehensive_test.py first.")
            return
        
        # Render sections
        self.render_performance_overview(filters)
        st.divider()
        
        self.render_strategy_comparison(filters)
        st.divider()
        
        self.render_risk_analysis(filters)
        st.divider()
        
        self.render_best_performers()
        st.divider()
        
        self.render_detailed_analysis()
        
        # Footer
        st.markdown("---")
        st.markdown("*Dashboard generated by QuantMuse Comprehensive Testing Framework*")

def main():
    """Main execution"""
    dashboard = TestResultsDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
