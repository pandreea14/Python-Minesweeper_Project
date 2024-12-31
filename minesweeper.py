import tkinter as tk
import random
from collections import deque


class Minesweeper:
    def __init__(self, master, rows=10, cols=10, mines=15, time_limit=100):
        """Initializarea variabilelor jocului + UI
        Args:
            master (tk.Tk): Tkinter window root
            rows (int): nr de randuri
            cols (int): nr de coloane
            mines (int): nr de bombe
            time_limit (int): timpul pt terminarea jocului
        """
        self.master = master
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.time_limit = time_limit
        self.remaining_time = time_limit
        self.buttons = []
        self.board = []
        self.game_active = True
        self.mark_flag = False
        self.timeout = False
        self.setup_game()

    def setup_game(self):
        """Pregatirea tablei de joc - o matrice"""
        self.initialize_board()
        self.place_mines()
        self.create_ui()

    def initialize_board(self):
        """Intai adaug zero-uri in locuri random pe tabla de joc"""
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def place_mines(self):
        """Adaug bombe aleatoriu pe tabla si incrementez casutele adiacente"""
        mines_placed = 0
        while mines_placed < self.mines:
            row, col = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
            if self.board[row][col] != -1:
                self.board[row][col] = -1
                mines_placed += 1
                self.increment_adjacent_cells(row, col)

    def increment_adjacent_cells(self, row, col):
        """Incrementarea casutelor adiacente bombelor
        Args:
            row (int): indexul liniei la care este bomba
            col (int): indexul coloanei la care e bomba
        """
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r, c = row + dr, col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] != -1:
                    self.board[r][c] += 1

    def toggle_mark_flag(self):
        """Apasarea butonului de setat bombe te tabla de joc"""
        self.mark_flag = not self.mark_flag
        self.mark_button.config(
            bg="#7a0f18" if self.mark_flag else "pink",
            fg="white" if self.mark_flag else "black"
        )

    def handle_click(self, row, col):
        """gestionarea click-urilor pe celule
        Args:
            row (int): indexul liniei unde s-a facut click
            col (int): indexul coloanei unde s-a facut click
        """
        if not self.game_active:
            return

        if self.mark_flag:
            if self.buttons[row][col]["text"] == "B":
                self.buttons[row][col].config(text="", bg="SystemButtonFace")
            else:
                self.buttons[row][col].config(text="B", bg="#7a0f18", fg="white")
        else:
            if self.buttons[row][col]["text"] != "B":
                self.reveal_cell(row, col)

    def create_ui(self):
        """UI-ul jocului si scroll pentru nr mare de linii si coloane"""
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        window_width = min(self.cols * 50, screen_width - 100)
        window_height = min(self.rows * 50 + 100, screen_height - 100)
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.master.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.master.resizable(True, True)

        canvas = tk.Canvas(self.master)
        canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        v_scroll = tk.Scrollbar(self.master, orient=tk.VERTICAL, command=canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll = tk.Scrollbar(self.master, orient=tk.HORIZONTAL, command=canvas.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        canvas.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        self.timer_label = tk.Label(frame, text=f"Time: {self.remaining_time} s", font=("Arial", 14))
        self.timer_label.grid(row=0, column=0, columnspan=self.cols, pady=10)

        self.mark_button = tk.Button(
            frame, text="Bomb (B)", bg="pink", command=self.toggle_mark_flag
        )
        self.mark_button.grid(row=0, column=5, columnspan=self.cols, pady=10)

        for row in range(self.rows):
            button_row = []
            for col in range(self.cols):
                button = tk.Button(
                    frame, text="", width=3, height=1,
                    command=lambda r=row, c=col: self.handle_click(r, c), font=("Arial", 12)
                )
                button.grid(row=row + 3, column=col, padx=1, pady=1)
                button_row.append(button)
            self.buttons.append(button_row)

        self.update_timer()

    def update_timer(self):
        """Update la timer si gestionarea cazului cand expira timpul"""
        if self.remaining_time > 0 and self.game_active:
            self.timer_label.config(text=f"Time: {self.remaining_time} s")
            self.remaining_time -= 1
            self.master.after(1000, self.update_timer)
        elif self.remaining_time == 0:
            self.game_active = False
            self.end_game(victory=False, timeout=True)

    def reveal_cell(self, row, col):
        """Dezvaluirea unei celule
        Args:
            row (int): indexul liniei unde s-a facut click
            col (int): indexul coloanei unde s-a facut click
        """
        if not self.game_active or self.buttons[row][col]["text"] == "B":
            return

        if self.board[row][col] == -1:
            self.buttons[row][col].config(text="X.X", bg="red", fg="black")
            self.end_game(False)
        else:
            self.uncover_cells(row, col)
            if self.check_victory():
                self.end_game(True)


if __name__ == "__main__":
    def start_game():
        rows, cols, mines, time_limit = (
            int(rows_entry.get()),
            int(cols_entry.get()),
            int(mines_entry.get()),
            int(time_entry.get())
        )
        game_window = tk.Toplevel(root)
        game_window.title("Minesweeper")
        Minesweeper(game_window, rows, cols, mines, time_limit)

    root = tk.Tk()
    root.title("Settings")
    root.resizable(False, False)

    frame = tk.Frame(root, bg="#d49fc3")
    frame.pack(padx=20, pady=10)

    tk.Label(
        frame, text="Minesweeper Game Setup", bg="pink", font=("Arial", 15)
    ).grid(row=0, column=0, columnspan=2, pady=20)

    for idx, text in enumerate(["Rows:", "Columns:", "Mines:", "Time Limit (s):"]):
        tk.Label(
            frame, text=text, bg="#d49fc3", font=("Arial", 12)
        ).grid(row=idx + 1, column=0, pady=5, padx=10)

    rows_entry, cols_entry, mines_entry, time_entry = (tk.Entry(frame) for _ in range(4))
    for idx, entry, default in zip(range(4), [rows_entry, cols_entry, mines_entry, time_entry], ["10", "10", "15", "100"]):
        entry.grid(row=idx + 1, column=1, pady=5, padx=10)
        entry.insert(0, default)

    tk.Button(
        frame, text="Start Game", font=("Arial", 15), fg="black", bg="#d49fc3",
        activebackground="pink", command=start_game
    ).grid(row=5, column=0, columnspan=2, pady=20)

    root.mainloop()