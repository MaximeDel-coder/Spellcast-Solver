import customtkinter as ctk
import tkinter as tk
import concurrent.futures
import itertools
import os
from collections import defaultdict
from multiprocessing import cpu_count
from functools import lru_cache
from typing import List, Tuple, Optional

from solver_core import worker_task, LETTER_VALUES

GRID_SIZE = 5          
CELL_WIDTH = 2         

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Localization dictionaries
LANGUAGES = {
    "English 🇬🇧": {
        "title": "Spellcast Solver",
        "stages": ["Letters", "Diamonds", "Double Word", "Double Letter", "Triple Letter"],
        "swaps": "Swaps:",
        "threads": "Threads:",
        "reset": "Reset Grid",
        "find": "Find Words!",
        "finding": "Calculating...",
        "score_pri": "🥇 Priority: Best Scores",
        "gems_pri": "💎 Priority: Max Diamonds",
        "err_dict": "The dictionary 'dictionary.csv' was not found."
    },
    "Français 🇫🇷": {
        "title": "Spellcast Solver",
        "stages": ["Lettres", "Diamants", "Mot Double", "Lettre Double", "Lettre Triple"],
        "swaps": "Jokers :",
        "threads": "Threads :",
        "reset": "Remise à Zéro",
        "find": "Chercher les mots !",
        "finding": "Calcul en cours...",
        "score_pri": "🥇 Priorité: Meilleurs Scores",
        "gems_pri": "💎 Priorité: Max Diamants",
        "err_dict": "Le dictionnaire 'dictionary.csv' est introuvable."
    },
    "Deutsch 🇩🇪": {
        "title": "Spellcast Solver",
        "stages": ["Buchstaben", "Diamanten", "Doppelwort", "Doppelbuchstabe", "Dreifachbuchstabe"],
        "swaps": "Joker:",
        "threads": "Threads:",
        "reset": "Zurücksetzen",
        "find": "Wörter finden!",
        "finding": "Berechne...",
        "score_pri": "🥇 Priorität: Beste Punktzahl",
        "gems_pri": "💎 Priorität: Max Diamanten",
        "err_dict": "Das Wörterbuch 'dictionary.csv' wurde nicht gefunden."
    },
    "Español 🇪🇸": {
        "title": "Spellcast Solver",
        "stages": ["Letras", "Diamantes", "Palabra Doble", "Letra Doble", "Letra Triple"],
        "swaps": "Comodines:",
        "threads": "Hilos:",
        "reset": "Reiniciar",
        "find": "¡Buscar palabras!",
        "finding": "Calculando...",
        "score_pri": "🥇 Prioridad: Mejores Puntuaciones",
        "gems_pri": "💎 Prioridad: Max Diamantes",
        "err_dict": "No se encontró el diccionario 'dictionary.csv'."
    }
}

