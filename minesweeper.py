import tkinter as tk
import random
from collections import deque


class Minesweeper:
    def __init__(self, master, rows=10, cols=10, mines=15, time_limit=100):
        """
        :param master (tk.Tk): Tkinter window root
        :param rows (int): nr de randuri
        :param cols (int): nr de coloane
        :param mines (int): nr de bombe
        :param time_limit (int): timpul pt terminarea jocului
        :return: Initializarea variabilelor jocului + apelarea UI-ului
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
        """
        :return: Pregatirea tablei de joc - o matrice
        """
        self.initialize_board()
        self.place_mines()
        self.create_ui()

    def initialize_board(self):
        """
        :return: Intai adaug zero-uri in locuri random pe tabla de joc
        """
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def place_mines(self):
        """
        :return: Adaug bombe aleatoriu pe tabla si incrementez casutele adiacente
        """
        mines_placed = 0
        while mines_placed < self.mines:
            row, col = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
            if self.board[row][col] != -1:
                self.board[row][col] = -1
                mines_placed += 1
                self.increment_adjacent_cells(row, col)

    def increment_adjacent_cells(self, row, col):
        """
        :param row (int): indexul liniei la care este bomba
        :param col (int): indexul coloanei la care e bomba
        :return: Incrementarea casutelor adiacente bombelor
        """
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r, c = row + dr, col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] != -1:
                    self.board[r][c] += 1

    def toggle_mark_flag(self):
        """
        :return: Apasarea butonului de setat bombe te tabla de joc
        """
        self.mark_flag = not self.mark_flag
        self.mark_button.config(
            bg="#7a0f18" if self.mark_flag else "pink",
            fg="white" if self.mark_flag else "black"
        )

    def handle_click(self, row, col):
        """
        :param row (int): indexul liniei unde s-a facut click
        :param col (int): indexul coloanei unde s-a facut click
        :return: gestionarea click-urilor pe celule
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
       screen_width = self.master.winfo_screenwidth()
       screen_height = self.master.winfo_screenheight()

       max_cols = 30
       max_rows = 20
       self.rows = min(self.rows, max_rows)
       self.cols = min(self.cols, max_cols)
       max_board_width = screen_width - 100
       max_board_height = screen_height - 100
       max_cell_size_width = max_board_width // self.cols
       max_cell_size_height = max_board_height // self.rows
       cell_size = min(50, max_cell_size_width, max_cell_size_height)

       window_width = self.cols * cell_size + 100
       window_height = self.rows * cell_size + 100
       x_position = (screen_width - window_width) // 2
       y_position = (screen_height - window_height) // 2

       self.master.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
       self.master.resizable(False, False)

       frame = tk.Frame(self.master, bg="white")
       frame.pack(fill=tk.BOTH, expand=True)

       self.timer_label = tk.Label(frame, text=f"Time: {self.remaining_time} s", font=("Arial", 14))
       self.timer_label.pack(pady=10)

       self.mark_button = tk.Button(
           frame, text="Bomb (B)", bg="pink", command=self.toggle_mark_flag
       )
       self.mark_button.pack(pady=10)

       board_frame = tk.Frame(frame, bg="lightgray")
       board_frame.pack(pady=10)

       self.buttons = []
       for row in range(self.rows):
           button_row = []
           for col in range(self.cols):
               button = tk.Button(
                   board_frame,
                   text="",
                   width=cell_size // 10,
                   height=cell_size // 20,
                   font=("Arial", max(8, cell_size // 5)),
                   command=lambda r=row, c=col: self.handle_click(r, c),
               )
               button.grid(row=row, column=col, padx=1, pady=1)
               button_row.append(button)
           self.buttons.append(button_row)

       self.update_timer()


    def update_timer(self):
        """
        :return: Update la timer si gestionarea cazului cand expira timpul
        """
        if self.remaining_time > 0 and self.game_active:
            self.timer_label.config(text=f"Time: {self.remaining_time} s")
            self.remaining_time -= 1
            self.master.after(1000, self.update_timer)
        elif self.remaining_time == 0:
            self.game_active = False
            self.end_game(False, True)

    def reveal_cell(self, row, col):
        """
        :param row (int): indexul liniei unde s-a facut click
        :param col (int): indexul coloanei unde s-a facut click
        :return: dezvaluirea unei celule
        """
        if not self.game_active or self.buttons[row][col]["text"] == "B":
            return

        if self.board[row][col] == -1:
            self.buttons[row][col].config(
                text="X_X",
                bg="red",
                fg="black"
            )
            self.master.update_idletasks()

            self.end_game(False, False)
        else:
            self.uncover_cells(row, col)
            if self.check_victory():
                self.end_game(True, False)

    def uncover_cells(self, row, col):
        """
        :param row(int): indexul liniei unde s-a facut click
        :param col (int): indexul coloanei unde s-a facut click
        :return: descopera celulele din jurul unei celule selectate
        """
        if self.buttons[row][col]["state"] == "disabled":
            return

        queue = deque([(row, col)])
        while queue:
            r, c = queue.popleft()
            if self.buttons[r][c]["state"] == "disabled":
                continue

            value = self.board[r][c]

            if value == 0:
                self.buttons[r][c].config(
                    text="",
                    bg="lightgray",
                    relief=tk.SUNKEN,
                    state="disabled"
                )
            else:
                self.buttons[r][c].config(
                    text=str(value),
                    bg="white",
                    font=("Arial", 10, "bold"),
                    state="disabled"
                )

            if value == 0:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            queue.append((nr, nc))

    def check_victory(self):
        """
        conditia de continuare a jocului este sa mai existe celule fara bombe nedezvaluite
        :return: true daca jucatorul a castigat, false altfel
        """
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] != -1 and self.buttons[row][col]["state"] != "disabled":
                    return False
        self.reveal_all_bombs()
        return True

    def reveal_all_bombs(self):
        """
        :return: dezvaluie bombele ramase te table de joc
        """
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == -1 and self.buttons[row][col]["text"] != "B":
                    self.buttons[row][col].config(
                        text="X_X",
                        bg="yellow",
                        fg="red",
                        state="disabled"
                    )
        self.master.update_idletasks() # executa imediat actualizarea UI-ului

    def end_game(self, victory, timeout):
        """
        :return:
        """
        self.game_active = False
        for row in range(self.rows):
            for col in range(self.cols):
                self.buttons[row][col].config(state="disabled")
                if self.buttons[row][col] == -1:
                    if self.buttons[row][col]["text"] != "B":
                        self.buttons[row][col].config(text="B", bg="#7a0f18", fg="white")
        if victory:
            print("You win!")
        else:
            print("You lose!")
        self.reveal_all_bombs()
        self.master.after(3000, self.final(timeout, victory))

    def final(self, timeout, victory):
        """
        :param timeout: true sau false in functie de timpul ramas - daca e true inseamna ca s-a pierdut deoarece a expirat timpul
        :param victory: true daca jucatorul a castigat, false daca a pierdut
        :return: un canvas overlay cu mesaj corespunzator cu posibilitatea de restart a jocului
        """
        overlay = tk.Canvas(self.master, highlightthickness=0)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        overlay.create_text(
            self.master.winfo_width() // 2,
            self.master.winfo_height() // 2 - 90,
            text="GAME OVER", fill="red", font=("Arial", 50, "bold")
        )

        if victory:
            overlay.create_text(
                self.master.winfo_width() // 2,
                self.master.winfo_height() // 2 - 20,
                text="YOU WON :)", fill="red", font=("Arial", 50, "bold")
            )
        elif timeout:
                overlay.create_text(
                    self.master.winfo_width() // 2,
                    self.master.winfo_height() // 2 - 20,
                    text="TIME'S UP! GAME OVER", fill="red", font=("Arial", 30, "bold")
                )
        else:
                overlay.create_text(
                    self.master.winfo_width() // 2,
                    self.master.winfo_height() // 2 - 20,
                    text="YOU LOST :(", fill="red", font=("Arial", 50, "bold")
                )

        overlay.create_text(
            self.master.winfo_width() // 2,
            self.master.winfo_height() // 2 + 40,
            text="Press Enter to Restart", fill="black", font=("Arial", 20, "italic")
        )

        self.master.bind("<Return>", lambda event: self.restart_game())
        self.master.after(10000, self.master.destroy)

    def restart_game(self):
        """
        :return: reinitializarea jocului cu setarile alese la inceput
        """
        self.master.unbind("<Return>")
        self.master.destroy()

        new_window = tk.Toplevel()
        new_window.title("Minesweeper")
        Minesweeper(new_window, self.rows, self.cols, self.mines, self.time_limit)

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