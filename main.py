import customtkinter as tk
from stockChessBot import BoardHTML
import stockfish as st
import threading
import keyboard
import time
from dotenv import load_dotenv

import sys

load_dotenv()


tk.set_appearance_mode("dark")
tk.set_default_color_theme("blue")


class DisplayStats:
    def __init__(self, parent):
        self.frame = tk.CTkFrame(parent)
        self.frame.pack(fill="x", pady=5, padx=10)

        tk.CTkLabel(self.frame, text="Win", font=("Arial", 10, "bold")).grid(
            row=0, column=0, padx=15
        )
        tk.CTkLabel(self.frame, text="Draw", font=("Arial", 10, "bold")).grid(
            row=0, column=1, padx=15
        )
        tk.CTkLabel(self.frame, text="Loss", font=("Arial", 10, "bold")).grid(
            row=0, column=2, padx=15
        )

        self.wins_label = tk.CTkLabel(self.frame, text="0%")
        self.wins_label.grid(row=1, column=0)
        self.draws_label = tk.CTkLabel(self.frame, text="0%")
        self.draws_label.grid(row=1, column=1)
        self.losses_label = tk.CTkLabel(self.frame, text="0%")
        self.losses_label.grid(row=1, column=2)

    def update(self, stats):
        self.wins_label.configure(text=f"{stats[0] / 10}%")
        self.draws_label.configure(text=f"{stats[1] / 10}%")
        self.losses_label.configure(text=f"{stats[2] / 10}%")


class LogBox:
    def __init__(self, parent):
        self.text_box = tk.CTkTextbox(parent, height=120, font=("Consolas", 11))
        self.text_box.pack(fill="both", expand=True, pady=5, padx=10)
        self.lines = ["Bot initialized"]
        self.text_box.insert("0.0", "\n".join(self.lines))

    def add_line(self, line):
        timestamp = time.strftime("%H:%M:%S")
        self.lines.append(f"[{timestamp}] {line}")
        if len(self.lines) > 50:
            self.lines.pop(0)
        self.text_box.delete("0.0", "end")
        self.text_box.insert("0.0", "\n".join(self.lines))
        self.text_box.see("end")

if sys.platform.startswith("linux"):
    tk.set_widget_scaling(2.5)
    tk.set_window_scaling(2.5)


