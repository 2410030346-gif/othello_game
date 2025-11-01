"""
Quick test to verify server functionality
"""

import socket
import time

def test_server_connection():
    """Test if we can connect to the server"""
    print("Testing server connection...")
    
    # Try to connect to localhost:5555
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(3.0)
        client.connect(('localhost', 5555))
        print("✓ Successfully connected to server!")
        client.close()
        return True
    except socket.timeout:
        print("✗ Connection timeout - server might not be running")
        return False
    except ConnectionRefusedError:
        print("✗ Connection refused - server is not running on port 5555")
        print("  Start the server with: python server.py")
        return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Othello Online Server Test")
    print("=" * 50)
    
    result = test_server_connection()
    
    if not result:
        print("\nTo start the server, run:")
        print("  python server.py")
        print("\nThen run this test again.")
    
    print("=" * 50)