class BoggleApp(ctk.CTk):
    """
    Main Interface (View/Controller) utilizing CustomTkinter for a modern design.
    Integrates the core Boggle algorithmic functionality.
    """

    def __init__(self):
        super().__init__()
        
        self.current_lang = "English 🇬🇧"
        
        self.title(LANGUAGES[self.current_lang]["title"])
        self.geometry("1100x800")
        self.minsize(900, 750)

        # Theme Tracking
        self.is_dark = True
        
        # Grid Entities
        self.cells = []
        self.overlays = []
        
        # Stages Tracking
        self._update_stage_names()
        self.current_stage_idx = 0
        
        # Board Modifier Variables
        self.diamonds: set = set()
        self.double_word: Optional[Tuple[int, int]] = None
        self.double_letter: Optional[Tuple[int, int]] = None
        self.triple_letter: Optional[Tuple[int, int]] = None
        
        # Results Cache
        self.playable_words_by_pts: List = [] 
        self.playable_words_by_gems: List = []
        self.dictionary: Optional[List[str]] = None 
        self.selected_word: Optional[str] = None

        self._build_ui()
        self.update_theme_colors()
        self.cells[0][0].focus_set()

    def _update_stage_names(self):
        stgs = LANGUAGES[self.current_lang]["stages"]
        self.stage_names = {
            stgs[0]: 0, 
            stgs[1]: 1, 
            stgs[2]: 2, 
            stgs[3]: 3, 
            stgs[4]: 4
        }

    def get_colors(self) -> dict:
        if self.is_dark:
            return {
                "default": "#2b2b2b",
                "diamond": "#c2477f",
                "dword": "#2c5b73",
                "dletter": "#3f7a3a",
                "tletter": "#91621f",
                "entry_bg": "#111111", 
                "entry_fg": "white",
                "list_bg": "#1e1e1e",
                "list_fg": "white",
                "cell_border": "#555"
            }
        else:
            return {
                "default": "white",
                "diamond": "#ffa1c9",
                "dword": "#8ec3d6",
                "dletter": "#a3d99f",
                "tletter": "#facc87",
                "entry_bg": "#f8f8f8",
                "entry_fg": "black",
                "list_bg": "white",
                "list_fg": "black",
                "cell_border": "#ccc"
            }

    def _build_ui(self):
        # 1. Top Bar (Title + Lang Dropdown + Theme Switch)
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=10)
        
        lang_dict = LANGUAGES[self.current_lang]
        
        self.lbl_title = ctk.CTkLabel(top_bar, text=lang_dict["title"], font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_title.pack(side="left")
        
        # Wrapper frame providing the requested rounded blue border line
        self.theme_wrapper = ctk.CTkFrame(
            top_bar,
            fg_color="transparent",
            border_width=2,
            border_color="#306998",
            corner_radius=8
        )
        self.theme_wrapper.pack(side="right")
        
        self.theme_segment = ctk.CTkSegmentedButton(
            self.theme_wrapper, 
            values=[" ☀ ", " ☾ "], 
            command=self.toggle_theme_segment,
            font=ctk.CTkFont(size=20),
            selected_color="#306998",
            selected_hover_color="#27567d",
            unselected_color=("#ebebeb", "#242424"),
            unselected_hover_color=("#ebebeb", "#242424"),
            fg_color=("#ebebeb", "#242424"),
            corner_radius=6,
            text_color="white"
        )
        self.theme_segment.set(" ☾ ")
        # Using a small internal pad simulates the inner squared sliding mechanic inside the bounding box
        self.theme_segment.pack(padx=2, pady=2)
        
        self.lang_var = ctk.StringVar(value="English 🇬🇧")
        self.lang_menu = ctk.CTkOptionMenu(top_bar, variable=self.lang_var, values=list(LANGUAGES.keys()), 
                                           command=self.change_language, width=130)
        self.lang_menu.pack(side="right", padx=15)

        # Main Paned Layout (Left / Right split)
        main_paned = ctk.CTkFrame(self, fg_color="transparent")
        main_paned.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        main_paned.grid_columnconfigure(0, weight=4) 
        main_paned.grid_columnconfigure(1, weight=5) 
        main_paned.grid_rowconfigure(0, weight=1)
        
        # --- LEFT PANEL ---
        left_frame = ctk.CTkFrame(main_paned, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        # Responsive Sub-Grid Frame
        self.grid_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        self.grid_frame.pack(pady=10, fill="both", expand=True)

        for r in range(GRID_SIZE):
            self.grid_frame.grid_rowconfigure(r, weight=1)
            row_entries, row_canv = [], []
            for c in range(GRID_SIZE):
                self.grid_frame.grid_columnconfigure(c, weight=1)
                
                cell = tk.Frame(self.grid_frame) 
                cell.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
                
                cv = tk.Canvas(cell, highlightthickness=0)
                cv.place(x=0, y=0, relwidth=1, relheight=1)
                cv.row_index, cv.col_index = r, c
                cv.bind("<Button-1>", self._on_cell_click)
                cv.bind("<Configure>", lambda e, rr=r, cc=c: self._on_canvas_configure(e, rr, cc))
                row_canv.append(cv)

                # Tk Entry reduced to 50% area keeping a 25% border all around
                e = tk.Entry(cell, width=CELL_WIDTH, font=("Arial", 30, "bold"), 
                             justify="center", bd=0, highlightthickness=0)
                e.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.5, relheight=0.5)
                e.row_index, e.col_index = r, c
                e.bind("<Button-1>", self._on_cell_click)
                e.bind("<KeyRelease>", self._on_key)
                row_entries.append(e)

            self.cells.append(row_entries)
            self.overlays.append(row_canv)

        # Modifiers Segmented Button
        self.stage_selector = ctk.CTkSegmentedButton(left_frame, values=list(self.stage_names.keys()), 
                                                     command=self._on_stage_change, font=ctk.CTkFont(size=14))
        # Ensure it selects the translated "Letters" item
        self.stage_selector.set(list(self.stage_names.keys())[0])
        self.stage_selector.pack(pady=20, fill="x")

        # Configurations & Controls
        ctrl_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        ctrl_frame.pack(pady=5, fill="x")
        
        self.lbl_swaps = ctk.CTkLabel(ctrl_frame, text=lang_dict["swaps"], font=ctk.CTkFont(weight="bold"))
        self.lbl_swaps.pack(side="left")
        self.swap_var = ctk.StringVar(value="0")
        self.swap_menu = ctk.CTkOptionMenu(ctrl_frame, variable=self.swap_var, values=["0","1","2","3"], width=60)
        self.swap_menu.pack(side="left", padx=(5, 15))
        
        self.lbl_threads = ctk.CTkLabel(ctrl_frame, text=lang_dict["threads"], font=ctk.CTkFont(weight="bold"))
        self.lbl_threads.pack(side="left")
        self.thread_var = ctk.StringVar(value="0")
        threads_vals = [str(x) for x in range(cpu_count() + 1)]
        self.thread_menu = ctk.CTkOptionMenu(ctrl_frame, variable=self.thread_var, values=threads_vals, width=60)
        self.thread_menu.pack(side="left", padx=5)
        
        self.btn_reset = ctk.CTkButton(left_frame, text=lang_dict["reset"], fg_color="#C84B31", hover_color="#A93B24", command=self.reset_grid, height=40, font=ctk.CTkFont(size=15, weight="bold"))
        self.btn_reset.pack(fill="x", pady=(15,0))

        self.btn_find = ctk.CTkButton(left_frame, text=lang_dict["find"], height=50, font=ctk.CTkFont(size=18, weight="bold"), command=self.find_words)
        self.btn_find.pack(fill="x", pady=15)

        # --- RIGHT PANEL (Stacked Lists) ---
        right_frame = ctk.CTkFrame(main_paned, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_rowconfigure(3, weight=1)
        
        self.lbl_score_pri = ctk.CTkLabel(right_frame, text=lang_dict["score_pri"], font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_score_pri.grid(row=0, column=0, pady=(0, 5), sticky="w")
        self.list_score = tk.Listbox(right_frame, font=("Courier", 16), borderwidth=0, highlightthickness=0)
        self.list_score.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        
        self.lbl_gems_pri = ctk.CTkLabel(right_frame, text=lang_dict["gems_pri"], font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_gems_pri.grid(row=2, column=0, pady=(0, 5), sticky="w")
        self.list_gems = tk.Listbox(right_frame, font=("Courier", 16), borderwidth=0, highlightthickness=0)
        self.list_gems.grid(row=3, column=0, sticky="nsew")

        for lb in (self.list_score, self.list_gems):
            lb.bind("<Motion>", self._on_list_hover)
            lb.bind("<Leave>", self._on_list_leave)
            lb.bind("<<ListboxSelect>>", self._on_list_select)

    def change_language(self, new_lang: str):
        self.current_lang = new_lang
        lang_dict = LANGUAGES[new_lang]
        
        # Title update
        self.title(lang_dict["title"])
        self.lbl_title.configure(text=lang_dict["title"])
        
        # Segmented update
        self._update_stage_names()
        st_vals = list(self.stage_names.keys())
        self.stage_selector.configure(values=st_vals)
        self.stage_selector.set(st_vals[self.current_stage_idx])
        
        # Options and Layout updates
        self.lbl_swaps.configure(text=lang_dict["swaps"])
        self.lbl_threads.configure(text=lang_dict["threads"])
        self.btn_reset.configure(text=lang_dict["reset"])
        self.btn_find.configure(text=lang_dict["find"])
        self.lbl_score_pri.configure(text=lang_dict["score_pri"])
        self.lbl_gems_pri.configure(text=lang_dict["gems_pri"])
        
    def toggle_theme_segment(self, value):
        self.is_dark = (value == " ☾ ")
        ctk.set_appearance_mode("Dark" if self.is_dark else "Light")
        
        text_col = "white" if self.is_dark else "black"
        # Makes sure both icons adapt clearly depending on background
        self.theme_segment.configure(text_color=text_col)
        
        self.update_theme_colors()
        self._on_stage_change(list(self.stage_names.keys())[self.current_stage_idx])

    def update_theme_colors(self):
        colors = self.get_colors()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.cells[r][c].master.configure(bg=colors["cell_border"])
                e = self.cells[r][c]
                e.configure(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["entry_fg"])
                self._update_cell_colour(r, c)
        
        for lb in [self.list_score, self.list_gems]:
            lb.configure(bg=colors["list_bg"], fg=colors["list_fg"], selectbackground="#306998")

    def _on_canvas_configure(self, event, r, c):
        self._update_cell_colour(r, c)

    def _update_cell_colour(self, r: int, c: int) -> None:
        cv = self.overlays[r][c]
        cv.delete("bg_color") 
        
        colors = self.get_colors()
        segments = []
        if (r, c) in self.diamonds:        segments.append(colors["diamond"])
        if (r, c) == self.double_word:     segments.append(colors["dword"])
        if (r, c) == self.double_letter:   segments.append(colors["dletter"])
        if (r, c) == self.triple_letter:   segments.append(colors["tletter"])

        n = len(segments)
        if n == 0:
            cv.configure(bg=colors["default"])
            return
            
        cv.configure(bg=colors["entry_bg"]) 
        w = cv.winfo_width()
        h = cv.winfo_height()
        if w < 2 or h < 2:
            return

        for i, col in enumerate(segments):
            x0 = i * w / n
            x1 = (i + 1) * w / n
            cv.create_rectangle(x0, 0, x1, h, fill=col, width=0, tags="bg_color")
            cv.tag_lower("bg_color")

    def _on_stage_change(self, value):
        self.current_stage_idx = self.stage_names[value]
        
        colors = self.get_colors()
        c = "#1f538d"
        
        # Map localized indices correctly instead of literal string checks
        if self.current_stage_idx == 1: c = colors["diamond"]
        elif self.current_stage_idx == 2: c = colors["dword"]
        elif self.current_stage_idx == 3: c = colors["dletter"]
        elif self.current_stage_idx == 4: c = colors["tletter"]
        
        self.stage_selector.configure(selected_color=c, selected_hover_color=c)

        if self.current_stage_idx == 0:
            self.cells[0][0].focus_set()

    def _on_key(self, event):
        if self.current_stage_idx != 0:
            return
        w: tk.Entry = event.widget
        text = w.get()
        if len(text) > 1: text = text[-1]
        
        w.delete(0, "end")
        if text.isalpha():
            w.insert(0, text.upper())
            self._focus_next(w.row_index, w.col_index)
            
    def _focus_next(self, row: int, col: int):
        idx = row * GRID_SIZE + col
        if idx >= GRID_SIZE * GRID_SIZE - 1: return
        idx += 1
        nr, nc = divmod(idx, GRID_SIZE)
        self.cells[nr][nc].focus_set()

    def _on_cell_click(self, event):
        w = event.widget
        r, c = w.row_index, w.col_index
        
        if self.current_stage_idx == 0:
            e = self.cells[r][c]
            e.focus_set()
            e.select_range(0, "end")
            return
            
        if self.current_stage_idx == 1: # Diamonds
            if (r, c) in self.diamonds: self.diamonds.remove((r, c))
            else: self.diamonds.add((r, c))
        elif self.current_stage_idx == 2: # DW
            self.double_word = None if self.double_word == (r, c) else (r, c)
            for old_r in range(GRID_SIZE):
                for old_c in range(GRID_SIZE):
                    self._update_cell_colour(old_r, old_c) 
        elif self.current_stage_idx == 3: # DL
            if self.double_letter == (r, c): 
                self.double_letter = None
            else:
                self.double_letter = (r, c)
                self.triple_letter = None # clear TL globally
            for old_r in range(GRID_SIZE):
                for old_c in range(GRID_SIZE):
                    self._update_cell_colour(old_r, old_c) 
        elif self.current_stage_idx == 4: # TL
            if self.triple_letter == (r, c): 
                self.triple_letter = None
            else:
                self.triple_letter = (r, c)
                self.double_letter = None # clear DL globally
            for old_r in range(GRID_SIZE):
                for old_c in range(GRID_SIZE):
                    self._update_cell_colour(old_r, old_c) 
            
        self._update_cell_colour(r, c)

    def reset_grid(self) -> None:
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.cells[r][c].delete(0, "end")
                
        self.diamonds.clear()
        self.double_word = None
        self.double_letter = None
        self.triple_letter = None
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self._update_cell_colour(r, c)
                
        def_txt = list(self.stage_names.keys())[0]
        self.stage_selector.set(def_txt)
        self._on_stage_change(def_txt)
        self.list_score.delete(0, "end")
        self.list_gems.delete(0, "end")
        self.selected_word = None
        self._clear_visuals()
        self.cells[0][0].focus_set()

    def _load_dictionary(self) -> List[str]:
        path = os.path.join(os.path.dirname(__file__), "dictionary.csv")
        words = []
        try:
            with open(path, newline="", encoding="utf-8") as f:
                for line in f:
                    w = line.strip().upper()
                    if 5 <= len(w) <= 25 and w.isalpha(): 
                        words.append(w)
        except Exception:
            from tkinter import messagebox
            messagebox.showerror("Error", LANGUAGES[self.current_lang]["err_dict"])
        return words

    def get_grid_letters(self):
        return tuple(tuple(self.cells[r][c].get().upper() for c in range(GRID_SIZE)) for r in range(GRID_SIZE))
        
    def find_words(self):
        if any(not self.cells[r][c].get() for r in range(GRID_SIZE) for c in range(GRID_SIZE)):
            pass
        
        max_swaps = int(self.swap_var.get())
        grid = self.get_grid_letters()
        
        flat_counter = defaultdict(int)
        for r in grid:
            for ch in r:
                if ch: flat_counter[ch] += 1
                
        diamonds = frozenset(self.diamonds)
        dword = self.double_word
        dletters = frozenset([self.double_letter]) if self.double_letter else frozenset()
        tletters = frozenset([self.triple_letter]) if self.triple_letter else frozenset()

        if self.dictionary is None:
            self.dictionary = self._load_dictionary()
            if not self.dictionary: return

        requested = int(self.thread_var.get())
        n_proc = max(1, cpu_count() if requested <= 0 else min(requested, cpu_count()))
        
        chunks = list(itertools.chain.from_iterable(itertools.zip_longest(*[iter(self.dictionary)]*n_proc, fillvalue=None)))
        slices = [[w for w in chunks[i::n_proc] if w] for i in range(n_proc)]

        best_score_glob, best_gems_glob = {}, {}
        
        self.btn_find.configure(text=LANGUAGES[self.current_lang]["finding"], state="disabled")
        self.update()
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=n_proc) as pool:
            futures = [pool.submit(worker_task, (slc, grid, flat_counter, diamonds, dword, dletters, tletters, max_swaps)) for slc in slices]
            for fut in concurrent.futures.as_completed(futures):
                part_score, part_gems = fut.result()
                for w, s in part_score.items():
                    if s > best_score_glob.get(w, -1):
                        best_score_glob[w] = s
                for w, g in part_gems.items():
                    if g > best_gems_glob.get(w, -99):
                        best_gems_glob[w] = g

        combined = []
        for w in set(best_score_glob.keys()) | set(best_gems_glob.keys()):
            s = best_score_glob.get(w, -1)
            g = best_gems_glob.get(w, -99)
            if s != -1: 
                combined.append((w, s, g))

        self.playable_words_by_pts = sorted(combined, key=lambda x: (-x[1], -x[2]))
        self.playable_words_by_gems = sorted(combined, key=lambda x: (-x[2], -x[1]))
        
        self.list_score.delete(0, "end")
        self.list_gems.delete(0, "end")
        self.selected_word = None
        self._clear_visuals()
        for w, s, g in self.playable_words_by_pts[:200]:
            self.list_score.insert("end", f"{w:15} {s:2} Pts | {g} 💎")
        for w, s, g in self.playable_words_by_gems[:200]:
            self.list_gems.insert("end", f"{w:15} {g} 💎  | {s:2} Pts")
            
        self.btn_find.configure(text=LANGUAGES[self.current_lang]["find"], state="normal")

    def _on_list_hover(self, event):
        lb = event.widget
        idx = lb.nearest(event.y)
        if idx < 0:
            self._on_list_leave(event)
            return
        line = lb.get(idx)
        if not line: return
        word = line.split()[0]
        if getattr(self, "_hover_word", None) == word:
            return
        self._hover_word = word
        self.highlight_path(word)

    def _on_list_leave(self, event):
        self._hover_word = None
        if getattr(self, "selected_word", None):
            self.highlight_path(self.selected_word)
        else:
            self._clear_visuals()

    def _on_list_select(self, event):
        lb = event.widget
        sel = lb.curselection()
        if sel:
            line = lb.get(sel[0])
            if line:
                self.selected_word = line.split()[0]
                self.highlight_path(self.selected_word)

    def _clear_visuals(self):
        for row in self.overlays:
            for cv in row:
                cv.delete("path")

    def _find_path(self, word: str) -> Optional[List[Tuple[int, int, bool]]]:
        L = len(word)
        dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        grid = self.get_grid_letters()
        swaps_max = int(self.swap_var.get())

        @lru_cache(maxsize=None)
        def dfs(r, c, idx, used_mask, swaps_left):
            if idx == L: return []
            for dr, dc in dirs:
                nr, nc = r+dr, c+dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    pos = nr*GRID_SIZE + nc
                    if used_mask & (1<<pos): continue
                    letter = grid[nr][nc]
                    needed = word[idx]
                    
                    is_swap = (letter != needed)
                    if is_swap and swaps_left == 0: continue
                    res = dfs(nr, nc, idx+1, used_mask|(1<<pos), swaps_left - is_swap)
                    if res is not None:
                        return [(nr, nc, is_swap)] + res
            return None

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                letter = grid[r][c]
                if not letter: continue
                is_swap = (letter != word[0])
                if is_swap and swaps_max == 0: continue
                path = dfs(r, c, 1, 1 << (r*GRID_SIZE + c), swaps_max - is_swap)
                if path is not None:
                    return [(r, c, is_swap)] + path
        return None

    def highlight_path(self, word: str):
        self._clear_visuals()
        path = self._find_path(word)
        if not path: return
        
        path_color = "white" if self.is_dark else "black"

        for i, (r, c, is_swap) in enumerate(path):
            cv = self.overlays[r][c]
            label_color = "#E85D04" if is_swap else path_color
            
            label = f"{i+1}{'*' if is_swap else ''}"
            # Anchored exactly at top-left to avoid intersecting with the middle text Entry
            cv.create_text(8, 8, text=label, anchor="nw",
                           font=("Arial", 16, "bold"), tags="path", fill=label_color)
            cv.tag_raise("path")

if __name__ == "__main__":
    app = BoggleApp()
    app.mainloop()
