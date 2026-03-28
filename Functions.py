"""
Tic Tac Toe Game — Terminal Version

A fully featured console-based Tic Tac Toe game with the following features:
- Two-player mode (hotseat)
- Player vs Computer with Easy and Medium difficulty
- Save and resume unfinished games
- Persistent all-time score across multiple launches
- Beautiful and stable scoreboard
- Match history
- Reset statistics submenu with confirmation
- Return to main menu by typing 'esc'
"""

import random
import json
import os
from typing import List, Dict, Optional


# ====================== COLORS ======================
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

# ====================== MESSAGES ======================
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


# ====================== SCORE SYSTEM ======================
def load_score() -> Dict[str, int]:
    """Load persistent all-time score from file."""
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Error loading score:", e)
    return {}


def save_score() -> None:
    """Save all-time score to file."""
    try:
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(total_score, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error saving score:", e)


def format_player_line(name: str, wins: int, leader: str | None, width: int) -> str:
    """
    Format a single player's line for the scoreboard.

    Adds win count, handles singular/plural form, highlights the leader,
    and aligns the text within the given table width.

    Args:
        name (str): Player name.
        wins (int): Number of wins.
        leader (str | None): Name of the current leader, or None if tied.
        width (int): Total width of the table.

    Returns:
        str: Formatted string ready to be printed.
    """
    win_text = "win" if wins == 1 else "wins"
    text = f"{name} — {wins} {win_text}"

    if name == leader:
        text += "  (Leader)"

    line = text.ljust(width - 2)
    color = Colors.GOLD if name == leader else Colors.CYAN

    return f"{color}║ {line} ║{Colors.RESET}"


def print_score_table(p1_name: str, p2_name: str) -> None:
    """
    Display a dynamic scoreboard for two players, including wins and ties.

    The table automatically adjusts its width based on the longest content
    (player names, scores, ties, and header), ensuring proper alignment
    even with long player names.

    The scoreboard includes:
    - Wins for each player
    - Leader indication (player with more wins)
    - Number of ties between the two players

    Args:
        p1_name (str): Name of the first player.
        p2_name (str): Name of the second player.

    Returns:
        None
    """
    p1_wins = total_score.get(p1_name, 0)
    p2_wins = total_score.get(p2_name, 0)

    leader = p1_name if p1_wins > p2_wins else p2_name if p2_wins > p1_wins else None

    def build_text(name, wins):
        """
        Build formatted text for a player's score line.

        Args:
            name (str): Player name.
            wins (int): Number of wins.

        Returns:
            str: Formatted score string.
        """
        win_text = "win" if wins == 1 else "wins"
        text = f"{name} — {wins} {win_text}"
        if name == leader:
            text += "  (Leader)"
        return text

    p1_text = build_text(p1_name, p1_wins)
    p2_text = build_text(p2_name, p2_wins)

    # Generate tie key for this specific pair of players
    if p1_name == "Computer" or p2_name == "Computer":
        human = p1_name if p1_name != "Computer" else p2_name
        tie_key = f"Tie_{human}_vs_Computer"
    else:
        players = sorted([p1_name, p2_name])
        tie_key = f"Tie_{players[0]}_vs_{players[1]}"
    ties = total_score.get(tie_key, 0)
    ties_text = f"Ties — {ties}"

    # Calculate table width dynamically
    content_width = max(
        len(p1_text),
        len(p2_text),
        len(ties_text),
        len(" SCOREBOARD ")
    )

    table_width = content_width + 2

    # Draw table
    print(f"\n{Colors.CYAN}╔{'═' * table_width}╗{Colors.RESET}")
    print(f"{Colors.CYAN}║{' SCOREBOARD '.center(table_width)}║{Colors.RESET}")
    print(f"{Colors.CYAN}╠{'═' * table_width}╣{Colors.RESET}")

    print(format_player_line(p1_name, p1_wins, leader, table_width))
    print(format_player_line(p2_name, p2_wins, leader, table_width))

    # Display ties
    print(f"{Colors.YELLOW}║ {ties_text.ljust(table_width - 2)} ║{Colors.RESET}")

    print(f"{Colors.CYAN}╚{'═' * table_width}╝{Colors.RESET}")


HISTORY_FILE = "history.json"

def load_history() -> None:
    """
    Load match history from file into memory.

    Reads saved match data from HISTORY_FILE and populates
    the global match_history list.

    If the file does not exist or is corrupted, initializes
    an empty history.

    Returns:
        None
    """
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
# ====================== RESET FUNCTIONS ======================
def confirm_action(message: str) -> bool:
    """
    Ask user for confirmation before performing a critical action.

    Args:
        message (str): Confirmation message.

    Returns:
        bool: True if user types 'YES', otherwise False.
    """
    confirm = input(f"{Colors.ERROR}{message}{Colors.RESET}").strip().upper()
    return confirm == "YES"


def get_menu_choice(prompt: str, valid_choices: tuple[str, ...]) -> str:
    """
    Get validated user input from a set of allowed choices.

    Args:
        prompt (str): Input message.
        valid_choices (tuple): Allowed values.

    Returns:
        str: Valid user choice or 'esc' if user wants to exit.
    """
    while True:
        choice = input(f"{Colors.WHITE}{prompt}{Colors.RESET}").strip().lower()

        if choice == "esc":
            return "esc"

        if choice in valid_choices:
            return choice

        print(f"{Colors.ERROR}Invalid input. Allowed: {', '.join(valid_choices)}{Colors.RESET}")


def save_history() -> None:
    """
    Save match history to a JSON file.
    """
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(match_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save history: {e}")



def reset_all_score() -> None:
    """
    Reset all-time wins score with confirmation.
    """
    global total_score

    if confirm_action("Reset ALL-TIME SCORE? Type YES to confirm: "):
        total_score.clear()

        if os.path.exists(SCORE_FILE):
            os.remove(SCORE_FILE)

        print(f"{Colors.GREEN}✅ All-time score has been reset.{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Reset cancelled.{Colors.RESET}")


def clear_match_history() -> None:
    """
    Clear match history with confirmation.
    """
    global match_history

    if confirm_action("Clear ALL match history? Type YES to confirm: "):
        match_history.clear()

        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)

        print(f"{Colors.GREEN}✅ Match history has been cleared.{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Cancelled.{Colors.RESET}")


def reset_everything() -> None:
    """
    Reset all game data including score, history, and saved game.
    """
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
    """
    Display submenu for resetting game statistics.
    Supports 'esc' to return to main menu.
    """
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

# ====================== CORE GAME FUNCTIONS ======================

def create_board() -> List[str]:
    """
    Create a new 3x3 Tic Tac Toe board.

    Returns:
        List[str]: List of strings from '1' to '9'.
    """
    return [str(i) for i in range(1, 10)]


def colorize_cell(cell: str) -> str:
    """
    Apply color formatting to a board cell.

    Args:
        cell (str): Cell value ('X', 'O', or number).

    Returns:
        str: Colored string for terminal output.
    """
    display = f" {cell} ".center(3)

    if cell == "X":
        return Colors.BLUE + display + Colors.RESET
    elif cell == "O":
        return Colors.RED + display + Colors.RESET

    return Colors.WHITE + display + Colors.RESET


def print_board(board: List[str]) -> None:
    """
    Print the Tic Tac Toe board with colors and borders.

    Args:
        board (List[str]): Current game board.
    """
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
    """
    Check if the given symbol has a winning combination.

    Args:
        board (List[str]): Current board.
        symbol (str): Player symbol ('X' or 'O').

    Returns:
        bool: True if player has won, else False.
    """
    win_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
        (0, 4, 8), (2, 4, 6)              # diagonals
    ]

    return any(all(board[i] == symbol for i in combo) for combo in win_combinations)


