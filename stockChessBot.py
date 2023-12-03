import stockfish as st
import pyautogui as p
from PIL import Image
import imagehash
import cv2
import numpy as np
from pyscreeze import Box
from skimage.metrics import structural_similarity as ssim
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import keyboard
from selenium.webdriver.common.action_chains import ActionChains
import os



game = st.Stockfish(r"C:\Users\jacob\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe", depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})

BOARD_IMG = './bot_assets/board.png'

PIECE_NAME = {
    0:'_',
    1:'P',
    2:'R',
    3:'N',
    4:'B',
    5:'Q',
    6:'K',
    7:'p',
    8:'r',
    9:'n',
    10:'b',
    11:'q',
    12:'k'
}


piece_mapping = {
    'br': 'r', 'bn': 'n', 'bb': 'b', 'bk': 'k', 'bq': 'q', 'bp': 'p',
    'wr': 'R', 'wn': 'N', 'wb': 'B', 'wk': 'K', 'wq': 'Q', 'wp': 'P'
}







def convertMoveString(moveString):
    char_list = list(moveString)

    char_list[0] = int(ord(char_list[0]) - ord('a'))
    char_list[1] = 8 - int(char_list[1])
    char_list[2] = int(ord(char_list[2]) - ord('a'))
    char_list[3] = 8 - int(char_list[3])
    return [char_list[1], char_list[0], char_list[3], char_list[2]]


def convertMoveStringHTML(moveString):
    char_list = list(moveString)

    char_list[0] = int(ord(char_list[0]) - ord('a'))
    char_list[1] = 8 - int(char_list[1])
    char_list[2] = int(ord(char_list[2]) - ord('a'))
    char_list[3] = 8 - int(char_list[3])
    return [char_list[0], char_list[1], char_list[2], char_list[3]]





class BoardVisual():
    def __init__(self, boundingBox) -> None:
        self.height = boundingBox.height
        self.width =  boundingBox.width
        self.left =  boundingBox.left
        self.top = boundingBox.top

        self.pos_array = []
        self.piece_array = np.zeros([8,8], dtype=str)

        self.Wdx = boundingBox.width//8
        self.Hdx = boundingBox.height//8

        tempArray = []

        for i in range(8):
            tempArray = []
            for j in range(8):
                tempArray.append((j*self.Wdx + boundingBox.left, i*self.Hdx + boundingBox.top))

            self.pos_array.append(tempArray)

    def get_fenString(self, turn):
        fen = ''
        for row in self.piece_array:
            empty_count = 0
            for square in row:
                if square == '_':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen += str(empty_count)
                        empty_count = 0
                    fen += square
            if empty_count > 0:
                fen += str(empty_count)
            fen += '/'

        # Remove the trailing '/'
        fen = fen[:-1]

        return fen +' '+ turn

    def screenTiles(self,name,x,y):
        p.screenshot(name, (self.pos_array[x][y][0],self.pos_array[x][y][1], self.Wdx, self.Hdx)) #left, top, width, height

    def move_piece(self, x, y, target_x, target_y):

        centerX = self.pos_array[x][y][0] + self.Wdx//2
        centerY = self.pos_array[x][y][1] + self.Hdx//2

        print(centerX, centerY)

        p.click(centerX, centerY)

        targetCenterX = self.pos_array[target_x][target_y][0] + self.Wdx//2
        targetCenterY = self.pos_array[target_x][target_y][1] + self.Hdx//2

        p.click(targetCenterX,targetCenterY) 
        p.moveTo(10,10)        

    def identify_tile(self):
        # Load images
        temp_image = cv2.imread('temp_tile.png', cv2.IMREAD_GRAYSCALE)
        similarity_array = np.zeros(12)

        # Apply Canny edge detection to extract outlines
        temp_edges = cv2.Canny(temp_image, 50, 150)

        for i in range(12):
            baseline_image = cv2.imread(f'./bot_assets/{i+1}.png', cv2.IMREAD_GRAYSCALE)
            
            # Apply Canny edge detection to the baseline image
            baseline_edges = cv2.Canny(baseline_image, 50, 150)

            # Compare outlines using SSIM
            similarity = ssim(temp_edges, baseline_edges)
            similarity_array[i] = similarity


        if similarity_array.max() <=0.7:
            return 0
        else:
            return similarity_array.argmax() +1


    def initialize_images(self):
        return
        for i in range(8):
            for j in range(8):
                self.screenTiles(f'./bot_assets/{i}{j}.png', i,j)

    def fill_pieces(self):
        for i in range(8):
            for j in range(8):
                self.screenTiles('temp_tile.png',i,j)
                pieceNum = int(self.identify_tile())
                self.piece_array[i,j] = PIECE_NAME[pieceNum]
                

