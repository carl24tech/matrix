#!/usr/bin/env python3
"""
Matrix Core Library - Shared functionality for matrix effects
Location: ~/matrix-tools/lib/matrix_core.py
"""

import os
import sys
import time
import random
import signal
import threading
import shutil
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any

@dataclass
class MatrixConfig:
    """Configuration for matrix effects"""
    density: float = 0.15  # Fixed: Increased for better visibility
    speed: float = 1.5     # Fixed: Changed from 0.05 to reasonable speed
    charset: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*"
    colors: List[str] = field(default_factory=lambda: ['32', '92', '36', '2'])  # Fixed: Use ANSI color codes
    fps: int = 30
    glitch_chance: float = 0.01  # Fixed: Increased from 0.001
    head_char: str = "█"
    trail_length: int = 10
    flicker: bool = True  # Added: Enable/disable flicker effect
    gravity: float = 0.05  # Added: Gravity effect for particles
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        # Ensure colors are properly formatted
        if self.colors and isinstance(self.colors[0], int):
            # Convert integer color codes to ANSI strings if needed
            self.colors = [str(c) for c in self.colors]
        
        # Ensure density is within bounds
        self.density = max(0.05, min(0.95, self.density))
        
        # Ensure speed is reasonable
        self.speed = max(0.5, min(5.0, self.speed))

class Terminal:
    """Terminal handling utilities"""
    
    _instance = None
    _original_settings = None
    
    @staticmethod
    def setup():
        """Setup terminal for matrix display with better compatibility"""
        try:
            # Hide cursor (multiple methods for compatibility)
            sys.stdout.write("\033[?25l")
            sys.stdout.write("\033[2J\033[H")
            
            # Try different methods to hide cursor
            if sys.platform != 'win32':
                try:
                    os.system('tput civis 2>/dev/null')
                except:
                    pass
                    
            # Set up raw mode for better input handling
            if sys.platform != 'win32' and sys.stdin.isatty():
                import termios
                import tty
                Terminal._original_settings = termios.tcgetattr(sys.stdin)
                tty.setraw(sys.stdin.fileno())
                
            # Flush output
            sys.stdout.flush()
            
        except Exception as e:
            print(f"Warning: Terminal setup failed: {e}")
            
    @staticmethod
    def cleanup():
        """Restore terminal settings"""
        try:
            # Show cursor
            sys.stdout.write("\033[?25h")
            sys.stdout.write("\033[0m")
            sys.stdout.write("\033[2J\033[H")
            
            # Restore terminal settings
            if Terminal._original_settings is not None:
                import termios
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, Terminal._original_settings)
                
            # Try different methods to show cursor
            if sys.platform != 'win32':
                try:
                    os.system('tput cnorm 2>/dev/null')
                except:
                    pass
                    
            sys.stdout.flush()
            
        except Exception as e:
            print(f"Warning: Terminal cleanup failed: {e}")
        
    @staticmethod
    def get_size() -> Tuple[int, int]:
        """Get terminal dimensions reliably"""
        try:
            # Try using shutil first (most reliable)
            columns, rows = shutil.get_terminal_size()
            return max(columns, 20), max(rows, 10)  # Minimum size
        except:
            try:
                # Fallback to os.get_terminal_size()
                size = os.get_terminal_size()
                return max(size.columns, 20), max(size.lines, 10)
            except:
                # Final fallback
                return 80, 24
            
    @staticmethod
    def move_cursor(x: int, y: int):
        """Move cursor to position (1-indexed for ANSI)"""
        # ANSI cursor positioning uses 1-indexed coordinates
        sys.stdout.write(f"\033[{y+1};{x+1}H")
        
    @staticmethod
    def set_color(color_code: str):
        """Set terminal color"""
        # Handle both string and integer color codes
        if isinstance(color_code, int):
            color_code = str(color_code)
            
        # Remove any existing color codes
        color_code = color_code.replace(';', '')
        
        # Standard ANSI color codes
        if color_code in ['32', '92', '36', '2', '33', '93', '35', '95']:
            sys.stdout.write(f"\033[{color_code}m")
        else:
            # Try 256-color mode
            sys.stdout.write(f"\033[38;5;{color_code}m")
        
    @staticmethod
    def reset_color():
        """Reset to default color"""
        sys.stdout.write("\033[0m")
        
    @staticmethod
    def clear_screen():
        """Clear screen and move cursor home"""
        sys.stdout.write("\033[2J\033[H")
        
    @staticmethod
    def get_char(timeout: float = 0) -> Optional[str]:
        """Get a single character from input without blocking"""
        if sys.platform == 'win32':
            import msvcrt
            if msvcrt.kbhit():
                return msvcrt.getch().decode('utf-8', errors='ignore')
            return None
        else:
            import select
            import termios
            import tty
            
            if select.select([sys.stdin], [], [], timeout)[0]:
                return sys.stdin.read(1)
            return None

