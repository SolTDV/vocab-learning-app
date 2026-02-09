import tkinter as tk
from tkinter import ttk, messagebox, font
import core as core
from datetime import datetime, date, timedelta
import math


# ==================================================
# CONFIGURATION & THEMING
# ==================================================

class Colors:
    """Centralized color palette for consistent design."""
    # Primary brand colors
    PRIMARY = "#3b82f6"  # Bright blue
    PRIMARY_DARK = "#1d4ed8"  # Darker blue
    PRIMARY_LIGHT = "#60a5fa"  # Lighter blue

    # Status colors
    SUCCESS = "#10b981"  # Green (correct)
    WARNING = "#f59e0b"  # Amber (hard)
    DANGER = "#ef4444"  # Red (incorrect)

    # Neutrals - using the light blue color from screenshot
    BG_PRIMARY = "#0f172a"  # Very dark (almost black)
    BG_SECONDARY = "#1e293b"  # Dark gray-blue
    BG_TERTIARY = "#334155"  # Medium gray-blue

    TEXT_PRIMARY = "#60a5fa"  # Light blue (from screenshot - very visible)
    TEXT_SECONDARY = "#93c5fd"  # Even lighter blue
    TEXT_MUTED = "#3b82f6"  # Medium blue

    # Special
    ACCENT = "#06b6d4"  # Cyan
    BORDER = "#475569"  # Border color
    OVERLAY = "rgba(0, 0, 0, 0.8)"


class Fonts:
    """Centralized font definitions."""

    def __init__(self):
        self.title_large = font.Font(size=16, weight="bold")
        self.title_medium = font.Font(size=13, weight="bold")
        self.title_small = font.Font(size=11, weight="bold")
        self.body = font.Font(size=10)
        self.body_small = font.Font(size=9)
        self.mono = font.Font(family="Courier", size=10)


fonts = None  # Will be initialized after root is created


# ==================================================
# UTILITY COMPONENTS
# ==================================================

