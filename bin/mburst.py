#!/usr/bin/env python3
"""
Matrix Burst - Explosion/burst effects with matrix characters
Location: ~/matrix-tools/bin/mburst
"""

import sys
import os
sys.path.insert(0, os.path.expanduser("~/matrix-tools/lib"))

import time
import random
import math
import signal
from matrix_core import MatrixBase, Terminal, MatrixConfig

class MatrixBurst(MatrixBase):
    """Matrix code with burst/explosion effects"""
    
    def __init__(self):
        super().__init__()
        self.particles = []
        self.burst_timer = 0.0  # Fixed: Initialize as float
        self.burst_interval = 3.0  # Seconds between bursts
        self.last_update_time = time.time()
        self.frame_count = 0
        
        # Validate terminal dimensions
        if self.width < 20 or self.height < 10:
            print("Warning: Terminal too small for burst effects")
            time.sleep(1)
        
    def create_burst(self, x=None, y=None):
        """Create a burst of matrix characters"""
        if x is None:
            x = random.randint(5, max(5, self.width - 5))
        if y is None:
            y = random.randint(5, max(5, self.height - 5))
            
        # Create explosion particles
        num_particles = random.randint(30, 60)
        
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 3.0)
            
            particle = {
                'x': float(x),
                'y': float(y),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'char': self.get_random_char(),
                'life': 1.0,
                'decay': random.uniform(0.01, 0.03),
                'trail': []  # Add trail effect
            }
            self.particles.append(particle)
            
        return num_particles  # Return count for debugging
        
    def update_particle_physics(self, particle):
        """Update individual particle physics"""
        # Apply velocity
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        
        # Apply gravity with variation
        gravity = 0.05 + (1.0 - particle['life']) * 0.02
        particle['vy'] += gravity
        
        # Add air resistance
        particle['vx'] *= 0.99
        particle['vy'] *= 0.99
        
        # Reduce life
        particle['life'] -= particle['decay']
        
        # Update character occasionally with life-based variation
        if random.random() < 0.1:
            # Characters change more rapidly as life decreases
            if random.random() < (1.0 - particle['life']):
                particle['char'] = self.get_random_char()
                
        # Add trail effect
        if random.random() < 0.3:
            trail_particle = particle.copy()
            trail_particle['life'] = particle['life'] * 0.5
            trail_particle['decay'] = particle['decay'] * 1.5
            trail_particle['x'] -= particle['vx'] * 0.5
            trail_particle['y'] -= particle['vy'] * 0.5
            self.particles.append(trail_particle)
        
    def update(self):
        """Update particles and create new bursts"""
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update timer with delta time for smoother animation
        self.burst_timer += delta_time
        
        # Create new burst at intervals
        if self.burst_timer >= self.burst_interval:
            # Create burst at random location
            self.create_burst()
            self.burst_timer = 0.0
            
            # Occasionally create multiple bursts
            if random.random() < 0.3:
                self.create_burst()
        
        # Random additional bursts based on particle count
        if len(self.particles) < 100 and random.random() < 0.02:
            self.create_burst()
            
        # Update existing particles
        for particle in self.particles[:]:  # Use slice copy for safe removal
            self.update_particle_physics(particle)
                
            # Remove dead particles
            if (particle['life'] <= 0 or 
                particle['x'] < -5 or particle['x'] >= self.width + 5 or
                particle['y'] < -5 or particle['y'] >= self.height + 10):
                self.particles.remove(particle)
                
    def render(self):
        """Render particles with improved performance"""
        # Clear screen efficiently
        sys.stdout.write("\033[2J\033[H")
        
        # Create a 2D array for rendering (performance optimization)
        render_buffer = [[None for _ in range(self.height)] for _ in range(self.width)]
        
        # Group particles by position
        for particle in self.particles:
            x, y = int(particle['x']), int(particle['y'])
            
            if 0 <= x < self.width and 0 <= y < self.height:
                # Keep the particle with highest life at each position
                if (render_buffer[x][y] is None or 
                    particle['life'] > render_buffer[x][y][1]):
                    render_buffer[x][y] = (particle['char'], particle['life'])
        
        # Render all particles
        for y in range(self.height):
            line_buffer = []
            for x in range(self.width):
                if render_buffer[x][y] is not None:
                    char, life = render_buffer[x][y]
                    
                    # Color based on life and position
                    color_idx = min(int(life * (len(self.config.colors) - 1)), 
                                  len(self.config.colors) - 1)
                    color_idx = max(0, color_idx)
                    
                    # Add brightness effect for explosion center
                    if life > 0.8:
                        char = char.upper()
                    
                    line_buffer.append(f"\033[{self.config.colors[color_idx]}m{char}")
                else:
                    line_buffer.append(" ")
            
            sys.stdout.write("".join(line_buffer))
            if y < self.height - 1:
                sys.stdout.write("\n")
        
        sys.stdout.write("\033[0m")  # Reset colors
        sys.stdout.flush()
        
        # Update frame counter
        self.frame_count += 1
        
    def handle_resize(self, signum, frame):
        """Handle terminal resize"""
        self.width, self.height = Terminal.get_size()
        # Clear particles on resize to avoid errors
        self.particles.clear()
        sys.stdout.write("\033[2J\033[H")
        
    def run(self):
        """Main loop with error handling"""
        Terminal.setup()
        
        # Set up signal handlers
        signal.signal(signal.SIGWINCH, self.handle_resize)
        
        try:
            # Initial burst to start
            self.create_burst(self.width // 2, self.height // 2)
            
            start_time = time.time()
            running_time = 0
            
            while self.running:
                frame_start = time.time()
                
                self.update()
                self.render()
                
                # Maintain consistent frame rate
                frame_time = time.time() - frame_start
                sleep_time = (1.0 / self.config.fps) - frame_time
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                # Update running time (for potential auto-exit)
                running_time = time.time() - start_time
                
                # Optional: Auto-exit after 30 seconds if no user input
                if running_time > 30 and len(self.particles) < 10:
                    break
                    
        except KeyboardInterrupt:
            print("\n\nBurst effect interrupted by user")
        except Exception as e:
            print(f"\nError in burst effect: {e}")
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
            
        burst = MatrixBurst()
        burst.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
