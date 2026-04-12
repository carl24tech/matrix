#!/bin/bash
# Matrix Tools Wrapper
# Location: ~/matrix-tools/bin/matrix

MATRIX_HOME="$HOME/matrix-tools"

# Check if required directories and files exist
check_requirements() {
    local missing=0
    
    if [ ! -d "$MATRIX_HOME/bin" ]; then
        echo "Error: $MATRIX_HOME/bin directory not found"
        missing=1
    fi
    
    if [ ! -d "$MATRIX_HOME/config" ]; then
        echo "Warning: $MATRIX_HOME/config directory not found, creating..."
        mkdir -p "$MATRIX_HOME/config"
    fi
    
    # Check if Python scripts exist
    for script in mrain mstream mburst mglitch; do
        if [ ! -f "$MATRIX_HOME/bin/$script" ]; then
            echo "Warning: $MATRIX_HOME/bin/$script not found"
            missing=1
        fi
    done
    
    if [ $missing -eq 1 ]; then
        echo ""
        echo "Please ensure all matrix tools are installed in: $MATRIX_HOME/bin"
        echo "Press any key to continue..."
        read -n 1
    fi
}

show_menu() {
    clear
    echo "╔════════════════════════════════════════╗"
    echo "║         MATRIX TOOLS MENU              ║"
    echo "╠════════════════════════════════════════╣"
    echo "║  1. Matrix Rain (Classic)              ║"
    echo "║  2. Matrix Stream (Wave Effect)        ║"
    echo "║  3. Matrix Burst (Explosion Effect)    ║"
    echo "║  4. Matrix Glitch (Digital Distortion) ║"
    echo "║  5. Run All (Cycle Through Effects)    ║"
    echo "║  6. Configure                          ║"
    echo "║  7. Exit                               ║"
    echo "╚════════════════════════════════════════╝"
    echo
    echo -n "Select option [1-7]: "
}

run_effect() {
    local effect=$1
    local effect_name=$2
    
    if [ ! -f "$effect" ]; then
        echo "Error: $effect_name not found at $effect"
        sleep 2
        return 1
    fi
    
    if [ ! -x "$effect" ]; then
        echo "Making $effect_name executable..."
        chmod +x "$effect"
    fi
    
    python3 "$effect" 2>/dev/null
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "Error: $effect_name exited with code $exit_code"
        sleep 2
        return 1
    fi
    
    return 0
}

run_all() {
    # Define effects with their display names and paths
    declare -a effects=(
        "$MATRIX_HOME/bin/mrain:Matrix Rain"
        "$MATRIX_HOME/bin/mstream:Matrix Stream"
        "$MATRIX_HOME/bin/mburst:Matrix Burst"
        "$MATRIX_HOME/bin/mglitch:Matrix Glitch"
    )
    
    for effect_entry in "${effects[@]}"; do
        effect_path="${effect_entry%:*}"
        effect_name="${effect_entry#*:}"
        
        echo "========================================="
        echo "Running: $effect_name"
        echo "Press Ctrl+C to skip to next effect"
        echo "========================================="
        sleep 2
        
        # Check if file exists before running
        if [ -f "$effect_path" ]; then
            # Run with timeout (30 seconds) if timeout command exists
            if command -v timeout &> /dev/null; then
                timeout --foreground 30s python3 "$effect_path" 2>/dev/null
            else
                # Fallback if timeout doesn't exist
                python3 "$effect_path" 2>/dev/null &
                local pid=$!
                sleep 30
                kill $pid 2>/dev/null
            fi
        else
            echo "Warning: $effect_name script not found at $effect_path"
            sleep 2
        fi
        
        clear
    done
    
    echo "All effects completed!"
    sleep 2
}

# Trap Ctrl+C to handle interruptions gracefully
trap 'echo ""; echo "Interrupted by user"; sleep 1; continue' INT

# Check requirements before starting
check_requirements

# Main menu loop
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1) run_effect "$MATRIX_HOME/bin/mrain" "Matrix Rain" ;;
        2) run_effect "$MATRIX_HOME/bin/mstream" "Matrix Stream" ;;
        3) run_effect "$MATRIX_HOME/bin/mburst" "Matrix Burst" ;;
        4) run_effect "$MATRIX_HOME/bin/mglitch" "Matrix Glitch" ;;
        5) run_all ;;
        6) 
            if [ -f "$MATRIX_HOME/config/matrix.conf" ]; then
                if command -v nano &> /dev/null; then
                    nano "$MATRIX_HOME/config/matrix.conf"
                elif command -v vim &> /dev/null; then
                    vim "$MATRIX_HOME/config/matrix.conf"
                else
                    echo "No text editor found (nano or vim)"
                    echo "Config file location: $MATRIX_HOME/config/matrix.conf"
                    sleep 3
                fi
            else
                echo "Config file not found. Creating template..."
                mkdir -p "$MATRIX_HOME/config"
                cat > "$MATRIX_HOME/config/matrix.conf" << 'EOF'
# Matrix Tools Configuration
# Created on $(date)

# Display settings
DEFAULT_COLOR=green
SPEED=normal
INTENSITY=high

# Effect durations (seconds)
RAIN_DURATION=30
STREAM_DURATION=30
BURST_DURATION=30
GLITCH_DURATION=30

# Customize your effects here
EOF
                echo "Template created at $MATRIX_HOME/config/matrix.conf"
                sleep 2
            fi
            ;;
        7) 
            echo "Exiting Matrix Tools... Goodbye!"
            exit 0 
            ;;
        *) 
            echo "Invalid option: $choice. Please select 1-7"
            sleep 1 
            ;;
    esac
done
