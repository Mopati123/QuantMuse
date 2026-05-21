#!/usr/bin/env python3
"""
Simple HTTP server for the QuantMuse Architecture Dashboard
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def start_server(port=8080):
    """Start the dashboard server"""
    dashboard_dir = Path(__file__).parent
    
    # Change to dashboard directory
    os.chdir(dashboard_dir)
    
    # Create server
    with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
        print(f"🚀 QuantMuse Architecture Dashboard")
        print(f"📍 Server running at: http://localhost:{port}")
        print(f"📁 Serving directory: {dashboard_dir}")
        print(f"🔄 Press Ctrl+C to stop the server")
        print()
        
        # Auto-open browser
        try:
            webbrowser.open(f'http://localhost:{port}')
            print("🌐 Opening dashboard in default browser...")
        except:
            print("⚠️  Could not auto-open browser. Please navigate manually.")
        
        print()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped. Goodbye!")

if __name__ == "__main__":
    import sys
    
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 8080.")
    
    start_server(port)