def is_tie(board: List[str]) -> bool:
    """
    Check if the game is a tie (board is full).

    Args:
        board (List[str]): Current board.

    Returns:
        bool: True if tie, else False.
    """
    return all(cell in ("X", "O") for cell in board)


def switch_player(current: str) -> str:
    """
    Switch player symbol.

    Args:
        current (str): Current symbol.

    Returns:
        str: Opposite symbol.
    """
    return "O" if current == "X" else "X"


def smart_computer_move(board: List[str], computer: str, player: str) -> int:
    """
    Medium difficulty AI.

    Strategy:
    1. Win if possible
    2. Block opponent
    3. Take center
    4. Take corners
    5. Take sides

    Returns:
        int: Chosen move (1-9).
    """
    # Try win or block
    for sym in (computer, player):
        for i in range(9):
            if board[i] not in ("X", "O"):
                board[i] = sym

                if check_winner(board, sym):
                    board[i] = str(i + 1)
                    return i + 1

                board[i] = str(i + 1)

    # Center
    if board[4] not in ("X", "O"):
        return 5

    # Corners
    for i in (0, 2, 6, 8):
        if board[i] not in ("X", "O"):
            return i + 1

    # Sides
    for i in (1, 3, 5, 7):
        if board[i] not in ("X", "O"):
            return i + 1

    # Random fallback
    free = [i + 1 for i in range(9) if board[i] not in ("X", "O")]
    return random.choice(free)


