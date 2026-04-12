#!/usr/bin/env python3
"""
Matrix Rain - Classic Matrix digital rain effect
Location: ~/matrix-tools/bin/mrain
"""

import sys
import os
sys.path.insert(0, os.path.expanduser("~/matrix-tools/lib"))

import time
import random
import signal
from matrix_core import MatrixBase, Terminal, MatrixConfig

class MatrixRain(MatrixBase):
    """Classic Matrix digital rain effect"""
    
    def __init__(self):
        super().__init__()
        self.columns = []
        self.frame_count = 0
        self.last_update_time = time.time()
        self.init_columns()
        
    def init_columns(self):
        """Initialize rain columns"""
        # Clear existing columns
        self.columns = []
        
        # Get density from config, default to 0.7 if not set
        density = getattr(self.config, 'density', 0.7)
        trail_length = getattr(self.config, 'trail_length', 10)
        
        for x in range(self.width):
            if random.random() < density:
                # Random speed variation
                speed_variation = random.uniform(0.7, 1.3)
                base_speed = getattr(self.config, 'speed', 1.0)
                
                column = {
                    'y': random.uniform(-trail_length, self.height),  # Start above screen
                    'speed': base_speed * speed_variation,
                    'chars': [],
                    'intensity': random.uniform(0.5, 1.0),
                    'head_bright': True,  # Head character brighter
                    'flicker': random.uniform(0.8, 1.2)  # Flicker effect
                }
                
                # Generate trail characters
                for i in range(trail_length):
                    column['chars'].append(self.get_random_char())
                    
                self.columns.append((x, column))
        
        # Ensure at least some columns exist
        if not self.columns and self.width > 0:
            for x in range(min(10, self.width)):
                column = {
                    'y': random.uniform(0, self.height),
                    'speed': random.uniform(0.5, 1.5),
                    'chars': [self.get_random_char() for _ in range(trail_length)],
                    'intensity': 1.0,
                    'head_bright': True,
                    'flicker': 1.0
                }
                self.columns.append((x, column))
                
    def update(self):
        """Update rain state with delta time"""
        current_time = time.time()
        delta_time = min(current_time - self.last_update_time, 0.1)  # Cap delta time
        self.last_update_time = current_time
        
        # Get configuration values
        trail_length = getattr(self.config, 'trail_length', 10)
        flicker_enabled = getattr(self.config, 'flicker', True)
        
        for idx, (x, col) in enumerate(self.columns):
            # Move column down with delta time compensation
            col['y'] += col['speed'] * delta_time * self.config.fps
            
            # Reset if completely off screen
            if col['y'] - len(col['chars']) > self.height:
                # Reset column at top with new properties
                col['y'] = -random.randint(1, trail_length)
                col['speed'] = random.uniform(0.5, 2.0) * getattr(self.config, 'speed', 1.0)
                col['chars'] = [self.get_random_char() for _ in range(trail_length)]
                col['intensity'] = random.uniform(0.5, 1.0)
                col['flicker'] = random.uniform(0.7, 1.3)
                continue
                
            # Update head character occasionally
            if random.random() < 0.15:  # Increased frequency
                col['chars'][0] = self.get_random_char()
                
            # Shift characters down (trail effect)
            # Use frame counter for smoother animation
            if self.frame_count % max(1, int(2 / delta_time)) == 0:
                # Create new head and shift trail
                new_char = self.get_random_char()
                col['chars'] = [new_char] + col['chars'][:-1]
                
            # Apply flicker effect
            if flicker_enabled and random.random() < 0.05:
                col['flicker'] = random.uniform(0.5, 1.5)
                
    def render(self):
        """Render the matrix rain efficiently"""
        # Clear screen
        sys.stdout.write("\033[2J\033[H")
        
        # Create screen buffer for characters and colors
        screen_buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        color_buffer = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Get trail length from config
        trail_length = getattr(self.config, 'trail_length', 10)
        
        # Draw columns
        for x, col in self.columns:
            y_pos = int(col['y'])
            
            # Skip if completely off screen
            if y_pos < -trail_length or y_pos - trail_length > self.height:
                continue
                
            # Draw each character in the trail
            for i, char in enumerate(col['chars']):
                y = y_pos - i
                
                if 0 <= y < self.height and 0 <= x < self.width:
                    # Calculate intensity based on position in trail
                    position_factor = 1.0 - (i / trail_length)
                    
                    # Head character is brighter
                    if i == 0 and col.get('head_bright', True):
                        intensity = min(1.0, position_factor * 1.5)
                    else:
                        intensity = position_factor * col['intensity']
                    
                    # Apply flicker
                    intensity *= col.get('flicker', 1.0)
                    
                    # Determine color based on intensity and position
                    if intensity > 0.8:
                        color_idx = 0  # Bright green
                    elif intensity > 0.5:
                        color_idx = 1  # Medium green
                    elif intensity > 0.2:
                        color_idx = 2  # Dim green
                    else:
                        color_idx = 3  # Very dim
                    
                    # Ensure color index is within bounds
                    color_idx = min(color_idx, len(self.config.colors) - 1)
                    
                    # Store in buffer
                    screen_buffer[y][x] = char
                    color_buffer[y][x] = self.config.colors[color_idx]
                    
        # Render the buffer
        for y in range(self.height):
            line_parts = []
            current_color = None
            
            for x in range(self.width):
                char = screen_buffer[y][x]
                color = color_buffer[y][x]
                
                if char != ' ':
                    if color != current_color:
                        if current_color is not None:
                            line_parts.append("\033[0m")
                        line_parts.append(f"\033[{color}m")
                        current_color = color
                    line_parts.append(char)
                else:
                    if current_color is not None:
                        line_parts.append("\033[0m")
                        current_color = None
                    line_parts.append(' ')
                    
            # Reset color at end of line
            if current_color is not None:
                line_parts.append("\033[0m")
                
            sys.stdout.write("".join(line_parts))
            if y < self.height - 1:
                sys.stdout.write("\n")
                
        sys.stdout.flush()
        
    def handle_resize(self, signum, frame):
        """Handle terminal resize"""
        self.width, self.height = Terminal.get_size()
        self.init_columns()  # Reinitialize for new size
        sys.stdout.write("\033[2J\033[H")
        
    def run(self):
        """Main loop with error handling and performance optimization"""
        Terminal.setup()
        
        # Set up signal handlers
        signal.signal(signal.SIGWINCH, self.handle_resize)
        
        try:
            start_time = time.time()
            frame_times = []
            
            while self.running:
                frame_start = time.time()
                
                # Update and render
                self.update()
                self.render()
                
                # Calculate frame time
                frame_time = time.time() - frame_start
                frame_times.append(frame_time)
                
                # Keep last 60 frame times for average calculation
                if len(frame_times) > 60:
                    frame_times.pop(0)
                
                # Maintain consistent frame rate
                target_frame_time = 1.0 / self.config.fps
                sleep_time = target_frame_time - frame_time
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                elif sleep_time < -0.01:  # Running too slow
                    # Dynamically adjust if running behind
                    avg_frame_time = sum(frame_times) / len(frame_times)
                    if avg_frame_time > target_frame_time * 1.5:
                        # Reduce quality slightly for performance
                        self.frame_count += 2  # Skip some updates
                
                self.frame_count += 1
                
                # Optional: Auto-exit after 30 seconds for menu integration
                if time.time() - start_time > 30:
                    break
                    
        except KeyboardInterrupt:
            print("\n\nMatrix Rain interrupted by user")
        except Exception as e:
            print(f"\nError in Matrix Rain: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

def main():
    """Entry point with error handling"""
    try:
        # Check if required modules exist
        try:
            from matrix_core import MatrixBase, Terminal, MatrixConfig
        except ImportError as e:
            print(f"Error: Could not import matrix_core module: {e}")
            print("Please ensure ~/matrix-tools/lib/matrix_core.py exists")
            print("\nCreating basic matrix_core module...")
            create_basic_core()
            sys.exit(1)
            
        rain = MatrixRain()
        rain.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

def create_basic_core():
    """Create a basic matrix_core module if missing"""
    core_path = os.path.expanduser("~/matrix-tools/lib/matrix_core.py")
    os.makedirs(os.path.dirname(core_path), exist_ok=True)
    
    with open(core_path, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""Matrix Core Module - Basic implementation"""

import sys
import os
import random
import termios
import tty
import select

class Terminal:
    @staticmethod
    def setup():
        """Setup terminal for raw mode"""
        if sys.platform != 'win32':
            import tty
            import termios
            Terminal.fd = sys.stdin.fileno()
            Terminal.old_settings = termios.tcgetattr(Terminal.fd)
            tty.setraw(Terminal.fd)
    
    @staticmethod
    def cleanup():
        """Restore terminal settings"""
        if sys.platform != 'win32' and hasattr(Terminal, 'old_settings'):
            import termios
            termios.tcsetattr(Terminal.fd, termios.TCSADRAIN, Terminal.old_settings)
    
    @staticmethod
    def get_size():
        """Get terminal size"""
        try:
            import shutil
            columns, rows = shutil.get_terminal_size()
            return columns, rows
        except:
            return 80, 24
    
    @staticmethod
    def set_color(color_code):
        """Set terminal color"""
        sys.stdout.write(f"\\033[{color_code}m")
    
    @staticmethod
    def reset_color():
        """Reset terminal color"""
        sys.stdout.write("\\033[0m")
    
    @staticmethod
    def move_cursor(x, y):
        """Move cursor to position"""
        sys.stdout.write(f"\\033[{y+1};{x+1}H")

class MatrixConfig:
    def __init__(self):
        self.fps = 30
        self.speed = 1.0
        self.colors = ['32', '92', '36', '2']  # Green, bright green, cyan, dim
        self.density = 0.7
        self.trail_length = 10

class MatrixBase:
    def __init__(self):
        self.config = MatrixConfig()
        self.width, self.height = Terminal.get_size()
        self.running = True
        self.chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()"
    
    def get_random_char(self):
        """Get a random matrix character"""
        return random.choice(self.chars)
    
    def cleanup(self):
        """Clean up terminal"""
        Terminal.cleanup()
        sys.stdout.write("\\033[2J\\033[H\\033[0m")
''')
    
    print(f"Created basic matrix_core at {core_path}")

if __name__ == "__main__":
    main()
