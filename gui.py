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
        self.root.title("StockChessBot")
        self.game = st.Stockfish(stockfish_path, depth=24, parameters={"Threads": 2, "Minimum Thinking Time": 30})
        self.board = BoardHTML()
        self.playing = False

        self.root.attributes("-topmost", 1)

        # Create a frame to hold the variables
        self.variables_frame = tk.CTkFrame(self.root)
        self.variables_frame.pack(side='right', padx=10)

        # Display boardHTML variables
        self.castling_rights_label = tk.CTkLabel(self.variables_frame, text="Castling Rights: " + self.board.castlingString)
        self.castling_rights_label.pack()
        self.turn_label = tk.CTkLabel(self.variables_frame, text="Turn: " + self.board.turn)
        self.turn_label.pack()
        self.playing_label = tk.CTkLabel(self.variables_frame, text="Playing: " + str(self.playing))
        self.playing_label.pack()

        self.display_stats_label = tk.CTkLabel(self.variables_frame, text="Display Stats: " + str(self.board.getStats()))
        self.display_stats_label.pack()



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
        self.login_button.pack(pady = 10)

        # Update castling K button
        self.update_castlingK_button = tk.CTkButton(self.root, text="Update castling K", command=self.update_castlingK)
        self.update_castlingK_button.pack(pady = 10)

        # Update castling Q button
        self.update_castlingQ_button = tk.CTkButton(self.root, text="Update castling Q", command=self.update_castlingQ)
        self.update_castlingQ_button.pack(pady = 10)

        # Update castling k button
        self.update_castlingk_button = tk.CTkButton(self.root, text="Update castling k", command=self.update_castlingk)
        self.update_castlingk_button.pack(pady = 10)

        # Update castling q button
        self.update_castlingq_button = tk.CTkButton(self.root, text="Update castling q", command=self.update_castlingq)
        self.update_castlingq_button.pack(pady = 10)

        # End game button
        self.end_button = tk.CTkButton(self.root, text="End Game", command=self.end_button)
        self.end_button.pack(pady=10)

        self.root.update_idletasks()
        # Add more buttons as needed

        self.root.mainloop()

    def start_game(self):
        self.playing = True
        self.playing_label.configure(text="Playing: " + str(self.playing))
        while self.playing:
            try:
                self.board.play()
                
            except st.models.StockfishException as e:
                print(e)
                self.board.resetStockfish()
            except Exception as e:
                print(e.with_traceback())
                break

    def start_game_thread(self):
        self.thread = threading.Thread(target=self.start_game)
        self.thread.start()

    def end_button(self):
        self.playing = False
        self.board.endGame()
        self.playing_label.configure(text="Playing: "+ str(self.playing))

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
        self.update_labels()
        self.board.setTurn('w')

    def set_turnB(self):
        self.board.setTurn('b')

    def login(self):
        self.board.login()

    def update_castlingK(self):
        self.board.updateCastlingRights(0)

    def update_castlingQ(self):
        self.board.updateCastlingRights(1)

    def update_castlingk(self):
        self.board.updateCastlingRights(2)

    def update_castlingq(self):
        self.board.updateCastlingRights(3)

    def update_labels(self):
        self.castling_rights_label.configure(text="Castling Rights: " + self.board.castlingString)
        self.turn_label.configure(text="Turn: " + self.board.turn)
        self.display_stats_label.configure(text="Display Stats: " + str(self.board.getStats()))

        self.root.after(1000, self.update_labels)

if __name__ == "__main__":
    gui = ChessBotGUI()
