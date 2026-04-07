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
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class MatrixConfig:
    """Configuration for matrix effects"""
    density: float = 0.05
    speed: float = 0.05
    charset: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*"
    colors: List[int] = [22, 28, 34, 40, 46, 82, 118, 154, 190, 226]
    fps: int = 30
    glitch_chance: float = 0.001
    head_char: str = "█"
    trail_length: int = 10

class Terminal:
    """Terminal handling utilities"""
    
    @staticmethod
    def setup():
        """Setup terminal for matrix display"""
        os.system('setterm -cursor off > /dev/tty1 2>&1')
        os.system('tput civis')
        os.system('clear')
        os.system('printf "\\033[?25l"')
        
    @staticmethod
    def cleanup():
        """Restore terminal settings"""
        os.system('tput cnorm')
        os.system('printf "\\033[?25h"')
        os.system('reset')
        
    @staticmethod
    def get_size() -> Tuple[int, int]:
        """Get terminal dimensions"""
        try:
            size = os.get_terminal_size()
            return size.columns, size.lines
        except:
            return 80, 24
            
    @staticmethod
    def move_cursor(x: int, y: int):
        """Move cursor to position"""
        sys.stdout.write(f"\033[{y};{x}H")
        
    @staticmethod
    def set_color(code: int):
        """Set 256-color mode color"""
        sys.stdout.write(f"\033[38;5;{code}m")
        
    @staticmethod
    def reset_color():
        """Reset to default color"""
        sys.stdout.write("\033[0m")

class MatrixBase:
    """Base class for matrix effects"""
    
    def __init__(self, config: Optional[MatrixConfig] = None):
        self.config = config or MatrixConfig()
        self.running = True
        self.width, self.height = Terminal.get_size()
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGWINCH, self.resize_handler)
        
    def signal_handler(self, signum, frame):
        """Handle termination signals"""
        self.running = False
        
    def resize_handler(self, signum, frame):
        """Handle terminal resize"""
        self.width, self.height = Terminal.get_size()
        
    def get_random_char(self) -> str:
        """Get random character from charset"""
        return random.choice(self.config.charset)
        
    def cleanup(self):
        """Clean up terminal"""
        Terminal.cleanup()