class Card(tk.Frame):
    """Reusable card component with consistent styling."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=Colors.BG_SECONDARY,
            relief=tk.FLAT,
            bd=0,
            **kwargs
        )
        self.config(highlightthickness=1, highlightbackground=Colors.BORDER)


class StatBox(tk.Frame):
    """Display a single statistic with label and value."""

    def __init__(self, parent, label: str, value: str = "0", value_color=Colors.ACCENT):
        super().__init__(parent, bg=Colors.BG_SECONDARY)

        tk.Label(
            self,
            text=value,
            font=fonts.title_large,
            fg=value_color,
            bg=Colors.BG_SECONDARY
        ).pack(anchor="center")

        tk.Label(
            self,
            text=label,
            font=fonts.body_small,
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY
        ).pack(anchor="center")

        self.value_label = self.winfo_children()[0]


class ProgressRing(tk.Canvas):
    """Circular progress indicator."""

    def __init__(self, parent, value: float = 0, size: int = 80, **kwargs):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=Colors.BG_PRIMARY,
            highlightthickness=0,
            **kwargs
        )
        self.size = size
        self.value = value
        self.draw_ring(value)

    def draw_ring(self, value: float):
        """Draw circular progress ring."""
        self.delete("all")

        radius = self.size / 2 - 8
        center = self.size / 2

        # Background ring
        self.create_oval(
            center - radius, center - radius,
            center + radius, center + radius,
            outline=Colors.BG_TERTIARY,
            width=6
        )

        # Progress ring
        angle = (value / 100) * 360
        self.create_arc(
            center - radius, center - radius,
            center + radius, center + radius,
            start=90, extent=-angle,
            outline=Colors.PRIMARY,
            width=6,
            style=tk.ARC
        )

        # Center text
        self.create_text(
            center, center,
            text=f"{int(value)}%",
            font=fonts.title_small,
            fill=Colors.TEXT_PRIMARY
        )


# ==================================================
# MAIN APPLICATION
# ==================================================

class VocabTrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vocab Trainer")
        self.root.geometry("1000x700")
        self.root.config(bg=Colors.BG_PRIMARY)

        # Initialize fonts now that root exists
        global fonts
        fonts = Fonts()

        # Session tracking
        self.session_active = False
        self.session_stats = {
            "reviewed": 0,
            "correct": 0,
            "word_results": {}
        }

        # Configure style
        self.setup_styles()

        # Create UI
        self.create_ui()
        self.refresh_all()

        # Handle close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_styles(self):
        """Configure ttk styles for dark theme."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        style.configure(
            "TNotebook",
            background=Colors.BG_PRIMARY,
            foreground=Colors.TEXT_PRIMARY
        )
        style.configure(
            "TNotebook.Tab",
            background=Colors.BG_SECONDARY,
            foreground=Colors.TEXT_PRIMARY,
            padding=[20, 10]
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", Colors.PRIMARY)],
            foreground=[("selected", Colors.TEXT_PRIMARY)]
        )

        # Treeview
        style.configure(
            "Treeview",
            background=Colors.BG_SECONDARY,
            foreground=Colors.TEXT_PRIMARY,
            fieldbackground=Colors.BG_SECONDARY,
            borderwidth=0
        )
        style.configure("Treeview.Heading", background=Colors.BG_TERTIARY)
        style.map("Treeview", background=[("selected", Colors.PRIMARY)])

        # Progressbar
        style.configure(
            "TProgressbar",
            background=Colors.PRIMARY,
            troughcolor=Colors.BG_TERTIARY
        )

    def create_ui(self):
        """Build main UI structure."""
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Study tab
        self.study_tab = tk.Frame(self.notebook, bg=Colors.BG_PRIMARY)
        self.notebook.add(self.study_tab, text="📚 Study")
        self.create_study_tab()

        # Words tab
        self.words_tab = tk.Frame(self.notebook, bg=Colors.BG_PRIMARY)
        self.notebook.add(self.words_tab, text="📝 Manage Words")
        self.create_words_tab()

        # Stats tab
        self.stats_tab = tk.Frame(self.notebook, bg=Colors.BG_PRIMARY)
        self.notebook.add(self.stats_tab, text="📊 Statistics")
        self.create_stats_tab()

    def create_study_tab(self):
        """Build the study/dashboard tab."""
        # Main container
        main_frame = tk.Frame(self.study_tab, bg=Colors.BG_PRIMARY)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        tk.Label(
            main_frame,
            text="Daily Dashboard",
            font=fonts.title_large,
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_PRIMARY
        ).pack(anchor="w", pady=(0, 20))

        # Dashboard card
        dashboard_card = Card(main_frame)
        dashboard_card.pack(fill="x", pady=(0, 20))

        # Stats grid
        stats_grid = tk.Frame(dashboard_card, bg=Colors.BG_SECONDARY)
        stats_grid.pack(fill="x", padx=15, pady=15)

        # Create stat boxes
        stats_frame = tk.Frame(stats_grid, bg=Colors.BG_SECONDARY)
        stats_frame.pack(fill="x")

        self.stat_streak = StatBox(stats_frame, "Current Streak", "0")
        self.stat_streak.pack(side="left", expand=True)

        self.stat_due = StatBox(stats_frame, "Due Today", "0")
        self.stat_due.pack(side="left", expand=True)

        self.stat_xp = StatBox(stats_frame, "Total XP", "0", Colors.WARNING)
        self.stat_xp.pack(side="left", expand=True)

        self.stat_words = StatBox(stats_frame, "Total Words", "0")
        self.stat_words.pack(side="left", expand=True)

        # Progress
        tk.Label(
            dashboard_card,
            text="Today's Progress",
            font=fonts.body_small,
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY
        ).pack(anchor="w", padx=15, pady=(10, 5))

        progress_frame = tk.Frame(dashboard_card, bg=Colors.BG_SECONDARY)
        progress_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.progress_ring = ProgressRing(progress_frame, 0, size=100)
        self.progress_ring.pack(side="left", padx=(0, 20))

        progress_info = tk.Frame(progress_frame, bg=Colors.BG_SECONDARY)
        progress_info.pack(side="left", expand=True, fill="y")

        tk.Label(
            progress_info,
            text="0 / 0 words studied",
            font=fonts.body,
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY
        ).pack(anchor="w")

        tk.Label(
            progress_info,
            text="Keep up the momentum!",
            font=fonts.body_small,
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY
        ).pack(anchor="w")

        self.progress_label = progress_info.winfo_children()[0]
        self.progress_sublabel = progress_info.winfo_children()[1]

        # Study controls
        control_card = Card(main_frame)
        control_card.pack(fill="x", pady=(0, 20))

        control_frame = tk.Frame(control_card, bg=Colors.BG_SECONDARY)
        control_frame.pack(fill="x", padx=15, pady=15)

        tk.Label(
            control_frame,
            text="Study Target",
            font=fonts.body_small,
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY
        ).pack(anchor="w")

        input_frame = tk.Frame(control_frame, bg=Colors.BG_SECONDARY)
        input_frame.pack(fill="x", pady=(5, 0))

        self.target_entry = tk.Entry(
            input_frame,
            width=10,
            font=fonts.body,
            bg=Colors.BG_TERTIARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT,
            relief=tk.FLAT,
            bd=0
        )
        self.target_entry.pack(side="left", padx=(0, 10))
        self.target_entry.insert(0, "10")

        # Study button
        self.study_btn = tk.Button(
            input_frame,
            text="🚀 Start Study Session",
            command=self.start_session,
            font=fonts.title_small,
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=8,
            activebackground=Colors.PRIMARY_DARK,
            activeforeground=Colors.TEXT_PRIMARY
        )
        self.study_btn.pack(side="left")

        # Heatmap button
        tk.Button(
            control_card,
            text="📅 View Heatmap",
            command=self.show_heatmap,
            font=fonts.body_small,
            bg=Colors.BG_TERTIARY,
            fg=Colors.ACCENT,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5
        ).pack(pady=10)

    def create_words_tab(self):
        """Build the word management tab."""
        main_frame = tk.Frame(self.words_tab, bg=Colors.BG_PRIMARY)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        tk.Label(
            main_frame,
            text="Manage Vocabulary",
            font=fonts.title_large,
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_PRIMARY
        ).pack(anchor="w", pady=(0, 20))

        # Add word card
        add_card = Card(main_frame)
        add_card.pack(fill="x", pady=(0, 20))

        add_frame = tk.Frame(add_card, bg=Colors.BG_SECONDARY)
        add_frame.pack(fill="x", padx=15, pady=15)

        # Input fields
        fields = [
            ("Word", "word_entry"),
            ("Example Sentence", "sentence_entry"),
            ("Meaning / Notes", "note_entry")
        ]

        for label, attr_name in fields:
            tk.Label(
                add_frame,
                text=label,
                font=fonts.body_small,
                fg=Colors.TEXT_SECONDARY,
                bg=Colors.BG_SECONDARY
            ).pack(anchor="w", pady=(5, 2))

            entry = tk.Entry(
                add_frame,
                width=50,
                font=fonts.body,
                bg=Colors.BG_TERTIARY,
                fg=Colors.TEXT_PRIMARY,
                insertbackground=Colors.ACCENT,
                relief=tk.FLAT,
                bd=0
            )
            entry.pack(fill="x", pady=(0, 10))
            setattr(self, attr_name, entry)

        tk.Button(
            add_frame,
            text="+ Add Word",
            command=self.add_word,
            font=fonts.title_small,
            bg=Colors.SUCCESS,
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            activebackground="#059669"
        ).pack(anchor="w", pady=(10, 0))

        # Search card
        search_card = Card(main_frame)
        search_card.pack(fill="x", pady=(0, 20))

        search_frame = tk.Frame(search_card, bg=Colors.BG_SECONDARY)
        search_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(
            search_frame,
            text="🔍 Search",
            font=fonts.body_small,
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY
        ).pack(anchor="w")

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=fonts.body,
            bg=Colors.BG_TERTIARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT,
            relief=tk.FLAT,
            bd=0
        )
        self.search_entry.pack(fill="x", pady=(5, 0))
        self.search_var.trace_add("write", lambda *args: self.refresh_word_table())

        # Words table
        table_card = Card(main_frame)
        table_card.pack(fill="both", expand=True)

        table_frame = tk.Frame(table_card, bg=Colors.BG_SECONDARY)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("word", "sentence", "note", "accuracy")
        self.word_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15
        )

        # Configure columns
        widths = {"word": 80, "sentence": 250, "note": 120, "accuracy": 70}
        for col in columns:
            self.word_table.heading(col, text=col.title())
            self.word_table.column(col, width=widths.get(col, 100))

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.word_table.yview)
        self.word_table.configure(yscroll=scrollbar.set)

        self.word_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind events
        self.word_table.bind("<Double-1>", lambda e: self.show_word_details())

        # Action buttons
        btn_frame = tk.Frame(main_frame, bg=Colors.BG_PRIMARY)
        btn_frame.pack(fill="x", pady=(10, 0))

        tk.Button(
            btn_frame,
            text="✏️ Edit",
            command=self.edit_word_dialog,
            font=fonts.body_small,
            bg=Colors.ACCENT,
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            btn_frame,
            text="🗑️ Delete",
            command=self.delete_word,
            font=fonts.body_small,
            bg=Colors.DANGER,
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5
        ).pack(side="left")

    def create_stats_tab(self):
        """Build the statistics tab."""
        main_frame = tk.Frame(self.stats_tab, bg=Colors.BG_PRIMARY)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        tk.Label(
            main_frame,
            text="Statistics & Progress",
            font=fonts.title_large,
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_PRIMARY
        ).pack(anchor="w", pady=(0, 20))

        # Overall stats card
        stats_card = Card(main_frame)
        stats_card.pack(fill="x", pady=(0, 20))

        stats_frame = tk.Frame(stats_card, bg=Colors.BG_SECONDARY)
        stats_frame.pack(fill="x", padx=15, pady=15)

        self.stat_accuracy = StatBox(stats_frame, "Overall Accuracy", "0%", Colors.SUCCESS)
        self.stat_accuracy.pack(side="left", expand=True)

        self.stat_reviews = StatBox(stats_frame, "Total Reviews", "0")
        self.stat_reviews.pack(side="left", expand=True)

        self.stat_longest_streak = StatBox(stats_frame, "Longest Streak", "0", Colors.WARNING)
        self.stat_longest_streak.pack(side="left", expand=True)

        # Box distribution
        dist_card = Card(main_frame)
        dist_card.pack(fill="x", pady=(0, 20))

        tk.Label(
            dist_card,
            text="Memory Boxes Distribution",
            font=fonts.title_small,
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY
        ).pack(anchor="w", padx=15, pady=(10, 5))

        dist_frame = tk.Frame(dist_card, bg=Colors.BG_SECONDARY)
        dist_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.box_labels = {}
        for i in range(1, 6):
            tk.Label(
                dist_frame,
                text=f"Box {i}: 0",
                font=fonts.body_small,
                fg=Colors.TEXT_SECONDARY,
                bg=Colors.BG_SECONDARY
            ).pack(anchor="w")
            self.box_labels[i] = dist_frame.winfo_children()[-1]

        # Difficult words
        difficult_card = Card(main_frame)
        difficult_card.pack(fill="x")

        tk.Label(
            difficult_card,
            text="Most Difficult Words",
            font=fonts.title_small,
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.difficult_frame = tk.Frame(difficult_card, bg=Colors.BG_SECONDARY)
        self.difficult_frame.pack(fill="x", padx=15, pady=(0, 15))

    # ==================================================
    # STUDY SESSION
    # ==================================================

    def start_session(self):
        """Start a study session."""
        if self.session_active:
            messagebox.showinfo("Session Running", "Finish current session first")
            return

        try:
            target = int(self.target_entry.get())
            if target <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid positive number")
            return

        self.session_active = True
        self.session_stats = {"reviewed": 0, "correct": 0, "word_results": {}}

        plan = core.build_study_plan(target)
        if not plan:
            messagebox.showinfo("No Words", "No words available to study")
            self.session_active = False
            return

        self.open_session_window(plan)

    def open_session_window(self, plan: list):
        """Open the study session window."""
        session_window = tk.Toplevel(self.root)
        session_window.title("Study Session")
        session_window.geometry("600x450")
        session_window.config(bg=Colors.BG_PRIMARY)

        # Session state
        state = {
            "index": 0,
            "correct": 0,
            "reviewed": 0,
            "can_rate": False,
            "answered": False,
            "hint_level": 0,
            "hint_used": False
        }

        # Header
        header = tk.Frame(session_window, bg=Colors.BG_PRIMARY)
        header.pack(fill="x", padx=20, pady=10)

        tk.Label(
            header,
            text=f"Word {1}/{len(plan)}",
            font=fonts.title_small,
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_PRIMARY
        ).pack(side="left")

        stats_lbl = tk.Label(
            header,
            text="",
            font=fonts.body_small,
            fg=Colors.ACCENT,
            bg=Colors.BG_PRIMARY
        )
        stats_lbl.pack(side="right")

        # Card
        card = Card(session_window)
        card.pack(fill="both", expand=True, padx=20, pady=10)

        card_frame = tk.Frame(card, bg=Colors.BG_SECONDARY)
        card_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Sentence
        sentence_lbl = tk.Label(
            card_frame,
            text="",
            font=fonts.title_medium,
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY,
            wraplength=500,
            justify="center",
            pady=15
        )
        sentence_lbl.pack(pady=(0, 20), fill="x")

        # Answer input
        answer_entry = tk.Entry(
            card_frame,
            font=fonts.body,
            bg=Colors.BG_TERTIARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT,
            relief=tk.FLAT,
            bd=0,
            width=30
        )
        answer_entry.pack(pady=(0, 10))

        # Hint
        hint_lbl = tk.Label(
            card_frame,
            text="",
            font=fonts.body_small,
            fg=Colors.TEXT_MUTED,
            bg=Colors.BG_SECONDARY
        )
        hint_lbl.pack(pady=(0, 10))

        tk.Button(
            card_frame,
            text="💡 Hint",
            command=lambda: self.show_hint(state, plan, hint_lbl),
            font=fonts.body_small,
            bg=Colors.BG_TERTIARY,
            fg=Colors.ACCENT,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5
        ).pack(pady=(0, 20))

        # Feedback
        feedback_lbl = tk.Label(
            card_frame,
            text="",
            font=fonts.body,
            fg=Colors.SUCCESS,
            bg=Colors.BG_SECONDARY
        )
        feedback_lbl.pack(pady=(0, 15))

        # Submit button
        def submit():
            guess = answer_entry.get().strip()
            if not guess or state["answered"]:
                return

            state["answered"] = True
            word = plan[state["index"]]
            is_correct = guess.lower() == word.lower()

            if is_correct:
                feedback_lbl.config(text="✓ Correct!", fg=Colors.SUCCESS)
                core.vocab[word]["times_correct"] += 1
                state["correct"] += 1
            else:
                feedback_lbl.config(text=f"✗ Wrong — {word}", fg=Colors.DANGER)

            core.vocab[word]["times_reviewed"] += 1
            core.progress["total_reviews"] = core.progress.get("total_reviews", 0) + 1
            state["reviewed"] += 1  # Track reviews in session
            self.session_stats["reviewed"] += 1
            if is_correct:
                self.session_stats["correct"] += 1

            # Record history
            core.vocab[word].setdefault("history", []).append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "correct": is_correct
            })

            # Update stats
            stats_lbl.config(
                text=f"Accuracy: {(state['correct'] / max(1, state['index'] + 1) * 100):.0f}%"
            )

            # Enable rating
            state["can_rate"] = True
            for btn in rating_buttons:
                btn.config(state="normal")
            submit_btn.config(state="disabled")

        submit_btn = tk.Button(
            card_frame,
            text="Submit",
            command=submit,
            font=fonts.title_small,
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=8,
            activebackground=Colors.PRIMARY_DARK
        )
        submit_btn.pack()

        session_window.bind("<Return>", lambda e: submit() if not state["answered"] else None)
        answer_entry.focus()

        # Rating buttons
        btn_frame = tk.Frame(card_frame, bg=Colors.BG_SECONDARY)
        btn_frame.pack(fill="x", pady=15)

        def rate(rating):
            if not state["can_rate"]:
                return

            word = plan[state["index"]]
            core.schedule_next_review(word, rating)
            core.save_vocab()

            state["index"] += 1

            if state["index"] >= len(plan):
                self.finish_session(plan, state, session_window)
            else:
                self.load_study_word(state, plan, sentence_lbl, answer_entry,
                                     hint_lbl, feedback_lbl, stats_lbl, submit_btn)

        rating_buttons = [
            tk.Button(btn_frame, text="1 Again", command=lambda: rate(1),
                      font=fonts.body_small, bg=Colors.DANGER, fg="blue",
                      relief=tk.FLAT, bd=0, padx=10, pady=5, state="disabled"),
            tk.Button(btn_frame, text="2 Hard", command=lambda: rate(2),
                      font=fonts.body_small, bg=Colors.WARNING, fg="blue",
                      relief=tk.FLAT, bd=0, padx=10, pady=5, state="disabled"),
            tk.Button(btn_frame, text="3 Good", command=lambda: rate(3),
                      font=fonts.body_small, bg=Colors.ACCENT, fg="blue",
                      relief=tk.FLAT, bd=0, padx=10, pady=5, state="disabled"),
            tk.Button(btn_frame, text="4 Easy", command=lambda: rate(4),
                      font=fonts.body_small, bg=Colors.SUCCESS, fg="blue",
                      relief=tk.FLAT, bd=0, padx=10, pady=5, state="disabled"),
        ]

        for btn in rating_buttons:
            btn.pack(side="left", padx=5)

        session_window.bind("1", lambda e: rate(1) if state["can_rate"] else None)
        session_window.bind("2", lambda e: rate(2) if state["can_rate"] else None)
        session_window.bind("3", lambda e: rate(3) if state["can_rate"] else None)
        session_window.bind("4", lambda e: rate(4) if state["can_rate"] else None)

        self.load_study_word(state, plan, sentence_lbl, answer_entry,
                             hint_lbl, feedback_lbl, stats_lbl, submit_btn)

    def load_study_word(self, state, plan, sentence_lbl, answer_entry,
                        hint_lbl, feedback_lbl, stats_lbl, submit_btn):
        """Load next word in study session."""
        word = plan[state["index"]]
        sentence = core.vocab[word]["sentence"]
        # Replace word with brackets so it's clearly visible as a blank
        blank = core.re.sub(word, f"[{len(word) * '_'}]", sentence, flags=core.re.IGNORECASE)

        sentence_lbl.config(text=blank, fg=Colors.TEXT_PRIMARY)
        answer_entry.delete(0, tk.END)
        hint_lbl.config(text="")
        feedback_lbl.config(text="")
        submit_btn.config(state="normal")

        state["can_rate"] = False
        state["answered"] = False
        state["hint_level"] = 0
        state["hint_used"] = False

        answer_entry.focus()

    def show_hint(self, state, plan, hint_lbl):
        """Show hint for current word."""
        word = plan[state["index"]]
        state["hint_level"] = min(state["hint_level"] + 1, len(word))
        state["hint_used"] = True

        # Show letters revealed so far with visual separation
        revealed = word[:state["hint_level"]]
        remaining = "•" * (len(word) - state["hint_level"])  # Bullets for hidden letters
        hint = revealed + remaining
        hint_lbl.config(text=f"💡 Hint: {hint}", fg=Colors.ACCENT)

    def finish_session(self, plan, state, session_window):
        """Finish study session and show summary."""
        core.update_streak()

        # Track for the daily goal: how many reviews were completed in this session
        num_reviews_this_session = state["reviewed"]

        core.progress["studied_today"] = core.progress.get("studied_today", 0) + num_reviews_this_session
        core.progress["xp"] = core.progress.get("xp", 0) + state["correct"] * 5

        today = str(date.today())
        history = core.progress.setdefault("history", {})
        # History tracks number of words reviewed per day
        history[today] = history.get(today, 0) + num_reviews_this_session

        core.save_progress()
        core.save_vocab()

        new_achievements = core.check_achievements()
        if new_achievements:
            messagebox.showinfo("🎉 Achievements Unlocked", "\n".join(new_achievements))

        session_window.destroy()
        self.session_active = False

        accuracy = (state["correct"] / len(plan) * 100) if plan else 0
        messagebox.showinfo(
            "Session Complete",
            f"Words reviewed: {len(plan)}\nCorrect: {state['correct']}\nAccuracy: {accuracy:.1f}%"
        )

        self.refresh_all()

    # ==================================================
    # WORD MANAGEMENT
    # ==================================================

    def add_word(self):
        """Add a new word."""
        word = self.word_entry.get().strip()
        sentence = self.sentence_entry.get().strip()
        note = self.note_entry.get().strip()

        if not word or not sentence:
            messagebox.showerror("Error", "Word and sentence are required")
            return

        if core.add_word_gui_logic(word, sentence, note):
            messagebox.showinfo("Success", f"Added '{word}'!")
            self.word_entry.delete(0, tk.END)
            self.sentence_entry.delete(0, tk.END)
            self.note_entry.delete(0, tk.END)
            self.refresh_word_table()
            self.refresh_all()
        else:
            messagebox.showerror("Error", "Word already exists or invalid input")

    def get_selected_word(self) -> str:
        """Get currently selected word from table."""
        selected = self.word_table.selection()
        if not selected:
            messagebox.showerror("Error", "Select a word first")
            return None
        return self.word_table.item(selected[0])["values"][0]

    def delete_word(self):
        """Delete selected word."""
        word = self.get_selected_word()
        if not word:
            return

        if messagebox.askyesno("Confirm", f"Delete '{word}'?"):
            if core.remove_word(word):
                messagebox.showinfo("Deleted", f"Removed '{word}'")
                self.refresh_word_table()
                self.refresh_all()
            else:
                messagebox.showerror("Error", "Failed to delete word")

    def edit_word_dialog(self):
        """Open edit word dialog."""
        word = self.get_selected_word()
        if not word:
            return

        data = core.vocab[word]

        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Edit '{word}'")
        edit_win.geometry("500x300")
        edit_win.config(bg=Colors.BG_PRIMARY)

        frame = tk.Frame(edit_win, bg=Colors.BG_PRIMARY)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(
            frame,
            text="Sentence",
            font=fonts.body_small,
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_PRIMARY
        ).pack(anchor="w")

        sentence_entry = tk.Entry(
            frame,
            font=fonts.body,
            bg=Colors.BG_SECONDARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT,
            relief=tk.FLAT,
            bd=0,
            width=40
        )
        sentence_entry.insert(0, data["sentence"])
        sentence_entry.pack(fill="x", pady=(0, 15))

        tk.Label(
            frame,
            text="Notes",
            font=fonts.body_small,
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_PRIMARY
        ).pack(anchor="w")

        note_entry = tk.Entry(
            frame,
            font=fonts.body,
            bg=Colors.BG_SECONDARY,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT,
            relief=tk.FLAT,
            bd=0,
            width=40
        )
        note_entry.insert(0, data["note"])
        note_entry.pack(fill="x", pady=(0, 20))

        def save():
            if core.edit_word(word, sentence_entry.get(), note_entry.get()):
                edit_win.destroy()
                self.refresh_word_table()
                messagebox.showinfo("Saved", "Changes saved!")
            else:
                messagebox.showerror("Error", "Failed to save changes")

        tk.Button(
            frame,
            text="Save Changes",
            command=save,
            font=fonts.title_small,
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            activebackground=Colors.PRIMARY_DARK
        ).pack(anchor="w")

    def show_word_details(self):
        """Show detailed stats for a word."""
        word = self.get_selected_word()
        if not word:
            return

        data = core.vocab[word]
        reviewed = data.get("times_reviewed", 0)
        correct = data.get("times_correct", 0)
        accuracy = (correct / reviewed * 100) if reviewed > 0 else 0

        details_win = tk.Toplevel(self.root)
        details_win.title(f"'{word}' Details")
        details_win.geometry("400x300")
        details_win.config(bg=Colors.BG_PRIMARY)

        frame = tk.Frame(details_win, bg=Colors.BG_PRIMARY)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        details = [
            (f"Word", word),
            (f"Sentence", data["sentence"][:50] + "..." if len(data["sentence"]) > 50 else data["sentence"]),
            (f"Reviewed", str(reviewed)),
            (f"Correct", str(correct)),
            (f"Accuracy", f"{accuracy:.1f}%"),
            (f"Memory Box", f"{data.get('box', 1)}/5"),
            (f"Next Review", data.get("next_review", "N/A")),
        ]

        for label, value in details:
            tk.Label(
                frame,
                text=f"{label}: {value}",
                font=fonts.body,
                fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_PRIMARY
            ).pack(anchor="w", pady=5)

    def refresh_word_table(self):
        """Refresh the word table based on search."""
        for row in self.word_table.get_children():
            self.word_table.delete(row)

        query = self.search_var.get().lower()

        for word, data in core.vocab.items():
            if query and not (query in word.lower() or
                              query in data["sentence"].lower() or
                              query in data["note"].lower()):
                continue

            accuracy = core.get_word_accuracy(word)
            self.word_table.insert(
                "",
                "end",
                values=(word, data["sentence"][:40] + "..." if len(data["sentence"]) > 40 else data["sentence"],
                        data["note"][:20] + "..." if len(data["note"]) > 20 else data["note"], f"{accuracy:.0f}%")
            )

    # ==================================================
    # STATISTICS
    # ==================================================

    def show_heatmap(self):
        """Show study activity heatmap."""
        heatmap_win = tk.Toplevel(self.root)
        heatmap_win.title("Study Activity Heatmap")
        heatmap_win.geometry("600x400")
        heatmap_win.config(bg=Colors.BG_PRIMARY)

        frame = tk.Frame(heatmap_win, bg=Colors.BG_PRIMARY)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            frame,
            text="Last 84 Days (12 weeks)",
            font=fonts.title_medium,
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_PRIMARY
        ).pack(anchor="w", pady=(0, 15))

        heatmap_frame = tk.Frame(frame, bg=Colors.BG_SECONDARY)
        heatmap_frame.pack(fill="both", expand=True)

        history = core.progress.get("history", {})
        today = datetime.today()

        for i in range(84):
            day = today - timedelta(days=83 - i)
            key = day.date().isoformat()
            value = history.get(key, 0)

            if value == 0:
                color = Colors.BG_TERTIARY
            elif value < 10:
                color = "#1e40af"
            elif value < 25:
                color = "#059669"
            elif value < 50:
                color = Colors.SUCCESS
            else:
                color = Colors.ACCENT

            cell = tk.Label(
                heatmap_frame,
                text="",
                width=3,
                height=2,
                bg=color
            )
            cell.grid(row=i // 12, column=i % 12, padx=2, pady=2)

    def refresh_stats(self):
        """Refresh all statistics displays."""
        # Dashboard
        self.stat_streak.value_label.config(
            text=str(core.progress.get("current_streak", 0))
        )
        self.stat_due.value_label.config(
            text=str(core.get_due_count())
        )
        self.stat_xp.value_label.config(
            text=str(core.progress.get("xp", 0))
        )
        self.stat_words.value_label.config(
            text=str(len(core.vocab))
        )

        # Progress
        due = core.get_due_count()
        suggested = core.suggested_daily_target()
        studied = core.progress.get("studied_today", 0)
        progress_percent = min(100, (studied / suggested) * 100 if suggested > 0 else 0)

        self.progress_ring.draw_ring(progress_percent)
        self.progress_label.config(text=f"{studied} / {suggested} words studied")
        self.progress_sublabel.config(text="Great work!" if progress_percent >= 100 else "Keep going!")

        # Stats tab
        accuracy = core.get_overall_accuracy()
        self.stat_accuracy.value_label.config(text=f"{accuracy:.1f}%")

        total_reviews = sum(d.get("times_reviewed", 0) for d in core.vocab.values())
        self.stat_reviews.value_label.config(text=str(total_reviews))

        self.stat_longest_streak.value_label.config(
            text=str(core.progress.get("longest_streak", 0))
        )

        # Box distribution
        distribution = core.get_box_distribution()
        for box, count in distribution.items():
            self.box_labels[box].config(text=f"Box {box}: {count} words")

        # Difficult words
        for widget in self.difficult_frame.winfo_children():
            widget.destroy()

        difficult = core.get_difficult_words(5)
        for word, error_rate in difficult:
            tk.Label(
                self.difficult_frame,
                text=f"• {word}: {error_rate * 100:.0f}% error rate",
                font=fonts.body_small,
                fg=Colors.TEXT_SECONDARY,
                bg=Colors.BG_SECONDARY
            ).pack(anchor="w", pady=2)

        if not difficult:
            tk.Label(
                self.difficult_frame,
                text="No data yet",
                font=fonts.body_small,
                fg=Colors.TEXT_MUTED,
                bg=Colors.BG_SECONDARY
            ).pack(anchor="w")

    def refresh_all(self):
        """Refresh all displays."""
        self.refresh_word_table()
        self.refresh_stats()

    def on_close(self):
        """Handle window close."""
        core.save_vocab()
        core.save_progress()
        core.save_stats()
        self.root.destroy()


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = VocabTrainerApp(root)
    root.mainloop()