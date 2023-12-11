# Chess Bot

This is a Chess Bot that uses the Stockfish chess engine to play chess games.

## Features

- Play chess against a bot powered by the Stockfish chess engine.
- Set the bot's skill level.
- Manually set the turn.

## Installation

1. Clone this repository.
2. Install the required Python packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

3. Download the Stockfish chess engine and set the `stockfish_path` variable in the `.env` file to the path of the Stockfish executable file.

## Usage

Before you start, make sure you have Google Chrome installed on your machine. The bot uses it to automate interactions with chess.com.

1. Run the `gui.py` script to start the application:

    ```bash
    python gui.py
    ```

2. The GUI will open in a new window. Here, you can set the bot's skill level and manually set the turn.

3. Once you've set your preferences, the bot will play on your behalf on chess.com. It uses the Stockfish chess engine to decide its moves.

Remember, the bot requires Google Chrome to be installed on your machine to function correctly.

To build the binary, run the following command:

```bash
pyinstaller --onefile --add-binary='./stockfish-windows-x86-64.exe;.' gui.py
```