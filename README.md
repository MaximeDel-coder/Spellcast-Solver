# Spellcast Solver

A powerful 5x5 word solver built in Python with a modern graphical interface (`customtkinter`), **specifically designed for the Discord activity "Spellcast"**. Please note that this is *not* a general-purpose Boggle solver. This solver helps you find the highest scoring words on a Spellcast board, taking into account special tiles like Diamonds, Double Words (DW), Double Letters (DL), Triple Letters (TL), and even letter swaps (blanks)!

## Features
- **5x5 Interactive Grid**: Click and type letters directly into the intuitive UI.
- **Special Tiles Annotations**: Mark specific tiles for Diamonds, Double Words, Double Letters, and Triple Letters to calculate the exact maximum score.
- **Swap Support**: Configure how many letter swaps are allowed, and let the solver handle the complex permutations.
- **Multithreaded Deep Search**: Utilizes your CPU cores via Python's multithreading/multiprocessing to crunch the dictionary and calculate the paths incredibly fast.
- **Visual Path Highlights**: Hover over a result word to preview its path, or click on it to lock the path permanently over the grid. A letter marked with an asterisk `*` designates a swap!
- **Internationalization**: UI supports English, French, German, and Spanish dynamically.
- **Dark/Light Mode**: Beautiful modern UI that adapts to your preferences.

## Project Structure
- `solver/main.py`: The main GUI application. Run this to use the program!
- `solver/solver_core.py`: The core multithreaded DFS engine.
- `solver/dictionary.csv`: A comprehensive list of valid playable words.
- `build_dictionary.py`: A utility script that leverages the `nltk` library to fetch English lemmas and build an initial CSV dictionary from WordNet.
- `tests/test_solver.py`: Unit test suite ensuring the reliability of the solver.

## Installation

1. Ensure you have **Python 3.10+** installed.
2. Clone or download this repository.
3. It is highly recommended to use a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Mac/Linux
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Use the Solver

1. Start the planner by running:
   ```bash
   python solver/main.py
   ```
2. **Letters Stage**: Fill the 5x5 grid by typing the characters. The cursor automatically advances to the next cell.
3. **Diamonds Stage**: Select "Diamonds" from the modifier bar. Click on any grid cell that contains a diamond to highlight it.
4. **Multiplier Stages**: Select the appropriate option (Double Word, Double/Triple Letter) and click on cells to define their multipliers.
5. **Swaps & Threads**: Indicate the maximum number of letter swaps allowed (0 to 3) and how many CPU threads to allocate for the search.
6. **Find Words**: Click the "Find words!" button. The multithreaded engine will find all possible word paths and display them sorted by either "Top by Score" or "Top by Diamonds".
7. **View Path**: Hover your mouse over any word in the lists to highlight the path required to spell it on the board.

## License

This project is licensed under the **MIT License**. You are free to copy, modify, publish, use, and distribute this software, provided you include the original copyright notice and permission notice. See the `LICENSE` file for more details.
