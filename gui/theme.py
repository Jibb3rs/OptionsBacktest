"""
HUD-Style Dark Theme - Options Backtesting System
Central theme configuration imported everywhere.
"""

C = {
    "bg": "#0d1117",
    "card_bg": "#161b22",
    "card_border": "#30363d",
    "text": "#e6edf3",
    "dim": "#8b949e",
    "accent": "#58a6ff",
    "up": "#3fb950",
    "down": "#f85149",
    "yellow": "#d29922",
    "input_bg": "#0d1117",
    "input_border": "#30363d",
    "btn_bg": "#21262d",
    "btn_hover": "#30363d",
}

FONT = "Consolas"
FONT_LABEL = (FONT, 12, "bold")
FONT_VALUE = (FONT, 13)
FONT_VALUE_LG = (FONT, 14)
FONT_SMALL = (FONT, 10)
FONT_TITLE = (FONT, 18, "bold")
FONT_SUBTITLE = (FONT, 12)
FONT_MONO = (FONT, 11)
FONT_CODE = (FONT, 10)


def apply_theme(root):
    """Apply the HUD dark theme globally to ttk styles and root window."""
    from tkinter import ttk

    root.configure(bg=C["bg"])

    style = ttk.Style(root)
    style.theme_use("clam")

    # ── Global defaults ──
    style.configure(".", background=C["bg"], foreground=C["text"],
                    font=(FONT, 11), borderwidth=0, relief="flat")
    style.map(".", foreground=[("disabled", C["dim"])])

    # ── TFrame ──
    style.configure("TFrame", background=C["bg"])
    style.configure("Card.TFrame", background=C["card_bg"])

    # ── TLabel ──
    style.configure("TLabel", background=C["bg"], foreground=C["text"],
                    font=(FONT, 11))
    style.configure("Title.TLabel", font=FONT_TITLE, foreground=C["text"],
                    background=C["bg"])
    style.configure("Subtitle.TLabel", font=FONT_SUBTITLE, foreground=C["dim"],
                    background=C["bg"])
    style.configure("Header.TLabel", font=FONT_LABEL, foreground=C["accent"],
                    background=C["bg"])
    style.configure("Info.TLabel", font=(FONT, 10), foreground=C["dim"],
                    background=C["bg"])
    style.configure("Success.TLabel", font=(FONT, 12, "bold"),
                    foreground=C["up"], background=C["bg"])
    style.configure("Danger.TLabel", font=(FONT, 12, "bold"),
                    foreground=C["down"], background=C["bg"])
    style.configure("Warning.TLabel", font=(FONT, 12, "bold"),
                    foreground=C["yellow"], background=C["bg"])
    style.configure("CardLabel.TLabel", background=C["card_bg"],
                    foreground=C["text"])
    style.configure("CardDim.TLabel", background=C["card_bg"],
                    foreground=C["dim"], font=(FONT, 10))
    style.configure("CardHeader.TLabel", background=C["card_bg"],
                    foreground=C["accent"], font=FONT_LABEL)

    # ── TLabelframe ──
    style.configure("TLabelframe", background=C["card_bg"],
                    foreground=C["accent"], relief="solid",
                    bordercolor=C["card_border"], borderwidth=1)
    style.configure("TLabelframe.Label", background=C["card_bg"],
                    foreground=C["accent"], font=FONT_LABEL)

    # ── TButton ──
    style.configure("TButton", background=C["btn_bg"], foreground=C["text"],
                    font=(FONT, 11, "bold"), padding=(16, 6),
                    borderwidth=1, relief="solid")
    style.map("TButton",
              background=[("active", C["btn_hover"]),
                          ("disabled", C["card_bg"])],
              foreground=[("disabled", C["dim"])],
              bordercolor=[("active", C["accent"])])

    style.configure("Big.TButton", font=(FONT, 13, "bold"),
                    padding=(20, 10), background=C["btn_bg"])
    style.map("Big.TButton",
              background=[("active", C["btn_hover"])],
              bordercolor=[("active", C["accent"])])

    style.configure("Action.TButton", background="#1a3a5c",
                    foreground=C["text"], font=(FONT, 11, "bold"),
                    bordercolor=C["accent"])
    style.map("Action.TButton",
              background=[("active", "#1f4d7a")])

    style.configure("Green.TButton", background="#1a7f37",
                    foreground=C["text"], font=(FONT, 11, "bold"),
                    bordercolor=C["up"])
    style.map("Green.TButton",
              background=[("active", "#238636")])

    # ── TEntry ──
    style.configure("TEntry", fieldbackground=C["input_bg"],
                    foreground=C["text"], bordercolor=C["input_border"],
                    insertcolor=C["text"], font=FONT_VALUE,
                    borderwidth=1, relief="solid", padding=4)
    style.map("TEntry",
              bordercolor=[("focus", C["accent"])],
              fieldbackground=[("readonly", C["card_bg"])])

    # ── TSpinbox ──
    style.configure("TSpinbox", fieldbackground=C["input_bg"],
                    foreground=C["text"], bordercolor=C["input_border"],
                    arrowcolor=C["dim"], insertcolor=C["text"],
                    font=FONT_VALUE, borderwidth=1, padding=4)
    style.map("TSpinbox",
              bordercolor=[("focus", C["accent"])],
              fieldbackground=[("readonly", C["card_bg"])])

    # ── TCombobox ──
    style.configure("TCombobox", fieldbackground=C["input_bg"],
                    foreground=C["text"], bordercolor=C["input_border"],
                    arrowcolor=C["dim"], font=FONT_VALUE,
                    borderwidth=1, padding=4)
    style.map("TCombobox",
              bordercolor=[("focus", C["accent"])],
              fieldbackground=[("readonly", C["input_bg"])])
    # Combobox dropdown list
    root.option_add("*TCombobox*Listbox.background", C["card_bg"])
    root.option_add("*TCombobox*Listbox.foreground", C["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", C["accent"])
    root.option_add("*TCombobox*Listbox.selectForeground", C["bg"])
    root.option_add("*TCombobox*Listbox.font", (FONT, 11))

    # ── TCheckbutton ──
    style.configure("TCheckbutton", background=C["bg"], foreground=C["text"],
                    font=(FONT, 11), indicatorcolor=C["input_bg"],
                    indicatorrelief="solid")
    style.map("TCheckbutton",
              background=[("active", C["bg"])],
              indicatorcolor=[("selected", C["accent"])])

    # ── TRadiobutton ──
    style.configure("TRadiobutton", background=C["bg"], foreground=C["text"],
                    font=(FONT, 11), indicatorcolor=C["input_bg"],
                    indicatorrelief="solid")
    style.map("TRadiobutton",
              background=[("active", C["bg"])],
              indicatorcolor=[("selected", C["accent"])])

    # ── TNotebook ──
    style.configure("TNotebook", background=C["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=C["card_bg"],
                    foreground=C["dim"], font=(FONT, 11, "bold"),
                    padding=(10, 5), borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", C["bg"])],
              foreground=[("selected", C["text"])],
              padding=[("selected", (16, 10))],
              expand=[("selected", [2, 4, 2, 0])])

    # ── TScrollbar ──
    style.configure("TScrollbar", background=C["card_bg"],
                    troughcolor=C["bg"], bordercolor=C["bg"],
                    arrowcolor=C["dim"])
    style.map("TScrollbar",
              background=[("active", C["card_border"])])

    # ── TSeparator ──
    style.configure("TSeparator", background=C["card_border"])

    # ── Treeview ──
    style.configure("Treeview", background=C["card_bg"],
                    foreground=C["text"], fieldbackground=C["card_bg"],
                    font=(FONT, 11), rowheight=28, borderwidth=0)
    style.configure("Treeview.Heading", background=C["btn_bg"],
                    foreground=C["accent"], font=FONT_LABEL,
                    borderwidth=1, relief="solid")
    style.map("Treeview",
              background=[("selected", C["accent"])],
              foreground=[("selected", C["bg"])])
    style.map("Treeview.Heading",
              background=[("active", C["btn_hover"])])

    # ── TPanedwindow ──
    style.configure("TPanedwindow", background=C["bg"])

    # ── TProgressbar ──
    style.configure("TProgressbar", background=C["accent"],
                    troughcolor=C["card_bg"], bordercolor=C["card_border"])


def style_canvas(canvas):
    """Style a tk.Canvas for the dark theme."""
    canvas.configure(bg=C["bg"], highlightthickness=0, bd=0)


def style_text(text_widget, code=False):
    """Style a tk.Text or ScrolledText widget."""
    text_widget.configure(
        bg=C["card_bg"] if code else C["bg"],
        fg=C["text"],
        insertbackground=C["accent"],
        selectbackground=C["accent"],
        selectforeground=C["bg"],
        font=FONT_CODE if code else FONT_MONO,
        relief="flat",
        borderwidth=0,
        highlightthickness=1,
        highlightcolor=C["card_border"],
        highlightbackground=C["card_border"],
    )


def style_listbox(listbox):
    """Style a tk.Listbox widget."""
    listbox.configure(
        bg=C["card_bg"],
        fg=C["text"],
        selectbackground=C["accent"],
        selectforeground=C["bg"],
        font=(FONT, 11),
        relief="flat",
        borderwidth=0,
        highlightthickness=1,
        highlightcolor=C["card_border"],
        highlightbackground=C["card_border"],
    )


def style_menu(menu):
    """Style a tk.Menu widget."""
    menu.configure(
        bg=C["card_bg"],
        fg=C["text"],
        activebackground=C["accent"],
        activeforeground=C["bg"],
        font=(FONT, 11),
        relief="flat",
        borderwidth=0,
    )


def chart_colors():
    """Return a dict of matplotlib styling parameters."""
    return {
        "figure.facecolor": C["bg"],
        "axes.facecolor": C["card_bg"],
        "axes.edgecolor": C["card_border"],
        "axes.labelcolor": C["dim"],
        "text.color": C["dim"],
        "xtick.color": C["dim"],
        "ytick.color": C["dim"],
        "grid.color": "#21262d",
        "grid.alpha": 0.3,
        "legend.facecolor": C["card_bg"],
        "legend.edgecolor": C["card_border"],
        "legend.labelcolor": C["dim"],
    }
