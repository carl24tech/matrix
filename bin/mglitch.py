#!/usr/bin/env python3
"""
Matrix Glitch - Matrix rain with glitch/distortion effects
Location: ~/matrix-tools/bin/mglitch
"""

import sys
import os
sys.path.insert(0, os.path.expanduser("~/matrix-tools/lib"))

import time
import random
from matrix_core import MatrixBase, Terminal, MatrixConfig

class MatrixGlitch(MatrixBase):
    """Matrix effect with digital glitch artifacts"""
    
    def __init__(self):
        super().__init__()
        self.config.density = 0.06
        self.columns = []
        self.glitch_blocks = []
        self.init_columns()
        
    def init_columns(self):
        """Initialize columns"""
        for x in range(self.width):
            if random.random() < self.config.density:
                column = {
                    'y': random.randint(0, self.height),
                    'speed': random.uniform(0.5, 2.0) * self.config.speed,
                    'chars': [self.get_random_char() for _ in range(self.config.trail_length)],
                    'glitch_timer': 0
                }
                self.columns.append((x, column))
                
    def create_glitch(self):
        """Create a glitch block"""
        x = random.randint(0, self.width - 10)
        y = random.randint(0, self.height - 5)
        width = random.randint(5, 20)
        height = random.randint(2, 8)
        
        glitch = {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'life': 1.0,
            'chars': [[self.get_random_char() for _ in range(width)] for _ in range(height)],
            'offset_x': random.randint(-2, 2)
        }
        self.glitch_blocks.append(glitch)
        
    def update(self):
        """Update state"""
        # Update columns
        for x, col in self.columns:
            col['y'] += col['speed']
            
            if col['y'] - len(col['chars']) > self.height:
                col['y'] = 0
                col['chars'] = [self.get_random_char() for _ in range(self.config.trail_length)]
                
            if random.random() < 0.1:
                col['chars'][0] = self.get_random_char()
                
            if int(col['y']) % 2 == 0:
                col['chars'] = [self.get_random_char()] + col['chars'][:-1]
                
            # Column glitch
            col['glitch_timer'] -= 1
            if col['glitch_timer'] <= 0 and random.random() < self.config.glitch_chance:
                col['glitch_timer'] = random.randint(5, 20)
                
        # Create glitch blocks
        if random.random() < self.config.glitch_chance * 2:
            self.create_glitch()
            
        # Update glitch blocks
        for glitch in self.glitch_blocks[:]:
            glitch['life'] -= 0.02
            
            # Update glitch characters
            if random.random() < 0.3:
                y = random.randint(0, glitch['height'] - 1)
                x = random.randint(0, glitch['width'] - 1)
                glitch['chars'][y][x] = self.get_random_char()
                
            if glitch['life'] <= 0:
                self.glitch_blocks.remove(glitch)
                
    def render(self):
        """Render matrix with glitch effects"""
        Terminal.move_cursor(0, 0)
        
        # Create screen buffer
        screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        colors = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw columns
        for x, col in self.columns:
            y_pos = int(col['y'])
            glitch_offset = 0
            
            # Apply column glitch
            if col['glitch_timer'] > 0:
                glitch_offset = random.randint(-2, 2)
                
            for i, char in enumerate(col['chars']):
                y = y_pos - i
                if 0 <= y < self.height:
                    draw_x = x + glitch_offset
                    
                    if 0 <= draw_x < self.width:
                        screen[y][draw_x] = char
                        color_idx = min(i, len(self.config.colors) - 1)
                        colors[y][draw_x] = self.config.colors[color_idx]
                        
        # Draw glitch blocks
        for glitch in self.glitch_blocks:
            for y in range(glitch['height']):
                for x in range(glitch['width']):
                    screen_y = glitch['y'] + y
                    screen_x = glitch['x'] + x + glitch['offset_x']
                    
                    if 0 <= screen_y < self.height and 0 <= screen_x < self.width:
                        screen[screen_y][screen_x] = glitch['chars'][y][x]
                        color_idx = int(glitch['life'] * len(self.config.colors))
                        color_idx = max(0, min(color_idx, len(self.config.colors) - 1))
                        colors[screen_y][screen_x] = self.config.colors[color_idx]
                        
        # Render screen
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
    glitch = MatrixGlitch()
    glitch.run()

if __name__ == "__main__":
    main()
