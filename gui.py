import customtkinter as tk
from stockChessBot import BoardHTML
import stockfish as st
import os
import threading
import keyboard

tk.set_appearance_mode("dark")




class ChessBotGUI:
    def __init__(self):
        self.root = tk.CTk()
        self.root.title("StockChessBot")
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


        
        class DisplayStats:
            def __init__(self, variables_frame):
                self.variables_frame = variables_frame
                self.display_stats_label = tk.CTkLabel(self.variables_frame, text="")
                self.display_stats_label.pack()

            def present_stats(self, stats):
                self.display_stats_label.configure(text="W: {}, D: {}, L: {}".format(*stats))

        self.display_stats = DisplayStats(self.variables_frame)


        # Skill Level Slider
        self.skill_level = tk.IntVar(value=20)
        self.skill_slider = tk.CTkSlider(self.variables_frame, from_=1, to=20, variable=self.skill_level)
        self.skill_slider.pack(pady=10)
        self.skill_slider.bind("<B1-Motion>", self.set_skill)
        self.display_skill = tk.CTkLabel(self.variables_frame, text="Skill Level " + str(self.skill_level.get()))
        self.display_skill.pack()


        # Create a progress ba
        self.progress_bar = tk.CTkProgressBar(self.variables_frame, orientation='horizontal', mode='determinate')
        self.progress_bar.pack()
        self.progress_label = tk.CTkLabel(self.variables_frame, text=f"{self.progress_bar.get()}%")
        self.progress_label.pack()


        # Start Game button
        self.start_button = tk.CTkButton(self.root, text="Start Game", command=self.start_game_thread)
        self.start_button.pack(pady=10)

        # Set Turn button
        self.turn_buttonW = tk.CTkButton(self.root, text="Set Turn white", command=self.set_turnW)
        self.turn_buttonW.pack(pady=10)
        self.turn_buttonB = tk.CTkButton(self.root, text="Set Turn black", command=self.set_turnB)
        self.turn_buttonB.pack(pady=10)

        # Login button
        self.login_button = tk.CTkButton(self.root, text="Login", command=self.login)
        self.login_button.pack(pady=10)

        # Update castling K button
        self.update_castlingK_button = tk.CTkButton(self.root, text="Update castling K", command=self.update_castlingK)
        self.update_castlingK_button.pack(pady=10)

        # Update castling Q button
        self.update_castlingQ_button = tk.CTkButton(self.root, text="Update castling Q", command=self.update_castlingQ)
        self.update_castlingQ_button.pack(pady=10)

        # Update castling k button
        self.update_castlingk_button = tk.CTkButton(self.root, text="Update castling k", command=self.update_castlingk)
        self.update_castlingk_button.pack(pady=10)

        # Update castling q button
        self.update_castlingq_button = tk.CTkButton(self.root, text="Update castling q", command=self.update_castlingq)
        self.update_castlingq_button.pack(pady=10)

        # End game button
        self.end_button = tk.CTkButton(self.root, text="End Game", command=self.end_button)
        self.end_button.pack(pady=10)


        self.root.update_idletasks()
        self.root.mainloop()


    def __del__(self):
        self.board.quit()


    def start_game(self):
        self.playing = True
        self.playing_label.configure(text="Playing: " + str(self.playing))

        if self.board.turn == 'w':
            self.board.play()

        while self.playing:
            try:
                if self.board.hasOponentMoved() or keyboard.is_pressed('e'):
                    self.board.play()
                    self.update_stats()
                    self.progress_bar.set(self.board.getStats()['wdl'][0]/1000)
                    self.progress_label.configure(text=f"{self.progress_bar.get()*100}%")
                
            except st.models.StockfishException as e:
                print(e)
                self.board.resetStockfish()
            except Exception as e:
                print(e.with_traceback())
                break


    def update_stats(self):
        # self.display_stats_label.configure(text="Display Stats: " + str(self.board.getStats()))
        self.display_stats.present_stats(self.board.getStats()['wdl'])

    def start_game_thread(self):
        self.thread = threading.Thread(target=self.start_game)
        self.thread.start()

    def end_button(self):
        self.playing = False
        self.playing_label.configure(text="Playing: "+ str(self.playing))


    def set_skill(self, event=None):
        skill = self.skill_level.get()
        if skill >= 1 and skill <= 20:
            self.board.setSkillLevel(int(skill))
            self.display_skill.configure(text="Skill Level: " + str(self.board.skillLevel))
            
        else:
            print("Invalid skill level")

    def set_turnW(self):
        # Code to set turn goes here
        self.board.setTurn('w')
        self.turn_label.configure(text="Turn: " + self.board.turn)

    def set_turnB(self):
        self.board.setTurn('b')
        self.turn_label.configure(text="Turn: " + self.board.turn)

    def login(self):
        self.board.login()

    def update_castlingK(self):
        self.board.updateCastlingRights(0)
        self.castling_rights_label.configure(text="Castling Rights: " + self.board.castlingString)

    def update_castlingQ(self):
        self.board.updateCastlingRights(1)
        self.castling_rights_label.configure(text="Castling Rights: " + self.board.castlingString)

    def update_castlingk(self):
        self.board.updateCastlingRights(2)
        self.castling_rights_label.configure(text="Castling Rights: " + self.board.castlingString)

    def update_castlingq(self):
        self.board.updateCastlingRights(3)
        self.castling_rights_label.configure(text="Castling Rights: " + self.board.castlingString)
        self.turn_label.configure(text="Turn: " + self.board.turn)
        self.display_stats_label.configure(text="Display Stats: " + str(self.board.getStats()))
        # self.progress_bar_percentage = tk.IntVar(value= self.board.getStats()['wdl'][0]) 




if __name__ == "__main__":
    gui = ChessBotGUI()
