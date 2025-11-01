"""
Othello Game - Standalone Executable Builder
This script packages the Othello game into a standalone executable using PyInstaller.
"""

import subprocess
import sys
import os
import shutil

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller is installed")
        return True
    except ImportError:
        print("✗ PyInstaller is not installed")
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("\n📦 Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install PyInstaller")
        return False

def create_icon():
    """Create a simple icon file if it doesn't exist"""
    # Note: You can replace this with a custom .ico file
    print("\nℹ️  To use a custom icon, place 'othello_icon.ico' in the game folder")
    return None

def build_executable():
    """Build the standalone executable"""
    print("\n🔨 Building standalone executable...")
    
    # PyInstaller command with options
    cmd = [
        "pyinstaller",
        "--name=Othello",                    # Name of the executable
        "--onefile",                          # Single file executable
        "--windowed",                         # No console window (GUI only)
        "--add-data=game_settings.json;.",   # Include settings file (if exists)
        "--icon=othello_icon.ico",           # Icon file (if exists)
        "--clean",                            # Clean cache before building
        "main.py"                             # Main entry point
    ]
    
    # Check if icon exists, if not remove that option
    if not os.path.exists("othello_icon.ico"):
        cmd = [c for c in cmd if not c.startswith("--icon")]
        print("ℹ️  Building without custom icon")
    
    # Check if settings file exists
    if not os.path.exists("game_settings.json"):
        cmd = [c for c in cmd if not c.startswith("--add-data")]
        print("ℹ️  Building without settings file")
    
    try:
        subprocess.check_call(cmd)
        print("✓ Executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False
    except FileNotFoundError:
        print("✗ PyInstaller command not found. Try reinstalling PyInstaller.")
        return False

def cleanup_build_files():
    """Clean up temporary build files"""
    print("\n🧹 Cleaning up build files...")
    dirs_to_remove = ["build", "__pycache__"]
    files_to_remove = ["Othello.spec"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed: {dir_name}/")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"  Removed: {file_name}")
    
    print("✓ Cleanup complete")

def create_readme():
    """Create a README for distribution"""
    readme_content = """# Othello Game - Standalone Application

## 🎮 About
A feature-rich Othello (Reversi) game with AI opponents, stunning visual effects, and sound feedback.

## 🚀 How to Run
1. Double-click `Othello.exe` to launch the game
2. No installation required - it's completely portable!

## 🎯 Features
- **AI Opponents**: Classic Minimax and Modern Deep Learning AI
- **Multiple Difficulty Levels**: Easy, Medium, and Hard
- **Visual Effects**: Smooth animations, pulsing moves, glowing highlights
- **Sound Effects**: Satisfying audio feedback for all actions
- **Customization**: Choose board colors, disc colors, and more
- **Local Multiplayer**: Play with a friend on the same computer

## 🎲 How to Play
1. Click **PLAY** from the main menu
2. Choose **Play vs AI** or **Play Friend**
3. If playing AI, select difficulty level
4. Click on valid moves (shown with green circles) to place your disc
5. Flip opponent's discs by sandwiching them between your pieces
6. Player with the most discs at the end wins!

## ⚙️ System Requirements
- Windows 7 or later
- 100 MB free disk space
- 2 GB RAM (minimum)

## 🐛 Troubleshooting
- If the game doesn't start, try running as administrator
- Make sure Windows Defender isn't blocking the executable
- Check that you have the latest Visual C++ Redistributables installed

## 📝 Credits
Developed with Python, Pygame, and PyTorch
AI algorithms: Minimax with Alpha-Beta Pruning & Deep Q-Learning

## 📧 Support
For issues or questions, please refer to the documentation files included.

---
Version 1.0 | © 2025
"""
    
    with open("README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✓ README.txt created")

def main():
    """Main build process"""
    print("=" * 60)
    print("🎮 OTHELLO GAME - STANDALONE EXECUTABLE BUILDER")
    print("=" * 60)
    
    # Step 1: Check PyInstaller
    if not check_pyinstaller():
        response = input("\n❓ Would you like to install PyInstaller now? (y/n): ")
        if response.lower() == 'y':
            if not install_pyinstaller():
                print("\n❌ Cannot proceed without PyInstaller. Exiting...")
                return
        else:
            print("\n❌ Cannot build without PyInstaller. Exiting...")
            return
    
    # Step 2: Check for icon
    create_icon()
    
    # Step 3: Build executable
    if not build_executable():
        print("\n❌ Build process failed. Please check the errors above.")
        return
    
    # Step 4: Create distribution files
    print("\n📄 Creating distribution files...")
    create_readme()
    
    # Step 5: Cleanup
    response = input("\n❓ Would you like to clean up build files? (y/n): ")
    if response.lower() == 'y':
        cleanup_build_files()
    
    # Step 6: Summary
    print("\n" + "=" * 60)
    print("✅ BUILD COMPLETE!")
    print("=" * 60)
    print(f"\n📦 Your executable is ready in the 'dist' folder:")
    print(f"   📁 dist/Othello.exe")
    print(f"\n📋 Distribution files:")
    print(f"   📄 README.txt")
    print(f"\n🎯 Next steps:")
    print(f"   1. Test the executable: dist/Othello.exe")
    print(f"   2. Create a distribution package with:")
    print(f"      - Othello.exe")
    print(f"      - README.txt")
    print(f"      - Any additional documentation")
    print(f"   3. Share your game!")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
