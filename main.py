import pygame
import math
import numpy as np
import json
import os
import time
import random
from datetime import datetime
from constants import BOARD_SIZE, TILE_SIZE, WINDOW_SIZE, BLACK, WHITE, GREEN
from board import Board
from game import Game
from ai import choose_move

# Try to import modern AI (PyTorch-based)
USE_MODERN_AI = False
modern_ai_instance = None
try:
    from modern_ai import ModernOthelloAI
    import os
    # Check if trained model exists
    if os.path.exists('othello_model_final.pth') or os.path.exists('othello_model.pth'):
        model_path = 'othello_model_final.pth' if os.path.exists('othello_model_final.pth') else 'othello_model.pth'
        modern_ai_instance = ModernOthelloAI(model_path=model_path)
        USE_MODERN_AI = True
        print(f"🧠 Modern AI loaded successfully from {model_path}")
    else:
        print("⚠️  PyTorch available but no trained model found. Using classic AI.")
        print("   To train: run 'python train_modern_ai.py'")
except ImportError:
    print("ℹ️  PyTorch not installed. Using classic Minimax AI.")
    print("   To use Modern AI: pip install torch")

from server_user_manager import ServerUserManager as UserManager

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Initialize user manager
user_manager = UserManager()

# Avatar sets for players
AVATAR_EMOJIS = ['😀', '😎', '🤖', '👾', '🐱', '🐶', '🦁', '🐼', '🐯', '🦊', '🐸', '🐵', '🦄', '🐨', '🐷', '🦉', '🐙', '🦖', '🎮', '⭐']

# Current game avatars (will be set when game starts)
player1_avatar = None
player2_avatar = None

# Settings file management
SETTINGS_FILE = "game_settings.json"

def load_settings():
    """Load saved game settings from file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_settings(settings):
    """Save game settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Failed to save settings: {e}")

# Sound generation functions
def generate_sound(frequency, duration, volume=0.3):
    """Generate a simple sine wave sound"""
    sample_rate = 22050
    samples = int(sample_rate * duration)
    wave = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
    # Apply volume and convert to 16-bit
    wave = (wave * volume * 32767).astype(np.int16)
    # Create stereo sound
    stereo_wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo_wave)

def generate_flip_sound():
    """Generate a flip/whoosh sound for disc flipping"""
    sample_rate = 22050
    duration = 0.15
    samples = int(sample_rate * duration)
    
    # Create a descending frequency sweep for flip effect
    start_freq = 800
    end_freq = 300
    frequencies = np.linspace(start_freq, end_freq, samples)
    
    # Generate the sweep
    time_array = np.linspace(0, duration, samples)
    wave = np.sin(2 * np.pi * frequencies * time_array)
    
    # Apply envelope for smooth start and end
    envelope = np.exp(-3 * time_array / duration)
    wave = wave * envelope
    
    # Apply volume and convert to 16-bit
    wave = (wave * 0.2 * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo_wave)

# Generate all sound effects
click_sound = generate_sound(800, 0.1, 0.2)
hover_sound = generate_sound(600, 0.05, 0.15)
place_sound = generate_sound(400, 0.15, 0.25)
flip_sound = generate_flip_sound()
win_sound = generate_sound(523, 0.3, 0.3)  # C note
error_sound = generate_sound(200, 0.2, 0.2)

# Initial screen setup
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE), pygame.RESIZABLE)
pygame.display.set_caption("Othello")

# Game states
STATE_MAIN_MENU = "main_menu"
STATE_LOGIN = "login"
STATE_USER_INPUT = "user_input"
STATE_USER_PROFILE = "user_profile"
STATE_PLAY_MODE = "play_mode"
STATE_DIFFICULTY = "difficulty"
STATE_ONLINE_CONNECT = "online_connect"
STATE_ONLINE_WAITING = "online_waiting"
STATE_PLAYING = "playing"
STATE_ACHIEVEMENTS = "achievements"
STATE_FRIENDS = "friends"
STATE_ADD_FRIEND = "add_friend"

current_state = STATE_MAIN_MENU

# User authentication variables
selected_provider = None
user_email_input = ""
user_name_input = ""
active_input_field = "email"  # 'email' or 'username'
user_input_error = ""  # Error message for validation
game_start_time = None

# Friends and achievements variables
friend_email_input = ""
add_friend_message = ""
friends_list = []
pending_requests = []
all_achievements = []
user_achievements = []
newly_unlocked_achievements = []
achievement_notification_time = 0

# Background colors dictionaries
GRID_COLORS = {
    "Green": (0, 128, 0),
    "Blue": (0, 100, 150),
    "Purple": (75, 0, 130),
    "Teal": (0, 128, 128),
    "Brown": (101, 67, 33),
    "Navy": (0, 51, 102)
}

INTERFACE_COLORS = {
    "Dark Gray": (40, 40, 40),
    "Dark Blue": (25, 25, 60),
    "Dark Purple": (40, 20, 60),
    "Dark Red": (60, 20, 20),
    "Dark Teal": (20, 50, 50),
    "Dark Brown": (50, 35, 20)
}

# Load saved settings
saved_settings = load_settings()
current_grid_color = saved_settings.get("grid_color", "Green")
current_interface_color = saved_settings.get("interface_color", "Dark Gray")

# Validate saved colors exist in dictionaries, otherwise use defaults
if current_grid_color not in GRID_COLORS:
    current_grid_color = "Green"
if current_interface_color not in INTERFACE_COLORS:
    current_interface_color = "Dark Gray"

grid_bg_color = GRID_COLORS[current_grid_color]
interface_bg_color = INTERFACE_COLORS[current_interface_color]

board = None
game = None

AI_ENABLED = True
AI_DIFFICULTY = 'medium'
HUMAN_COLOR = 'B'
AI_COLOR = 'W'

# Online multiplayer variables
from network import NetworkClient
network_client = NetworkClient()
online_mode = False
online_player_color = None
waiting_for_opponent = False
opponent_disconnected = False

ai_thinking = False
fullscreen = False
settings_open = False  # Track if settings panel is visible
last_move = None  # Track last move (row, col) to highlight it

# Animation variables
menu_animation_offset = 0
menu_animation_direction = 1
game_over_sound_played = False  # Track if we've played the game over sound
game_saved_to_history = False  # Track if we've saved this game to user history
animating_discs = []  # List of discs currently animating: [(row, col, start_color, end_color, progress)]
ANIMATION_SPEED = 0.20  # Smoother animation progress per frame (0 to 1)

def draw_gradient_rect(surface, rect, color1, color2, vertical=True):
    """Draw a rectangle with a gradient fill"""
    if vertical:
        for i in range(rect.height):
            ratio = i / rect.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.x, rect.y + i), 
                           (rect.x + rect.width, rect.y + i))
    else:
        for i in range(rect.width):
            ratio = i / rect.width
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.x + i, rect.y), 
                           (rect.x + i, rect.y + rect.height))

def draw_button(surface, rect, text, font, base_color, hover_color, is_hovered, text_color=(255, 255, 255)):
    """Draw an attractive button with gradient, shadow, and hover effects"""
    color = hover_color if is_hovered else base_color
    
    # Draw multiple shadow layers for depth
    for i in range(3):
        shadow_rect = rect.copy()
        shadow_rect.x += 2 + i
        shadow_rect.y += 2 + i
        shadow_alpha = 80 - (i * 20)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, shadow_alpha), shadow_surface.get_rect(), border_radius=20)
        surface.blit(shadow_surface, shadow_rect)
    
    # Draw gradient button with enhanced colors
    if is_hovered:
        gradient_start = tuple(min(255, c + 30) for c in color)
        gradient_end = tuple(min(255, c + 60) for c in color)
    else:
        gradient_start = color
        gradient_end = tuple(min(255, c + 40) for c in color)
    
    draw_gradient_rect(surface, rect, gradient_start, gradient_end, vertical=True)
    
    # Add inner glow effect
    if is_hovered:
        glow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        glow_rect = glow_surface.get_rect()
        pygame.draw.rect(glow_surface, (*hover_color, 60), glow_rect, border_radius=20)
        surface.blit(glow_surface, rect)
    
    # Draw outer border with glow effect if hovered
    if is_hovered:
        for i in range(3):
            border_color = (*hover_color, 100 - i * 30)
            border_surface = pygame.Surface((rect.width + i * 2, rect.height + i * 2), pygame.SRCALPHA)
            border_rect = border_surface.get_rect()
            pygame.draw.rect(border_surface, border_color, border_rect, 2, border_radius=20)
            surface.blit(border_surface, (rect.x - i, rect.y - i))
        border_color = (255, 255, 255)
        border_width = 3
    else:
        border_color = (200, 200, 220)
        border_width = 2
    
    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=20)
    
    # Draw text with shadow
    text_shadow = font.render(text, True, (0, 0, 0))
    text_shadow_rect = text_shadow.get_rect(center=(rect.centerx + 2, rect.centery + 2))
    surface.blit(text_shadow, text_shadow_rect)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def draw_achievement_notification(surface, width, achievements, notification_time):
    """Draw achievement unlock notification"""
    current_time = time.time()
    elapsed = current_time - notification_time
    
    # Show notification for 5 seconds
    if elapsed > 5:
        return False  # Hide notification
    
    # Slide in animation (first 0.5 seconds)
    slide_progress = min(1.0, elapsed / 0.5)
    # Fade out animation (last 0.5 seconds)
    fade_progress = 1.0 if elapsed < 4.5 else (5 - elapsed) / 0.5
    
    alpha = int(255 * fade_progress)
    
    # Notification box
    box_width = 450
    box_height = 100 * len(achievements)
    box_x = width - box_width - 20
    box_y = 20 + int((1 - slide_progress) * -box_height)
    
    # Create semi-transparent surface
    notification_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    
    # Background
    bg_color = (*pygame.Color(40, 60, 100), alpha)
    pygame.draw.rect(notification_surface, bg_color, (0, 0, box_width, box_height), border_radius=15)
    
    # Border with glow effect
    border_color = (*pygame.Color(255, 200, 100), alpha)
    pygame.draw.rect(notification_surface, border_color, (0, 0, box_width, box_height), 3, border_radius=15)
    
    # Draw each achievement
    y_offset = 10
    for achievement in achievements:
        # Icon
        icon_font = pygame.font.SysFont("Segoe UI Emoji", 40)
        icon_surface = icon_font.render(achievement['icon'], True, (255, 255, 255, alpha))
        notification_surface.blit(icon_surface, (15, y_offset + 10))
        
        # "Achievement Unlocked!" text
        title_font = pygame.font.SysFont("Arial", 18, bold=True)
        title_color = (*pygame.Color(255, 200, 100), alpha)
        title_surface = title_font.render("🏆 Achievement Unlocked!", True, title_color)
        notification_surface.blit(title_surface, (75, y_offset + 10))
        
        # Achievement name
        name_font = pygame.font.SysFont("Arial", 22, bold=True)
        name_color = (*pygame.Color(255, 255, 150), alpha)
        name_surface = name_font.render(achievement['name'], True, name_color)
        notification_surface.blit(name_surface, (75, y_offset + 35))
        
        # Points
        points_font = pygame.font.SysFont("Arial", 18, bold=True)
        points_color = (*pygame.Color(100, 255, 100), alpha)
        points_surface = points_font.render(f"+{achievement['points']} points", True, points_color)
        notification_surface.blit(points_surface, (75, y_offset + 60))
        
        y_offset += 90
    
    surface.blit(notification_surface, (box_x, box_y))
    return True  # Still showing

def pick_random_avatars():
    """Pick two different random avatars for the players"""
    global player1_avatar, player2_avatar
    avatars = random.sample(AVATAR_EMOJIS, 2)  # Pick 2 different avatars
    player1_avatar = avatars[0]
    player2_avatar = avatars[1]

