#!/bin/bash
# Matrix Tools Installation Script

set -e

MATRIX_HOME="$HOME/matrix-tools"
BIN_DIR="$HOME/.local/bin"

echo "Installing Matrix Tools..."

# Create directories
mkdir -p "$MATRIX_HOME"/{bin,lib,config}

# Make all Python scripts executable
chmod +x "$MATRIX_HOME"/bin/*.py 2>/dev/null || true
chmod +x "$MATRIX_HOME"/bin/matrix

# Create symlinks in ~/.local/bin
mkdir -p "$BIN_DIR"
ln -sf "$MATRIX_HOME/bin/matrix" "$BIN_DIR/matrix"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$HOME/.bashrc"
    echo "Added $BIN_DIR to PATH"
fi

echo "Installation complete!"
echo "Run 'matrix' to start the Matrix Tools menu"
echo "Or run individual tools: mrain, mstream, mburst, mglitch"
