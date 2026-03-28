import random
import json
import os
from typing import List, Dict, Optional
class Colors:
    """ANSI color codes for enhanced terminal output."""
    HEADER = "\033[95m"
    BLUE = "\033[94m"  # X symbol
    RED = "\033[91m"  # O symbol
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"
    ERROR = "\033[41m"  # Red background for errors
    GOLD = "\033[93m"
SAVE_FILE = "saved_game.json"
SCORE_FILE = "score.json"
match_history: List[Dict] = []
total_score: Dict[str, int] = {}
resume_msgs = [
    "Maaan, you didn’t even start a game! Go play first 😎",
    "Hey, time traveler! No game to resume yet 🚀",
    "Oops! Nothing to resume… start a game first 🕹️"
]
number_error_msgs = [
    "Oops! That’s not a number… try 1–9 😉",
    "Wrong input! Please enter a number from 1 to 9 🧐",
    "Focus, friend! Only numbers 1-9 are allowed"
]
symbol_error_msgs = [
    "Please choose only X or O 😊",
    "That's not a valid symbol. Use X or O",
    "Only X and O are allowed, try again"
]
cell_taken_msgs = [
    "Haha, that cell is already taken! Pick another 🏃‍♂️",
    "Someone beat you to it! Try a free spot 🏁",
    "Nope, that cell's busy 😎"
]
victory_msgs = [
    "🎉 Whoa! Victory dance time!",
    "🏆 Champion! Bow down, mortal!"
]
tie_msgs = [
    "🤝 It's a tie! Everyone gets a cookie!",
    "😅 Stalemate! Better luck next round!"
]
play_again_msgs = [
    "Want to play another round?",
    "One more game?"
]
def load_score() -> Dict[str, int]:
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Error loading score:", e)
    return {}
