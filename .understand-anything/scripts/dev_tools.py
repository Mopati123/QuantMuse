#!/usr/bin/env python3
"""
Development tools for QuantMuse architecture management
Provides utilities for developers to interact with the knowledge graph
"""

import json
import webbrowser
from pathlib import Path
from datetime import datetime

class QuantMuseDevTools:
    def __init__(self):
        self.ua_dir = Path(".understand-anything")
        self.kg_path = self.ua_dir / "knowledge-graph.json"
        self.dg_path = self.ua_dir / "domain-graph.json"
        self.tours_path = self.ua_dir / "tours.json"
    
    def load_knowledge_graph(self):
        """Load the knowledge graph"""
        if not self.kg_path.exists():
            return None
        with open(self.kg_path, 'r') as f:
            return json.load(f)
    
    def load_domain_graph(self):
        """Load the domain graph"""
        if not self.dg_path.exists():
            return None
        with open(self.dg_path, 'r') as f:
            return json.load(f)
    
    def search_components(self, query, node_type=None):
        """Search for components in the knowledge graph"""
        kg = self.load_knowledge_graph()
        if not kg:
            return []
        
        results = []
        query_lower = query.lower()
        
        for node in kg.get('nodes', []):
            if node_type and node.get('type') != node_type:
                continue
            
            # Search in name, summary, and tags
            searchable_text = f"{node.get('name', '')} {node.get('summary', '')} {' '.join(node.get('tags', []))}"
            
            if query_lower in searchable_text.lower():
                results.append(node)
        
        return results
    
    def get_component_details(self, component_id):
        """Get detailed information about a specific component"""
        kg = self.load_knowledge_graph()
        if not kg:
            return None
        
        # Find the component
        component = None
        for node in kg.get('nodes', []):
            if node.get('id') == component_id:
                component = node
                break
        
        if not component:
            return None
        
        # Find related components
        related = []
        for edge in kg.get('edges', []):
            if edge.get('source') == component_id:
                related.append({'type': 'outgoing', 'edge': edge})
            elif edge.get('target') == component_id:
                related.append({'type': 'incoming', 'edge': edge})
        
        return {
            'component': component,
            'relationships': related
        }
    
    def get_architecture_overview(self):
        """Get high-level architecture overview"""
        kg = self.load_knowledge_graph()
        dg = self.load_domain_graph()
        
        if not kg:
            return None
        
        overview = {
            'timestamp': datetime.now().isoformat(),
            'total_components': len(kg.get('nodes', [])),
            'total_relationships': len(kg.get('edges', [])),
            'component_types': {},
            'domains': []
        }
        
        # Count component types
        for node in kg.get('nodes', []):
            node_type = node.get('type', 'unknown')
            overview['component_types'][node_type] = overview['component_types'].get(node_type, 0) + 1
        
        # Add domain information
        if dg:
            domains = [n for n in dg.get('nodes', []) if n.get('type') == 'domain']
            overview['domains'] = [{'id': d['id'], 'name': d['name'], 'description': d.get('description', '')} for d in domains]
        
        return overview
    
    def list_tours(self):
        """List available guided tours"""
        if not self.tours_path.exists():
            return []
        
        with open(self.tours_path, 'r') as f:
            tours_data = json.load(f)
        
        return tours_data.get('tours', [])
    
    def get_critical_components(self):
        """Identify critical components based on connectivity and tags"""
        kg = self.load_knowledge_graph()
        if not kg:
            return []
        
        # Count connections for each node
        connection_counts = {}
        for edge in kg.get('edges', []):
            source = edge.get('source')
            target = edge.get('target')
            
            connection_counts[source] = connection_counts.get(source, 0) + 1
            connection_counts[target] = connection_counts.get(target, 0) + 1
        
        # Find critical components
        critical = []
        for node in kg.get('nodes', []):
            node_id = node.get('id')
            connections = connection_counts.get(node_id, 0)
            tags = node.get('tags', [])
            
            # Critical if highly connected or tagged as core
            if connections > 5 or 'core' in tags:
                critical.append({
                    'component': node,
                    'connections': connections,
                    'criticality': 'high' if 'core' in tags else 'medium'
                })
        
        # Sort by connections
        critical.sort(key=lambda x: x['connections'], reverse=True)
        return critical[:10]  # Top 10 critical components
    
    def open_dashboard(self):
        """Open the interactive dashboard"""
        dashboard_path = self.ua_dir / "dashboard" / "index.html"
        if dashboard_path.exists():
            webbrowser.open(f'file://{dashboard_path.absolute()}')
            return True
        return False
    
    def start_dashboard_server(self, port=8080):
        """Start the dashboard server"""
        server_script = self.ua_dir / "dashboard" / "server.py"
        if server_script.exists():
            import subprocess
            import os
            
            # Change to dashboard directory
            os.chdir(self.ua_dir / "dashboard")
            
            # Start server
            try:
                subprocess.run([sys.executable, "server.py", str(port)], check=True)
                return True
            except subprocess.CalledProcessError:
                return False
            except KeyboardInterrupt:
                return True
        return False

