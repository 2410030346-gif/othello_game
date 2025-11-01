import socket
import pickle
import threading
import queue
import json

class NetworkClient:
    """Client for online multiplayer"""
    
    def __init__(self):
        self.client = None
        self.connected = False
        self.player_color = None
        self.game_id = None
        self.receive_queue = queue.Queue()
        self.receive_thread = None
        
    def connect(self, host='localhost', port=5555):
        """Connect to the game server"""
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(5.0)  # 5 second timeout
            self.client.connect((host, port))
            self.connected = True
            
            # Start receiving thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False
            return False
    
    def _receive_loop(self):
        """Background thread for receiving data"""
        while self.connected:
            try:
                data = self.client.recv(4096)
                if not data:
                    break
                message = pickle.loads(data)
                self.receive_queue.put(message)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Receive error: {e}")
                break
        self.connected = False
    
    def send(self, data):
        """Send data to server"""
        if not self.connected:
            return False
        try:
            self.client.send(pickle.dumps(data))
            return True
        except Exception as e:
            print(f"Send error: {e}")
            self.connected = False
            return False
    
    def get_message(self):
        """Get next message from queue (non-blocking)"""
        try:
            return self.receive_queue.get_nowait()
        except queue.Empty:
            return None
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.client:
            try:
                self.client.close()
            except:
                pass


class GameServer:
    """Simple game server for hosting matches"""
    
    def __init__(self, port=5555):
        self.port = port
        self.server = None
        self.games = {}  # game_id -> game_data
        self.waiting_players = []
        self.clients = {}  # client_socket -> player_info
        self.running = False
        
    def start(self):
        """Start the server"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('0.0.0.0', self.port))
            self.server.listen(10)
            self.running = True
            
            print(f"Server started on port {self.port}")
            
            # Accept connections in background
            accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
            accept_thread.start()
            
            return True
        except Exception as e:
            print(f"Server start error: {e}")
            return False
    
    def _accept_loop(self):
        """Accept incoming connections"""
        while self.running:
            try:
                client, addr = self.server.accept()
                print(f"New connection from {addr}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(client, addr), 
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                if self.running:
                    print(f"Accept error: {e}")
    
    def _handle_client(self, client, addr):
        """Handle a connected client"""
        player_id = f"player_{addr[0]}_{addr[1]}"
        
        try:
            # Check if we have a waiting player
            if self.waiting_players:
                # Match with waiting player
                opponent = self.waiting_players.pop(0)
                game_id = f"game_{len(self.games)}"
                
                # Create game
                self.games[game_id] = {
                    'player1': opponent,
                    'player2': client,
                    'player1_color': 'B',
                    'player2_color': 'W',
                    'current_turn': 'B',
                    'board': None
                }
                
                # Store client info
                self.clients[opponent] = {'game_id': game_id, 'color': 'B', 'player_id': player_id + '_1'}
                self.clients[client] = {'game_id': game_id, 'color': 'W', 'player_id': player_id + '_2'}
                
                # Notify both players
                self._send(opponent, {'type': 'game_start', 'color': 'B', 'game_id': game_id})
                self._send(client, {'type': 'game_start', 'color': 'W', 'game_id': game_id})
                
                print(f"Game {game_id} started!")
            else:
                # Add to waiting list
                self.waiting_players.append(client)
                self._send(client, {'type': 'waiting'})
                print(f"Player {player_id} waiting for opponent...")
            
            # Game loop
            while self.running:
                try:
                    data = client.recv(4096)
                    if not data:
                        break
                    
                    message = pickle.loads(data)
                    self._process_message(client, message)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Client handler error: {e}")
                    break
                    
        except Exception as e:
            print(f"Client setup error: {e}")
        finally:
            self._cleanup_client(client)
    
    def _process_message(self, client, message):
        """Process message from client"""
        if client not in self.clients:
            return
        
        client_info = self.clients[client]
        game_id = client_info['game_id']
        
        if game_id not in self.games:
            return
        
        game = self.games[game_id]
        
        if message['type'] == 'move':
            # Forward move to opponent
            opponent = game['player1'] if game['player2'] == client else game['player2']
            self._send(opponent, message)
            
        elif message['type'] == 'chat':
            # Forward chat to opponent
            opponent = game['player1'] if game['player2'] == client else game['player2']
            self._send(opponent, message)
    
    def _send(self, client, data):
        """Send data to client"""
        try:
            client.send(pickle.dumps(data))
        except Exception as e:
            print(f"Send error: {e}")
    
    def _cleanup_client(self, client):
        """Clean up disconnected client"""
        if client in self.waiting_players:
            self.waiting_players.remove(client)
        
        if client in self.clients:
            client_info = self.clients[client]
            game_id = client_info.get('game_id')
            
            if game_id and game_id in self.games:
                game = self.games[game_id]
                opponent = game['player1'] if game['player2'] == client else game['player2']
                
                # Notify opponent
                self._send(opponent, {'type': 'opponent_disconnected'})
                
                # Clean up game
                del self.games[game_id]
                if opponent in self.clients:
                    del self.clients[opponent]
            
            del self.clients[client]
        
        try:
            client.close()
        except:
            pass
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server:
            self.server.close()
