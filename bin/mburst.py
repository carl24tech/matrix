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
from matrix_core import MatrixBase, Terminal, MatrixConfig

class MatrixBurst(MatrixBase):
    """Matrix code with burst/explosion effects"""
    
    def __init__(self):
        super().__init__()
        self.particles = []
        self.burst_timer = 0
        self.burst_interval = 3  # Seconds between bursts
        
    def create_burst(self, x=None, y=None):
        """Create a burst of matrix characters"""
        if x is None:
            x = random.randint(5, self.width - 5)
        if y is None:
            y = random.randint(5, self.height - 5)
            
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
                'decay': random.uniform(0.01, 0.03)
            }
            self.particles.append(particle)
            
    def update(self):
        """Update particles and create new bursts"""
        self.burst_timer += 1.0 / self.config.fps
        
        # Create new burst
        if self.burst_timer >= self.burst_interval:
            self.create_burst()
            self.burst_timer = 0
            
        # Random additional bursts
        if random.random() < 0.01:
            self.create_burst()
            
        # Update existing particles
        for particle in self.particles[:]:
            # Apply physics
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.05  # Gravity
            
            # Reduce life
            particle['life'] -= particle['decay']
            
            # Update character occasionally
            if random.random() < 0.1:
                particle['char'] = self.get_random_char()
                
            # Remove dead particles
            if (particle['life'] <= 0 or 
                particle['x'] < 0 or particle['x'] >= self.width or
                particle['y'] >= self.height):
                self.particles.remove(particle)
                
    def render(self):
        """Render particles"""
        Terminal.move_cursor(0, 0)
        sys.stdout.write("\033[2J")
        
        # Group particles by position for better rendering
        positions = {}
        
        for particle in self.particles:
            x, y = int(particle['x']), int(particle['y'])
            
            if 0 <= x < self.width and 0 <= y < self.height:
                key = (x, y)
                
                if key not in positions:
                    positions[key] = []
                    
                positions[key].append((particle['char'], particle['life']))
                
        # Render particles
        for (x, y), chars in positions.items():
            Terminal.move_cursor(x, y)
            
            # Use the brightest/latest character
            char, life = max(chars, key=lambda c: c[1])
            
            # Color based on life
            color_idx = int(life * (len(self.config.colors) - 1))
            color_idx = max(0, min(color_idx, len(self.config.colors) - 1))
            
            Terminal.set_color(self.config.colors[color_idx])
            sys.stdout.write(char)
            
        Terminal.reset_color()
        sys.stdout.flush()
        
    def run(self):
        """Main loop"""
        Terminal.setup()
        
        try:
            while self.running:
                self.update()
                self.render()
                time.sleep(1.0 / self.config.fps)
        finally:
            self.cleanup()

def main():
    burst = MatrixBurst()
    burst.run()

if __name__ == "__main__":
    main()
