import random
import time
import os
import sys

GREEN = '\033[32m'
DARK_GREEN = '\033[2;32m'
RESET = '\033[0m'
BOLD = '\033[1m'

CHARS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝ012345789ABCDEF"

def clear_screen():
    os.system('clear')

def get_terminal_size():
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except:
        return 80, 24

def matrix_effect():
    clear_screen()
    
    try:
        cols, rows = get_terminal_size()
    except:
        cols, rows = 80, 24
    
    columns = [random.randint(1, rows-1) for _ in range(cols)]
    speeds = [random.uniform(0.05, 0.3) for _ in range(cols)]
    lengths = [random.randint(3, 12) for _ in range(cols)]
    counters = [0 for _ in range(cols)]
    
    sys.stdout.write(f"{GREEN}{BOLD}")
    sys.stdout.flush()
    
    while True:
        for i in range(cols):
            if counters[i] <= 0:
                columns[i] = random.randint(1, rows-1)
                lengths[i] = random.randint(3, 15)
                speeds[i] = random.uniform(0.03, 0.2)
                counters[i] = lengths[i] * 2
            
            for j in range(rows):
                sys.stdout.write(f"\033[{j+1};{i+1}H")
                
                if j == columns[i]:
                    sys.stdout.write(f"{BOLD}{GREEN}{random.choice(CHARS)}{RESET}")
                elif j < columns[i] and j > columns[i] - lengths[i]:
                    brightness = (columns[i] - j) / lengths[i]
                    char = random.choice(CHARS)
                    if brightness > 0.6:
                        sys.stdout.write(f"{GREEN}{char}{RESET}")
                    elif brightness > 0.3:
                        sys.stdout.write(f"{DARK_GREEN}{char}{RESET}")
                    else:
                        sys.stdout.write(f"{DARK_GREEN}{char}{RESET}")
                elif j < columns[i] and j > columns[i] - 2:
                    if random.random() < 0.01:
                        sys.stdout.write(f"{BOLD}{GREEN}{random.choice(CHARS)}{RESET}")
                    else:
                        sys.stdout.write(" ")
                else:
                    sys.stdout.write(" ")
            
            columns[i] += 1
            counters[i] -= 1
            
            if columns[i] > rows + lengths[i]:
                columns[i] = 0
                counters[i] = 0
            
            time.sleep(speeds[i] / cols)
        
        sys.stdout.flush()

def main_menu():
    clear_screen()
    
    title = f"""
{GREEN}{BOLD}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                         MATRIX TOOL                          ║
║                                                              ║
║                    ╔═══════════════════╗                     ║
║                    ║  1. Start Matrix  ║                     ║
║                    ║  2. Exit          ║                     ║
║                    ╚═══════════════════╝                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{RESET}
"""
    
    print(title)
    
    while True:
        choice = input(f"{GREEN}>> {RESET}")
        if choice == "1":
            try:
                matrix_effect()
            except KeyboardInterrupt:
                clear_screen()
                print(f"{GREEN}Exited Matrix...{RESET}")
                sys.exit(0)
        elif choice == "2":
            clear_screen()
            print(f"{GREEN}Goodbye.{RESET}")
            sys.exit(0)

if __name__ == "__main__":
    main_menu()
