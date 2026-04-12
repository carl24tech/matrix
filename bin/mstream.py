#!/usr/bin/env python3
"""
Matrix Stream - Stream/column variation with more dramatic effects
Location: ~/matrix-tools/bin/mstream
"""

import sys
import os
sys.path.insert(0, os.path.expanduser("~/matrix-tools/lib"))

import time
import random
import math
import signal
from matrix_core import MatrixBase, Terminal, MatrixConfig

class MatrixStream(MatrixBase):
    """Stream variation with wave effects"""
    
    def __init__(self):
        super().__init__()
        # Fixed: Use proper configuration values
        self.config.density = 0.15  # Increased from 0.08 for better visibility
        self.config.speed = 1.5  # Fixed: Changed from 0.03 to reasonable speed
        self.streams = []
        self.time = 0
        self.last_update_time = time.time()
        self.frame_count = 0
        self.init_streams()
        
    def init_streams(self):
        """Initialize streams with better default values"""
        self.streams = []
        
        # Get density from config
        density = getattr(self.config, 'density', 0.15)
        
        for x in range(self.width):
            if random.random() < density:
                stream = {
                    'x': float(x),  # Fixed: Store as float for smoother movement
                    'phase': random.uniform(0, 2 * math.pi),
                    'frequency': random.uniform(0.02, 0.08),  # Adjusted range
                    'amplitude': random.uniform(0.5, 3.0),  # Increased amplitude
                    'particles': [],
                    'color_variation': random.uniform(0.7, 1.3),
                    'speed_multiplier': random.uniform(0.8, 1.2)
                }
                
                # Initialize particles with better distribution
                num_particles = random.randint(8, 20)
                for i in range(num_particles):
                    stream['particles'].append({
                        'y': random.uniform(-10, self.height),
                        'char': self.get_random_char(),
                        'age': random.uniform(0, 1),
                        'x_offset': 0,
                        'brightness': random.uniform(0.3, 1.0),
                        'flicker': random.uniform(0.8, 1.2)
                    })
                    
                self.streams.append(stream)
        
        # Ensure at least some streams exist
        if not self.streams and self.width > 0:
            for x in range(min(5, self.width)):
                self.create_single_stream(x)
                
    def create_single_stream(self, x):
        """Create a single stream at position x"""
        stream = {
            'x': float(x),
            'phase': random.uniform(0, 2 * math.pi),
            'frequency': random.uniform(0.02, 0.08),
            'amplitude': random.uniform(1.0, 2.5),
            'particles': [],
            'color_variation': random.uniform(0.8, 1.2),
            'speed_multiplier': random.uniform(0.9, 1.1)
        }
        
        for i in range(random.randint(10, 15)):
            stream['particles'].append({
                'y': random.uniform(-5, self.height),
                'char': self.get_random_char(),
                'age': random.uniform(0, 1),
                'x_offset': 0,
                'brightness': random.uniform(0.5, 1.0),
                'flicker': 1.0
            })
            
        self.streams.append(stream)
                
    def update(self):
        """Update stream state with delta time"""
        current_time = time.time()
        delta_time = min(current_time - self.last_update_time, 0.1)
        self.last_update_time = current_time
        self.time += delta_time * 5  # Fixed: Use delta time for wave animation
        
        # Get base speed from config
        base_speed = getattr(self.config, 'speed', 1.5)
        
        for stream in self.streams:
            # Update existing particles
            particles_to_remove = []
            
            for idx, particle in enumerate(stream['particles']):
                # Calculate wave offset with smoother animation
                wave_offset = math.sin(self.time * stream['frequency'] + stream['phase'])
                particle['x_offset'] = wave_offset * stream['amplitude']
                
                # Move particle down with speed variation
                speed = base_speed * stream['speed_multiplier'] * delta_time * self.config.fps
                particle['y'] += speed
                
                # Update age based on position
                particle['age'] = min(1.0, particle['y'] / (self.height + 20))
                
                # Update character occasionally with life-based variation
                if random.random() < 0.08:
                    particle['char'] = self.get_random_char()
                
                # Update flicker effect
                if random.random() < 0.1:
                    particle['flicker'] = random.uniform(0.7, 1.3)
                
                # Mark for removal if off screen
                if particle['y'] > self.height + 10 or particle['y'] < -10:
                    particles_to_remove.append(idx)
                    
            # Remove old particles (reverse order to avoid index issues)
            for idx in reversed(particles_to_remove):
                stream['particles'].pop(idx)
            
            # Add new particles at top
            if random.random() < 0.4:  # Increased frequency
                new_particle = {
                    'y': -random.uniform(0, 5),
                    'char': self.get_random_char(),
                    'age': 0,
                    'x_offset': 0,
                    'brightness': random.uniform(0.7, 1.0),
                    'flicker': random.uniform(0.9, 1.1)
                }
                stream['particles'].append(new_particle)
                
            # Occasionally add burst of particles
            if random.random() < 0.02:
                for _ in range(random.randint(2, 5)):
                    stream['particles'].append({
                        'y': -random.uniform(0, 2),
                        'char': self.get_random_char(),
                        'age': 0,
                        'x_offset': 0,
                        'brightness': random.uniform(0.8, 1.0),
                        'flicker': random.uniform(0.8, 1.2)
                    })
                
    def render(self):
        """Render streams with improved visual effects"""
        # Clear screen efficiently
        sys.stdout.write("\033[2J\033[H")
        
        # Create render buffer
        render_buffer = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw particles
        for stream in self.streams:
            for particle in stream['particles']:
                x = int(stream['x'] + particle.get('x_offset', 0))
                y = int(particle['y'])
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Calculate color based on age and brightness
                    if particle['age'] < 0.1:  # Head of stream
                        color_idx = 0  # Brightest
                    elif particle['age'] < 0.3:
                        color_idx = 1  # Bright
                    elif particle['age'] < 0.6:
                        color_idx = 2  # Medium
                    else:
                        color_idx = 3  # Dim
                    
                    # Apply brightness and flicker
                    brightness = particle.get('brightness', 0.7) * particle.get('flicker', 1.0)
                    if brightness < 0.4:
                        color_idx = min(color_idx + 1, len(self.config.colors) - 1)
                    
                    # Ensure color index is within bounds
                    color_idx = min(color_idx, len(self.config.colors) - 1)
                    
                    # Choose character (head character for stream leaders)
                    if particle['age'] < 0.15 and random.random() < 0.3:
                        char = self.config.get('head_char', '█')  # Use block for head
                    else:
                        char = particle['char']
                    
                    # Store in buffer (keep highest brightness if multiple particles)
                    if (render_buffer[y][x] is None or 
                        particle['age'] < render_buffer[y][x][1]):
                        render_buffer[y][x] = (char, particle['age'], color_idx)
        
        # Render buffer
        for y in range(self.height):
            line_parts = []
            current_color = None
            
            for x in range(self.width):
                if render_buffer[y][x] is not None:
                    char, age, color_idx = render_buffer[y][x]
                    color_code = self.config.colors[color_idx]
                    
                    if color_code != current_color:
                        if current_color is not None:
                            line_parts.append("\033[0m")
                        line_parts.append(f"\033[{color_code}m")
                        current_color = color_code
                    
                    # Add intensity variation for head characters
                    if age < 0.1:
                        char = char.upper()
                    
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
        self.init_streams()  # Reinitialize for new size
        sys.stdout.write("\033[2J\033[H")
        
    def run(self):
        """Main loop with error handling"""
        Terminal.setup()
        
        # Set up signal handlers
        signal.signal(signal.SIGWINCH, self.handle_resize)
        
        try:
            start_time = time.time()
            
            while self.running:
                frame_start = time.time()
                
                self.update()
                self.render()
                
                # Maintain consistent frame rate
                frame_time = time.time() - frame_start
                sleep_time = (1.0 / self.config.fps) - frame_time
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                self.frame_count += 1
                
                # Auto-exit after 30 seconds for menu integration
                if time.time() - start_time > 30:
                    break
                    
        except KeyboardInterrupt:
            print("\n\nMatrix Stream interrupted by user")
        except Exception as e:
            print(f"\nError in Matrix Stream: {e}")
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
            sys.exit(1)
            
        stream = MatrixStream()
        stream.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
