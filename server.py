"""
Othello Online Game Server

Run this script to host online multiplayer games.
Players can connect and get automatically matched.

Usage:
    python server.py [port]
    
Default port: 5555 (or PORT environment variable for cloud deployment)
"""

import sys
import os
from network import GameServer

def main():
    # For Render deployment, use PORT environment variable
    # For local testing, use command line argument or default 5555
    port = int(os.environ.get('PORT', 5555))
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number. Using port {port}")
    
    print("=" * 50)
    print("Othello Online Game Server")
    print("=" * 50)
    print(f"Starting server on port {port}...")
    print(f"Environment: {'Render' if os.environ.get('RENDER') else 'Local'}")
    
    server = GameServer(port)
    
    if server.start():
        print(f"Server running! Players can connect to:")
        print(f"  - localhost:{port} (local)")
        print(f"  - YOUR_IP_ADDRESS:{port} (network)")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        try:
            # Keep server running
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down server...")
            server.stop()
            print("Server stopped.")
    else:
        print("Failed to start server!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
