#!/usr/bin/env python3
"""
Test Runner for QuantMuse Multi-Broker System
Simplified test execution for immediate validation
"""

import asyncio
import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_logging():
    """Setup logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def run_basic_tests():
    """Run basic component tests"""
    print("🧪 Starting Basic Component Tests")
    print("=" * 50)
    
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'test_results': {}
    }
    
    # Test 1: Asset Mapper
    print("\n📊 Testing Asset Mapper...")
    try:
        from brokers.asset_mapper import AssetMapper
        mapper = AssetMapper()
        
        # Test basic mapping
        deriv_symbol = mapper.map_to_broker('EUR/USD', 'deriv')
        mt5_symbol = mapper.map_to_broker('EUR/USD', 'mt5')
        
        assert deriv_symbol == 'frxEURUSD', f"Expected frxEURUSD, got {deriv_symbol}"
        assert mt5_symbol == 'EURUSD', f"Expected EURUSD, got {mt5_symbol}"
        
        # Test reverse mapping
        standard_name = mapper.map_from_broker('frxEURUSD', 'deriv')
        assert standard_name == 'EUR/USD', f"Expected EUR/USD, got {standard_name}"
        
        # Test asset info
        asset_info = mapper.get_asset_info('EUR/USD')
        assert asset_info is not None, "Asset info should not be None"
        assert asset_info.asset_type.value == 'forex', "EUR/USD should be forex"
        
        print("✅ Asset Mapper - PASSED")
        results['passed_tests'] += 1
        results['test_results']['Asset Mapper'] = 'PASSED'
        
    except Exception as e:
        print(f"❌ Asset Mapper - FAILED: {e}")
        results['failed_tests'] += 1
        results['test_results']['Asset Mapper'] = f'FAILED: {e}'
    
    results['total_tests'] += 1
    
    # Test 2: Deriv Broker
    print("\n🔄 Testing Deriv Broker...")
    try:
        from brokers.deriv_broker import DerivBroker
        broker = DerivBroker('test_token', demo_mode=True)
        
        assert broker.demo_mode == True, "Demo mode should be True"
        assert broker.api_token == 'test_token', "API token should match"
        
        # Test asset mappings
        assert 'EUR/USD' in broker.asset_mappings['forex'], "EUR/USD should be in forex mappings"
        assert 'Gold' in broker.asset_mappings['commodities'], "Gold should be in commodities mappings"
        
        # Test order parameter mapping
        order_params = {
            'symbol': 'EUR/USD',
            'type': 'CALL',
            'amount': 10,
            'duration': 60
        }
        deriv_order = broker._map_order_to_deriv(order_params)
        assert deriv_order['parameters']['symbol'] == 'frxEURUSD', "Symbol should be mapped to Deriv format"
        assert deriv_order['parameters']['contract_type'] == 'CALL', "Contract type should be CALL"
        
        print("✅ Deriv Broker - PASSED")
        results['passed_tests'] += 1
        results['test_results']['Deriv Broker'] = 'PASSED'
        
    except Exception as e:
        print(f"❌ Deriv Broker - FAILED: {e}")
        results['failed_tests'] += 1
        results['test_results']['Deriv Broker'] = f'FAILED: {e}'
    
    results['total_tests'] += 1
    
    # Test 3: MT5 Broker
    print("\n📈 Testing MT5 Broker...")
    try:
        from brokers.mt5_broker import MT5Broker
        broker = MT5Broker(12345678, 'test_password', 'Demo_Server', demo_mode=True)
        
        assert broker.demo_mode == True, "Demo mode should be True"
        assert broker.login == 12345678, "Login should match"
        
        # Test asset mappings
        assert 'EUR/USD' in broker.asset_mappings['forex'], "EUR/USD should be in forex mappings"
        assert 'XAUUSD' in broker.asset_mappings['commodities'], "XAUUSD should be in commodities mappings"
        
        # Test order parameter mapping
        order_params = {
            'symbol': 'EURUSD',
            'type': 'market_buy',
            'volume': 0.01,
            'price': 1.1000
        }
        mt5_order = broker._map_order_to_mt5(order_params)
        assert mt5_order['symbol'] == 'EURUSD', "Symbol should remain EURUSD"
        assert mt5_order['type'] == 0, "Type should be mapped to MT5 ORDER_TYPE_BUY (0)"
        
        print("✅ MT5 Broker - PASSED")
        results['passed_tests'] += 1
        results['test_results']['MT5 Broker'] = 'PASSED'
        
    except Exception as e:
        print(f"❌ MT5 Broker - FAILED: {e}")
        results['failed_tests'] += 1
        results['test_results']['MT5 Broker'] = f'FAILED: {e}'
    
    results['total_tests'] += 1
    
    # Test 4: Order Router
    print("\n🔀 Testing Order Router...")
    try:
        from brokers.multi_broker_router import MultiBrokerOrderRouter, RoutingStrategy, OrderRequest
        router = MultiBrokerOrderRouter()
        
        # Test configuration
        assert router.config['strategy'] == RoutingStrategy.COST_OPTIMIZED, "Default strategy should be cost_optimized"
        assert router.config['split_orders'] == True, "Split orders should be enabled by default"
        
        # Test order mapping
        order_request = OrderRequest('EUR/USD', 'forex', 'BUY', 0.1)
        deriv_order = router._map_order_to_broker('deriv', order_request)
        assert 'symbol' in deriv_order, "Deriv order should have symbol"
        assert 'type' in deriv_order, "Deriv order should have type"
        
        mt5_order = router._map_order_to_broker('mt5', order_request)
        assert 'symbol' in mt5_order, "MT5 order should have symbol"
        assert 'type' in mt5_order, "MT5 order should have type"
        
        print("✅ Order Router - PASSED")
        results['passed_tests'] += 1
        results['test_results']['Order Router'] = 'PASSED'
        
    except Exception as e:
        print(f"❌ Order Router - FAILED: {e}")
        results['failed_tests'] += 1
        results['test_results']['Order Router'] = f'FAILED: {e}'
    
    results['total_tests'] += 1
    
    # Test 5: Risk Manager
    print("\n⚠️ Testing Risk Manager...")
    try:
        from brokers.unified_risk_manager import UnifiedRiskManager, create_risk_config
        risk_config = create_risk_config()
        risk_manager = UnifiedRiskManager(risk_config)
        
        # Test risk limits initialization
        assert 'max_total_exposure' in risk_manager.risk_limits, "Should have max_total_exposure limit"
        assert risk_manager.risk_limits['max_total_exposure'].max_value == 200000, "Max total exposure should be 200K"
        
        # Test risk score calculation
        risk_score = risk_manager._calculate_overall_risk_score()
        assert 0 <= risk_score <= 1, "Risk score should be between 0 and 1"
        
        print("✅ Risk Manager - PASSED")
        results['passed_tests'] += 1
        results['test_results']['Risk Manager'] = 'PASSED'
        
    except Exception as e:
        print(f"❌ Risk Manager - FAILED: {e}")
        results['failed_tests'] += 1
        results['test_results']['Risk Manager'] = f'FAILED: {e}'
    
    results['total_tests'] += 1
    
    # Test 6: Transition System
    print("\n🔄 Testing Transition System...")
    try:
        from brokers.paper_to_live_transition import PaperToLiveTransition, create_transition_config
        transition_config = create_transition_config()
        transition = PaperToLiveTransition(transition_config)
        
        # Test transition phases
        assert len(transition.transition_phases) == 5, "Should have 5 transition phases"
        assert transition.transition_phases[0].phase.value == 'paper_only', "First phase should be paper_only"
        assert transition.transition_phases[-1].phase.value == 'full_live', "Last phase should be full_live"
        
        # Test transition start
        start_result = transition.start_transition()
        assert start_result['success'] == True, "Transition start should succeed"
        assert transition.transition_state.current_phase.value == 'paper_only', "Should start in paper_only phase"
        
        print("✅ Transition System - PASSED")
        results['passed_tests'] += 1
        results['test_results']['Transition System'] = 'PASSED'
        
    except Exception as e:
        print(f"❌ Transition System - FAILED: {e}")
        results['failed_tests'] += 1
        results['test_results']['Transition System'] = f'FAILED: {e}'
    
    results['total_tests'] += 1
    
    # Test 7: Dashboard Integration
    print("\n📊 Testing Dashboard Integration...")
    try:
        # Test that dashboard files exist
        dashboard_file = 'multi_broker_dashboard.html'
        assert os.path.exists(dashboard_file), f"Dashboard file {dashboard_file} should exist"
        
        # Test that dashboard has required elements
        with open(dashboard_file, 'r') as f:
            content = f.read()
            assert 'QuantMuse Multi-Broker' in content, "Dashboard should contain QuantMuse Multi-Broker"
            assert 'broker-tabs' in content, "Dashboard should have broker tabs"
            assert 'performance-comparison-chart' in content, "Dashboard should have performance chart"
        
        print("✅ Dashboard Integration - PASSED")
        results['passed_tests'] += 1
        results['test_results']['Dashboard Integration'] = 'PASSED'
        
    except Exception as e:
        print(f"❌ Dashboard Integration - FAILED: {e}")
        results['failed_tests'] += 1
        results['test_results']['Dashboard Integration'] = f'FAILED: {e}'
    
    results['total_tests'] += 1
    
    return results

def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("🧪 QUANTMUSE MULTI-BROKER SYSTEM TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']}")
    print(f"Failed: {results['failed_tests']}")
    
    if results['total_tests'] > 0:
        success_rate = results['passed_tests'] / results['total_tests']
        print(f"Success Rate: {success_rate:.1%}")
    
    print("\n📊 Test Results by Category:")
    for test_name, result in results['test_results'].items():
        status = "✅ PASS" if result == 'PASSED' else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print("\n" + "=" * 60)
    
    if results['total_tests'] > 0:
        success_rate = results['passed_tests'] / results['total_tests']
        if success_rate >= 0.9:
            print("🎉 EXCELLENT: System is ready for production!")
        elif success_rate >= 0.8:
            print("✅ GOOD: System is mostly ready, minor issues to address")
        elif success_rate >= 0.7:
            print("⚠️  WARNING: System has several issues to address")
        else:
            print("🚨 CRITICAL: System needs significant fixes before production")
    
    print("=" * 60)

async def main():
    """Main test execution"""
    setup_logging()
    
    print("🚀 QuantMuse Multi-Broker System Testing")
    print("Testing all components for proper functionality")
    print("This will validate that the system works as intended")
    
    # Run basic tests
    results = await run_basic_tests()
    
    # Print summary
    print_summary(results)
    
    # Return results for programmatic use
    return results

if __name__ == "__main__":
    # Run the test suite
    results = asyncio.run(main())
    
    # Exit with appropriate code
    if results['total_tests'] > 0:
        success_rate = results['passed_tests'] / results['total_tests']
        exit_code = 0 if success_rate >= 0.8 else 1
    else:
        exit_code = 1
    
    sys.exit(exit_code)
