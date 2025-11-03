"""
Othello Game Server with HTTP Health Check for Render

This version includes an HTTP health check endpoint for Render compatibility
while maintaining TCP socket support for game connections.
"""

import sys
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from network import GameServer

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks"""
    
    def do_GET(self):
        """Handle GET requests for health check"""
        if self.path == '/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            response = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Othello Game Server</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #fff; }
                    .container { max-width: 600px; margin: 0 auto; text-align: center; }
                    h1 { color: #00d4ff; }
                    .status { background: #16213e; padding: 20px; border-radius: 10px; margin: 20px 0; }
                    .online { color: #00ff00; font-size: 24px; font-weight: bold; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎮 Othello Game Server</h1>
                    <div class="status">
                        <p class="online">● ONLINE</p>
                        <p>Game server is running and ready for connections!</p>
                        <p>Players: Connect via the Othello game client</p>
                    </div>
                    <p>GitHub: <a href="https://github.com/2410030346-gif/othello_game" style="color: #00d4ff;">othello_game</a></p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def run_http_server(port):
    """Run HTTP server for health checks"""
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f"HTTP health check server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"HTTP server error: {e}")

def main():
    # Get ports from environment
    http_port = int(os.environ.get('PORT', 10000))  # Render assigns this for HTTP
    game_port = int(os.environ.get('GAME_PORT', http_port + 1))  # TCP game server
    
    # Override with command line if provided
    if len(sys.argv) > 1:
        try:
            http_port = int(sys.argv[1])
            game_port = http_port + 1
        except ValueError:
            print(f"Invalid port number. Using port {http_port}")
    
    print("=" * 60)
    print("Othello Online Game Server (Render Compatible)")
    print("=" * 60)
    print(f"Environment: {'Render' if os.environ.get('RENDER') else 'Local'}")
    print(f"HTTP Health Check Port: {http_port}")
    print(f"Game Server Port: {game_port}")
    print("=" * 60)
    
    # Start HTTP health check server in background
    http_thread = threading.Thread(target=run_http_server, args=(http_port,), daemon=True)
    http_thread.start()
    
    # Start game server
    game_server = GameServer(game_port)
    
    if game_server.start():
        print(f"\n✓ Game server running on port {game_port}")
        print(f"✓ Health check available at http://localhost:{http_port}")
        print("\nPlayers can connect to:")
        print(f"  - Game Port: {game_port}")
        print(f"  - Health Check: http://localhost:{http_port}")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 60)
        
        try:
            # Keep server running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nShutting down server...")
            game_server.stop()
            print("Server stopped.")
    else:
        print("Failed to start game server!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
