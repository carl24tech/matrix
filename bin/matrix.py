#!/bin/bash
# Matrix Tools Wrapper
# Location: ~/matrix-tools/bin/matrix

MATRIX_HOME="$HOME/matrix-tools"

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

run_all() {
    effects=("$MATRIX_HOME/bin/mrain" "$MATRIX_HOME/bin/mstream" "$MATRIX_HOME/bin/mburst" "$MATRIX_HOME/bin/mglitch")
    
    for effect in "${effects[@]}"; do
        echo "Running $(basename $effect)... Press Ctrl+C to skip to next effect"
        sleep 2
        timeout --foreground 30s python3 "$effect" 2>/dev/null
        clear
    done
}

# Main menu loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1) python3 "$MATRIX_HOME/bin/mrain" ;;
        2) python3 "$MATRIX_HOME/bin/mstream" ;;
        3) python3 "$MATRIX_HOME/bin/mburst" ;;
        4) python3 "$MATRIX_HOME/bin/mglitch" ;;
        5) run_all ;;
        6) nano "$MATRIX_HOME/config/matrix.conf" ;;
        7) echo "Exiting Matrix Tools..."; exit 0 ;;
        *) echo "Invalid option"; sleep 1 ;;
    esac
done