def save_score() -> None:
    try:
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(total_score, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error saving score:", e)
def format_player_line(name: str, wins: int, leader: str | None, width: int) -> str:
    win_text = "win" if wins == 1 else "wins"
    text = f"{name} — {wins} {win_text}"
    if name == leader:
        text += "  (Leader)"
    line = text.ljust(width - 2)
    color = Colors.GOLD if name == leader else Colors.CYAN
    return f"{color}║ {line} ║{Colors.RESET}"
def print_score_table(p1_name: str, p2_name: str) -> None:
    p1_wins = total_score.get(p1_name, 0)
    p2_wins = total_score.get(p2_name, 0)
    leader = p1_name if p1_wins > p2_wins else p2_name if p2_wins > p1_wins else None
    def build_text(name, wins):
        win_text = "win" if wins == 1 else "wins"
        text = f"{name} — {wins} {win_text}"
        if name == leader:
            text += "  (Leader)"
        return text
    p1_text = build_text(p1_name, p1_wins)
    p2_text = build_text(p2_name, p2_wins)
    if p1_name == "Computer" or p2_name == "Computer":
        human = p1_name if p1_name != "Computer" else p2_name
        tie_key = f"Tie_{human}_vs_Computer"
    else:
        players = sorted([p1_name, p2_name])
        tie_key = f"Tie_{players[0]}_vs_{players[1]}"
    ties = total_score.get(tie_key, 0)
    ties_text = f"Ties — {ties}"
    content_width = max(
        len(p1_text),
        len(p2_text),
        len(ties_text),
        len(" SCOREBOARD ")
    )
    table_width = content_width + 2
    print(f"\n{Colors.CYAN}╔{'═' * table_width}╗{Colors.RESET}")
    print(f"{Colors.CYAN}║{' SCOREBOARD '.center(table_width)}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠{'═' * table_width}╣{Colors.RESET}")
    print(format_player_line(p1_name, p1_wins, leader, table_width))
    print(format_player_line(p2_name, p2_wins, leader, table_width))
    print(f"{Colors.YELLOW}║ {ties_text.ljust(table_width - 2)} ║{Colors.RESET}")
    print(f"{Colors.CYAN}╚{'═' * table_width}╝{Colors.RESET}")
HISTORY_FILE = "history.json"
def load_history() -> None:
    global match_history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                match_history = json.load(f)
        except Exception as e:
            print(f"{Colors.ERROR}Failed to load match history. File may be corrupted: {e}{Colors.RESET}")
            match_history = []
    else:
        match_history = []
def confirm_action(message: str) -> bool:
    confirm = input(f"{Colors.ERROR}{message}{Colors.RESET}").strip().upper()
    return confirm == "YES"
def get_menu_choice(prompt: str, valid_choices: tuple[str, ...]) -> str:
    while True:
        choice = input(f"{Colors.WHITE}{prompt}{Colors.RESET}").strip().lower()
        if choice == "esc":
            return "esc"
        if choice in valid_choices:
            return choice
        print(f"{Colors.ERROR}Invalid input. Allowed: {', '.join(valid_choices)}{Colors.RESET}")
def save_history() -> None:
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(match_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save history: {e}")
def reset_all_score() -> None:
    global total_score
    if confirm_action("Reset ALL-TIME SCORE? Type YES to confirm: "):
        total_score.clear()
        if os.path.exists(SCORE_FILE):
            os.remove(SCORE_FILE)
        print(f"{Colors.GREEN}✅ All-time score has been reset.{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Reset cancelled.{Colors.RESET}")
def clear_match_history() -> None:
    global match_history
    if confirm_action("Clear ALL match history? Type YES to confirm: "):
        match_history.clear()
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        print(f"{Colors.GREEN}✅ Match history has been cleared.{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Cancelled.{Colors.RESET}")
def reset_everything() -> None:
    global total_score, match_history
    if confirm_action("Reset EVERYTHING (score + history)? Type YES to confirm: "):
        total_score.clear()
        match_history.clear()
        for file in (SCORE_FILE, SAVE_FILE, HISTORY_FILE):
            if os.path.exists(file):
                os.remove(file)
        print(f"{Colors.GREEN}✅ Everything has been reset.{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Reset cancelled.{Colors.RESET}")
def reset_statistics_menu() -> None:
    while True:
        print(f"\n{Colors.YELLOW}Reset Statistics:{Colors.RESET}")
        print("1. Reset All-Time Score")
        print("2. Clear Match History")
        print("3. Reset Everything")
        print("4. Back to Main Menu")
        print("Type 'esc' to return")
        choice = get_menu_choice("Select (1-4): ", ("1", "2", "3", "4"))
        if choice == "esc" or choice == "4":
            return
        elif choice == "1":
            reset_all_score()
        elif choice == "2":
            clear_match_history()
        elif choice == "3":
            reset_everything()
def create_board() -> List[str]:
    return [str(i) for i in range(1, 10)]
def colorize_cell(cell: str) -> str:
    display = f" {cell} ".center(3)
    if cell == "X":
        return Colors.BLUE + display + Colors.RESET
    elif cell == "O":
        return Colors.RED + display + Colors.RESET
    return Colors.WHITE + display + Colors.RESET
def print_board(board: List[str]) -> None:
    print(f"{Colors.CYAN}\n╔═════╦═════╦═════╗{Colors.RESET}")
    for i in range(0, 9, 3):
        row = (
            f"{Colors.CYAN}║{Colors.RESET} {colorize_cell(board[i])} {Colors.CYAN}║{Colors.RESET} "
            f"{colorize_cell(board[i + 1])} {Colors.CYAN}║{Colors.RESET} {colorize_cell(board[i + 2])} {Colors.CYAN}║{Colors.RESET}"
        )
        print(row)
        if i < 6:
            print(f"{Colors.CYAN}╠═════╬═════╬═════╣{Colors.RESET}")
    print(f"{Colors.CYAN}╚═════╩═════╩═════╝{Colors.RESET}")
def check_winner(board: List[str], symbol: str) -> bool:
    win_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
        (0, 4, 8), (2, 4, 6)              # diagonals
    ]
    return any(all(board[i] == symbol for i in combo) for combo in win_combinations)
def is_tie(board: List[str]) -> bool:
    return all(cell in ("X", "O") for cell in board)
def switch_player(current: str) -> str:
    return "O" if current == "X" else "X"
def smart_computer_move(board: List[str], computer: str, player: str) -> int:
    for sym in (computer, player):
        for i in range(9):
            if board[i] not in ("X", "O"):
                board[i] = sym
                if check_winner(board, sym):
                    board[i] = str(i + 1)
                    return i + 1
                board[i] = str(i + 1)
    if board[4] not in ("X", "O"):
        return 5
    for i in (0, 2, 6, 8):
        if board[i] not in ("X", "O"):
            return i + 1
    for i in (1, 3, 5, 7):
        if board[i] not in ("X", "O"):
            return i + 1
    free = [i + 1 for i in range(9) if board[i] not in ("X", "O")]
    return random.choice(free)
def get_computer_move(board: List[str], computer_symbol: str, player_symbol: str, difficulty: int) -> int:
    free = [i + 1 for i in range(9) if board[i] not in ("X", "O")]
    if difficulty == 1:
        move = random.choice(free)
        level = "Easy"
    else:
        move = smart_computer_move(board, computer_symbol, player_symbol)
        level = "Medium"
    print(f"{Colors.YELLOW}Computer ({level}) chooses {move}{Colors.RESET}")
    return move
def get_move(player_name: str, board: List[str]) -> str | int:
    while True:
        inp = input(
            f"{Colors.WHITE}{player_name}, choose tile (1-9) or type 'esc': {Colors.RESET}"
        ).strip().lower()
        if inp == "esc":
            return "MENU"
        if not inp.isdigit():
            print(f"{Colors.ERROR}{random.choice(number_error_msgs)}{Colors.RESET}")
            continue
        move = int(inp)
        if move not in range(1, 10):
            print(f"{Colors.ERROR}{random.choice(number_error_msgs)}{Colors.RESET}")
            continue
        if board[move - 1] in ("X", "O"):
            print(f"{Colors.ERROR}{random.choice(cell_taken_msgs)}{Colors.RESET}")
            continue
        return move
def choose_symbol(player_name: str) -> str:
    while True:
        sym = input(
            f"{Colors.WHITE}{player_name}, choose your symbol (X/O): {Colors.RESET}"
        ).strip().upper()
        if sym in ("X", "O"):
            return sym
        print(f"{Colors.ERROR}{random.choice(symbol_error_msgs)}{Colors.RESET}")
def ask_play_again() -> bool:
    while True:
        ans = input(
            f"{Colors.CYAN}{random.choice(play_again_msgs)} (y/n): {Colors.RESET}"
        ).strip().lower()
        if ans in ("y", "yes",):
            return True
        if ans in ("n", "no", ):
            return False
        print(f"{Colors.ERROR}Please answer y or n.{Colors.RESET}")
def save_current_game(data: Dict) -> None:
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save game: {e}")
def load_saved_game() -> Optional[Dict]:
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load saved game: {e}")
        return None
def delete_saved_game() -> None:
    if not os.path.exists(SAVE_FILE):
        return
    try:
        os.remove(SAVE_FILE)
    except Exception as e:
        print(f"[ERROR] Failed to delete saved game: {e}")
def save_match(player1: str, player2: str, board: List[str], winner: str) -> None:
    match_history.append({
        "player1": player1,
        "player2": player2,
        "final_board": board[:],  # copy to avoid mutation
        "winner": winner
    })
    save_history()
    if player1 == "Computer" or player2 == "Computer":
        # Separate tie counter for each human vs computer
        human = player1 if player1 != "Computer" else player2
        tie_key = f"Tie_{human}_vs_Computer"
    else:
        players = sorted([player1, player2])
        tie_key = f"Tie_{players[0]}_vs_{players[1]}"
    if winner == "Tie":
        total_score[tie_key] = total_score.get(tie_key, 0) + 1
    else:
        total_score[winner] = total_score.get(winner, 0) + 1
    save_score()
def run_game_session(
    mode: str,
    board: List[str],
    current_symbol: str,
    p1_name: str,
    p2_name: str,
    player_symbols: Dict = None,
    player_symbol: str = None,
    computer_symbol: str = None,
    computer_difficulty: int = None
) -> None:
    def get_current_player_name() -> str:
        """Return the name of the current player."""
        if mode == "1":
            return player_symbols[current_symbol]
        return p1_name if current_symbol == player_symbol else p2_name
    while True:
        print_board(board)
        player_name = get_current_player_name()
        if mode == "1" or current_symbol == player_symbol:
            move = get_move(player_name, board)
        else:
            move = get_computer_move(board, computer_symbol, player_symbol, computer_difficulty)
        if move == "MENU":
            print(f"{Colors.YELLOW}⏪ Returning to Main Menu...{Colors.RESET}")
            save_current_game({
                "mode": mode,
                "board": board,
                "current_symbol": current_symbol,
                "player1_name": p1_name,
                "player2_name": p2_name,
                "player_symbols": player_symbols or {},
                "player_symbol": player_symbol,
                "computer_symbol": computer_symbol,
                "computer_difficulty": computer_difficulty
            })
            return
        board[move - 1] = current_symbol
        if check_winner(board, current_symbol):
            print_board(board)
            winner_name = get_current_player_name()
            print(f"{Colors.GREEN}🏆 {winner_name} wins! {random.choice(victory_msgs)}{Colors.RESET}")
            save_match(p1_name, p2_name, board, winner_name)
            delete_saved_game()
            print_score_table(p1_name, p2_name)
            if not ask_play_again():
                return
            board = create_board()
            current_symbol = "X"
            continue
        if is_tie(board):
            print_board(board)
            print(f"{Colors.YELLOW}🤝 It's a tie! {random.choice(tie_msgs)}{Colors.RESET}")
            save_match(p1_name, p2_name, board, "Tie")
            delete_saved_game()
            print_score_table(p1_name, p2_name)
            if not ask_play_again():
                return
            board = create_board()
            current_symbol = "X"
            continue
        current_symbol = switch_player(current_symbol)
def main_menu() -> str:
    print(f"{Colors.CYAN}\n🎮 Tic Tac Toe — Main Menu{Colors.RESET}")
    print(f"{Colors.BLUE}1. Two Players")
    print(f"{Colors.YELLOW}2. Player vs Computer")
    print(f"{Colors.GREEN}3. Resume Last Game")
    print(f"{Colors.WHITE}4. Show Match History")
    print(f"{Colors.RED}5. Reset Statistics...{Colors.RESET}")
    print(f"{Colors.RED}6. Exit{Colors.RESET}")
    if total_score:
        print(f"\n{Colors.YELLOW}All-time wins:{Colors.RESET}")
        for player, wins in sorted(total_score.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {player}: {wins} wins")
    while True:
        choice = input(f"{Colors.WHITE}Select (1-6) or type 'esc': {Colors.RESET}").strip().lower()
        if choice == "esc":
            return "6"  # treat as exit
        if choice in ("1", "2", "3", "4", "5", "6"):
            return choice
        print(f"{Colors.ERROR}{random.choice(number_error_msgs)}{Colors.RESET}")
def get_computer_difficulty() -> int:
    while True:
        inp = input(f"{Colors.WHITE}Difficulty (1=Easy, 2=Medium): {Colors.RESET}").strip()
        if inp in ("1", "2"):
            return int(inp)
        print(f"{Colors.ERROR}{random.choice(number_error_msgs)}{Colors.RESET}")
def start_new_game(mode: str) -> None:
    if mode == "1":
        p1_name = input("Player 1 name: ").strip() or "Player 1"
        p2_name = input("Player 2 name: ").strip() or "Player 2"
        p1_symbol = choose_symbol(p1_name)
        p2_symbol = "O" if p1_symbol == "X" else "X"
        player_symbols = {p1_symbol: p1_name, p2_symbol: p2_name}
        player_symbol = None
        computer_symbol = None
        computer_difficulty = None
    else:
        p1_name = input("Your name: ").strip() or "You"
        player_symbol = choose_symbol(p1_name)
        computer_symbol = "O" if player_symbol == "X" else "X"
        computer_difficulty = get_computer_difficulty()
        player_symbols = None
        p2_name = "Computer"
    for name in (p1_name, p2_name):
        if name not in total_score:
            total_score[name] = 0
    board = create_board()
    current_symbol = "X"
    print(f"\n{Colors.GREEN}Starting new game: {p1_name} vs {p2_name}{Colors.RESET}")
    run_game_session(mode, board, current_symbol, p1_name, p2_name,
                     player_symbols, player_symbol, computer_symbol, computer_difficulty)
def resume_game(saved: Dict) -> None:
    print(f"{Colors.GREEN}✅ Resuming game: {saved['player1_name']} vs {saved['player2_name']}{Colors.RESET}")
    mode = saved["mode"]
    board = saved.get("board", create_board())
    current_symbol = saved.get("current_symbol", "X")
    p1_name = saved["player1_name"]
    p2_name = saved["player2_name"]
    player_symbols = saved.get("player_symbols", {})
    player_symbol = saved.get("player_symbol")
    computer_symbol = saved.get("computer_symbol")
    computer_difficulty = saved.get("computer_difficulty", 2)
    for name in (p1_name, p2_name):
        if name not in total_score:
            total_score[name] = 0
    run_game_session(mode, board, current_symbol, p1_name, p2_name,
                     player_symbols, player_symbol, computer_symbol, computer_difficulty)
def show_history() -> None:
    if not match_history:
        print(f"{Colors.YELLOW}📂 No previous matches yet.{Colors.RESET}")
        return
    print(f"{Colors.CYAN}\n📂 Match History:{Colors.RESET}")
    for idx, match in enumerate(match_history, 1):
        print(
            f"{Colors.HEADER}{idx}. {match['player1']} vs {match['player2']} → Winner: {match['winner']}{Colors.RESET}")
        print_board(match['final_board'])
        print("-" * 40)
def play_game() -> None:
    global total_score
    total_score = load_score()
    load_history()
    while True:
        mode = main_menu()
        if mode == "6":
            print(f"{Colors.CYAN}👋 Goodbye! Thanks for playing.{Colors.RESET}")
            break
        if mode == "4":
            show_history()
            continue
        if mode == "5":
            reset_statistics_menu()
            continue
        if mode == "3":
            saved = load_saved_game()
            if saved:
                resume_game(saved)
            else:
                print(f"{Colors.YELLOW}{random.choice(resume_msgs)}{Colors.RESET}")
            continue
        start_new_game(mode)
if __name__ == "__main__":
    try:
        play_game()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Game interrupted. Goodbye!{Colors.RESET}")