def main():
    """Command line interface for dev tools"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='QuantMuse Development Tools')
    parser.add_argument('command', choices=[
        'search', 'details', 'overview', 'tours', 'critical', 'dashboard', 'server'
    ], help='Command to execute')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--type', help='Component type filter')
    parser.add_argument('--id', help='Component ID')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    
    args = parser.parse_args()
    
    tools = QuantMuseDevTools()
    
    if args.command == 'search':
        if not args.query:
            print("Error: --query required for search command")
            sys.exit(1)
        
        results = tools.search_components(args.query, args.type)
        print(f"Found {len(results)} components matching '{args.query}':")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.get('name', result.get('id'))} ({result.get('type')})")
            print(f"   {result.get('summary', 'No summary')[:100]}...")
            print()
    
    elif args.command == 'details':
        if not args.id:
            print("Error: --id required for details command")
            sys.exit(1)
        
        details = tools.get_component_details(args.id)
        if details:
            comp = details['component']
            print(f"Component: {comp.get('name', comp.get('id'))}")
            print(f"Type: {comp.get('type')}")
            print(f"Summary: {comp.get('summary', 'No summary')}")
            print(f"Tags: {', '.join(comp.get('tags', []))}")
            print(f"\\nRelationships ({len(details['relationships'])}):")
            for rel in details['relationships']:
                edge = rel['edge']
                direction = "→" if rel['type'] == 'outgoing' else "←"
                print(f"  {direction} {edge.get('type', 'unknown')} {edge.get('target' if rel['type'] == 'outgoing' else 'source')}")
        else:
            print(f"Component '{args.id}' not found")
    
    elif args.command == 'overview':
        overview = tools.get_architecture_overview()
        if overview:
            print("QuantMuse Architecture Overview")
            print("=" * 40)
            print(f"Total Components: {overview['total_components']}")
            print(f"Total Relationships: {overview['total_relationships']}")
            print("\\nComponent Types:")
            for ctype, count in overview['component_types'].items():
                print(f"  {ctype}: {count}")
            
            if overview['domains']:
                print("\\nBusiness Domains:")
                for domain in overview['domains']:
                    print(f"  • {domain['name']}: {domain['description'][:60]}...")
        else:
            print("Could not load architecture overview")
    
    elif args.command == 'tours':
        tours = tools.list_tours()
        print(f"Available Guided Tours ({len(tours)}):")
        for i, tour in enumerate(tours, 1):
            print(f"{i}. {tour.get('name')}")
            print(f"   {tour.get('description', 'No description')[:80]}...")
            print(f"   Duration: {tour.get('estimatedTime', 'Unknown')} • Difficulty: {tour.get('difficulty', 'Unknown')}")
            print()
    
    elif args.command == 'critical':
        critical = tools.get_critical_components()
        print(f"Critical Components ({len(critical)}):")
        for i, item in enumerate(critical, 1):
            comp = item['component']
            print(f"{i}. {comp.get('name', comp.get('id'))} ({item['connections']} connections)")
            print(f"   Criticality: {item['criticality']}")
            print(f"   {comp.get('summary', 'No summary')[:80]}...")
            print()
    
    elif args.command == 'dashboard':
        if tools.open_dashboard():
            print("🌐 Dashboard opened in default browser")
        else:
            print("❌ Dashboard not found. Please ensure the analysis is complete.")
    
    elif args.command == 'server':
        print(f"🚀 Starting dashboard server on port {args.port}...")
        if tools.start_dashboard_server(args.port):
            print("Server started successfully")
        else:
            print("❌ Failed to start server")

if __name__ == "__main__":
    main()