class BoardHTML(webdriver.Chrome):
    def __init__(self):
        super(BoardHTML, self).__init__()

        self.position = {}
        self.size = {}
        self.previousFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        self.turn = ''
        self.castlingRights = 'KQkq'
        self.skillLevel = 20

    def findBoard(self):
        svg_element = self.find_element(By.CLASS_NAME,"coordinates")
        self.location = svg_element.location
        self.size = svg_element.size


    def getBoardAsFen(self):
        elements = self.find_elements(By.CSS_SELECTOR, "div[class*=piece]")

        

        b = [['_' for _ in range(8)] for _ in range(8)]



        for element in elements:
            attr = element.get_attribute("class")
            if attr.find("square") == -1:
                continue
            _, piece, pos = attr.split()
            _,pos = pos.split('-')
            pos = list(pos)
            x = int(pos[0])-1
            y = 8 - int(pos[1])

            b[y][x] = piece_mapping[piece]

        fen = ''
        for row in b:
            empty_count = 0
            for square in row:
                if square == '_':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen += str(empty_count)
                        empty_count = 0
                    fen += square
            if empty_count > 0:
                fen += str(empty_count)
            fen += '/'

        # Remove the trailing '/'
        fen = fen[:-1]

        return f'{fen} {self.turn} {self.castlingRights} - 0 1'

    def movePiece(self,x, y, target_x, target_y):

        self.findBoard()

        Wdx = self.size['width']/8
        Hdx = self.size['height']/8
        centerX = self.location['x'] + Wdx/2 + x*Wdx
        centerY = self.location['y'] + Hdx/2 + y*Hdx


        targetCenter_x = self.location['x'] + Wdx/2 + target_x*Wdx
        targetCenter_y = self.location['y'] + Hdx/2 + target_y*Hdx

        print(targetCenter_x, targetCenter_y)


        actions = ActionChains(self, duration=100)
        actions.move_by_offset(centerX, centerY)
        actions.click()
        actions.move_by_offset(-centerX, -centerY)
        actions.move_by_offset(targetCenter_x, targetCenter_y)
        actions.click()
        actions.move_by_offset(-targetCenter_x, -targetCenter_y)
        actions.perform()
        self.previousFen = self.getBoardAsFen()

    def login(self):
        self.get("https://www.chess.com/login")
        self.find_element(By.ID, "username").send_keys('cribbengalos')
        self.find_element(By.ID, "password").send_keys('Hansjens1')
        self.find_element(By.ID, "login").click()

    def hasOponentMoved(self):
        new = self.getBoardAsFen()
        if new != self.previousFen:
            self.previousFen = new
            time.sleep(0.4)
            return True
        else:
            self.previousFen = new
            time.sleep(0.4)
            return False
        
    def setTurn(self, turn):
        self.turn = turn

    def updateCastlingRights(self, rights):
        if rights:
            self.castlingRights = 'KQkq'
        else: 
            self.castlingRights = '-'
    
    def setSkillLevel(self, level):
        self.skillLevel = level
        game.set_skill_level(level)
    


    def play(self):
        

        self.findBoard()

        while True:
            if self.hasOponentMoved() or keyboard.is_pressed('e'):
                fen = self.getBoardAsFen()
                game.set_fen_position(fen)
                print(game.get_board_visual())
                movestring = game.get_best_move_time(1000)
                print(movestring)
                print(game.get_evaluation())
                bestmove = convertMoveStringHTML(movestring)
                print(bestmove)
                self.movePiece(*bestmove)
                time.sleep(0.4)
            else:
                time.sleep(0.4)
                continue


        

# board = BoardHTML()

# board.login()
# board.setSkillLevel(20)
# # board.setTurn(input('ready'))
# while True:
#     try:
#         board.play()
#     except st.models.StockfishException as e:
#         game = st.Stockfish(r"C:\Users\jacob\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe", depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})
#         print('Stockfish restarted')

#         continue
#     except Exception as e:
#         print(e)
#         continue










# Load the web page
# board.get("https://www.chess.com/play/computer")
# board.login()
# board.setSkillLevel(20)


# board.setTurn(input('ready'))
# board.findBoard()
# while True:
#     if keyboard.is_pressed('r'):
#         while True:
#             try:
#                 if board.hasOponentMoved() or keyboard.is_pressed('e'):
#                     fen = board.getBoardAsFen()
#                     game.set_fen_position(fen)
#                     print(game.get_board_visual())
#                     movestring = game.get_best_move_time(1000)
#                     print(movestring)
#                     print(game.get_evaluation())
#                     bestmove = convertMoveStringHTML(movestring)
#                     print(bestmove)
#                     board.movePiece(*bestmove)
#                     time.sleep(0.4)
                
#                 if keyboard.is_pressed('q'):
#                     board.setTurn(input('ready'))
                    
                    
                    

#             except st.models.StockfishException as e:
#                 game = st.Stockfish(r"C:\Users\jacob\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe", depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})
#                 print('Stockfish restarted')

#                 continue
#             except Exception as e:
#                 print(e)
#                 continue



# # Close the browser window
# board.quit()







