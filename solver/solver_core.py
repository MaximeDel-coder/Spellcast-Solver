from typing import Dict, Set, Tuple, List, Optional
from functools import lru_cache

# Letter scores (approximate Spellcast / Scrabble values)
LETTER_VALUES: Dict[str, int] = {
    "A": 1, "B": 4, "C": 5, "D": 3, "E": 1, "F": 5,
    "G": 3, "H": 4, "I": 1, "J": 7, "K": 6, "L": 3,
    "M": 4, "N": 2, "O": 1, "P": 4, "Q": 8, "R": 2,
    "S": 2, "T": 2, "U": 4, "V": 5, "W": 5, "X": 7,
    "Y": 4, "Z": 8,
}

def _has_enough_letters_flat(word: str, counter: Dict[str, int], swaps: int) -> bool:
    """
    Verifies if 'word' can be spelled using the available letters and the allowed number of swaps.
    
    Args:
        word (str): The target word to check.
        counter (Dict[str, int]): Character frequency counter from the grid.
        swaps (int): Number of allowed letter swaps (blanks).
        
    Returns:
        bool: True if the word is buildable, False otherwise.
    """
    missing = 0
    for ch in word:
        if counter[ch] > 0:
            counter[ch] -= 1
        else:
            missing += 1
            if missing > swaps:
                return False
    return True

def _score_word_dfs(
    word: str, 
    grid: Tuple[Tuple[str, ...], ...], 
    diamonds: frozenset, 
    dword: Optional[Tuple[int, int]], 
    dletters: frozenset, 
    tletters: frozenset, 
    swaps: int
) -> Tuple[int, int]:
    """
    Performs a depth-first search (DFS) to validate the physical path of a word on the 5x5 grid
    and calculates its maximum possible score considering all multipliers and diamonds.
    
    Args:
        word: The target word to trace.
        grid: A 5x5 tuple grid representing the letters on the board.
        diamonds, dword, dletters, tletters: Grid coordinates (r, c) of the corresponding specials.
        swaps: Maximum allowed swapped letters during the trace.
        
    Returns:
        Tuple[int, int]: (Best Score, Number of extra diamonds collected (net of swaps)).
                         Returns (-1, -99) if the word cannot be physically traced.
    """
    L = len(word)
    # 8 possible directions (horizontal, vertical, diagonal)
    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    best_score = -1
    best_gems = -99

    @lru_cache(maxsize=None)
    def dfs(r: int, c: int, idx: int, used_mask: int, swaps_left: int, score: int, word_mult: int, gems: int) -> None:
        nonlocal best_score, best_gems
        # Base case: word is fully traced
        if idx == L:
            final = score * word_mult
            if final > best_score or (final == best_score and gems - swaps > best_gems):
                best_score, best_gems = final, gems - swaps
            return
            
        # Recursive DFS exploring neighboring cells
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 5 and 0 <= nc < 5:
                pos = nr * 5 + nc
                if used_mask & (1 << pos): 
                    continue
                
                letter = grid[nr][nc]
                needed = word[idx]
                
                # Apply multipliers and gems
                mult = 3 if (nr, nc) in tletters else 2 if (nr, nc) in dletters else 1
                new_score = score + LETTER_VALUES[needed] * mult
                new_word_mult = word_mult * 2 if (nr, nc) == dword else word_mult
                new_gems = gems + ((nr, nc) in diamonds)
                new_mask = used_mask | (1 << pos)
                
                if letter == needed:
                    dfs(nr, nc, idx + 1, new_mask, swaps_left, new_score, new_word_mult, new_gems)
                elif swaps_left > 0:
                    dfs(nr, nc, idx + 1, new_mask, swaps_left - 1, new_score, new_word_mult, new_gems)

    # Initial grid entry points
    for r in range(5):
        for c in range(5):
            pos = r * 5 + c
            letter = grid[r][c]
            needed = word[0]
            
            mult = 3 if (r, c) in tletters else 2 if (r, c) in dletters else 1
            base = LETTER_VALUES.get(needed, 0) * mult
            word_mult = 2 if (r, c) == dword else 1
            gems = ((r, c) in diamonds)
            
            if letter == needed:
                dfs(r, c, 1, 1 << pos, swaps, base, word_mult, gems)
            elif swaps > 0:
                dfs(r, c, 1, 1 << pos, swaps - 1, base, word_mult, gems)
                
    return best_score, best_gems

def worker_task(args: Tuple) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Parallel worker task to analyze a fragmented section of the main dictionary.
    
    Args: 
        A tuple comprising:
        - word_slice: A slice of dictionary words to process.
        - grid, flat_counter, diamonds, dword, dletters, tletters: Grid state metadata.
        - max_swaps: Allowed swaps integer.
        
    Returns:
        Two dictionaries mapping valid words to their {word: best_score} and {word: best_gems}.
    """
    word_slice, grid, flat_counter, diamonds, dword, dletters, tletters, max_swaps = args
    best_score_dict: Dict[str, int] = {}
    best_gems_dict: Dict[str, int] = {}
    
    for swaps in range(max_swaps + 1):
        for word in word_slice:
            # Recreate counter mask for every word iteration
            counter_copy = flat_counter.copy()
            if not _has_enough_letters_flat(word, counter_copy, swaps):
                continue
            
            score, gems = _score_word_dfs(word, grid, diamonds, dword, dletters, tletters, swaps)
            if score == -1:          
                continue  # word is unplayable via DFS
                
            if score > best_score_dict.get(word, -1):
                best_score_dict[word] = score
            if gems > best_gems_dict.get(word, -99):
                best_gems_dict[word] = gems
                
    return best_score_dict, best_gems_dict
