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
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import shutil
from dotenv import load_dotenv
import random

load_dotenv()


# Resolve the final path (may be None if not found)
stockfish_path = "./stockfish.exe"


piece_mapping = {
    "br": "r",
    "bn": "n",
    "bb": "b",
    "bk": "k",
    "bq": "q",
    "bp": "p",
    "wr": "R",
    "wn": "N",
    "wb": "B",
    "wk": "K",
    "wq": "Q",
    "wp": "P",
}


def convertMoveStringHTML(moveString):
    char_list = list(moveString)
    char_list[0] = int(ord(char_list[0]) - ord("a"))
    char_list[1] = 8 - int(char_list[1])
    char_list[2] = int(ord(char_list[2]) - ord("a"))
    char_list[3] = 8 - int(char_list[3])
    return [char_list[0], char_list[1], char_list[2], char_list[3]]


def convertTimeString_millisecons(time_string: str) -> int:
    minutes, seconds = map(int, time_string.split(":"))
    milliseconds = minutes * 60000 + seconds * 1000
    return milliseconds


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
        super().__init__()

        self.previousFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.turn = "w"
        self.castlingRights = [True, True, True, True]
        self.castlingString = "KQkq"
        self.skillLevel = 12
        self.elo = 3000
        self.get("https://www.chess.com/play/computer")
        self.playing = False

    def __del__(self):
        self.quit()

    def findBoard(self):
        """
        Finds the chess board element on the webpage.
        """
        svg_element = self.find_element(By.CLASS_NAME, "coordinates")
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

        b = [["_" for _ in range(8)] for _ in range(8)]

        for element in elements:
            attr = element.get_attribute("class")

            if attr is None:
                continue

            if attr.find("square") == -1:
                continue

            # _, piece, pos = attr.split()
            # _,pos = pos.split('-')
            # pos = list(pos)

            pos = re.search(r"square-(\d+)", attr)
            piece = re.findall(r"[bw][a-z]", attr)[0].strip()

            if pos is None:
                print("Pos not found")
                continue

            pos = pos.group(1)

            x = int(pos[0]) - 1
            y = 8 - int(pos[1])

            b[y][x] = piece_mapping[piece]

        fen = ""
        for row in b:
            empty_count = 0
            for square in row:
                if square == "_":
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen += str(empty_count)
                        empty_count = 0
                    fen += square
            if empty_count > 0:
                fen += str(empty_count)
            fen += "/"

        # Remove the trailing '/'
        fen = fen[:-1]

        return f"{fen} {self.turn} {self.castlingString} - 0 1"

    def movePiece(self, x, y, target_x, target_y):
        """
        Moves a chess piece from the specified position to the target position on the board.

        Parameters:
        - x: An integer representing the x-coordinate of the starting position.
        - y: An integer representing the y-coordinate of the starting position.
        - target_x: An integer representing the x-coordinate of the target position.
        - target_y: An integer representing the y-coordinate of the target position.
        """
        self.findBoard()
        Wdx = self.size["width"] / 8
        Hdx = self.size["height"] / 8
        centerX = self.location["x"] + Wdx / 2 + x * Wdx
        centerY = self.location["y"] + Hdx / 2 + y * Hdx

        targetCenter_x = self.location["x"] + Wdx / 2 + target_x * Wdx
        targetCenter_y = self.location["y"] + Hdx / 2 + target_y * Hdx

        print(targetCenter_x, targetCenter_y)

        actions = ActionChains(self, duration=100)
        actions.move_by_offset(centerX, centerY)
        actions.click()
        actions.move_by_offset(-centerX, -centerY)
        actions.move_by_offset(targetCenter_x, targetCenter_y)
        actions.click()
        actions.move_by_offset(-targetCenter_x, -targetCenter_y)
        actions.perform()
        self.CastlingUpdate()
        self.previousFen = self.getBoardAsFen()

    def initializeStockfish(self):
        # Ensure we have a valid path to the Stockfish binary before initializing
        if not stockfish_path or not os.path.isfile(stockfish_path):
            # final attempt to locate in PATH
            found = shutil.which("stockfish") or shutil.which("stockfish.exe")
            if found:
                resolved = found
            else:
                raise FileNotFoundError(
                    "Stockfish binary not found. Set the STOCKFISH_PATH (or stockfish_path) environment variable "
                    "to the full path of the Stockfish executable, or install Stockfish in your PATH."
                )
        else:
            resolved = stockfish_path

        self.game = st.Stockfish(
            resolved, depth=19, parameters={"Threads": 2, "Minimum Thinking Time": 30}
        )

    def CastlingUpdate(self):

        currentFen = self.getBoardAsFen()
        board1 = st.Stockfish(
            stockfish_path,
            depth=18,
            parameters={"Threads": 2, "Minimum Thinking Time": 30},
        )
        board2 = st.Stockfish(
            stockfish_path,
            depth=18,
            parameters={"Threads": 2, "Minimum Thinking Time": 30},
        )

        board1.set_fen_position(self.previousFen)
        board2.set_fen_position(currentFen)

        if board1.get_what_is_on_square("e1") != board2.get_what_is_on_square("e1"):
            self.castlingRights[0] = False
            self.castlingRights[1] = False
        elif board1.get_what_is_on_square("e8") != board2.get_what_is_on_square("e8"):
            self.castlingRights[2] = False
            self.castlingRights[3] = False
        elif board1.get_what_is_on_square("a1") != board2.get_what_is_on_square("a1"):
            self.castlingRights[1] = False
        elif board1.get_what_is_on_square("h1") != board2.get_what_is_on_square("h1"):
            self.castlingRights[0] = False
        elif board1.get_what_is_on_square("a8") != board2.get_what_is_on_square("a8"):
            self.castlingRights[3] = False
        elif board1.get_what_is_on_square("h8") != board2.get_what_is_on_square("h8"):
            self.castlingRights[2] = False

        del board1
        del board2

        self.updateCastlingString()

    def login(self):
        self.get("https://www.chess.com/login")

        # Read credentials from environment (support common var names)
        username = os.environ.get("chess_username")
        password = os.environ.get("chess_password")
        if not username or not password:
            raise EnvironmentError(
                "Missing credentials: set 'username' and 'password' environment variables."
            )

        wait = WebDriverWait(self, 10)
        try:
            # Prefer the visible/login-specific inputs
            user_input = wait.until(
                EC.element_to_be_clickable((By.ID, "login-username"))
            )
            pass_input = wait.until(
                EC.element_to_be_clickable((By.ID, "login-password"))
            )
        except TimeoutException:
            raise RuntimeError(
                "Login inputs not found or not interactable on the login page"
            )

        user_input.clear()
        user_input.send_keys(username)
        pass_input.clear()
        pass_input.send_keys(password)

        # Click the login button when it's clickable
        try:
            login_btn = wait.until(EC.element_to_be_clickable((By.ID, "login")))
            login_btn.click()
        except TimeoutException:
            raise RuntimeError("Login button not found or not clickable")

    def hasOponentMoved(self):
        new = self.getBoardAsFen().split(" ")[0]
        self.CastlingUpdate()
        if new != self.previousFen.split(" ")[0]:
            self.previousFen = new
            return True
        else:
            self.previousFen = new
            return False

    def setTurn(self, turn):
        self.turn = turn
        print("Turn set to: ", turn)

    def updateCastlingRights(self, n):
        self.castlingRights[n] = not (self.castlingRights[n])
        print("Castling rights updated: ", self.castlingRights)
        self.updateCastlingString()

    def updateCastlingString(self):
        castling_symbols = ["K", "Q", "k", "q"]
        self.castlingString = "".join(
            symbol
            for symbol, right in zip(castling_symbols, self.castlingRights)
            if right
        )
        if not self.castlingString:
            self.castlingString = "-"

    def setSkillLevel(self, level):
        self.skillLevel = level
        self.game.set_skill_level(level)

    def setEloLevel(self, level):
        self.elo = level
        self.game.set_elo_rating(level)

    def endGame(self):
        del self.game
        print("Game ended")

    def resetStockfish(self):
        self.game = st.Stockfish(
            stockfish_path,
            depth=18,
            parameters={"Threads": 2, "Minimum Thinking Time": 30},
        )
        print("Stockfish restarted")

    def play(self) -> str | None:
        self.findBoard()
        fen = self.getBoardAsFen()
        self.game.set_fen_position(fen)
        print(self.game.get_board_visual())
        black_time, white_time = self.get_current_player_time()
        self.waitRandomTime()
        t1 = time.perf_counter()
        movestring = self.game.get_best_move()
        t2 = time.perf_counter()
        print(f"Get best move: {t2 - t1:0.4f} seconds")
        print(movestring)
        t1 = time.perf_counter()
        bestmove = convertMoveStringHTML(movestring)
        self.movePiece(*bestmove)
        t2 = time.perf_counter()
        print(f"Move piece: {t2 - t1:0.4f} seconds")

        return movestring

    def getStats(self):
        wdl = self.game.get_wdl_stats()
        return {"wdl": wdl, **self.game.get_evaluation()}

    def get_current_player_time(self):
        """Returns the top most player's time as the first element
        and the bottom player's time as the second element"""
        curr_time = self.find_elements(
            By.CSS_SELECTOR, "span[data-cy='clock-time'].clock-time-monospace"
        )
        if len(curr_time) > 0:
            top_time = convertTimeString_millisecons(curr_time[0].text)
            bottom_time = convertTimeString_millisecons(curr_time[1].text)

            print(top_time, bottom_time)

            return top_time, bottom_time
        return None, None

    def newGame(self):
        if self.find_elements(By.CSS_SELECTOR, "div[class*=game-over]"):
            # click new game button
            self.find_element(
                By.XPATH, '//button[@data-cy="game-over-modal-new-game-button"]'
            ).click()
            self.castlingRights = [True, True, True, True]
            self.castlingString = "KQkq"
            # locate when the new game starts
            while not self.find_element(By.XPATH, "//wc-chess-board"):
                pass
            self.identifyTurn()
            return True
        return False

    def identifyTurn(self):
        element = self.find_element(By.XPATH, "//wc-chess-board")
        class_name = element.get_attribute("class")

        if class_name is None:
            print("Board not found")
            return

        turn = "w"

        if "board" in class_name and "flipped" not in class_name:
            turn = "w"
        elif "board flipped" in class_name:
            turn = "b"
            # press x on the keyboard
            self.find_element(By.XPATH, "//body").send_keys("x")

        self.setTurn(turn)

    def waitRandomTime(self):
        MAX_WAIT_TIME = 50
        MIN_WAIT_TIME = 5
        sleepTime = MIN_WAIT_TIME + random.random() * (MAX_WAIT_TIME - MIN_WAIT_TIME)
        time.sleep(sleepTime)