def validate_email_format(email, provider):
    """Validate email format based on provider"""
    email = email.strip().lower()
    
    if not email:
        return False, "Email cannot be empty"
    
    # Check for @ symbol
    if '@' not in email:
        return False, "Email must contain @"
    
    # Provider-specific validation
    if provider == 'google':
        if not email.endswith('@gmail.com'):
            return False, "Google email must end with @gmail.com"
    elif provider == 'facebook':
        if not ('@' in email and '.' in email.split('@')[1]):
            return False, "Enter a valid email address"
    elif provider == 'google_play':
        if not email.endswith('@gmail.com'):
            return False, "Google Play requires Gmail (@gmail.com)"
    
    # Check for valid characters before @
    username_part = email.split('@')[0]
    if len(username_part) < 3:
        return False, "Email username too short (min 3 characters)"
    
    return True, ""

def draw_player_panel(surface, x, y, width, height, player_name, player_color, disc_count, is_current_turn, is_you=False, avatar_emoji=None):
    """Draw a player info panel with avatar and status"""
    # Panel background with gradient
    panel_rect = pygame.Rect(x, y, width, height)
    if is_current_turn:
        # Highlight if it's this player's turn
        bg_color1 = (40, 60, 80)
        bg_color2 = (60, 80, 100)
        border_color = (100, 200, 255)
    else:
        bg_color1 = (30, 30, 40)
        bg_color2 = (40, 40, 50)
        border_color = (80, 80, 100)
    
    draw_gradient_rect(surface, panel_rect, bg_color1, bg_color2, vertical=True)
    pygame.draw.rect(surface, border_color, panel_rect, 3, border_radius=15)
    
    # Avatar (circular disc representation)
    avatar_radius = min(width // 3, 40)
    avatar_x = x + width // 2
    avatar_y = y + avatar_radius + 20
    
    # Draw avatar background glow
    if is_current_turn:
        glow_radius = avatar_radius + 8
        glow_color = (255, 215, 0, 150)  # Gold glow
        for i in range(3):
            pygame.draw.circle(surface, glow_color, (avatar_x, avatar_y), glow_radius - i * 2, 2)
    
    # Draw avatar background circle
    avatar_bg_color = (50, 50, 60) if not is_current_turn else (70, 90, 110)
    pygame.draw.circle(surface, avatar_bg_color, (avatar_x, avatar_y), avatar_radius)
    pygame.draw.circle(surface, border_color, (avatar_x, avatar_y), avatar_radius, 3)
    
    # Draw emoji avatar if provided
    if avatar_emoji:
        try:
            # Use a large font size for emoji
            emoji_font = pygame.font.SysFont("Segoe UI Emoji", int(avatar_radius * 1.3))
            emoji_surface = emoji_font.render(avatar_emoji, True, (255, 255, 255))
            emoji_rect = emoji_surface.get_rect(center=(avatar_x, avatar_y))
            surface.blit(emoji_surface, emoji_rect)
        except:
            # Fallback to disc if emoji rendering fails
            avatar_color = BLACK if player_color == 'B' else WHITE
            pygame.draw.circle(surface, avatar_color, (avatar_x, avatar_y), avatar_radius - 5)
    else:
        # Draw disc as fallback
        avatar_color = BLACK if player_color == 'B' else WHITE
        pygame.draw.circle(surface, avatar_color, (avatar_x, avatar_y), avatar_radius - 5)
    
    # Player name
    name_font = pygame.font.SysFont("Arial", 20, bold=True)
    name_text = name_font.render(player_name, True, (255, 255, 255))
    name_rect = name_text.get_rect(center=(avatar_x, avatar_y + avatar_radius + 25))
    surface.blit(name_text, name_rect)
    
    # Color indicator (Black/White)
    color_label_font = pygame.font.SysFont("Arial", 16, bold=True)
    color_name = "Black" if player_color == 'B' else "White"
    color_display_color = (255, 255, 255) if player_color == 'W' else (0, 0, 0)
    
    # Draw small colored circle next to text
    circle_x = avatar_x - 35
    circle_y = name_rect.bottom + 18
    circle_radius = 8
    pygame.draw.circle(surface, color_display_color, (circle_x, circle_y), circle_radius)
    pygame.draw.circle(surface, (150, 150, 170), (circle_x, circle_y), circle_radius, 2)
    
    color_text = color_label_font.render(color_name, True, (150, 150, 180))
    color_rect = color_text.get_rect(midleft=(circle_x + circle_radius + 8, circle_y))
    surface.blit(color_text, color_rect)
    
    # "You" indicator
    if is_you:
        you_font = pygame.font.SysFont("Arial", 14, italic=True)
        you_text = you_font.render("(You)", True, (100, 200, 255))
        you_rect = you_text.get_rect(center=(avatar_x, color_rect.bottom + 15))
        surface.blit(you_text, you_rect)
        name_bottom = you_rect.bottom + 10  # Add extra spacing after "(You)"
    else:
        name_bottom = color_rect.bottom + 10  # Add extra spacing after color label
    
    # Score display
    score_font = pygame.font.SysFont("Arial", 32, bold=True)
    score_text = score_font.render(f"{disc_count}", True, (255, 215, 0))
    score_rect = score_text.get_rect(center=(avatar_x, name_bottom + 35))
    surface.blit(score_text, score_rect)
    
    # "Discs" label
    label_font = pygame.font.SysFont("Arial", 14)
    label_text = label_font.render("discs", True, (180, 180, 200))
    label_rect = label_text.get_rect(center=(avatar_x, score_rect.bottom + 18))
    surface.blit(label_text, label_rect)
    
    # Turn indicator
    if is_current_turn:
        turn_font = pygame.font.SysFont("Arial", 16, bold=True)
        turn_text = turn_font.render("YOUR TURN", True, (255, 215, 0))
        turn_rect = turn_text.get_rect(center=(avatar_x, y + height - 35))
        
        # Animated arrow
        arrow_y = turn_rect.top - 20
        arrow_offset = int(5 * math.sin(pygame.time.get_ticks() / 200))
        pygame.draw.polygon(surface, (255, 215, 0), [
            (avatar_x, arrow_y + arrow_offset),
            (avatar_x - 8, arrow_y - 10 + arrow_offset),
            (avatar_x + 8, arrow_y - 10 + arrow_offset)
        ])
        
        surface.blit(turn_text, turn_rect)

def draw_main_menu(surface, width, height, mouse_pos):
    """Draw the main menu screen"""
    # Gradient background
    bg_rect = pygame.Rect(0, 0, width, height)
    draw_gradient_rect(surface, bg_rect, (20, 20, 40), (60, 20, 80), vertical=True)
    
    # Animated circles in background
    for i in range(3):
        offset = (menu_animation_offset + i * 120) % 360
        x = width // 2 + int(math.cos(math.radians(offset)) * 100)
        y = height // 3 + int(math.sin(math.radians(offset)) * 50)
        pygame.draw.circle(surface, (80, 40, 120, 50), (x, y), 60)
    
    # Title
    title_font = pygame.font.SysFont("Arial", 80, bold=True)
    title_text = title_font.render("OTHELLO", True, (255, 105, 180))
    title_shadow = title_font.render("OTHELLO", True, (100, 20, 80))
    title_rect = title_text.get_rect(center=(width // 2, height // 4))
    surface.blit(title_shadow, (title_rect.x + 4, title_rect.y + 4))
    surface.blit(title_text, title_rect)
    
    # Subtitle
    subtitle_font = pygame.font.SysFont("Arial", 24, italic=True)
    subtitle_text = subtitle_font.render("The Classic Strategy Game", True, (255, 182, 193))
    subtitle_rect = subtitle_text.get_rect(center=(width // 2, height // 4 + 60))
    surface.blit(subtitle_text, subtitle_rect)
    
    # Buttons
    button_font = pygame.font.SysFont("Arial", 36, bold=True)
    button_width = 320
    button_height = 80
    button_spacing = 25
    
    play_rect = pygame.Rect((width - button_width) // 2, height // 2, button_width, button_height)
    exit_rect = pygame.Rect((width - button_width) // 2, height // 2 + button_height + button_spacing, button_width, button_height)
    
    # Check hover
    play_hover = play_rect.collidepoint(mouse_pos)
    exit_hover = exit_rect.collidepoint(mouse_pos)
    
    # More attractive colors with better contrast
    draw_button(surface, play_rect, "▶ PLAY", button_font, (40, 180, 100), (60, 220, 130), play_hover)
    draw_button(surface, exit_rect, "✖ EXIT", button_font, (220, 50, 80), (255, 80, 110), exit_hover)
    
    return play_rect, exit_rect

def draw_login_menu(surface, width, height, mouse_pos):
    """Draw the login options screen"""
    # Gradient background
    bg_rect = pygame.Rect(0, 0, width, height)
    draw_gradient_rect(surface, bg_rect, (30, 20, 50), (50, 30, 80), vertical=True)
    
    # Title
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    title_text = title_font.render("Login to Play Online", True, (255, 105, 180))
    title_rect = title_text.get_rect(center=(width // 2, height // 5))
    surface.blit(title_text, title_rect)
    
    # Subtitle
    subtitle_font = pygame.font.SysFont("Arial", 22, italic=True)
    subtitle_text = subtitle_font.render("Choose your login method", True, (200, 200, 255))
    subtitle_rect = subtitle_text.get_rect(center=(width // 2, height // 5 + 60))
    surface.blit(subtitle_text, subtitle_rect)
    
    # Buttons
    button_font = pygame.font.SysFont("Arial", 32, bold=True)
    button_width = 400
    button_height = 70
    button_spacing = 25
    
    start_y = height // 2 - 60
    google_rect = pygame.Rect((width - button_width) // 2, start_y, button_width, button_height)
    facebook_rect = pygame.Rect((width - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height)
    google_play_rect = pygame.Rect((width - button_width) // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height)
    back_rect = pygame.Rect((width - button_width) // 2, start_y + 3 * (button_height + button_spacing) + 20, button_width, button_height)
    
    # Check hover
    google_hover = google_rect.collidepoint(mouse_pos)
    facebook_hover = facebook_rect.collidepoint(mouse_pos)
    google_play_hover = google_play_rect.collidepoint(mouse_pos)
    back_hover = back_rect.collidepoint(mouse_pos)
    
    # Draw buttons with different colors for each service
    draw_button(surface, google_rect, "Login with Google", button_font, (66, 133, 244), (96, 163, 255), google_hover)
    draw_button(surface, facebook_rect, "Login with Facebook", button_font, (24, 119, 242), (54, 149, 255), facebook_hover)
    draw_button(surface, google_play_rect, "Login with Google Play", button_font, (1, 135, 95), (31, 165, 125), google_play_hover)
    draw_button(surface, back_rect, "Back", button_font, (100, 100, 100), (130, 130, 130), back_hover)
    
    return google_rect, facebook_rect, google_play_rect, back_rect

def draw_user_input_screen(surface, width, height, mouse_pos, provider, email_input, name_input, active_field, error_msg=""):
    """Draw the user input screen to collect email and username"""
    # Gradient background
    bg_rect = pygame.Rect(0, 0, width, height)
    draw_gradient_rect(surface, bg_rect, (25, 25, 50), (45, 35, 70), vertical=True)
    
    # Provider colors
    provider_colors = {
        'google': (66, 133, 244),
        'facebook': (24, 119, 242),
        'google_play': (1, 135, 95)
    }
    provider_names = {
        'google': 'Google',
        'facebook': 'Facebook',
        'google_play': 'Google Play'
    }
    
    color = provider_colors.get(provider, (100, 100, 255))
    provider_name = provider_names.get(provider, provider)
    
    # Title
    title_font = pygame.font.SysFont("Arial", 50, bold=True)
    title_text = title_font.render(f"Login with {provider_name}", True, color)
    title_rect = title_text.get_rect(center=(width // 2, height // 6))
    surface.blit(title_text, title_rect)
    
    # Instructions
    inst_font = pygame.font.SysFont("Arial", 20)
    inst_text = inst_font.render("Enter your details to continue", True, (200, 200, 220))
    inst_rect = inst_text.get_rect(center=(width // 2, height // 6 + 50))
    surface.blit(inst_text, inst_rect)
    
    # Email format hint based on provider
    hint_font = pygame.font.SysFont("Arial", 16, italic=True)
    if provider == 'google':
        hint_text = hint_font.render("Example: yourname@gmail.com", True, (150, 150, 180))
    elif provider == 'facebook':
        hint_text = hint_font.render("Example: yourname@example.com", True, (150, 150, 180))
    elif provider == 'google_play':
        hint_text = hint_font.render("Example: yourname@gmail.com", True, (150, 150, 180))
    else:
        hint_text = hint_font.render("Example: yourname@domain.com", True, (150, 150, 180))
    
    hint_rect = hint_text.get_rect(center=(width // 2, height // 6 + 80))
    surface.blit(hint_text, hint_rect)
    
    # Input fields
    input_width = 450
    input_height = 50
    input_spacing = 30
    
    start_y = height // 2 - 80
    
    # Email label and input
    label_font = pygame.font.SysFont("Arial", 22, bold=True)
    email_label = label_font.render("Email:", True, (220, 220, 255))
    surface.blit(email_label, (width // 2 - input_width // 2, start_y - 30))
    
    email_rect = pygame.Rect((width - input_width) // 2, start_y, input_width, input_height)
    email_active = active_field == "email"
    border_color = color if email_active else (100, 100, 120)
    pygame.draw.rect(surface, (50, 50, 70), email_rect)
    pygame.draw.rect(surface, border_color, email_rect, 3)
    
    # Email text
    input_font = pygame.font.SysFont("Arial", 24)
    email_surface = input_font.render(email_input, True, (255, 255, 255))
    surface.blit(email_surface, (email_rect.x + 10, email_rect.y + 12))
    
    # Username label and input
    name_label = label_font.render("Username:", True, (220, 220, 255))
    surface.blit(name_label, (width // 2 - input_width // 2, start_y + input_height + input_spacing - 30))
    
    name_rect = pygame.Rect((width - input_width) // 2, start_y + input_height + input_spacing, input_width, input_height)
    name_active = active_field == "username"
    border_color = color if name_active else (100, 100, 120)
    pygame.draw.rect(surface, (50, 50, 70), name_rect)
    pygame.draw.rect(surface, border_color, name_rect, 3)
    
    # Username text
    name_surface = input_font.render(name_input, True, (255, 255, 255))
    surface.blit(name_surface, (name_rect.x + 10, name_rect.y + 12))
    
    # Error message display
    if error_msg:
        error_font = pygame.font.SysFont("Arial", 18, bold=True)
        error_text = error_font.render(error_msg, True, (255, 100, 100))
        error_rect = error_text.get_rect(center=(width // 2, start_y + 2 * (input_height + input_spacing) - 10))
        surface.blit(error_text, error_rect)
    
    # Buttons
    button_font = pygame.font.SysFont("Arial", 30, bold=True)
    button_width = 200
    button_height = 60
    
    continue_rect = pygame.Rect(width // 2 - button_width - 10, start_y + 2 * (input_height + input_spacing) + 20, button_width, button_height)
    back_rect = pygame.Rect(width // 2 + 10, start_y + 2 * (input_height + input_spacing) + 20, button_width, button_height)
    
    continue_hover = continue_rect.collidepoint(mouse_pos)
    back_hover = back_rect.collidepoint(mouse_pos)
    
    # Enable continue button only if both fields are filled
    can_continue = len(email_input.strip()) > 0 and len(name_input.strip()) > 0
    continue_color = color if can_continue else (80, 80, 90)
    continue_hover_color = tuple(min(c + 30, 255) for c in color) if can_continue else (80, 80, 90)
    
    draw_button(surface, continue_rect, "CONTINUE", button_font, continue_color, continue_hover_color, continue_hover and can_continue)
    draw_button(surface, back_rect, "BACK", button_font, (100, 100, 100), (130, 130, 130), back_hover)
    
    return email_rect, name_rect, continue_rect, back_rect, can_continue

def draw_user_profile_screen(surface, width, height, mouse_pos, user_data):
    """Draw the user profile screen showing stats and history"""
    # Gradient background
    bg_rect = pygame.Rect(0, 0, width, height)
    draw_gradient_rect(surface, bg_rect, (20, 30, 50), (40, 50, 80), vertical=True)
    
    # Welcome message
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    title_text = title_font.render(f"Welcome, {user_data['username']}!", True, (100, 200, 255))
    title_rect = title_text.get_rect(center=(width // 2, 60))
    surface.blit(title_text, title_rect)
    
    # Stats panel
    stats_font = pygame.font.SysFont("Arial", 22, bold=True)
    stats_value_font = pygame.font.SysFont("Arial", 20)
    stats = user_data['stats']
    
    # Stats box
    stats_box = pygame.Rect(width // 2 - 300, 120, 600, 280)
    pygame.draw.rect(surface, (30, 40, 70), stats_box, border_radius=15)
    pygame.draw.rect(surface, (100, 150, 255), stats_box, 3, border_radius=15)
    
    # Stats title
    stats_title = stats_font.render("Your Statistics", True, (255, 200, 100))
    surface.blit(stats_title, (width // 2 - 80, 135))
    
    # Stats content in two columns
    y_offset = 175
    x_left = width // 2 - 250
    x_right = width // 2 + 20
    line_height = 35
    
    stats_items = [
        (f"Total Games:", f"{stats['total_games']}", x_left),
        (f"Wins:", f"{stats['wins']}", x_right),
        (f"Losses:", f"{stats['losses']}", x_left),
        (f"Draws:", f"{stats['draws']}", x_right),
        (f"Win Rate:", f"{stats['win_rate']}%", x_left),
        (f"Highest Score:", f"{stats['highest_score']}", x_right),
        (f"VS AI Games:", f"{stats['vs_ai_games']}", x_left),
        (f"Online Games:", f"{stats['online_games']}", x_right),
    ]
    
    for i, (label, value, x_pos) in enumerate(stats_items):
        y_pos = y_offset + (i // 2) * line_height
        label_surface = stats_value_font.render(label, True, (180, 180, 220))
        value_surface = stats_value_font.render(value, True, (255, 255, 150))
        surface.blit(label_surface, (x_pos, y_pos))
        surface.blit(value_surface, (x_pos + 150, y_pos))
    
    # Buttons
    button_font = pygame.font.SysFont("Arial", 32, bold=True)
    button_width = 280
    button_height = 70
    button_spacing = 20
    
    # Two columns of buttons
    left_x = width // 2 - button_width - 15
    right_x = width // 2 + 15
    start_y = 430
    
    # Left column: START PLAYING, ACHIEVEMENTS
    play_rect = pygame.Rect(left_x, start_y, button_width, button_height)
    achievements_rect = pygame.Rect(left_x, start_y + button_height + button_spacing, button_width, button_height)
    
    # Right column: FRIENDS, LOGOUT
    friends_rect = pygame.Rect(right_x, start_y, button_width, button_height)
    logout_rect = pygame.Rect(right_x, start_y + button_height + button_spacing, button_width, button_height)
    
    play_hover = play_rect.collidepoint(mouse_pos)
    achievements_hover = achievements_rect.collidepoint(mouse_pos)
    friends_hover = friends_rect.collidepoint(mouse_pos)
    logout_hover = logout_rect.collidepoint(mouse_pos)
    
    draw_button(surface, play_rect, "START PLAYING", button_font, (60, 180, 120), (80, 220, 150), play_hover)
    draw_button(surface, achievements_rect, "ACHIEVEMENTS", button_font, (180, 120, 60), (220, 150, 80), achievements_hover)
    draw_button(surface, friends_rect, "FRIENDS", button_font, (60, 120, 180), (80, 150, 220), friends_hover)
    draw_button(surface, logout_rect, "LOGOUT", button_font, (180, 60, 60), (220, 80, 80), logout_hover)
    
    return play_rect, achievements_rect, friends_rect, logout_rect

def draw_achievements_screen(surface, width, height, mouse_pos, all_achievements, user_achievements):
    """Draw the achievements screen showing all achievements and user progress"""
    # Gradient background
    bg_rect = pygame.Rect(0, 0, width, height)
    draw_gradient_rect(surface, bg_rect, (20, 30, 50), (40, 50, 80), vertical=True)
    
    # Title
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    title_text = title_font.render("Achievements", True, (255, 200, 100))
    title_rect = title_text.get_rect(center=(width // 2, 50))
    surface.blit(title_text, title_rect)
    
    # Calculate total points
    user_achievement_ids = [a['achievement_id'] for a in user_achievements]
    earned_points = sum(a['points'] for a in all_achievements if a['achievement_id'] in user_achievement_ids)
    total_points = sum(a['points'] for a in all_achievements)
    
    # Points display
    points_font = pygame.font.SysFont("Arial", 24, bold=True)
    points_text = points_font.render(f"Points: {earned_points} / {total_points}", True, (100, 200, 255))
    points_rect = points_text.get_rect(center=(width // 2, 95))
    surface.blit(points_text, points_rect)
    
    # Progress bar
    bar_width = 400
    bar_height = 20
    bar_x = (width - bar_width) // 2
    bar_y = 115
    progress = earned_points / total_points if total_points > 0 else 0
    
    pygame.draw.rect(surface, (40, 50, 70), (bar_x, bar_y, bar_width, bar_height), border_radius=10)
    pygame.draw.rect(surface, (100, 200, 255), (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=10)
    pygame.draw.rect(surface, (100, 150, 255), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=10)
    
    # Achievements list with scrolling
    list_y = 150
    list_height = height - 230
    item_height = 80
    padding = 10
    
    # Scrollable area
    scroll_rect = pygame.Rect(50, list_y, width - 100, list_height)
    pygame.draw.rect(surface, (30, 40, 70), scroll_rect, border_radius=10)
    pygame.draw.rect(surface, (100, 150, 255), scroll_rect, 2, border_radius=10)
    
    # Draw achievements
    y_offset = list_y + padding
    for achievement in all_achievements:
        is_unlocked = achievement['achievement_id'] in user_achievement_ids
        
        # Achievement box
        item_rect = pygame.Rect(60, y_offset, width - 120, item_height - padding)
        
        # Different colors for locked/unlocked
        if is_unlocked:
            pygame.draw.rect(surface, (60, 100, 60), item_rect, border_radius=8)
            pygame.draw.rect(surface, (100, 200, 100), item_rect, 2, border_radius=8)
        else:
            pygame.draw.rect(surface, (50, 50, 60), item_rect, border_radius=8)
            pygame.draw.rect(surface, (100, 100, 120), item_rect, 2, border_radius=8)
        
        # Icon (emoji)
        icon_font = pygame.font.SysFont("Segoe UI Emoji", 32)
        icon_text = icon_font.render(achievement['icon'], True, (255, 255, 255))
        surface.blit(icon_text, (75, y_offset + 15))
        
        # Achievement name
        name_font = pygame.font.SysFont("Arial", 20, bold=True)
        name_color = (255, 255, 150) if is_unlocked else (150, 150, 170)
        name_text = name_font.render(achievement['name'], True, name_color)
        surface.blit(name_text, (130, y_offset + 10))
        
        # Description
        desc_font = pygame.font.SysFont("Arial", 16)
        desc_color = (200, 200, 220) if is_unlocked else (120, 120, 140)
        desc_text = desc_font.render(achievement['description'], True, desc_color)
        surface.blit(desc_text, (130, y_offset + 35))
        
        # Points
        points_badge_font = pygame.font.SysFont("Arial", 18, bold=True)
        points_badge_text = points_badge_font.render(f"+{achievement['points']}", True, (255, 200, 100))
        surface.blit(points_badge_text, (width - 130, y_offset + 25))
        
        y_offset += item_height
        
        # Stop if we go off screen
        if y_offset > list_y + list_height - item_height:
            break
    
    # Back button
    button_font = pygame.font.SysFont("Arial", 32, bold=True)
    button_width = 200
    button_height = 60
    back_rect = pygame.Rect((width - button_width) // 2, height - 70, button_width, button_height)
    back_hover = back_rect.collidepoint(mouse_pos)
    draw_button(surface, back_rect, "BACK", button_font, (100, 100, 100), (130, 130, 130), back_hover)
    
    return back_rect

def draw_friends_screen(surface, width, height, mouse_pos, friends_list, pending_requests):
    """Draw the friends management screen"""
    # Gradient background
    bg_rect = pygame.Rect(0, 0, width, height)
    draw_gradient_rect(surface, bg_rect, (20, 30, 50), (40, 50, 80), vertical=True)
    
    # Title
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    title_text = title_font.render("Friends", True, (100, 200, 255))
    title_rect = title_text.get_rect(center=(width // 2, 50))
    surface.blit(title_text, title_rect)
    
    # Stats
    stats_font = pygame.font.SysFont("Arial", 20)
    stats_text = stats_font.render(f"Total Friends: {len(friends_list)}  |  Pending Requests: {len(pending_requests)}", True, (180, 180, 220))
    stats_rect = stats_text.get_rect(center=(width // 2, 95))
    surface.blit(stats_text, stats_rect)
    
    # Two sections: Pending Requests and Friends List
    section_height = (height - 250) // 2
    
    # === PENDING REQUESTS SECTION ===
    pending_y = 130
    pending_rect = pygame.Rect(50, pending_y, width - 100, section_height)
    pygame.draw.rect(surface, (30, 40, 70), pending_rect, border_radius=10)
    pygame.draw.rect(surface, (180, 100, 100), pending_rect, 2, border_radius=10)
    
    # Section title
    section_font = pygame.font.SysFont("Arial", 24, bold=True)
    section_title = section_font.render("Pending Requests", True, (255, 150, 150))
    surface.blit(section_title, (65, pending_y + 10))
    
    # List pending requests
    item_y = pending_y + 45
    item_font = pygame.font.SysFont("Arial", 18)
    
    if not pending_requests:
        no_requests_text = item_font.render("No pending friend requests", True, (150, 150, 170))
        surface.blit(no_requests_text, (70, item_y))
    else:
        for request in pending_requests[:3]:  # Show max 3
            # Friend info
            friend_text = item_font.render(f"📧 {request['email']}", True, (200, 200, 220))
            surface.blit(friend_text, (70, item_y))
            
            # Accept button (mini)
            accept_btn = pygame.Rect(width - 220, item_y - 5, 80, 30)
            accept_hover = accept_btn.collidepoint(mouse_pos)
            btn_color = (80, 180, 80) if accept_hover else (60, 150, 60)
            pygame.draw.rect(surface, btn_color, accept_btn, border_radius=5)
            accept_text = pygame.font.SysFont("Arial", 16, bold=True).render("Accept", True, (255, 255, 255))
            surface.blit(accept_text, (accept_btn.x + 15, accept_btn.y + 7))
            
            item_y += 40
    
    # === FRIENDS LIST SECTION ===
    friends_y = pending_y + section_height + 20
    friends_rect = pygame.Rect(50, friends_y, width - 100, section_height)
    pygame.draw.rect(surface, (30, 40, 70), friends_rect, border_radius=10)
    pygame.draw.rect(surface, (100, 150, 255), friends_rect, 2, border_radius=10)
    
    # Section title
    section_title = section_font.render("My Friends", True, (150, 200, 255))
    surface.blit(section_title, (65, friends_y + 10))
    
    # List friends
    item_y = friends_y + 45
    
    if not friends_list:
        no_friends_text = item_font.render("No friends yet. Add some friends!", True, (150, 150, 170))
        surface.blit(no_friends_text, (70, item_y))
    else:
        for friend in friends_list[:4]:  # Show max 4
            # Friend info
            friend_text = item_font.render(f"👤 {friend.get('username', 'Unknown')} ({friend['email']})", True, (200, 200, 220))
            surface.blit(friend_text, (70, item_y))
            
            # Stats if available
            if 'stats' in friend:
                stats = friend['stats']
                stats_text = pygame.font.SysFont("Arial", 14).render(
                    f"Games: {stats['total_games']} | Wins: {stats['wins']}", 
                    True, (150, 150, 170)
                )
                surface.blit(stats_text, (90, item_y + 20))
                item_y += 45
            else:
                item_y += 40
    
    # Buttons
    button_font = pygame.font.SysFont("Arial", 28, bold=True)
    button_width = 220
    button_height = 55
    button_spacing = 20
    
    add_friend_rect = pygame.Rect(width // 2 - button_width - button_spacing // 2, height - 70, button_width, button_height)
    back_rect = pygame.Rect(width // 2 + button_spacing // 2, height - 70, button_width, button_height)
    
    add_hover = add_friend_rect.collidepoint(mouse_pos)
    back_hover = back_rect.collidepoint(mouse_pos)
    
    draw_button(surface, add_friend_rect, "ADD FRIEND", button_font, (60, 180, 120), (80, 220, 150), add_hover)
    draw_button(surface, back_rect, "BACK", button_font, (100, 100, 100), (130, 130, 130), back_hover)
    
    return add_friend_rect, back_rect, pending_requests

def draw_add_friend_screen(surface, width, height, mouse_pos, friend_email_input, message=""):
    """Draw the add friend screen"""
    # Gradient background
    bg_rect = pygame.Rect(0, 0, width, height)
    draw_gradient_rect(surface, bg_rect, (20, 30, 50), (40, 50, 80), vertical=True)
    
    # Title
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    title_text = title_font.render("Add Friend", True, (100, 200, 255))
    title_rect = title_text.get_rect(center=(width // 2, height // 4))
    surface.blit(title_text, title_rect)
    
    # Instructions
    instruction_font = pygame.font.SysFont("Arial", 20)
    instruction_text = instruction_font.render("Enter your friend's email address:", True, (180, 180, 220))
    instruction_rect = instruction_text.get_rect(center=(width // 2, height // 2 - 80))
    surface.blit(instruction_text, instruction_rect)
    
    # Email input field
    input_width = 500
    input_height = 55
    input_rect = pygame.Rect((width - input_width) // 2, height // 2 - 30, input_width, input_height)
    
    pygame.draw.rect(surface, (60, 60, 80), input_rect, border_radius=8)
    pygame.draw.rect(surface, (100, 200, 255), input_rect, 3, border_radius=8)
    
    # Input text
    input_font = pygame.font.SysFont("Arial", 24)
    text_surface = input_font.render(friend_email_input, True, (255, 255, 255))
    text_rect = text_surface.get_rect(midleft=(input_rect.left + 15, input_rect.centery))
    surface.blit(text_surface, text_rect)
    
    # Message (success or error)
    if message:
        message_font = pygame.font.SysFont("Arial", 20)
        message_color = (100, 255, 100) if "success" in message.lower() else (255, 100, 100)
        message_text = message_font.render(message, True, message_color)
        message_rect = message_text.get_rect(center=(width // 2, height // 2 + 50))
        surface.blit(message_text, message_rect)
    
    # Buttons
    button_font = pygame.font.SysFont("Arial", 32, bold=True)
    button_width = 200
    button_height = 60
    button_spacing = 30
    
    send_rect = pygame.Rect(width // 2 - button_width - button_spacing // 2, height // 2 + 110, button_width, button_height)
    back_rect = pygame.Rect(width // 2 + button_spacing // 2, height // 2 + 110, button_width, button_height)
    
    send_hover = send_rect.collidepoint(mouse_pos)
    back_hover = back_rect.collidepoint(mouse_pos)
    
    draw_button(surface, send_rect, "SEND", button_font, (60, 180, 120), (80, 220, 150), send_hover)
    draw_button(surface, back_rect, "BACK", button_font, (100, 100, 100), (130, 130, 130), back_hover)
    
    return input_rect, send_rect, back_rect

def draw_play_mode_menu(surface, width, height, mouse_pos):
    """Draw the play mode selection screen"""
    # Gradient background
    bg_rect = pygame.Rect(0, 0, width, height)
    draw_gradient_rect(surface, bg_rect, (20, 40, 20), (20, 80, 60), vertical=True)
    
    # Title
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    title_text = title_font.render("Select Play Mode", True, (255, 105, 180))
    title_rect = title_text.get_rect(center=(width // 2, height // 5))
    surface.blit(title_text, title_rect)
    
    # Buttons
    button_font = pygame.font.SysFont("Arial", 36, bold=True)
    button_width = 350
    button_height = 70
    button_spacing = 25
    
    start_y = height // 2 - 80
    ai_rect = pygame.Rect((width - button_width) // 2, start_y, button_width, button_height)
    friend_rect = pygame.Rect((width - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height)
    back_rect = pygame.Rect((width - button_width) // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height)
    
    # Check hover
    ai_hover = ai_rect.collidepoint(mouse_pos)
    friend_hover = friend_rect.collidepoint(mouse_pos)
    back_hover = back_rect.collidepoint(mouse_pos)
    
    draw_button(surface, ai_rect, "Play vs AI", button_font, (120, 60, 180), (150, 80, 220), ai_hover)
    draw_button(surface, friend_rect, "Play vs Friend", button_font, (60, 120, 180), (80, 150, 220), friend_hover)
    draw_button(surface, back_rect, "Back", button_font, (100, 100, 100), (130, 130, 130), back_hover)
    
    return ai_rect, friend_rect, back_rect

def draw_difficulty_menu(surface, width, height, mouse_pos):
    """Draw the difficulty selection screen"""
    # Gradient background
    bg_rect = pygame.Rect(0, 0, width, height)
    draw_gradient_rect(surface, bg_rect, (40, 20, 20), (80, 20, 60), vertical=True)
    
    # Title
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    title_text = title_font.render("Select Difficulty", True, (255, 105, 180))
    title_rect = title_text.get_rect(center=(width // 2, height // 5))
    surface.blit(title_text, title_rect)
    
    # Buttons
    button_font = pygame.font.SysFont("Arial", 36, bold=True)
    button_width = 300
    button_height = 70
    button_spacing = 30
    
    easy_rect = pygame.Rect((width - button_width) // 2, height // 2 - 120, button_width, button_height)
    medium_rect = pygame.Rect((width - button_width) // 2, height // 2 - 30, button_width, button_height)
    hard_rect = pygame.Rect((width - button_width) // 2, height // 2 + 60, button_width, button_height)
    back_rect = pygame.Rect((width - button_width) // 2, height // 2 + 150, button_width, button_height)
    
    # Check hover
    easy_hover = easy_rect.collidepoint(mouse_pos)
    medium_hover = medium_rect.collidepoint(mouse_pos)
    hard_hover = hard_rect.collidepoint(mouse_pos)
    back_hover = back_rect.collidepoint(mouse_pos)
    
    draw_button(surface, easy_rect, "EASY", button_font, (60, 180, 60), (80, 220, 80), easy_hover)
    draw_button(surface, medium_rect, "MEDIUM", button_font, (180, 140, 60), (220, 180, 80), medium_hover)
    draw_button(surface, hard_rect, "HARD", button_font, (180, 60, 60), (220, 80, 80), hard_hover)
    draw_button(surface, back_rect, "Back", button_font, (100, 100, 100), (130, 130, 130), back_hover)
    
    return easy_rect, medium_rect, hard_rect, back_rect

def draw_online_connect_menu(surface, width, height, mouse_pos, server_input, error_msg=""):
    """Draw the online connection screen"""
    # Gradient background
    bg_rect = pygame.Rect(0, 0, width, height)
    draw_gradient_rect(surface, bg_rect, (20, 20, 40), (40, 20, 80), vertical=True)
    
    # Title
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    title_text = title_font.render("Connect to Server", True, (255, 105, 180))
    title_rect = title_text.get_rect(center=(width // 2, height // 5))
    surface.blit(title_text, title_rect)
    
    # Server input field
    input_font = pygame.font.SysFont("Arial", 24)
    input_width = 400
    input_height = 50
    input_rect = pygame.Rect((width - input_width) // 2, height // 2 - 80, input_width, input_height)
    
    pygame.draw.rect(surface, (60, 60, 80), input_rect)
    pygame.draw.rect(surface, (255, 105, 180), input_rect, 2)
    
    # Label
    label_text = input_font.render("Server Address:", True, (200, 200, 200))
    label_rect = label_text.get_rect(center=(width // 2, height // 2 - 120))
    surface.blit(label_text, label_rect)
    
    # Input text
    text_surface = input_font.render(server_input, True, (255, 255, 255))
    text_rect = text_surface.get_rect(midleft=(input_rect.left + 10, input_rect.centery))
    surface.blit(text_surface, text_rect)
    
    # Hint text
    hint_font = pygame.font.SysFont("Arial", 18)
    hint_text = hint_font.render("(e.g., localhost:5555 or 192.168.1.100:5555)", True, (150, 150, 150))
    hint_rect = hint_text.get_rect(center=(width // 2, height // 2 - 30))
    surface.blit(hint_text, hint_rect)
    
    # Error message
    if error_msg:
        error_font = pygame.font.SysFont("Arial", 20)
        error_text = error_font.render(error_msg, True, (255, 100, 100))
        error_rect = error_text.get_rect(center=(width // 2, height // 2 + 20))
        surface.blit(error_text, error_rect)
    
    # Buttons
    button_font = pygame.font.SysFont("Arial", 32, bold=True)
    button_width = 200
    button_height = 60
    
    connect_rect = pygame.Rect((width - button_width) // 2 - 120, height // 2 + 70, button_width, button_height)
    back_rect = pygame.Rect((width - button_width) // 2 + 120, height // 2 + 70, button_width, button_height)
    
    connect_hover = connect_rect.collidepoint(mouse_pos)
    back_hover = back_rect.collidepoint(mouse_pos)
    
    draw_button(surface, connect_rect, "CONNECT", button_font, (60, 180, 120), (80, 220, 150), connect_hover)
    draw_button(surface, back_rect, "BACK", button_font, (100, 100, 100), (130, 130, 130), back_hover)
    
    return input_rect, connect_rect, back_rect

def draw_online_waiting_menu(surface, width, height):
    """Draw the waiting for opponent screen"""
    # Gradient background with animation
    bg_rect = pygame.Rect(0, 0, width, height)
    draw_gradient_rect(surface, bg_rect, (20, 20, 40), (40, 20, 80), vertical=True)
    
    # Animated circles
    import time
    t = time.time()
    for i in range(3):
        angle = t * 2 + i * (2 * 3.14159 / 3)
        x = int(width // 2 + 100 * math.cos(angle))
        y = int(height // 2 + 100 * math.sin(angle))
        radius = int(20 + 10 * math.sin(t * 3 + i))
        pygame.draw.circle(surface, (255, 105, 180), (x, y), radius)
    
    # Title
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    title_text = title_font.render("Waiting for Opponent", True, (255, 105, 180))
    title_rect = title_text.get_rect(center=(width // 2, height // 3))
    surface.blit(title_text, title_rect)
    
    # Subtitle with dots animation
    dots = "." * (int(t * 2) % 4)
    subtitle_font = pygame.font.SysFont("Arial", 30)
    subtitle_text = subtitle_font.render(f"Searching{dots}", True, (200, 200, 200))
    subtitle_rect = subtitle_text.get_rect(center=(width // 2, height // 2 + 150))
    surface.blit(subtitle_text, subtitle_rect)
    
    # Cancel button
    button_font = pygame.font.SysFont("Arial", 32, bold=True)
    button_width = 200
    button_height = 60
    cancel_rect = pygame.Rect((width - button_width) // 2, height // 2 + 220, button_width, button_height)
    
    mouse_pos = pygame.mouse.get_pos()
    cancel_hover = cancel_rect.collidepoint(mouse_pos)
    
    draw_button(surface, cancel_rect, "CANCEL", button_font, (180, 60, 60), (220, 80, 80), cancel_hover)
    
    return cancel_rect

# Online connection variables
server_input = "localhost:5555"
connection_error = ""

# Pick initial random avatars for players
pick_random_avatars()

running = True
clock = pygame.time.Clock()

while running:
    width, height = screen.get_size()
    mouse_pos = pygame.mouse.get_pos()
    
    # Update menu animation
    menu_animation_offset += 2 * menu_animation_direction
    if menu_animation_offset >= 360 or menu_animation_offset <= 0:
        menu_animation_direction *= -1
    
    # Main menu state
    if current_state == STATE_MAIN_MENU:
        play_rect, exit_rect = draw_main_menu(screen, width, height, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    click_sound.play()
                    current_state = STATE_PLAY_MODE
                elif exit_rect.collidepoint(event.pos):
                    click_sound.play()
                    running = False
    
    # Login state
    elif current_state == STATE_LOGIN:
        google_rect, facebook_rect, google_play_rect, back_rect = draw_login_menu(screen, width, height, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if google_rect.collidepoint(event.pos):
                    # Go to user input screen for Google
                    selected_provider = 'google'
                    user_email_input = ""
                    user_name_input = ""
                    active_input_field = "email"
                    current_state = STATE_USER_INPUT
                elif facebook_rect.collidepoint(event.pos):
                    # Go to user input screen for Facebook
                    selected_provider = 'facebook'
                    user_email_input = ""
                    user_name_input = ""
                    active_input_field = "email"
                    current_state = STATE_USER_INPUT
                elif google_play_rect.collidepoint(event.pos):
                    # Go to user input screen for Google Play
                    selected_provider = 'google_play'
                    user_email_input = ""
                    user_name_input = ""
                    active_input_field = "email"
                    current_state = STATE_USER_INPUT
                elif back_rect.collidepoint(event.pos):
                    current_state = STATE_MAIN_MENU
    
    # User input state - collect email and username
    elif current_state == STATE_USER_INPUT:
        email_rect, name_rect, continue_rect, back_rect, can_continue = draw_user_input_screen(
            screen, width, height, mouse_pos, selected_provider, user_email_input, user_name_input, active_input_field, user_input_error
        )
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check which input field was clicked
                if email_rect.collidepoint(event.pos):
                    active_input_field = "email"
                    user_input_error = ""  # Clear error when clicking field
                elif name_rect.collidepoint(event.pos):
                    active_input_field = "username"
                    user_input_error = ""  # Clear error when clicking field
                elif continue_rect.collidepoint(event.pos) and can_continue:
                    # Validate email format
                    is_valid, error_msg = validate_email_format(user_email_input, selected_provider)
                    if is_valid:
                        # Login/register the user
                        user_data = user_manager.login_user(user_email_input.strip(), user_name_input.strip(), selected_provider)
                        current_state = STATE_USER_PROFILE
                        user_input_error = ""
                    else:
                        # Show validation error
                        user_input_error = error_msg
                elif back_rect.collidepoint(event.pos):
                    current_state = STATE_LOGIN
                    user_input_error = ""
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if active_input_field == "email":
                        user_email_input = user_email_input[:-1]
                    else:
                        user_name_input = user_name_input[:-1]
                    user_input_error = ""  # Clear error when typing
                elif event.key == pygame.K_TAB:
                    # Switch between fields
                    active_input_field = "username" if active_input_field == "email" else "email"
                elif event.key == pygame.K_RETURN and can_continue:
                    # Same as clicking continue
                    is_valid, error_msg = validate_email_format(user_email_input, selected_provider)
                    if is_valid:
                        user_data = user_manager.login_user(user_email_input.strip(), user_name_input.strip(), selected_provider)
                        current_state = STATE_USER_PROFILE
                        user_input_error = ""
                    else:
                        user_input_error = error_msg
                elif event.unicode:
                    # Add character to active field
                    if active_input_field == "email" and len(user_email_input) < 40:
                        user_email_input += event.unicode
                        user_input_error = ""  # Clear error when typing
                    elif active_input_field == "username" and len(user_name_input) < 20:
                        user_name_input += event.unicode
                        user_input_error = ""  # Clear error when typing
    
    # User profile state - show stats and options
    elif current_state == STATE_USER_PROFILE:
        user_data = user_manager.get_current_user()
        if user_data:
            play_rect, achievements_rect, friends_rect, logout_rect = draw_user_profile_screen(screen, width, height, mouse_pos, user_data)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_rect.collidepoint(event.pos):
                        current_state = STATE_PLAY_MODE
                    elif achievements_rect.collidepoint(event.pos):
                        # Load achievements
                        all_achievements = user_manager.get_all_achievements()
                        user_achievements = user_manager.get_user_achievements()
                        current_state = STATE_ACHIEVEMENTS
                    elif friends_rect.collidepoint(event.pos):
                        # Load friends data
                        friends_list = user_manager.get_friends_list()
                        pending_requests = user_manager.get_friend_requests()
                        current_state = STATE_FRIENDS
                    elif logout_rect.collidepoint(event.pos):
                        user_manager.logout_user()
                        current_state = STATE_MAIN_MENU
        else:
            # No user data, return to main menu
            current_state = STATE_MAIN_MENU
    
    # Achievements screen state
    elif current_state == STATE_ACHIEVEMENTS:
        back_rect = draw_achievements_screen(screen, width, height, mouse_pos, all_achievements, user_achievements)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    current_state = STATE_USER_PROFILE
    
    # Friends screen state
    elif current_state == STATE_FRIENDS:
        add_friend_rect, back_rect, pending_requests = draw_friends_screen(screen, width, height, mouse_pos, friends_list, pending_requests)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if add_friend_rect.collidepoint(event.pos):
                    friend_email_input = ""
                    add_friend_message = ""
                    current_state = STATE_ADD_FRIEND
                elif back_rect.collidepoint(event.pos):
                    current_state = STATE_USER_PROFILE
                else:
                    # Check if clicked on an accept button for pending requests
                    item_y = 130 + 45  # Starting position of requests
                    for i, request in enumerate(pending_requests[:3]):
                        accept_btn = pygame.Rect(width - 220, item_y - 5, 80, 30)
                        if accept_btn.collidepoint(event.pos):
                            # Accept friend request
                            result = user_manager.accept_friend(request['email'])
                            if result:
                                # Refresh lists
                                friends_list = user_manager.get_friends_list()
                                pending_requests = user_manager.get_friend_requests()
                            break
                        item_y += 40
    
    # Add friend screen state
    elif current_state == STATE_ADD_FRIEND:
        input_rect, send_rect, back_rect = draw_add_friend_screen(screen, width, height, mouse_pos, friend_email_input, add_friend_message)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if send_rect.collidepoint(event.pos):
                    if friend_email_input.strip():
                        # Send friend request
                        result = user_manager.add_friend(friend_email_input.strip())
                        if result:
                            add_friend_message = "Friend request sent successfully!"
                            friend_email_input = ""
                        else:
                            add_friend_message = "Failed to send request. Check email."
                    else:
                        add_friend_message = "Please enter an email address"
                elif back_rect.collidepoint(event.pos):
                    current_state = STATE_FRIENDS
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    friend_email_input = friend_email_input[:-1]
                    add_friend_message = ""
                elif event.key == pygame.K_RETURN:
                    if friend_email_input.strip():
                        result = user_manager.add_friend(friend_email_input.strip())
                        if result:
                            add_friend_message = "Friend request sent successfully!"
                            friend_email_input = ""
                        else:
                            add_friend_message = "Failed to send request. Check email."
                elif event.unicode and len(friend_email_input) < 50:
                    friend_email_input += event.unicode
                    add_friend_message = ""
    
    # Play mode selection state
    elif current_state == STATE_PLAY_MODE:
        ai_rect, friend_rect, back_rect = draw_play_mode_menu(screen, width, height, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ai_rect.collidepoint(event.pos):
                    click_sound.play()
                    current_state = STATE_DIFFICULTY
                elif friend_rect.collidepoint(event.pos):
                    click_sound.play()
                    # Start game with AI disabled
                    pick_random_avatars()  # Pick new avatars for new game
                    AI_ENABLED = False
                    online_mode = False
                    board = Board()
                    game = Game(board)
                    last_move = None  # Reset last move
                    current_state = STATE_PLAYING
                    game_over_sound_played = False
                    game_saved_to_history = False
                    game_start_time = time.time()
                elif back_rect.collidepoint(event.pos):
                    click_sound.play()
                    current_state = STATE_MAIN_MENU
    
    # Online connection state
    elif current_state == STATE_ONLINE_CONNECT:
        input_rect, connect_rect, back_rect = draw_online_connect_menu(screen, width, height, mouse_pos, server_input, connection_error)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if connect_rect.collidepoint(event.pos):
                    # Try to connect
                    try:
                        parts = server_input.split(':')
                        host = parts[0] if parts[0] else 'localhost'
                        port = int(parts[1]) if len(parts) > 1 else 5555
                        
                        if network_client.connect(host, port):
                            connection_error = ""
                            current_state = STATE_ONLINE_WAITING
                            waiting_for_opponent = True
                        else:
                            connection_error = "Failed to connect to server"
                    except Exception as e:
                        connection_error = f"Connection error: {str(e)}"
                elif back_rect.collidepoint(event.pos):
                    current_state = STATE_PLAY_MODE
                    connection_error = ""
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    server_input = server_input[:-1]
                elif event.key == pygame.K_RETURN:
                    # Same as clicking connect
                    pass
                elif event.unicode and len(server_input) < 30:
                    # Allow typing
                    server_input += event.unicode
    
    # Online waiting state
    elif current_state == STATE_ONLINE_WAITING:
        cancel_rect = draw_online_waiting_menu(screen, width, height)
        
        # Check for messages from server
        message = network_client.get_message()
        if message:
            if message['type'] == 'game_start':
                pick_random_avatars()  # Pick new avatars for online game
                online_player_color = message['color']
                online_mode = True
                AI_ENABLED = False
                board = Board()
                game = Game(board)
                last_move = None  # Reset last move
                current_state = STATE_PLAYING
                game_over_sound_played = False
                game_saved_to_history = False
                game_start_time = time.time()
                waiting_for_opponent = False
                opponent_disconnected = False
                print(f"Game started! You are playing as {online_player_color}")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                network_client.disconnect()
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if cancel_rect.collidepoint(event.pos):
                    network_client.disconnect()
                    current_state = STATE_PLAY_MODE
                    waiting_for_opponent = False
    
    # Difficulty selection state
    elif current_state == STATE_DIFFICULTY:
        easy_rect, medium_rect, hard_rect, back_rect = draw_difficulty_menu(screen, width, height, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if easy_rect.collidepoint(event.pos):
                    click_sound.play()
                    pick_random_avatars()  # Pick new avatars
                    AI_ENABLED = True
                    AI_DIFFICULTY = 'easy'
                    difficulty_name = 'Easy'
                    board = Board()
                    game = Game(board)
                    last_move = None  # Reset last move
                    current_state = STATE_PLAYING
                    game_over_sound_played = False
                    game_saved_to_history = False
                    game_start_time = time.time()
                elif medium_rect.collidepoint(event.pos):
                    click_sound.play()
                    pick_random_avatars()  # Pick new avatars
                    AI_ENABLED = True
                    AI_DIFFICULTY = 'medium'
                    difficulty_name = 'Medium'
                    board = Board()
                    game = Game(board)
                    last_move = None  # Reset last move
                    current_state = STATE_PLAYING
                    game_over_sound_played = False
                    game_saved_to_history = False
                    game_start_time = time.time()
                elif hard_rect.collidepoint(event.pos):
                    click_sound.play()
                    pick_random_avatars()  # Pick new avatars
                    AI_ENABLED = True
                    AI_DIFFICULTY = 'hard'
                    difficulty_name = 'Hard'
                    board = Board()
                    game = Game(board)
                    last_move = None  # Reset last move
                    current_state = STATE_PLAYING
                    game_over_sound_played = False
                    game_saved_to_history = False
                    game_start_time = time.time()
                elif back_rect.collidepoint(event.pos):
                    click_sound.play()
                    current_state = STATE_PLAY_MODE
    
    # Playing state
    elif current_state == STATE_PLAYING:
        # Calculate dynamic tile size based on window size
        tile_size = min(width, height) // BOARD_SIZE
        board_size_pixels = tile_size * BOARD_SIZE
        
        # Calculate board position (centered)
        board_x = (width - board_size_pixels) // 2
        board_y = (height - board_size_pixels) // 2
        
        # Create fonts
        font = pygame.font.SysFont(None, max(24, tile_size // 2))
        button_font = pygame.font.SysFont(None, max(20, tile_size // 3))
        
        # Fill screen with interface background color
        screen.fill(interface_bg_color)
        
        # Draw the board area with grid background
        board_rect = pygame.Rect(board_x, board_y, board_size_pixels, board_size_pixels)
        pygame.draw.rect(screen, grid_bg_color, board_rect)

        # Update animations
        updated_animations = []
        for anim_row, anim_col, start_color, end_color, progress in animating_discs:
            new_progress = min(1.0, progress + ANIMATION_SPEED)
            if new_progress < 1.0:
                updated_animations.append((anim_row, anim_col, start_color, end_color, new_progress))
        animating_discs[:] = updated_animations

        # Draw board grid and discs
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = board_x + col * tile_size
                y = board_y + row * tile_size
                pygame.draw.rect(screen, BLACK, (x, y, tile_size, tile_size), 1)
                disc = board.grid[row][col]
                
                # Check if this disc is animating
                animating = False
                anim_progress = 0
                start_color = None
                end_color = None
                for anim_row, anim_col, s_color, e_color, progress in animating_discs:
                    if anim_row == row and anim_col == col:
                        animating = True
                        anim_progress = progress
                        start_color = s_color
                        end_color = e_color
                        break
                
                if disc:
                    if animating:
                        # Draw flipping animation
                        # Scale width based on progress (0 -> 1 -> 0 -> 1 for flip effect)
                        if anim_progress < 0.5:
                            # First half: shrink from start color
                            scale = 1.0 - (anim_progress * 2)
                            color = start_color
                        else:
                            # Second half: grow to end color
                            scale = (anim_progress - 0.5) * 2
                            color = end_color
                        
                        # Draw ellipse to simulate 3D flip
                        radius = tile_size // 2 - 5
                        width_scale = max(0.1, scale)  # Minimum width to avoid invisible disc
                        
                        # Draw disc with horizontal scaling
                        center_x = x + tile_size // 2
                        center_y = y + tile_size // 2
                        
                        # Draw ellipse (horizontally scaled circle)
                        ellipse_rect = pygame.Rect(
                            center_x - int(radius * width_scale),
                            center_y - radius,
                            int(radius * 2 * width_scale),
                            radius * 2
                        )
                        pygame.draw.ellipse(screen, color, ellipse_rect)
                    else:
                        # Draw normal disc
                        color = BLACK if disc == 'B' else WHITE
                        pygame.draw.circle(screen, color, (x + tile_size // 2, y + tile_size // 2), tile_size // 2 - 5)

        # Highlight the last move with a glowing border
        if last_move:
            lm_row, lm_col = last_move
            lm_x = board_x + lm_col * tile_size
            lm_y = board_y + lm_row * tile_size
            # Animated glow effect
            glow_pulse = int(20 * abs(math.sin(pygame.time.get_ticks() / 300)))
            glow_color = (255, 255, 0)  # Yellow glow
            pygame.draw.rect(screen, glow_color, (lm_x + 2, lm_y + 2, tile_size - 4, tile_size - 4), 4 + glow_pulse // 5)

        # Highlight valid moves
        valid_moves = board.get_valid_moves(game.current_player)
        for row, col in valid_moves:
            cx = board_x + col * tile_size + tile_size // 2
            cy = board_y + row * tile_size + tile_size // 2
            pygame.draw.circle(screen, (200, 200, 200), (cx, cy), max(4, tile_size // 12))

        # Draw large turn indicator overlay for clarity
        if not game.check_game_over():
            turn_font = pygame.font.Font(None, 48)
            if AI_ENABLED:
                if game.current_player == HUMAN_COLOR:
                    turn_text = turn_font.render("YOUR TURN", True, (0, 255, 100))
                    turn_bg_color = (0, 100, 0)
                else:
                    if ai_thinking:
                        turn_text = turn_font.render("AI THINKING...", True, (255, 200, 100))
                    else:
                        turn_text = turn_font.render("AI'S TURN", True, (255, 100, 100))
                    turn_bg_color = (100, 0, 0)
            else:
                # Friend mode - just show whose turn
                if game.current_player == 'B':
                    turn_text = turn_font.render("BLACK'S TURN", True, (200, 200, 200))
                    turn_bg_color = (30, 30, 30)
                else:
                    turn_text = turn_font.render("WHITE'S TURN", True, (50, 50, 50))
                    turn_bg_color = (200, 200, 200)
            
            # Position at top center of the board
            turn_rect = turn_text.get_rect(center=(width // 2, board_y - 40))
            
            # Draw semi-transparent background
            bg_surface = pygame.Surface((turn_rect.width + 40, turn_rect.height + 20))
            bg_surface.set_alpha(220)
            bg_surface.fill(turn_bg_color)
            bg_rect = bg_surface.get_rect(center=turn_rect.center)
            screen.blit(bg_surface, bg_rect)
            
            # Draw border
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 3)
            
            # Draw text
            screen.blit(turn_text, turn_rect)

        # Get current score
        score = game.get_score()
        
        # Draw player panels on left and right sides
        panel_width = min(250, (width - board_size_pixels) // 2 - 40)
        panel_height = min(400, board_size_pixels)
        panel_y = board_y + (board_size_pixels - panel_height) // 2
        
        # Left panel (Black player)
        left_panel_x = max(20, (board_x - panel_width) // 2)
        
        # Right panel (White player)
        right_panel_x = board_x + board_size_pixels + (width - board_x - board_size_pixels - panel_width) // 2
        
        # Determine player names and status
        if online_mode:
            # Online mode - show who you are
            if online_player_color == 'B':
                black_name = "You"
                white_name = "Opponent"
                black_is_you = True
                white_is_you = False
            else:
                black_name = "Opponent"
                white_name = "You"
                black_is_you = False
                white_is_you = True
        elif AI_ENABLED:
            # VS AI mode
            if HUMAN_COLOR == 'B':
                black_name = "You"
                white_name = "AI"
                black_is_you = True
                white_is_you = False
            else:
                black_name = "AI"
                white_name = "You"
                black_is_you = False
                white_is_you = True
        else:
            # VS Friend mode
            black_name = "Player 1"
            white_name = "Player 2"
            black_is_you = False
            white_is_you = False
        
        # Check if user is logged in, use their username
        current_user = user_manager.get_current_user()
        if current_user:
            user_name = current_user['username']
            if online_mode:
                if online_player_color == 'B':
                    black_name = user_name
                else:
                    white_name = user_name
            elif AI_ENABLED:
                if HUMAN_COLOR == 'B':
                    black_name = user_name
                else:
                    white_name = user_name
        
        # Draw player panels
        draw_player_panel(screen, left_panel_x, panel_y, panel_width, panel_height,
                         black_name, 'B', score['B'], game.current_player == 'B', black_is_you, player1_avatar)
        
        draw_player_panel(screen, right_panel_x, panel_y, panel_width, panel_height,
                         white_name, 'W', score['W'], game.current_player == 'W', white_is_you, player2_avatar)

        # Buttons (top-right corner)
        button_width = max(80, width // 8)
        button_height = max(30, height // 20)
        button_spacing = 10
        start_x = width - button_width - 10
        start_y = 10

        # Settings button (always visible)
        settings_rect = pygame.Rect(start_x, start_y, button_width, button_height)
        settings_color = (255, 180, 0) if settings_open else (150, 150, 150)
        pygame.draw.rect(screen, settings_color, settings_rect)
        pygame.draw.rect(screen, WHITE, settings_rect, 2)
        settings_text = button_font.render("Settings", True, WHITE)
        text_rect = settings_text.get_rect(center=settings_rect.center)
        screen.blit(settings_text, text_rect)

        # Settings panel (only show when settings_open is True)
        if settings_open:
            # Calculate panel dimensions
            panel_width = button_width + 20
            panel_height = 7 * (button_height + button_spacing) + 30
            panel_x = start_x - 10
            panel_y = start_y + button_height + button_spacing
            
            # Draw semi-transparent panel background
            panel_surface = pygame.Surface((panel_width, panel_height))
            panel_surface.set_alpha(230)
            panel_surface.fill((30, 30, 40))
            screen.blit(panel_surface, (panel_x, panel_y))
            pygame.draw.rect(screen, (255, 105, 180), (panel_x, panel_y, panel_width, panel_height), 2)
            
            # Adjust button positions for panel
            panel_button_x = start_x
            panel_start_y = panel_y + 15
            
            restart_rect = pygame.Rect(panel_button_x, panel_start_y, button_width, button_height)
            menu_rect = pygame.Rect(panel_button_x, panel_start_y + button_height + button_spacing, button_width, button_height)
            toggle_rect = pygame.Rect(panel_button_x, panel_start_y + 2 * (button_height + button_spacing), button_width, button_height)
            
            diff_e_rect = pygame.Rect(panel_button_x, panel_start_y + 3 * (button_height + button_spacing), button_width // 3 - 5, button_height)
            diff_m_rect = pygame.Rect(panel_button_x + button_width // 3, panel_start_y + 3 * (button_height + button_spacing), button_width // 3 - 5, button_height)
            diff_h_rect = pygame.Rect(panel_button_x + 2 * button_width // 3, panel_start_y + 3 * (button_height + button_spacing), button_width // 3 - 5, button_height)
            
            play_black_rect = pygame.Rect(panel_button_x, panel_start_y + 4 * (button_height + button_spacing), button_width // 2 - 5, button_height)
            play_white_rect = pygame.Rect(panel_button_x + button_width // 2, panel_start_y + 4 * (button_height + button_spacing), button_width // 2 - 5, button_height)
            
            grid_color_rect = pygame.Rect(panel_button_x, panel_start_y + 5 * (button_height + button_spacing), button_width, button_height)
            interface_color_rect = pygame.Rect(panel_button_x, panel_start_y + 6 * (button_height + button_spacing), button_width, button_height)

            # Draw buttons
            pygame.draw.rect(screen, (100, 100, 250), restart_rect)
            pygame.draw.rect(screen, WHITE, restart_rect, 2)
            restart_text = button_font.render("Restart", True, WHITE)
            text_rect = restart_text.get_rect(center=restart_rect.center)
            screen.blit(restart_text, text_rect)
            
            # Menu button
            pygame.draw.rect(screen, (150, 100, 200), menu_rect)
            pygame.draw.rect(screen, WHITE, menu_rect, 2)
            menu_text = button_font.render("Menu", True, WHITE)
            text_rect = menu_text.get_rect(center=menu_rect.center)
            screen.blit(menu_text, text_rect)

            # AI toggle button
            ai_toggle_color = (50, 200, 50) if AI_ENABLED else (200, 50, 50)
            pygame.draw.rect(screen, ai_toggle_color, toggle_rect)
            pygame.draw.rect(screen, WHITE, toggle_rect, 2)
            toggle_text = button_font.render("AI: ON" if AI_ENABLED else "AI: OFF", True, WHITE)
            text_rect = toggle_text.get_rect(center=toggle_rect.center)
            screen.blit(toggle_text, text_rect)

            # Difficulty buttons
            for rect, diff, label in [(diff_e_rect, 'easy', 'E'), (diff_m_rect, 'medium', 'M'), (diff_h_rect, 'hard', 'H')]:
                color = (100, 250, 100) if AI_DIFFICULTY == diff else (100, 100, 100)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, WHITE, rect, 2)
                text = button_font.render(label, True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

            # Player color choice buttons
            pygame.draw.rect(screen, BLACK, play_black_rect)
            pygame.draw.rect(screen, WHITE, play_black_rect, 2)
            black_text = button_font.render("B", True, WHITE)
            text_rect = black_text.get_rect(center=play_black_rect.center)
            screen.blit(black_text, text_rect)

            pygame.draw.rect(screen, WHITE, play_white_rect)
            pygame.draw.rect(screen, BLACK, play_white_rect, 2)
            white_text = button_font.render("W", True, BLACK)
            text_rect = white_text.get_rect(center=play_white_rect.center)
            screen.blit(white_text, text_rect)

            # Highlight selected human color
            if HUMAN_COLOR == 'B':
                pygame.draw.rect(screen, (0, 200, 0), play_black_rect, 3)
            else:
                pygame.draw.rect(screen, (0, 200, 0), play_white_rect, 3)

            # Draw grid color selector button
            pygame.draw.rect(screen, grid_bg_color, grid_color_rect)
            pygame.draw.rect(screen, WHITE, grid_color_rect, 2)
            grid_text = button_font.render(f"Grid: {current_grid_color}", True, WHITE)
            text_rect = grid_text.get_rect(center=grid_color_rect.center)
            screen.blit(grid_text, text_rect)
            
            # Draw interface color selector button
            pygame.draw.rect(screen, interface_bg_color, interface_color_rect)
            pygame.draw.rect(screen, WHITE, interface_color_rect, 2)
            interface_text = button_font.render(f"UI: {current_interface_color}", True, WHITE)
            text_rect = interface_text.get_rect(center=interface_color_rect.center)
            screen.blit(interface_text, text_rect)
        else:
            # When settings closed, set dummy rects to avoid errors
            restart_rect = menu_rect = toggle_rect = pygame.Rect(0, 0, 0, 0)
            diff_e_rect = diff_m_rect = diff_h_rect = pygame.Rect(0, 0, 0, 0)
            play_black_rect = play_white_rect = pygame.Rect(0, 0, 0, 0)
            grid_color_rect = interface_color_rect = pygame.Rect(0, 0, 0, 0)

        # Draw AI thinking overlay if active
        if ai_thinking:
            thinking_text = button_font.render("AI thinking...", True, (255, 105, 180))
            thinking_rect = thinking_text.get_rect(center=(width // 2, 20))
            bg = pygame.Surface((thinking_rect.width + 10, thinking_rect.height + 6))
            bg.set_alpha(180)
            bg.fill((0, 0, 0))
            screen.blit(bg, (thinking_rect.x - 5, thinking_rect.y - 3))
            screen.blit(thinking_text, thinking_rect)

        # Check if game is over and display winner
        if game.check_game_over():
            winner, counts = game.winner()
            
            # Save game to user history (only once)
            if not game_saved_to_history and user_manager.get_current_user():
                # Calculate game duration
                game_duration = int(time.time() - game_start_time) if game_start_time else 0
                
                # Determine game mode
                if online_mode:
                    game_mode = 'online'
                elif AI_ENABLED:
                    game_mode = 'vs_ai'
                else:
                    game_mode = 'vs_friend'
                
                # Determine result from player's perspective
                player_color = HUMAN_COLOR if AI_ENABLED or online_mode else 'B'  # In friend mode, track for Black
                if winner is None:
                    result = 'draw'
                elif winner == player_color:
                    result = 'win'
                else:
                    result = 'loss'
                
                # Create game data
                game_data = {
                    'game_mode': game_mode,
                    'result': result,
                    'player_score': counts.get(player_color, 0),
                    'opponent_score': counts.get('W' if player_color == 'B' else 'B', 0),
                    'difficulty': difficulty_name if AI_ENABLED else 'N/A',
                    'duration': game_duration
                }
                
                # Save to user history
                user_manager.add_game_to_history(game_data)
                game_saved_to_history = True
                
                # Check for newly unlocked achievements
                newly_unlocked = user_manager.check_achievements()
                if newly_unlocked:
                    newly_unlocked_achievements = newly_unlocked
                    achievement_notification_time = time.time()
            
            # Play game over sound once
            if not game_over_sound_played:
                if winner is None:
                    # Tie - neutral sound
                    click_sound.play()
                elif winner == HUMAN_COLOR:
                    # Player wins
                    win_sound.play()
                else:
                    # Player loses or AI wins
                    error_sound.play()
                game_over_sound_played = True
            
            game_over_font = pygame.font.SysFont(None, 72)
            result_font = pygame.font.SysFont(None, 48)
            
            # Draw semi-transparent overlay
            overlay = pygame.Surface((width, height))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Game Over text
            game_over_text = game_over_font.render("GAME OVER", True, (255, 20, 147))
            game_over_rect = game_over_text.get_rect(center=(width // 2, height // 3))
            screen.blit(game_over_text, game_over_rect)
            
            # Winner message
            if winner is None:
                result_text = result_font.render("It's a TIE!", True, (255, 182, 193))
            else:
                winner_name = "Black" if winner == 'B' else "White"
                
                if AI_ENABLED:
                    if winner == HUMAN_COLOR:
                        result_text = result_font.render(f"YOU WIN! ({winner_name})", True, (255, 105, 180))
                    else:
                        result_text = result_font.render(f"YOU LOSE! ({winner_name} wins)", True, (255, 182, 193))
                else:
                    result_text = result_font.render(f"{winner_name} WINS!", True, (255, 105, 180))
            
            result_rect = result_text.get_rect(center=(width // 2, height // 2))
            screen.blit(result_text, result_rect)
            
            # Final score
            score_final = result_font.render(f"Black: {counts['B']}  White: {counts['W']}", True, (255, 192, 203))
            score_rect = score_final.get_rect(center=(width // 2, height // 2 + 60))
            screen.blit(score_final, score_rect)
            
            # Game over buttons
            game_over_button_font = pygame.font.SysFont("Arial", 36, bold=True)
            button_width = 200
            button_height = 60
            button_spacing = 20
            button_y = height // 2 + 140
            
            game_over_restart_rect = pygame.Rect(width // 2 - button_width - button_spacing // 2, button_y, button_width, button_height)
            game_over_menu_rect = pygame.Rect(width // 2 + button_spacing // 2, button_y, button_width, button_height)
            
            # Check hover for game over buttons
            game_over_restart_hover = game_over_restart_rect.collidepoint(mouse_pos)
            game_over_menu_hover = game_over_menu_rect.collidepoint(mouse_pos)
            
            # Draw restart button
            restart_color = (60, 180, 120) if not game_over_restart_hover else (80, 220, 150)
            pygame.draw.rect(screen, restart_color, game_over_restart_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), game_over_restart_rect, 3, border_radius=10)
            restart_text = game_over_button_font.render("RESTART", True, (255, 255, 255))
            restart_text_rect = restart_text.get_rect(center=game_over_restart_rect.center)
            screen.blit(restart_text, restart_text_rect)
            
            # Draw menu button
            menu_color = (180, 60, 120) if not game_over_menu_hover else (220, 80, 150)
            pygame.draw.rect(screen, menu_color, game_over_menu_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), game_over_menu_rect, 3, border_radius=10)
            menu_text = game_over_button_font.render("MENU", True, (255, 255, 255))
            menu_text_rect = menu_text.get_rect(center=game_over_menu_rect.center)
            screen.blit(menu_text, menu_text_rect)
        else:
            # If game is not over, set these to empty rects
            game_over_restart_rect = pygame.Rect(0, 0, 0, 0)
            game_over_menu_rect = pygame.Rect(0, 0, 0, 0)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                if not fullscreen:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                # Check game over buttons first (highest priority)
                if game.check_game_over():
                    if game_over_restart_rect.collidepoint((mx, my)):
                        click_sound.play()
                        pick_random_avatars()  # Pick new avatars on restart
                        board = Board()
                        game = Game(board)
                        last_move = None  # Reset last move
                        game_over_sound_played = False
                        game_saved_to_history = False
                        game_start_time = time.time()
                        settings_open = False
                        continue
                    elif game_over_menu_rect.collidepoint((mx, my)):
                        click_sound.play()
                        # Disconnect if in online mode
                        if online_mode:
                            network_client.disconnect()
                            online_mode = False
                        current_state = STATE_MAIN_MENU
                        settings_open = False
                        continue
                
                # Check settings button
                if settings_rect.collidepoint((mx, my)):
                    click_sound.play()
                    settings_open = not settings_open
                elif settings_open:
                    # Only process other buttons if settings panel is open
                    if restart_rect.collidepoint((mx, my)):
                        click_sound.play()
                        pick_random_avatars()  # Pick new avatars on restart
                        board = Board()
                        game = Game(board)
                        last_move = None  # Reset last move
                        game_over_sound_played = False
                        game_saved_to_history = False
                        game_start_time = time.time()
                    elif menu_rect.collidepoint((mx, my)):
                        click_sound.play()
                        current_state = STATE_MAIN_MENU
                        settings_open = False  # Close settings when going to menu
                    elif toggle_rect.collidepoint((mx, my)):
                        click_sound.play()
                        AI_ENABLED = not AI_ENABLED
                    elif diff_e_rect.collidepoint((mx, my)):
                        click_sound.play()
                        AI_DIFFICULTY = 'easy'
                    elif diff_m_rect.collidepoint((mx, my)):
                        click_sound.play()
                        AI_DIFFICULTY = 'medium'
                    elif diff_h_rect.collidepoint((mx, my)):
                        click_sound.play()
                        AI_DIFFICULTY = 'hard'
                    elif play_black_rect.collidepoint((mx, my)):
                        click_sound.play()
                        pick_random_avatars()  # Pick new avatars
                        HUMAN_COLOR = 'B'
                        AI_COLOR = 'W'
                        board = Board()
                        game = Game(board)
                        last_move = None  # Reset last move
                        game_over_sound_played = False
                        game_saved_to_history = False
                        game_start_time = time.time()
                    elif play_white_rect.collidepoint((mx, my)):
                        pick_random_avatars()  # Pick new avatars
                        HUMAN_COLOR = 'W'
                        AI_COLOR = 'B'
                        board = Board()
                        game = Game(board)
                        last_move = None  # Reset last move
                        game_over_sound_played = False
                        game_saved_to_history = False
                        game_start_time = time.time()
                    elif grid_color_rect.collidepoint((mx, my)):
                        color_names = list(GRID_COLORS.keys())
                        current_index = color_names.index(current_grid_color)
                        next_index = (current_index + 1) % len(color_names)
                        current_grid_color = color_names[next_index]
                        grid_bg_color = GRID_COLORS[current_grid_color]
                        # Save settings when color changes
                        save_settings({"grid_color": current_grid_color, "interface_color": current_interface_color})
                    elif interface_color_rect.collidepoint((mx, my)):
                        color_names = list(INTERFACE_COLORS.keys())
                        current_index = color_names.index(current_interface_color)
                        next_index = (current_index + 1) % len(color_names)
                        current_interface_color = color_names[next_index]
                        interface_bg_color = INTERFACE_COLORS[current_interface_color]
                        # Save settings when color changes
                        save_settings({"grid_color": current_grid_color, "interface_color": current_interface_color})
                    else:
                        # Board click
                        row, col = (my - board_y) // tile_size, (mx - board_x) // tile_size
                        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and board.is_valid_move(row, col, game.current_player):
                            # Check if it's the player's turn in online mode
                            if online_mode and game.current_player != online_player_color:
                                continue  # Not your turn
                            
                            flipped = board.place_disc(row, col, game.current_player)
                            place_sound.play()  # Play placement sound
                            last_move = (row, col)  # Track last move for highlighting
                            # Add flipped discs to animation
                            opponent_color = WHITE if game.current_player == 'B' else BLACK
                            player_color = BLACK if game.current_player == 'B' else WHITE
                            for flip_row, flip_col in flipped:
                                animating_discs.append((flip_row, flip_col, opponent_color, player_color, 0.0))
                            # Play flip sound if discs were flipped
                            if flipped:
                                flip_sound.play()
                            
                            # Send move to opponent if online
                            if online_mode:
                                network_client.send({'type': 'move', 'row': row, 'col': col, 'player': game.current_player})
                            
                            game.switch_player()
                else:
                    # Settings closed, allow board clicks
                    row, col = (my - board_y) // tile_size, (mx - board_x) // tile_size
                    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and board.is_valid_move(row, col, game.current_player):
                        # Check if it's the player's turn in online mode
                        if online_mode and game.current_player != online_player_color:
                            continue  # Not your turn
                        
                        flipped = board.place_disc(row, col, game.current_player)
                        place_sound.play()  # Play placement sound
                        last_move = (row, col)  # Track last move for highlighting
                        # Add flipped discs to animation
                        opponent_color = WHITE if game.current_player == 'B' else BLACK
                        player_color = BLACK if game.current_player == 'B' else WHITE
                        for flip_row, flip_col in flipped:
                            animating_discs.append((flip_row, flip_col, opponent_color, player_color, 0.0))
                        # Play flip sound if discs were flipped
                        if flipped:
                            flip_sound.play()
                        
                        # Send move to opponent if online
                        if online_mode:
                            network_client.send({'type': 'move', 'row': row, 'col': col, 'player': game.current_player})
                        
                        game.switch_player()
                        
                        # Add smooth transition after player move
                        if AI_ENABLED:
                            # Show "YOUR MOVE" confirmation with fade effect
                            pygame.display.flip()
                            pygame.time.wait(800)  # Brief pause to see the move

        # Handle online opponent moves
        if online_mode and network_client.connected:
            message = network_client.get_message()
            if message:
                if message['type'] == 'move':
                    row, col = message['row'], message['col']
                    opponent_player = message['player']
                    if board.is_valid_move(row, col, opponent_player):
                        flipped = board.place_disc(row, col, opponent_player)
                        place_sound.play()  # Play placement sound
                        # Add flipped discs to animation
                        opponent_color = WHITE if opponent_player == 'B' else BLACK
                        player_color = BLACK if opponent_player == 'B' else WHITE
                        for flip_row, flip_col in flipped:
                            animating_discs.append((flip_row, flip_col, opponent_color, player_color, 0.0))
                        # Play flip sound if discs were flipped
                        if flipped:
                            flip_sound.play()
                        game.switch_player()
                elif message['type'] == 'opponent_disconnected':
                    opponent_disconnected = True
        
        # Show disconnection message
        if opponent_disconnected:
            disconnect_font = pygame.font.SysFont("Arial", 36, bold=True)
            disconnect_text = disconnect_font.render("Opponent Disconnected!", True, (255, 100, 100))
            disconnect_rect = disconnect_text.get_rect(center=(width // 2, 50))
            pygame.draw.rect(screen, (40, 40, 40), disconnect_rect.inflate(20, 10))
            screen.blit(disconnect_text, disconnect_rect)

        # Process AI turns
        def _process_auto_turns():
            if game.check_game_over():
                return False
            
            if game.pass_if_needed():
                return True

            if AI_ENABLED and game.current_player == AI_COLOR:
                global ai_thinking, last_move
                ai_thinking = True
                
                # Force immediate redraw to show "AI'S TURN" indicator
                # This happens before the AI actually thinks
                pygame.display.flip()
                pygame.event.pump()
                
                # Display AI type indicator
                if USE_MODERN_AI and modern_ai_instance:
                    overlay_text = font.render("🧠 Modern AI thinking...", True, (100, 200, 255))
                else:
                    overlay_text = font.render("AI thinking...", True, (255, 105, 180))
                
                overlay_rect = overlay_text.get_rect(center=(width // 2, 20))
                screen.blit(overlay_text, overlay_rect)
                pygame.display.flip()
                pygame.event.pump()
                pygame.time.wait(1500)  # AI thinking time
                
                # Choose move using Modern AI or Classic AI
                if USE_MODERN_AI and modern_ai_instance:
                    # Use Modern Deep Learning AI
                    valid_moves = board.get_valid_moves(AI_COLOR)
                    ai_move = modern_ai_instance.choose_move(board, AI_COLOR, valid_moves, training=False)
                else:
                    # Use Classic Minimax AI
                    ai_move = choose_move(board, AI_COLOR, difficulty=AI_DIFFICULTY)
                
                ai_thinking = False
                if ai_move:
                    flipped = board.place_disc(ai_move[0], ai_move[1], AI_COLOR)
                    place_sound.play()  # Play placement sound
                    last_move = (ai_move[0], ai_move[1])  # Track last move for highlighting
                    # Add flipped discs to animation
                    opponent_color = WHITE if AI_COLOR == 'B' else BLACK
                    ai_color_rgb = BLACK if AI_COLOR == 'B' else WHITE
                    for flip_row, flip_col in flipped:
                        animating_discs.append((flip_row, flip_col, opponent_color, ai_color_rgb, 0.0))
                    # Play flip sound if discs were flipped
                    if flipped:
                        flip_sound.play()
                    game.switch_player()
                    
                    # Smooth transition - show AI move with multiple screen updates
                    for i in range(40):  # Smooth 4-second display (40 frames * 100ms)
                        pygame.display.flip()
                        pygame.time.wait(100)
                        pygame.event.pump()  # Keep window responsive
                    return True
            return False

        while not game.check_game_over() and _process_auto_turns():
            continue
    
    # Draw achievement notifications if any
    if newly_unlocked_achievements and achievement_notification_time:
        still_showing = draw_achievement_notification(screen, width, newly_unlocked_achievements, achievement_notification_time)
        if not still_showing:
            newly_unlocked_achievements = []
            achievement_notification_time = None
    
    pygame.display.flip()
    clock.tick(60)

# Cleanup
if network_client.connected:
    network_client.disconnect()
    
pygame.quit()