def get_computer_move(board: List[str], computer_symbol: str, player_symbol: str, difficulty: int) -> int:
    """
    Get computer move based on difficulty.

    Args:
        difficulty (int): 1 = Easy, 2 = Medium

    Returns:
        int: Move (1-9)
    """
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
    """
    Get player move or return 'MENU' if user exits.

    Args:
        player_name (str): Player name.

    Returns:
        int | str: Move (1-9) or 'MENU'
    """
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
    """
    Let player choose X or O.

    Args:
        player_name (str): Player name.

    Returns:
        str: 'X' or 'O'
    """
    while True:
        sym = input(
            f"{Colors.WHITE}{player_name}, choose your symbol (X/O): {Colors.RESET}"
        ).strip().upper()

        if sym in ("X", "O"):
            return sym

        print(f"{Colors.ERROR}{random.choice(symbol_error_msgs)}{Colors.RESET}")


def ask_play_again() -> bool:
    """
    Ask if players want to continue.

    Returns:
        bool: True if yes, False if no.
    """
    while True:
        ans = input(
            f"{Colors.CYAN}{random.choice(play_again_msgs)} (y/n): {Colors.RESET}"
        ).strip().lower()

        if ans in ("y", "yes", "да", "д"):
            return True
        if ans in ("n", "no", "нет", "н"):
            return False

        print(f"{Colors.ERROR}Please answer y or n.{Colors.RESET}")

# ====================== SAVE / LOAD ======================

def save_current_game(data: Dict) -> None:
    """
    Save current game state to a file.

    Args:
        data (Dict): Game state data to save.
    """
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save game: {e}")


def load_saved_game() -> Optional[Dict]:
    """
    Load saved game from file if it exists.

    Returns:
        Optional[Dict]: Loaded game data or None if not available.
    """
    if not os.path.exists(SAVE_FILE):
        return None

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load saved game: {e}")
        return None


def delete_saved_game() -> None:
    """
    Delete saved game file if it exists.
    """
    if not os.path.exists(SAVE_FILE):
        return

    try:
        os.remove(SAVE_FILE)
    except Exception as e:
        print(f"[ERROR] Failed to delete saved game: {e}")


def save_match(player1: str, player2: str, board: List[str], winner: str) -> None:
    """
    Save completed match and update all-time score.

    Args:
        player1 (str): First player name.
        player2 (str): Second player name.
        board (List[str]): Final board state.
        winner (str): Winner name or "Tie".
    """
    match_history.append({
        "player1": player1,
        "player2": player2,
        "final_board": board[:],  # copy to avoid mutation
        "winner": winner
    })

    # Save history immediately
    save_history()

    # Unique key for ties between specific players
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

# ====================== GAME SESSION ======================
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
    """
     Run the main game session loop.

    This function handles the full gameplay cycle:
    - rendering the board
    - processing player and computer moves
    - detecting wins and ties
    - saving and resuming games
    - updating scores and match history

    Supports both:
    - Two-player mode
    - Player vs Computer mode

    Args:
        mode (str): Game mode ("1" for two players, "2" for vs computer).
        board (List[str]): Current board state.
        current_symbol (str): Current player's symbol ("X" or "O").
        p1_name (str): Player 1 name.
        p2_name (str): Player 2 name (or "Computer").
        player_symbols (Optional[Dict]): Mapping of symbols to player names (for PvP).
        player_symbol (Optional[str]): Player's symbol (for PvC).
        computer_symbol (Optional[str]): Computer's symbol.
        computer_difficulty (Optional[int]): Difficulty level (1=Easy, 2=Medium).

    Returns:
        None
    """

    def get_current_player_name() -> str:
        """Return the name of the current player."""
        if mode == "1":
            return player_symbols[current_symbol]
        return p1_name if current_symbol == player_symbol else p2_name

    while True:
        print_board(board)

        player_name = get_current_player_name()

        # Get move
        if mode == "1" or current_symbol == player_symbol:
            move = get_move(player_name, board)
        else:
            move = get_computer_move(board, computer_symbol, player_symbol, computer_difficulty)

        # Exit to menu
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

        # Apply move
        board[move - 1] = current_symbol

        # Check win
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

        # Check tie
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

        # Next turn
        current_symbol = switch_player(current_symbol)

