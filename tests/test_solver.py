import sys
import os
from collections import defaultdict

# Append the solver directory to sys.path to allow imports during tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../solver')))

from solver_core import _has_enough_letters_flat, _score_word_dfs

def test_has_enough_letters():
    """Validates whether a word is constructible given flat letter counts and allowed swaps."""
    counter = defaultdict(int)
    counter["A"] = 2
    counter["B"] = 1
    
    # Playable without swaps
    assert _has_enough_letters_flat("AAB", counter.copy(), 0) is True
    
    # Unplayable without swaps (Missing an 'A')
    assert _has_enough_letters_flat("AAAB", counter.copy(), 0) is False
    
    # Playable using 1 swap
    assert _has_enough_letters_flat("AAAB", counter.copy(), 1) is True
    
    # Playable using 1 swap replacing a completely non-existent letter
    assert _has_enough_letters_flat("AABZ", counter.copy(), 1) is True

def test_score_word_dfs_basic():
    """Tests the basic score calculation without any diamonds or active multipliers."""
    grid = tuple(tuple(["A"] * 5) for _ in range(5))
    
    score, gems = _score_word_dfs("AAAA", grid, frozenset(), None, frozenset(), frozenset(), 0)
    
    # The letter 'A' is worth 1 point. 4 valid 'A' letters stringed = 4 points.
    assert score == 4
    assert gems == 0

def test_score_word_dfs_with_diamonds():
    """Validates that diamond pickups are accurately reflected in the gems output counter."""
    grid = (
        tuple(["C", "A", "T", "S", "X"]),
        *([tuple(["X"] * 5)] * 4) # Fill the rest of the 5x5 grid with 'X'
    )
    
    # Emplace a diamond on C (0,0) and T (0,2)
    diamonds = frozenset([(0, 0), (0, 2)]) 
    
    score, gems = _score_word_dfs("CATS", grid, diamonds, None, frozenset(), frozenset(), 0)
    
    # C=5, A=1, T=2, S=2 => total of 10 points
    assert score == 10
    # The path should collect both diamonds
    assert gems == 2

def test_unplayable_word():
    """Tests if an impossible to trace word (too physically distant) returns the error score (-1)."""
    # Distant A check: A trace physically impossible with diagonals constraints
    grid2 = (
        tuple(["A", "X", "X", "X", "X"]),
        tuple(["X", "X", "X", "X", "X"]),
        tuple(["X", "X", "A", "X", "X"]),
        tuple(["X", "X", "X", "X", "X"]),
        tuple(["X", "X", "X", "X", "X"]),
    )
    score, gems = _score_word_dfs("AA", grid2, frozenset(), None, frozenset(), frozenset(), 0)
    
    assert score == -1 # Returns -1 as the path is broken