class ChessBotGUI:
    def __init__(self):
        self.root = tk.CTk()
        self.root.title("StockChessBot Pro")
        self.root.geometry("340x800")
        self.root.attributes("-topmost", 1)

        self.board = BoardHTML()
        self.playing = False

        self.setup_ui()
        self.root.mainloop()

    def setup_ui(self):
        # 1. Header (Status)
        self.header = tk.CTkFrame(self.root, fg_color="#2b2b2b")
        self.header.pack(fill="x", padx=10, pady=(10, 5))

        self.status_label = tk.CTkLabel(
            self.header, text="IDLE", font=("Arial", 18, "bold"), text_color="#888888"
        )
        self.status_label.pack(side="left", padx=15, pady=10)

        self.info_frame = tk.CTkFrame(self.header, fg_color="transparent")
        self.info_frame.pack(side="right", padx=15)

        self.turn_indicator = tk.CTkLabel(
            self.info_frame, text="Turn: White", font=("Arial", 11)
        )
        self.turn_indicator.pack()
        self.castling_indicator = tk.CTkLabel(
            self.info_frame, text="KQkq", font=("Consolas", 10), text_color="#aaaaaa"
        )
        self.castling_indicator.pack()

        # 2. Evaluation
        self.eval_frame = tk.CTkFrame(self.root)
        self.eval_frame.pack(fill="x", padx=10, pady=5)

        self.progress_bar = tk.CTkProgressBar(
            self.eval_frame, mode="determinate", height=12
        )
        self.progress_bar.pack(fill="x", padx=20, pady=(15, 5))
        self.progress_bar.set(0.5)

        self.progress_label = tk.CTkLabel(
            self.eval_frame, text="Evaluation: 50.0%", font=("Arial", 11, "bold")
        )
        self.progress_label.pack(pady=(0, 10))

        # 3. Stats
        self.stats = DisplayStats(self.root)

        # 4. Config Tabs
        self.tabs = tk.CTkTabview(self.root, height=320)
        self.tabs.pack(fill="both", padx=10, pady=5)
        self.tabs.add("Engine")
        self.tabs.add("Actions")

        # -- Engine Tab --
        engine_tab = self.tabs.tab("Engine")

        tk.CTkLabel(engine_tab, text="Mode Selection", font=("Arial", 11, "bold")).pack(
            pady=(5, 0)
        )
        self.mode = tk.StringVar(value="Elo")
        self.mode_selector = tk.CTkSegmentedButton(
            engine_tab,
            values=["Elo", "Skill"],
            variable=self.mode,
            command=self.toggle_mode,
        )
        self.mode_selector.pack(pady=5, padx=10, fill="x")

        self.level_var = tk.IntVar(value=1200)
        self.level_label = tk.CTkLabel(engine_tab, text="Elo Level: 1200")
        self.level_label.pack(pady=(10, 0))
        self.level_slider = tk.CTkSlider(
            engine_tab,
            from_=100,
            to=3000,
            variable=self.level_var,
            command=self.update_level_ui,
        )
        self.level_slider.pack(fill="x", padx=20)

        tk.CTkLabel(
            engine_tab, text="Response Speed (Wait Time)", font=("Arial", 11, "bold")
        ).pack(pady=(15, 0))
        self.speed_var = tk.DoubleVar(value=2.0)
        self.speed_slider = tk.CTkSlider(
            engine_tab,
            from_=0.1,
            to=8.0,
            variable=self.speed_var,
            command=self.update_speed_ui,
        )
        self.speed_slider.pack(fill="x", padx=20)
        self.speed_label = tk.CTkLabel(
            engine_tab, text="Min Wait: 2.0s", font=("Arial", 10)
        )
        self.speed_label.pack()

        tk.CTkLabel(
            engine_tab, text="Manual Turn Correction", font=("Arial", 11, "bold")
        ).pack(pady=(15, 0))
        self.turn_var = tk.StringVar(value="White")
        self.turn_selector = tk.CTkSegmentedButton(
            engine_tab,
            values=["White", "Black"],
            variable=self.turn_var,
            command=self.manual_turn_set,
        )
        self.turn_selector.pack(pady=5, padx=10, fill="x")

        # -- Actions Tab --
        actions_tab = self.tabs.tab("Actions")
        tk.CTkButton(
            actions_tab,
            text="Login to Chess.com",
            command=self.login,
            fg_color="#3b3b3b",
        ).pack(pady=8, fill="x", padx=30)
        tk.CTkButton(
            actions_tab,
            text="Identify Board State",
            command=self.identify_state,
            fg_color="#3b3b3b",
        ).pack(pady=8, fill="x", padx=30)
        tk.CTkButton(
            actions_tab,
            text="Force New Game",
            command=self.new_game,
            fg_color="#3b3b3b",
        ).pack(pady=8, fill="x", padx=30)

        tk.CTkLabel(
            actions_tab, text="Shortcuts:", font=("Arial", 11, "bold"), justify="left"
        ).pack(pady=(20, 0), padx=30, anchor="w")
        tk.CTkLabel(
            actions_tab,
            text="[E]  Force Bot Move\n[X]  Flip Board (Internal)",
            font=("Consolas", 10),
            justify="left",
        ).pack(padx=30, anchor="w")

        # 5. Log
        self.log_box = LogBox(self.root)

        # 6. Main Buttons
        self.btn_frame = tk.CTkFrame(self.root, fg_color="transparent")
        self.btn_frame.pack(fill="x", side="bottom", padx=10, pady=15)

        self.start_btn = tk.CTkButton(
            self.btn_frame,
            text="START BOT",
            fg_color="#2d8a2d",
            hover_color="#1e5c1e",
            font=("Arial", 15, "bold"),
            height=45,
            command=self.start_game_thread,
        )
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.stop_btn = tk.CTkButton(
            self.btn_frame,
            text="STOP",
            fg_color="#a83232",
            hover_color="#7d2525",
            font=("Arial", 15, "bold"),
            height=45,
            command=self.stop_game,
        )
        self.stop_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

    def update_level_ui(self, _=None):
        val = int(self.level_var.get())
        if self.mode.get() == "Elo":
            self.level_label.configure(text=f"Elo Level: {val}")
        else:
            # Skill level 1-20
            skill = int(self.level_var.get())
            self.level_label.configure(text=f"Skill Level: {skill}")

    def update_speed_ui(self, _=None):
        val = round(self.speed_var.get(), 1)
        self.speed_label.configure(text=f"Min Wait: {val}s")
        self.board.min_wait = val
        self.board.max_wait = val + 4.0

    def toggle_mode(self, value):
        if value == "Elo":
            self.level_slider.configure(from_=100, to=3000)
            self.level_var.set(1200)
        else:
            self.level_slider.configure(from_=1, to=20)
            self.level_var.set(12)
        self.update_level_ui()

    def manual_turn_set(self, value):
        turn_code = "w" if value == "White" else "b"
        self.board.setTurn(turn_code)
        self.turn_indicator.configure(text=f"Turn: {value}")
        self.log_box.add_line(f"Turn manually set to {value}")

    def start_game_thread(self):
        if self.playing:
            return
        self.playing = True
        self.status_label.configure(text="PLAYING", text_color="#4CAF50")
        self.start_btn.configure(state="disabled")

        # Apply settings
        self.board.initializeStockfish()
        if self.mode.get() == "Elo":
            self.board.setEloLevel(int(self.level_var.get()))
        else:
            self.board.setSkillLevel(int(self.level_var.get()))

        self.log_box.add_line("Bot starting...")
        self.thread = threading.Thread(target=self.game_loop, daemon=True)
        self.thread.start()

    def stop_game(self):
        self.playing = False
        self.status_label.configure(text="IDLE", text_color="#888888")
        self.start_btn.configure(state="normal")
        self.board.playing = False
        self.log_box.add_line("Bot stopped.")

    def game_loop(self):
        try:
            if self.board.turn == "w":
                self.log_box.add_line("Initial move (White)...")
                self.board.play()

            while self.playing:
                if self.board.hasOponentMoved() or keyboard.is_pressed("e"):
                    self.castling_indicator.configure(text=self.board.castlingString)
                    self.log_box.add_line("Thinking...")

                    move = self.board.play()
                    self.log_box.add_line(f"Move made: {move}")

                    # Update Stats
                    stats = self.board.getStats()
                    self.stats.update(stats["wdl"])

                    # Update Eval Progress
                    eval_val = stats["wdl"][0] / 1000 + stats["wdl"][1] / 2000
                    self.progress_bar.set(eval_val)
                    self.progress_label.configure(
                        text=f"Evaluation: {round(eval_val * 100, 1)}%"
                    )

                    # Check for new game
                    if self.board.newGame():
                        self.log_box.add_line("New game detected.")
                        self.identify_state()

                time.sleep(0.5)
        except Exception as e:
            self.log_box.add_line(f"Error: {str(e)}")
            self.stop_game()

    def login(self):
        self.log_box.add_line("Attempting login...")
        try:
            self.board.login()
            self.log_box.add_line("Login command sent.")
        except Exception as e:
            self.log_box.add_line(f"Login failed: {str(e)}")

    def identify_state(self):
        self.board.identifyTurn()
        turn_text = "White" if self.board.turn == "w" else "Black"
        self.turn_indicator.configure(text=f"Turn: {turn_text}")
        self.castling_indicator.configure(text=self.board.castlingString)
        self.log_box.add_line(f"State synced. Turn: {turn_text}")

    def new_game(self):
        self.board.newGame()
        self.log_box.add_line("Force new game triggered.")


if __name__ == "__main__":
    gui = ChessBotGUI()
