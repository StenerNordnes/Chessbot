"""
This script is a chess bot that uses the Stockfish chess engine and Selenium WebDriver to play chess on chess.com against the computer. It captures the chessboard from the screen, identifies the pieces, and makes moves based on the analysis of the Stockfish engine.

The script consists of the following classes and functions:

- `convertMoveString(moveString)`: Converts a move string in algebraic notation to a list of coordinates.
- `convertMoveStringHTML(moveString)`: Converts a move string in algebraic notation to a list of coordinates for HTML chessboard.
- `class BoardVisual`: Represents the visual chessboard on the screen. It captures screenshots of each tile, identifies the pieces, and provides methods for moving pieces.
- `class BoardHTML`: Represents the HTML chessboard on chess.com. It provides methods for capturing the current position, making moves, and retrieving the FEN string representation of the board.
- `board = BoardHTML()`: Creates an instance of the `BoardHTML` class.
- `game = st.Stockfish(...)`: Creates an instance of the Stockfish chess engine.
- `turn = input('ready')`: Waits for user input to start the game.
- `while True:`: Main game loop that listens for the 'r' key press, captures the current position, analyzes it with Stockfish, and makes the best move on the chessboard.

To use this script, you need to have the Stockfish chess engine installed and provide the correct file path to the Stockfish executable. You also need to have the necessary Python libraries installed: stockfish, pyautogui, PIL, imagehash, cv2, numpy, pyscreeze, skimage, selenium, and keyboard.
"""
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
from dotenv import dotenv_values


config = dotenv_values(".env")
stockfish_path = config['stockfish_path']


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
    """
    Represents a chess board in HTML format.

    Attributes:
    - position: A dictionary representing the current position of the chess pieces on the board.
    - size: A dictionary representing the size of the chess board.

    Methods:
    - findBoard(): Finds the chess board element on the webpage.
    - getBoardAsFen(turn): Returns the current position of the chess board in FEN notation.
    - movePiece(x, y, target_x, target_y): Moves a chess piece from the specified position to the target position on the board.
    """
    def __init__(self):
        super(BoardHTML, self).__init__()

        self.position = {}
        self.size = {}
        self.previousFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        self.turn = 'w'
        self.castlingRights = [True, True, True, True]
        self.castlingString = 'KQkq'
        self.skillLevel = 20
        self.get("https://www.chess.com/play/computer")
        self.playing = False
        self.game = st.Stockfish(stockfish_path, depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})


        def __del__(self):
            self.quit()

    def findBoard(self):
        """
        Finds the chess board element on the webpage.
        """
        svg_element = self.find_element(By.CLASS_NAME,"coordinates")
        self.location = svg_element.location
        self.size = svg_element.size


    def getBoardAsFen(self):
        """
        Returns the current position of the chess board in FEN notation.

        Parameters:
        - turn: A string representing the current turn (e.g., 'w' for white, 'b' for black).

        Returns:
        - fen: A string representing the FEN notation of the current position.
        """
        elements = self.find_elements(By.CSS_SELECTOR, "div[class*=piece]")

        b = [['_' for _ in range(8)] for _ in range(8)]

        for element in elements:
            attr = element.get_attribute("class")

            if attr.find('square') == -1:
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

        return f'{fen} {self.turn} {self.castlingString} - 0 1'

    def movePiece(self,x, y, target_x, target_y):
        """
        Moves a chess piece from the specified position to the target position on the board.

        Parameters:
        - x: An integer representing the x-coordinate of the starting position.
        - y: An integer representing the y-coordinate of the starting position.
        - target_x: An integer representing the x-coordinate of the target position.
        - target_y: An integer representing the y-coordinate of the target position.
        """
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
        self.find_element(By.ID, "username").send_keys(config['username'])
        self.find_element(By.ID, "password").send_keys(config['password'])
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
        print('Turn set to: ', turn)

    def updateCastlingRights(self, n):
        self.castlingRights[n] = not(self.castlingRights[n])
        print('Castling rights updated: ', self.castlingRights)
        self.updateCastlingString()

    def updateCastlingString(self):
        castling_symbols = ['K', 'Q', 'k', 'q']
        self.castlingString = ''.join(symbol for symbol, right in zip(castling_symbols, self.castlingRights) if right)
        if not self.castlingString:
            self.castlingString = '-'
        
        
    
    def setSkillLevel(self, level):
        self.skillLevel = level
        self.game.set_skill_level(level)

    def endGame(self):
        self.playing = False
        print('Game ended')
    
    def resetStockfish(self):
        self.game = st.Stockfish(stockfish_path, depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})
        print('Stockfish restarted')
    


    def play(self):    
        self.playing = True
        while self.playing:
            if self.hasOponentMoved() or keyboard.is_pressed('e'):
                self.findBoard()
                fen = self.getBoardAsFen()
                self.game.set_fen_position(fen)
                print(self.game.get_board_visual())
                movestring = self.game.get_best_move()
                print(movestring)
                print(self.game.get_evaluation())
                bestmove = convertMoveStringHTML(movestring)
                print(bestmove)
                self.movePiece(*bestmove)
            
            time.sleep(0.4)

    def getStats(self):
        wdl = self.game.get_wdl_stats()
        return {"wdl": wdl, **self.game.get_evaluation()}
        









