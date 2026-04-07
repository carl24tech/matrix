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
from matrix_core import MatrixBase, Terminal, MatrixConfig

class MatrixRain(MatrixBase):
    """Classic Matrix digital rain effect"""
    
    def __init__(self):
        super().__init__()
        self.columns = []
        self.init_columns()
        
    def init_columns(self):
        """Initialize rain columns"""
        for x in range(self.width):
            if random.random() < self.config.density:
                column = {
                    'y': random.randint(0, self.height),
                    'speed': random.uniform(0.5, 2.0) * self.config.speed,
                    'chars': [],
                    'intensity': random.uniform(0.5, 1.0)
                }
                
                # Generate trail characters
                for i in range(self.config.trail_length):
                    column['chars'].append(self.get_random_char())
                    
                self.columns.append((x, column))
                
    def update(self):
        """Update rain state"""
        for x, col in self.columns:
            # Move column down
            col['y'] += col['speed']
            
            # Reset if off screen
            if col['y'] - len(col['chars']) > self.height:
                col['y'] = 0
                col['chars'] = [self.get_random_char() for _ in range(self.config.trail_length)]
                continue
                
            # Update characters
            if random.random() < 0.1:
                col['chars'][0] = self.get_random_char()
                
            # Shift characters
            if int(col['y']) % 2 == 0:
                col['chars'] = [self.get_random_char()] + col['chars'][:-1]
                
    def render(self):
        """Render the matrix rain"""
        Terminal.move_cursor(0, 0)
        
        # Create screen buffer
        screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        colors = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw columns
        for x, col in self.columns:
            y_pos = int(col['y'])
            
            for i, char in enumerate(col['chars']):
                y = y_pos - i
                if 0 <= y < self.height:
                    screen[y][x] = char
                    
                    # Calculate color based on position in trail
                    color_idx = min(i, len(self.config.colors) - 1)
                    colors[y][x] = self.config.colors[color_idx]
                    
        # Render screen buffer
        for y in range(self.height):
            for x in range(self.width):
                if screen[y][x] != ' ':
                    Terminal.move_cursor(x, y)
                    Terminal.set_color(colors[y][x])
                    sys.stdout.write(screen[y][x])
                    
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
    rain = MatrixRain()
    rain.run()

if __name__ == "__main__":
    main()
