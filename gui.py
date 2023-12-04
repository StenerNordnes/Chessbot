import customtkinter as tk
from stockChessBot import BoardHTML
import stockfish as st
import os
import threading
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

stockfish_path = os.environ.get('stockfish_path')

class ChessBotGUI:
    def __init__(self):
        self.root = tk.CTk()
        self.root.title("StochChessBot")
        self.game = st.Stockfish(stockfish_path, depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})
        self.board = BoardHTML()

        self.root.attributes("-topmost", 1)

        # Start Game button
        self.start_button = tk.CTkButton(self.root, text="Start Game", command=self.start_game_thread)
        self.start_button.pack()

        # Set Skill button
        self.skill_button = tk.CTkButton(self.root, text="Set Skill", command=self.set_skill)
        self.skill_button.pack()

        # Set Turn button
        self.turn_buttonW = tk.CTkButton(self.root, text="Set Turn white", command=self.set_turnW)
        self.turn_buttonW.pack()
        self.turn_buttonB = tk.CTkButton(self.root, text="Set Turn black", command=self.set_turnB)
        self.turn_buttonB.pack()

        # Login button
        self.login_button = tk.CTkButton(self.root, text="Login", command=self.login)
        self.login_button.pack()

        # Add more buttons as needed

        self.root.mainloop()

    def start_game(self):
        while True:
            try:
                self.board.play()
            except st.models.StockfishException as e:
                self.game = st.Stockfish(stockfish_path, depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})
                self.board.updateCastlingRights(False)
                print('Stockfish restarted')
            except Exception as e:
                print(e)
                break

    def start_game_thread(self):
        threading.Thread(target=self.start_game).start()

    def set_skill(self):
        self.skill_level = tk.StringVar()
        self.skill_entry = tk.CTkEntry(self.root, textvariable=self.skill_level)
        self.skill_entry.pack()
        self.skill_button = tk.CTkButton(self.root, text="Set Skill", command=self.update_skill)
        self.skill_button.pack()

    def update_skill(self):
        skill = self.skill_level.get()
        if skill.isdigit():
            self.board.setSkillLevel(int(skill))
        else:
            print("Invalid skill level")

    def set_turnW(self):
        # Code to set turn goes here
        self.board.setTurn('w')

    def set_turnB(self):
        self.board.setTurn('b')

    def login(self):
        self.board.login()

if __name__ == "__main__":
    gui = ChessBotGUI()
