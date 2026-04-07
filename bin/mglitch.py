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
            if col['glitch_timer']
