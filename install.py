#!/usr/bin/env python3
"""
Installation script for HumidStat Humidity Monitor
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    dependencies = [
        "ttkbootstrap>=1.10.1",
        "matplotlib>=3.7.0",
        "pyserial>=3.5",
        "pythonping>=1.1.4"
    ]
    
    print("Installing HumidStat dependencies...")
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✓ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {dep}: {e}")
            return False
    
    print("\n✓ All dependencies installed successfully!")
    return True

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)"""
    if sys.platform == "win32":
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "HumidStat.lnk")
            target = os.path.join(os.getcwd(), "main.py")
            wDir = os.getcwd()
            icon = target
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon
            shortcut.save()
            
            print("✓ Desktop shortcut created")
        except ImportError:
            print("Desktop shortcut creation requires pywin32 (optional)")
        except Exception as e:
            print(f"Could not create desktop shortcut: {e}")

def main():
    """Main installation process"""
    print("=" * 50)
    print("HumidStat - Humidity Monitor Installation")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"Python {sys.version} detected ✓")
    
    # Install dependencies
    if not install_dependencies():
        print("Installation failed!")
        sys.exit(1)
    
    # Create desktop shortcut
    create_desktop_shortcut()
    
    print("\n" + "=" * 50)
    print("Installation completed successfully!")
    print("You can now run the application with: python main.py")
    print("=" * 50)

if __name__ == "__main__":
    main()