class MatrixBase:
    """Base class for matrix effects"""
    
    def __init__(self, config: Optional[MatrixConfig] = None):
        self.config = config or MatrixConfig()
        self.running = True
        self.width, self.height = Terminal.get_size()
        self.frame_count = 0
        self.start_time = time.time()
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGWINCH, self.resize_handler)
        
        # For platforms without SIGWINCH
        if not hasattr(signal, 'SIGWINCH'):
            self.resize_handler = lambda x, y: None
            
    def signal_handler(self, signum, frame):
        """Handle termination signals gracefully"""
        self.running = False
        # Don't print anything here to avoid messing up the display
        
    def resize_handler(self, signum, frame):
        """Handle terminal resize"""
        try:
            new_width, new_height = Terminal.get_size()
            
            # Only update if size actually changed
            if new_width != self.width or new_height != self.height:
                self.width, self.height = new_width, new_height
                # Clear screen to avoid rendering artifacts
                Terminal.clear_screen()
                
        except Exception as e:
            # Silently ignore resize errors
            pass
            
    def get_random_char(self) -> str:
        """Get random character from charset"""
        try:
            return random.choice(self.config.charset)
        except IndexError:
            # Fallback if charset is empty
            return "."
            
    def get_random_chars(self, count: int) -> List[str]:
        """Get multiple random characters"""
        return [self.get_random_char() for _ in range(count)]
        
    def cleanup(self):
        """Clean up terminal resources"""
        Terminal.cleanup()
        
    def should_update(self, chance: float) -> bool:
        """Determine if an update should occur based on chance"""
        return random.random() < chance
        
    def clamp(self, value: int, min_val: int, max_val: int) -> int:
        """Clamp a value between min and max"""
        return max(min_val, min(value, max_val))
        
    def lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation"""
        return a + (b - a) * self.clamp(t, 0.0, 1.0)
        
    def get_color_by_intensity(self, intensity: float) -> str:
        """Get color code based on intensity (0-1)"""
        idx = int(intensity * (len(self.config.colors) - 1))
        idx = self.clamp(idx, 0, len(self.config.colors) - 1)
        return self.config.colors[idx]

class AnimationTimer:
    """Helper class for frame rate management"""
    
    def __init__(self, fps: int = 30):
        self.fps = fps
        self.frame_time = 1.0 / fps
        self.last_frame = time.time()
        self.frame_times = []
        
    def wait(self):
        """Wait until next frame"""
        current = time.time()
        elapsed = current - self.last_frame
        sleep_time = self.frame_time - elapsed
        
        if sleep_time > 0:
            time.sleep(sleep_time)
            
        # Track frame times for performance monitoring
        frame_duration = time.time() - self.last_frame
        self.frame_times.append(frame_duration)
        
        # Keep last 60 frame times
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
            
        self.last_frame = time.time()
        
    def get_average_fps(self) -> float:
        """Get average FPS over last 60 frames"""
        if not self.frame_times:
            return self.fps
            
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else self.fps
        
    def is_running_slow(self, threshold: float = 1.5) -> bool:
        """Check if animation is running slower than threshold"""
        avg_fps = self.get_average_fps()
        return avg_fps < (self.fps / threshold)

class ColorPalette:
    """Predefined color palettes for matrix effects"""
    
    # Classic green matrix
    CLASSIC_GREEN = ['32', '92', '36', '2']
    
    # Neon blue matrix
    NEON_BLUE = ['34', '94', '36', '4']
    
    # Red alert matrix
    RED_ALERT = ['31', '91', '33', '1']
    
    # Rainbow matrix (slower)
    RAINBOW = ['196', '202', '208', '214', '220', '226', '190', '154', '118', '82', '46']
    
    # Cyberpunk pink/cyan
    CYBERPUNK = ['198', '199', '200', '201', '51', '45', '39']
    
    @staticmethod
    def get_palette(name: str) -> List[str]:
        """Get a color palette by name"""
        palettes = {
            'classic': ColorPalette.CLASSIC_GREEN,
            'green': ColorPalette.CLASSIC_GREEN,
            'blue': ColorPalette.NEON_BLUE,
            'red': ColorPalette.RED_ALERT,
            'rainbow': ColorPalette.RAINBOW,
            'cyberpunk': ColorPalette.CYBERPUNK
        }
        return palettes.get(name.lower(), ColorPalette.CLASSIC_GREEN)

# Module initialization check
if __name__ == "__main__":
    # Test the core functionality
    print("Matrix Core Library v2.0")
    print(f"Terminal size: {Terminal.get_size()}")
    print(f"Available color palettes: classic, green, blue, red, rainbow, cyberpunk")
    
    # Test configuration
    config = MatrixConfig()
    print(f"Default config: density={config.density}, speed={config.speed}, fps={config.fps}")
    
    # Test terminal setup/cleanup
    print("\nTesting terminal setup (2 seconds)...")
    Terminal.setup()
    time.sleep(2)
    Terminal.cleanup()
    print("Terminal test complete")
    
