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
from matrix_core import MatrixBase, Terminal, MatrixConfig

class MatrixStream(MatrixBase):
    """Stream variation with wave effects"""
    
    def __init__(self):
        super().__init__()
        self.config.density = 0.08
        self.config.speed = 0.03
        self.streams = []
        self.time = 0
        self.init_streams()
        
    def init_streams(self):
        """Initialize streams"""
        for x in range(self.width):
            if random.random() < self.config.density:
                stream = {
                    'x': x,
                    'phase': random.uniform(0, 2 * math.pi),
                    'frequency': random.uniform(0.01, 0.05),
                    'amplitude': random.uniform(0, 2),
                    'particles': []
                }
                
                # Initialize particles
                for i in range(random.randint(5, 15)):
                    stream['particles'].append({
                        'y': random.uniform(0, self.height),
                        'char': self.get_random_char(),
                        'age': random.uniform(0, 1)
                    })
                    
                self.streams.append(stream)
                
    def update(self):
        """Update stream state"""
        self.time += 0.1
        
        for stream in self.streams:
            # Update existing particles
            for particle in stream['particles']:
                # Move particle down with wave effect
                wave_offset = math.sin(self.time * stream['frequency'] + stream['phase'])
                particle['y'] += self.config.speed * 3
                particle['x_offset'] = wave_offset * stream['amplitude']
                particle['age'] += 0.01
                
                # Update character occasionally
                if random.random() < 0.05:
                    particle['char'] = self.get_random_char()
                    
            # Remove old particles
            stream['particles'] = [p for p in stream['particles'] 
                                 if p['y'] < self.height + 5 and p['age'] < 1]
            
            # Add new particles at top
            if random.random() < 0.3:
                stream['particles'].append({
                    'y': 0,
                    'char': self.get_random_char(),
                    'age': 0,
                    'x_offset': 0
                })
                
    def render(self):
        """Render streams"""
        Terminal.move_cursor(0, 0)
        
        # Clear screen
        sys.stdout.write("\033[2J")
        
        # Draw particles
        for stream in self.streams:
            for particle in stream['particles']:
                x = int(stream['x'] + particle.get('x_offset', 0))
                y = int(particle['y'])
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    Terminal.move_cursor(x, y)
                    
                    # Color based on age
                    color_idx = int(particle['age'] * (len(self.config.colors) - 1))
                    color_idx = max(0, min(color_idx, len(self.config.colors) - 1))
                    
                    Terminal.set_color(self.config.colors[color_idx])
                    
                    # Bright head, dimmer tail
                    if particle['age'] < 0.1:
                        sys.stdout.write(self.config.head_char)
                    else:
                        sys.stdout.write(particle['char'])
                        
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
    stream = MatrixStream()
    stream.run()

if __name__ == "__main__":
    main()
