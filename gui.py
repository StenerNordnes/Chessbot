import customtkinter as tk
from stockChessBot import BoardHTML
import stockfish as st
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
        self.root.geometry("+{}+{}".format(self.root.winfo_screenwidth() - self.root.winfo_reqwidth(), 0))

        # Create a frame to hold the variables
        self.variables_frame = tk.CTkFrame(self.root)
        self.variables_frame.pack(side='right', padx=10, pady=(10, 0))

        self.variables_display_frame = tk.CTkFrame(self.variables_frame)
        self.variables_display_frame.pack(pady=(5, 10))

        self.castling_rights_label = tk.CTkLabel(self.variables_display_frame, text="Castling: ").grid(row=0, column=0, padx = 5,)
        self.castling_rights_value_label = tk.CTkLabel(self.variables_display_frame, text=self.board.castlingString)
        self.castling_rights_value_label.grid(row=1, column=0, padx = 5)


        self.turn_label = tk.CTkLabel(self.variables_display_frame, text="Turn: ").grid(row=0, column=1, padx = 5)
        self.turn_value_label = tk.CTkLabel(self.variables_display_frame, text=self.board.turn)
        self.turn_value_label.grid(row=1, column=1, padx = 5)

        tk.CTkLabel(self.variables_display_frame, text="Status: ").grid(row=0, column=2,padx = 5)
        self.playing_value_label = tk.CTkLabel(self.variables_display_frame, text='Idle')
        self.playing_value_label.grid(row=1, column=2, padx = 5)

        
        class DisplayStats:
            def __init__(self, variables_frame):
                self.variables_frame = variables_frame
                self.display_stats_frame = tk.CTkFrame(self.variables_frame)
                
                self.display_stats_frame.pack(pady=(0, 10))  # Add padding to the bottom

                tk.CTkLabel(self.display_stats_frame, text="Win: ").grid(row=0, column=0, padx=5)
                tk.CTkLabel(self.display_stats_frame, text="Draw: ").grid(row=0, column=1, padx=5)
                tk.CTkLabel(self.display_stats_frame, text="Lose: ").grid(row=0, column=2, padx=5)

                self.wins_percentage_label = tk.CTkLabel(self.display_stats_frame, text="0 %")
                self.wins_percentage_label.grid(row=1, column=0, padx=5)
                self.draws_percentage_label = tk.CTkLabel(self.display_stats_frame, text="0 %")
                self.draws_percentage_label.grid(row=1, column=1, padx=5)
                self.losses_percentage_label = tk.CTkLabel(self.display_stats_frame, text="0 %")
                self.losses_percentage_label.grid(row=1, column=2, padx=5)

            def present_stats(self, stats):
                self.wins_percentage_label.configure(text="{} %".format(stats[0]/10))
                self.draws_percentage_label.configure(text="{} %".format(stats[1]/10))
                self.losses_percentage_label.configure(text="{} %".format(stats[2]/10))


        self.display_stats = DisplayStats(self.variables_frame)


        # Skill Level Slider
        self.skill_level = tk.IntVar(value=12)
        self.display_skill = tk.CTkLabel(self.variables_frame, text="Skill Level " + str(self.skill_level.get()))
        self.display_skill.pack()
        self.skill_slider = tk.CTkSlider(self.variables_frame, from_=1, to=20, variable=self.skill_level)
        self.skill_slider.pack(pady=(0,20))
        self.skill_slider.bind("<B1-Motion>", self.set_skill)


        # Create a progress ba
        self.progress_bar = tk.CTkProgressBar(self.variables_frame, orientation='horizontal', mode='determinate')
        self.progress_bar.pack()
        self.progress_label = tk.CTkLabel(self.variables_frame, text=f"{round(self.progress_bar.get(),1)}%")
        self.progress_label.pack()


    


        class TextBox:
            def __init__(self, root):
                self.root = root
                self.text_box = tk.CTkTextbox(self.root)  # Set the state to 'disabled'
                self.text_box.pack(pady=(0, 10), padx=8)
                self.lines = ['Stockfish bot started']
                self.text_box.insert(tk.END, "\n".join(self.lines))

            def add_line(self, new_line):
                self.lines.append(new_line)
                if len(self.lines) > 8:
                    self.lines.pop(0)
                self.text_box.delete(1.0, tk.END)
                self.text_box.insert(tk.END, "\n".join(self.lines))
                self.text_box.see(tk.END)

        self.text_box = TextBox(self.variables_frame)

        buttons_frame = tk.CTkFrame(self.root)
        buttons_frame.pack()

        tk.CTkButton(buttons_frame, text="Start Game", command=self.start_game_thread).grid(row=0, column=0, pady=10, padx=5)
        tk.CTkButton(buttons_frame, text="Set Turn white", command=self.set_turnW).grid(row=1, column=0, pady=10, padx=5)
        tk.CTkButton(buttons_frame, text="Set Turn black", command=self.set_turnB).grid(row=2, column=0, pady=10, padx=5)
        tk.CTkButton(buttons_frame, text="Login", command=self.login).grid(row=3, column=0, pady=10, padx=5)
        tk.CTkButton(buttons_frame, text="End Game", command=self.end_button).grid(row=4, column=0, pady=10, padx=5)
        # tk.CTkButton(buttons_frame, text="Update castling K", command=self.update_castlingK).grid(row=0, column=0, pady=10, padx=5)
        # tk.CTkButton(buttons_frame, text="Update castling Q", command=self.update_castlingQ).grid(row=1, column=0, pady=10, padx=5)
        # tk.CTkButton(buttons_frame, text="Update castling k", command=self.update_castlingk).grid(row=2, column=0, pady=10, padx=5)
        # tk.CTkButton(buttons_frame, text="Update castling q", command=self.update_castlingq).grid(row=3, column=0, pady=10, padx=5)
        tk.CTkButton(buttons_frame, text = "Identify Turn", command = self.board.identifyTurn).grid(row=5, column=0, pady=10, padx=5)
        tk.CTkButton(buttons_frame, text = "New Game", command = self.board.newGame).grid(row=6, column=0, pady=10, padx=5)
        tk.CTkButton(buttons_frame, text = "Print time", command = self.board.get_current_player_time).grid(row=7, column=0, pady=10, padx=5)



        self.root.update_idletasks()
        self.root.mainloop()


    def __del__(self):
        del self.board


    def start_game(self):
        self.board.initializeStockfish()
        self.board.setSkillLevel(int(self.skill_level.get()))
        self.playing = True
        self.text_box.add_line('Game started') 
        self.skill_slider.configure(state='disabled')
        self.playing_value_label.configure(text= 'Playing' if self.playing else 'Idle')
        movestring = ''


        if self.board.turn == 'w':
            self.board.play()

        while self.playing:
            try:
                if self.board.hasOponentMoved() or keyboard.is_pressed('e'):
                    self.castling_rights_value_label.configure(text=self.board.castlingString)
                    self.text_box.add_line('Thinking...')
                    movestring = self.board.play()
                    self.text_box.add_line('Move made: ' + movestring)
                    self.update_stats()
                    self.progress_bar.set(self.board.getStats()['wdl'][0]/1000 + self.board.getStats()['wdl'][1]/2000)
                    self.progress_label.configure(text=f"{round(self.progress_bar.get()*100,2)}%")
                    self.playing = False
                    self.board.newGame()
                    self.playing = True


                
            except st.models.StockfishException as e:
                print(e)
                self.board.resetStockfish()
                self.text_box.add_line('Stockfish crashed, restarting...')
            except Exception as e:
                print(e.with_traceback())
                self.text_box.add_line('Error: ' + str(e))
                break

            finally:
                if movestring is None:
                    break


        print('Game ended successfully')
        self.text_box.add_line('Game ended successfully')
        self.skill_slider.configure(state='enabled')


    def update_stats(self):
        self.display_stats.present_stats(self.board.getStats()['wdl'])

    def start_game_thread(self):
        self.thread = threading.Thread(target=self.start_game)
        self.thread.start()

    def end_button(self):
        self.skill_slider.configure(state='normal')
        self.board.endGame()
        self.text_box.add_line('Game ended')
        self.playing_value_label.configure(text="Idle")


    def set_skill(self, event=None):
        skill = self.skill_level.get()
        if skill >= 1 and skill <= 20:
            self.display_skill.configure(text="Skill Level: " + str(skill))
            
        else:
            print("Invalid skill level")

    def set_turnW(self):
        # Code to set turn goes here
        if not self.playing:
            self.board.setTurn('w')
            self.turn_value_label.configure(text="Turn: " + self.board.turn)

    def set_turnB(self):
        if not self.playing:
            self.board.setTurn('b')
            self.turn_value_label.configure(text="Turn: " + self.board.turn)

    def login(self):
        self.board.login()

    def update_castlingK(self):
        self.board.updateCastlingRights(0)
        self.castling_rights_value_label.configure(text=self.board.castlingString)

    def update_castlingQ(self):
        self.board.updateCastlingRights(1)
        self.castling_rights_value_label.configure(text=self.board.castlingString)

    def update_castlingk(self):
        self.board.updateCastlingRights(2)
        self.castling_rights_value_label.configure(text=self.board.castlingString)

    def update_castlingq(self):
        self.board.updateCastlingRights(3)
        self.castling_rights_value_label.configure(text=self.board.castlingString)
        self.turn_value_label.configure(text=self.board.turn)



if __name__ == "__main__":
    gui = ChessBotGUI()