# ====================== MENU ======================

def main_menu() -> str:
    """
    Display the main menu and return the user's choice.

    Shows available game modes and options, including:
    - starting a new game
    - resuming a saved game
    - viewing match history
    - resetting statistics
    - exiting the program

    Also displays top players based on all-time wins.

    Returns:
        str: Selected menu option ("1"-"6").
    """
    print(f"{Colors.CYAN}\n🎮 Tic Tac Toe — Main Menu{Colors.RESET}")
    print(f"{Colors.BLUE}1. Two Players")
    print(f"{Colors.YELLOW}2. Player vs Computer")
    print(f"{Colors.GREEN}3. Resume Last Game")
    print(f"{Colors.WHITE}4. Show Match History")
    print(f"{Colors.RED}5. Reset Statistics...{Colors.RESET}")
    print(f"{Colors.RED}6. Exit{Colors.RESET}")

    # Show top players
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
    """
    Prompt user to select computer difficulty level.

    Available levels:
    - 1: Easy (random moves)
    - 2: Medium (basic strategy)

    Returns:
        int: Selected difficulty 1 (Easy) or 2 (Medium).
    """
    while True:
        inp = input(f"{Colors.WHITE}Difficulty (1=Easy, 2=Medium): {Colors.RESET}").strip()

        if inp in ("1", "2"):
            return int(inp)

        print(f"{Colors.ERROR}{random.choice(number_error_msgs)}{Colors.RESET}")


# ====================== GAME MODES ======================
def start_new_game(mode: str) -> None:
    """
    Initialize and start a new game session.

    Depending on the selected mode:
    - "1": Two-player mode (hotseat)
    - "2": Player vs Computer mode

    Handles:
    - player name input
    - symbol selection (X/O)
    - computer difficulty selection (if applicable)
    - initialization of game state (board, current player)
    - ensuring players exist in the score system

    Args:
        mode (str): Game mode ("1" for PvP, "2" for PvC).

    Returns:
        None
    """
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
    """
    Resume a previously saved game session.

    Restores game state from saved data, including:
    - board configuration
    - current player's turn
    - player names and symbols
    - computer settings (if applicable)

    Also ensures players exist in the score system.

    Args:
        saved (Dict): Dictionary containing saved game data.

    Returns:
        None
    """
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
    """
    Display match history in the terminal.

    Shows all previously played matches, including:
    - player names
    - winner (or tie)
    - final board state for each match

    If no matches are available, displays a placeholder message.

    Returns:
        None
    """
    if not match_history:
        print(f"{Colors.YELLOW}📂 No previous matches yet.{Colors.RESET}")
        return
    print(f"{Colors.CYAN}\n📂 Match History:{Colors.RESET}")
    for idx, match in enumerate(match_history, 1):
        print(
            f"{Colors.HEADER}{idx}. {match['player1']} vs {match['player2']} → Winner: {match['winner']}{Colors.RESET}")
        print_board(match['final_board'])
        print("-" * 40)


# ====================== MAIN ======================

def play_game() -> None:
    """
    Run the main application loop.

    This is the entry point of the program. It:
    - loads persistent data (scores and optionally history)
    - displays the main menu
    - routes user actions to corresponding features
    - handles game start, resume, statistics, and exit

    Menu options:
        "1", "2" → start a new game
        "3"      → resume saved game
        "4"      → show match history
        "5"      → reset statistics
        "6"      → exit application

    The loop continues until the user chooses to exit.

    Returns:
        None
    """
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