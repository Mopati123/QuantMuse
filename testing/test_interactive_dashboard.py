#!/usr/bin/env python3
"""
Comprehensive Testing Script for QuantMuse Interactive Dashboard
Tests all dashboard features, API endpoints, and WebSocket functionality
"""

import asyncio
import unittest
import logging
import json
import time
import requests
import websockets
from datetime import datetime
import threading
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InteractiveDashboardTestSuite:
    """Comprehensive test suite for interactive dashboard"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:5000/api"
        self.websocket_url = "ws://localhost:8765"
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'errors': []
        }
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all dashboard tests"""
        logger.info("🚀 Starting Interactive Dashboard Test Suite")
        logger.info("=" * 60)
        
        try:
            # API Tests
            self.test_api_endpoints()
            
            # WebSocket Tests
            self.test_websocket_functionality()
            
            # Dashboard UI Tests
            self.test_dashboard_ui_components()
            
            # Integration Tests
            self.test_end_to_end_workflows()
            
            # Performance Tests
            self.test_dashboard_performance()
            
            # Generate summary
            self.generate_test_summary()
            
            return self.test_results
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            self.test_results['errors'].append(f"Test suite error: {e}")
            return self.test_results
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        logger.info("🔌 Testing API Endpoints...")
        
        # Test System Status
        self._test_endpoint('GET', '/system/status', 'System Status')
        
        # Test Portfolio State
        self._test_endpoint('GET', '/portfolio/state', 'Portfolio State')
        
        # Test Brokers Status
        self._test_endpoint('GET', '/brokers/status', 'Brokers Status')
        
        # Test Order Placement
        self._test_order_placement()
        
        # Test Strategy Management
        self._test_strategy_management()
        
        # Test Risk Management
        self._test_risk_management()
        
        # Test Broker Management
        self._test_broker_management()
        
        # Test Transition Control
        self._test_transition_control()
        
        # Test Testing Tools
        self._test_testing_tools()
    
    def _test_endpoint(self, method: str, endpoint: str, test_name: str):
        """Test individual API endpoint"""
        try:
            url = f"{self.api_base_url}{endpoint}"
            
            if method == 'GET':
                response = requests.get(url, timeout=5)
            elif method == 'POST':
                response = requests.post(url, timeout=5)
            
            self.test_results['total_tests'] += 1
            
            if response.status_code == 200:
                self.test_results['passed_tests'] += 1
                logger.info(f"✅ {test_name} - PASSED")
            else:
                self.test_results['failed_tests'] += 1
                error_msg = f"{test_name} - FAILED: HTTP {response.status_code}"
                self.test_results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
                
        except requests.exceptions.RequestException as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"{test_name} - FAILED: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
        except Exception as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"{test_name} - ERROR: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def _test_order_placement(self):
        """Test order placement functionality"""
        try:
            url = f"{self.api_base_url}/orders/place"
            order_data = {
                'broker': 'deriv',
                'asset': 'EUR/USD',
                'type': 'market',
                'direction': 'buy',
                'volume': 0.01
            }
            
            response = requests.post(url, json=order_data, timeout=5)
            self.test_results['total_tests'] += 1
            
            if response.status_code in [200, 400]:  # 400 is acceptable if risk limits block
                self.test_results['passed_tests'] += 1
                logger.info("✅ Order Placement - PASSED")
            else:
                self.test_results['failed_tests'] += 1
                error_msg = f"Order Placement - FAILED: HTTP {response.status_code}"
                self.test_results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
                
        except Exception as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"Order Placement - ERROR: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def _test_strategy_management(self):
        """Test strategy management endpoints"""
        try:
            # Test strategy start
            url = f"{self.api_base_url}/strategies/start"
            strategy_data = {
                'strategy': 'momentum',
                'mode': 'paper'
            }
            
            response = requests.post(url, json=strategy_data, timeout=5)
            self.test_results['total_tests'] += 1
            
            if response.status_code == 200:
                self.test_results['passed_tests'] += 1
                logger.info("✅ Strategy Start - PASSED")
            else:
                self.test_results['failed_tests'] += 1
                error_msg = f"Strategy Start - FAILED: HTTP {response.status_code}"
                self.test_results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
            # Test strategy performance
            url = f"{self.api_base_url}/strategies/performance"
            response = requests.get(url, timeout=5)
            self.test_results['total_tests'] += 1
            
            if response.status_code == 200:
                self.test_results['passed_tests'] += 1
                logger.info("✅ Strategy Performance - PASSED")
            else:
                self.test_results['failed_tests'] += 1
                error_msg = f"Strategy Performance - FAILED: HTTP {response.status_code}"
                self.test_results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
                
        except Exception as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"Strategy Management - ERROR: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def _test_risk_management(self):
        """Test risk management endpoints"""
        try:
            # Test risk limits
            url = f"{self.api_base_url}/risk/limits"
            response = requests.get(url, timeout=5)
            self.test_results['total_tests'] += 1
            
            if response.status_code == 200:
                self.test_results['passed_tests'] += 1
                logger.info("✅ Risk Limits - PASSED")
            else:
                self.test_results['failed_tests'] += 1
                error_msg = f"Risk Limits - FAILED: HTTP {response.status_code}"
                self.test_results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
                
        except Exception as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"Risk Management - ERROR: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def _test_broker_management(self):
        """Test broker management endpoints"""
        try:
            # Test broker status
            url = f"{self.api_base_url}/brokers/status"
            response = requests.get(url, timeout=5)
            self.test_results['total_tests'] += 1
            
            if response.status_code == 200:
                self.test_results['passed_tests'] += 1
                logger.info("✅ Broker Status - PASSED")
            else:
                self.test_results['failed_tests'] += 1
                error_msg = f"Broker Status - FAILED: HTTP {response.status_code}"
                self.test_results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
                
        except Exception as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"Broker Management - ERROR: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def _test_transition_control(self):
        """Test transition control endpoints"""
        try:
            # Test transition status
            url = f"{self.api_base_url}/transition/status"
            response = requests.get(url, timeout=5)
            self.test_results['total_tests'] += 1
            
            if response.status_code == 200:
                self.test_results['passed_tests'] += 1
                logger.info("✅ Transition Status - PASSED")
            else:
                self.test_results['failed_tests'] += 1
                error_msg = f"Transition Status - FAILED: HTTP {response.status_code}"
                self.test_results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
                
        except Exception as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"Transition Control - ERROR: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def _test_testing_tools(self):
        """Test testing tools endpoints"""
        try:
            # Test scenario test
            url = f"{self.api_base_url}/testing/run_scenario"
            scenario_data = {
                'scenario': 'market_crash',
                'duration': 60
            }
            
            response = requests.post(url, json=scenario_data, timeout=5)
            self.test_results['total_tests'] += 1
            
            if response.status_code == 200:
                self.test_results['passed_tests'] += 1
                logger.info("✅ Scenario Test - PASSED")
            else:
                self.test_results['failed_tests'] += 1
                error_msg = f"Scenario Test - FAILED: HTTP {response.status_code}"
                self.test_results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
                
        except Exception as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"Testing Tools - ERROR: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def test_websocket_functionality(self):
        """Test WebSocket functionality"""
        logger.info("🔌 Testing WebSocket Functionality...")
        
        try:
            # Test WebSocket connection
            async def test_websocket_connection():
                try:
                    async with websockets.connect(self.websocket_url) as websocket:
                        self.test_results['total_tests'] += 1
                        
                        # Test connection
                        message = await websocket.recv()
                        if 'connected' in message.lower():
                            self.test_results['passed_tests'] += 1
                            logger.info("✅ WebSocket Connection - PASSED")
                        else:
                            self.test_results['failed_tests'] += 1
                            error_msg = "WebSocket Connection - FAILED: Invalid response"
                            self.test_results['errors'].append(error_msg)
                            logger.error(f"❌ {error_msg}")
                        
                        # Test subscription
                        subscribe_msg = json.dumps({'type': 'subscribe', 'subscription_type': 'portfolio'})
                        await websocket.send(subscribe_msg)
                        
                        # Wait for response
                        response = await websocket.recv()
                        self.test_results['total_tests'] += 1
                        
                        if 'portfolio' in response.lower():
                            self.test_results['passed_tests'] += 1
                            logger.info("✅ WebSocket Subscription - PASSED")
                        else:
                            self.test_results['failed_tests'] += 1
                            error_msg = "WebSocket Subscription - FAILED: Invalid response"
                            self.test_results['errors'].append(error_msg)
                            logger.error(f"❌ {error_msg}")
                        
                except Exception as e:
                    self.test_results['total_tests'] += 2  # Two tests attempted
                    self.test_results['failed_tests'] += 2
                    error_msg = f"WebSocket Test - ERROR: {e}"
                    self.test_results['errors'].append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
            # Run WebSocket test
            asyncio.run(test_websocket_connection())
            
        except Exception as e:
            self.test_results['total_tests'] += 2
            self.test_results['failed_tests'] += 2
            error_msg = f"WebSocket Functionality - ERROR: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def test_dashboard_ui_components(self):
        """Test dashboard UI components"""
        logger.info("🖥️ Testing Dashboard UI Components...")
        
        # Test dashboard HTML file exists
        try:
            import os
            dashboard_path = "interactive_control_dashboard.html"
            
            self.test_results['total_tests'] += 1
            
            if os.path.exists(dashboard_path):
                self.test_results['passed_tests'] += 1
                logger.info("✅ Dashboard HTML File - PASSED")
                
                # Test dashboard content
                with open(dashboard_path, 'r') as f:
                    content = f.read()
                    
                    # Check for essential components
                    essential_components = [
                        'QuantMuse Interactive Control Dashboard',
                        'main-tabs',
                        'portfolio-chart',
                        'price-chart',
                        'strategy-performance-chart',
                        'broker-performance-chart',
                        'risk-exposure-chart',
                        'transition-chart',
                        'WebSocket',
                        'placeOrder',
                        'startStrategy'
                    ]
                    
                    for component in essential_components:
                        self.test_results['total_tests'] += 1
                        
                        if component in content:
                            self.test_results['passed_tests'] += 1
                            logger.info(f"✅ UI Component '{component}' - PASSED")
                        else:
                            self.test_results['failed_tests'] += 1
                            error_msg = f"UI Component '{component}' - FAILED: Not found"
                            self.test_results['errors'].append(error_msg)
                            logger.error(f"❌ {error_msg}")
            else:
                self.test_results['failed_tests'] += 1
                error_msg = "Dashboard HTML File - FAILED: File not found"
                self.test_results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
                
        except Exception as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"Dashboard UI Components - ERROR: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def test_end_to_end_workflows(self):
        """Test end-to-end workflows"""
        logger.info("🔄 Testing End-to-End Workflows...")
        
        # Test complete trading workflow
        self._test_trading_workflow()
        
        # Test strategy workflow
        self._test_strategy_workflow()
        
        # Test risk management workflow
        self._test_risk_workflow()
    
    def _test_trading_workflow(self):
        """Test complete trading workflow"""
        try:
            # Step 1: Get portfolio state
            response = requests.get(f"{self.api_base_url}/portfolio/state", timeout=5)
            if response.status_code != 200:
                raise Exception("Failed to get portfolio state")
            
            # Step 2: Place order
            order_data = {
                'broker': 'deriv',
                'asset': 'EUR/USD',
                'type': 'market',
                'direction': 'buy',
                'volume': 0.01
            }
            
            response = requests.post(f"{self.api_base_url}/orders/place", json=order_data, timeout=5)
            if response.status_code not in [200, 400]:  # 400 acceptable if risk blocked
                raise Exception("Failed to place order")
            
            # Step 3: Get updated portfolio
            response = requests.get(f"{self.api_base_url}/portfolio/state", timeout=5)
            if response.status_code != 200:
                raise Exception("Failed to get updated portfolio")
            
            self.test_results['total_tests'] += 1
            self.test_results['passed_tests'] += 1
            logger.info("✅ Trading Workflow - PASSED")
            
        except Exception as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"Trading Workflow - FAILED: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def _test_strategy_workflow(self):
        """Test strategy management workflow"""
        try:
            # Step 1: Start strategy
            strategy_data = {
                'strategy': 'momentum',
                'mode': 'paper'
            }
            
            response = requests.post(f"{self.api_base_url}/strategies/start", json=strategy_data, timeout=5)
            if response.status_code != 200:
                raise Exception("Failed to start strategy")
            
            # Step 2: Get strategy performance
            response = requests.get(f"{self.api_base_url}/strategies/performance", timeout=5)
            if response.status_code != 200:
                raise Exception("Failed to get strategy performance")
            
            # Step 3: Stop strategy
            response = requests.post(f"{self.api_base_url}/strategies/stop", json={'strategy': 'momentum'}, timeout=5)
            if response.status_code != 200:
                raise Exception("Failed to stop strategy")
            
            self.test_results['total_tests'] += 1
            self.test_results['passed_tests'] += 1
            logger.info("✅ Strategy Workflow - PASSED")
            
        except Exception as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"Strategy Workflow - FAILED: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def _test_risk_workflow(self):
        """Test risk management workflow"""
        try:
            # Step 1: Get risk limits
            response = requests.get(f"{self.api_base_url}/risk/limits", timeout=5)
            if response.status_code != 200:
                raise Exception("Failed to get risk limits")
            
            # Step 2: Update risk limits
            limits_data = {
                'max_total_exposure': 250000,
                'max_per_broker': 125000
            }
            
            response = requests.post(f"{self.api_base_url}/risk/limits", json=limits_data, timeout=5)
            if response.status_code != 200:
                raise Exception("Failed to update risk limits")
            
            self.test_results['total_tests'] += 1
            self.test_results['passed_tests'] += 1
            logger.info("✅ Risk Workflow - PASSED")
            
        except Exception as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"Risk Workflow - FAILED: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def test_dashboard_performance(self):
        """Test dashboard performance"""
        logger.info("⚡ Testing Dashboard Performance...")
        
        # Test API response times
        self._test_api_performance()
        
        # Test concurrent connections
        self._test_concurrent_connections()
    
    def _test_api_performance(self):
        """Test API response times"""
        try:
            endpoints = [
                '/system/status',
                '/portfolio/state',
                '/brokers/status'
            ]
            
            total_time = 0
            for endpoint in endpoints:
                start_time = time.time()
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=5)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to ms
                total_time += response_time
                
                self.test_results['total_tests'] += 1
                
                if response_time < 1000:  # Less than 1 second
                    self.test_results['passed_tests'] += 1
                    logger.info(f"✅ API Performance {endpoint} - PASSED ({response_time:.2f}ms)")
                else:
                    self.test_results['failed_tests'] += 1
                    error_msg = f"API Performance {endpoint} - FAILED: {response_time:.2f}ms"
                    self.test_results['errors'].append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
            avg_time = total_time / len(endpoints)
            logger.info(f"📊 Average API Response Time: {avg_time:.2f}ms")
            
        except Exception as e:
            self.test_results['total_tests'] += len(endpoints)
            self.test_results['failed_tests'] += len(endpoints)
            error_msg = f"API Performance - ERROR: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def _test_concurrent_connections(self):
        """Test concurrent connections"""
        try:
            def make_request():
                try:
                    response = requests.get(f"{self.api_base_url}/system/status", timeout=5)
                    return response.status_code == 200
                except:
                    return False
            
            # Test 10 concurrent requests
            threads = []
            results = []
            
            start_time = time.time()
            
            for _ in range(10):
                thread = threading.Thread(target=lambda: results.append(make_request()))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            
            successful_requests = sum(results)
            total_time = (end_time - start_time) * 1000
            
            self.test_results['total_tests'] += 1
            
            if successful_requests >= 8 and total_time < 5000:  # At least 8/10 successful, under 5 seconds
                self.test_results['passed_tests'] += 1
                logger.info(f"✅ Concurrent Connections - PASSED ({successful_requests}/10 in {total_time:.2f}ms)")
            else:
                self.test_results['failed_tests'] += 1
                error_msg = f"Concurrent Connections - FAILED: {successful_requests}/10 in {total_time:.2f}ms"
                self.test_results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
            
        except Exception as e:
            self.test_results['total_tests'] += 1
            self.test_results['failed_tests'] += 1
            error_msg = f"Concurrent Connections - ERROR: {e}"
            self.test_results['errors'].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        logger.info("\n" + "=" * 60)
        logger.info("🧪 INTERACTIVE DASHBOARD TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {self.test_results['total_tests']}")
        logger.info(f"Passed: {self.test_results['passed_tests']}")
        logger.info(f"Failed: {self.test_results['failed_tests']}")
        
        if self.test_results['total_tests'] > 0:
            success_rate = self.test_results['passed_tests'] / self.test_results['total_tests']
            logger.info(f"Success Rate: {success_rate:.1%}")
        
        if self.test_results['errors']:
            logger.info("\n❌ Errors:")
            for error in self.test_results['errors']:
                logger.info(f"   - {error}")
        
        logger.info("\n📊 Test Categories:")
        categories = {
            'API Endpoints': 'api',
            'WebSocket': 'websocket',
            'UI Components': 'ui',
            'End-to-End': 'workflow',
            'Performance': 'performance'
        }
        
        for category, prefix in categories.items():
            category_tests = [e for e in self.test_results['errors'] if prefix in e.lower()]
            category_passed = self.test_results['total_tests'] - len(category_tests)
            
            if category_passed > 0:
                logger.info(f"   ✅ {category}: {category_passed} tests passed")
            if len(category_tests) > 0:
                logger.info(f"   ❌ {category}: {len(category_tests)} tests failed")
        
        logger.info("\n" + "=" * 60)
        
        if self.test_results['total_tests'] > 0:
            success_rate = self.test_results['passed_tests'] / self.test_results['total_tests']
            if success_rate >= 0.9:
                logger.info("🎉 EXCELLENT: Interactive Dashboard is ready for production!")
            elif success_rate >= 0.8:
                logger.info("✅ GOOD: Interactive Dashboard is mostly ready, minor issues to address")
            elif success_rate >= 0.7:
                logger.info("⚠️  WARNING: Interactive Dashboard has several issues to address")
            else:
                logger.info("🚨 CRITICAL: Interactive Dashboard needs significant fixes before production")
        
        logger.info("=" * 60)
        
        # Save detailed results
        self._save_test_results()
    
    def _save_test_results(self):
        """Save test results to file"""
        try:
            with open('interactive_dashboard_test_results.json', 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            logger.info("💾 Detailed test results saved to: interactive_dashboard_test_results.json")
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")

def main():
    """Main test execution"""
    test_suite = InteractiveDashboardTestSuite()
    results = test_suite.run_all_tests()
    
    # Exit with appropriate code
    if results['total_tests'] > 0:
        success_rate = results['passed_tests'] / results['total_tests']
        exit_code = 0 if success_rate >= 0.8 else 1
    else:
        exit_code = 1
    
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
