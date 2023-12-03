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

        # Create a frame to hold the variables
        self.variables_frame = tk.CTkFrame(self.root)
        self.variables_frame.pack(side='right', padx=10)

        # Display boardHTML variables
        self.castling_rights_label = tk.CTkLabel(self.variables_frame, text="Castling Rights: " + self.board.castlingRights)
        self.castling_rights_label.pack()
        self.turn_label = tk.CTkLabel(self.variables_frame, text="Turn: " + self.board.turn)
        self.turn_label.pack()

        # Add more labels/buttons as needed

        # Start Game button
        self.start_button = tk.CTkButton(self.root, text="Start Game", command=self.start_game_thread)
        self.start_button.pack(pady=10)

        # Set Skill button
        self.skill_button = tk.CTkButton(self.root, text="Set Skill", command=self.set_skill)
        self.skill_button.pack(pady=10)

        # Set Turn button
        self.turn_buttonW = tk.CTkButton(self.root, text="Set Turn white", command=self.set_turnW)
        self.turn_buttonW.pack(pady=10)
        self.turn_buttonB = tk.CTkButton(self.root, text="Set Turn black", command=self.set_turnB)
        self.turn_buttonB.pack(pady=10)

        # Login button
        self.login_button = tk.CTkButton(self.root, text="Login", command=self.login)
        self.login_button.pack(pady=10)

        self.root.update_idletasks()
        # Add more buttons as needed

        self.root.mainloop()

    def start_game(self):
        while True:
            try:
                self.board.play()
            except st.models.StockfishException as e:
                print(e)
                self.game = st.Stockfish(stockfish_path, depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})
                self.board.updateCastlingRights(False)
                print(self.board.previousFen)
                print('Is fen valid?: ',self.game.is_fen_valid(self.board.previousFen))


                print('Stockfish restarted')
                continue
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
