"""
PyQt5 Theme - Options Backtesting System
Dark and Light theme support with modern styling
"""

# Color Palettes
DARK_COLORS = {
    "bg": "#0e0e0e",
    "card_bg": "#1a1a1a",
    "alt_bg": "#202020",
    "card_border": "#2d2d2d",
    "text": "#f0f6fc",
    "dim": "#8b949e",
    "accent": "#ffdc00",
    "up": "#3fb950",
    "down": "#f85149",
    "yellow": "#e3b341",
    "input_bg": "#0e0e0e",
    "input_border": "#2d2d2d",
    "btn_bg": "#222222",
    "btn_hover": "#2d2d2d",
    "sidebar_bg": "#111111",
    "sidebar_active": "#1e1e1e",
    "shadow_color": "#000000",
}

LIGHT_COLORS = {
    "bg": "#ffffff",
    "card_bg": "#f6f8fa",
    "alt_bg": "#eaeef2",
    "card_border": "#d0d7de",
    "text": "#1f2328",
    "dim": "#656d76",
    "accent": "#b08800",
    "up": "#1a7f37",
    "down": "#cf222e",
    "yellow": "#9a6700",
    "input_bg": "#ffffff",
    "input_border": "#d0d7de",
    "btn_bg": "#f6f8fa",
    "btn_hover": "#eaeef2",
    "sidebar_bg": "#f0f2f5",
    "sidebar_active": "#e8eaed",
    "shadow_color": "#c8cdd4",
}

# Active color palette (default dark)
C = dict(DARK_COLORS)

# Font settings - use cross-platform monospace fonts
FONT_FAMILY = "SF Mono, Menlo, Monaco, Consolas, monospace"
FONT_SIZE = 13
FONT_SIZE_LARGE = 15
FONT_SIZE_SMALL = 11


def build_stylesheet(colors):
    """Build the complete stylesheet from a color palette"""
    c = colors
    return f"""
QMainWindow, QWidget {{
    background-color: {c['bg']};
    color: {c['text']};
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE}px;
}}

QFrame#panel {{
    background-color: {c['card_bg']};
    border: 1px solid {c['card_border']};
    border-bottom: 2px solid {c['shadow_color']};
    border-right: 2px solid {c['shadow_color']};
    border-radius: 8px;
}}

QFrame#sidebar {{
    background-color: {c['sidebar_bg']};
    border-right: 1px solid {c['card_border']};
    border-radius: 0px;
}}

QToolButton#navBtn {{
    background-color: transparent;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0px;
    color: {c['dim']};
    font-size: 10px;
    padding: 8px 4px;
    text-align: center;
}}

QToolButton#navBtn:checked {{
    border-left: 3px solid {c['accent']};
    background-color: {c['sidebar_active']};
    color: {c['accent']};
    font-weight: bold;
}}

QToolButton#navBtn:hover:!checked {{
    background-color: {c['alt_bg']};
    color: {c['text']};
}}

QPushButton#pillButton {{
    border-radius: 12px;
    padding: 5px 14px;
    border: 1px solid {c['card_border']};
    background-color: {c['btn_bg']};
    color: {c['dim']};
    font-size: 12px;
    font-weight: normal;
}}

QPushButton#pillButton:checked {{
    background-color: {c['accent']};
    color: {c['bg']};
    border-color: {c['accent']};
    font-weight: bold;
}}

QPushButton#pillButton:hover:!checked {{
    background-color: {c['btn_hover']};
    color: {c['text']};
}}

QFrame#metricCard {{
    background-color: {c['alt_bg']};
    border: 1px solid {c['card_border']};
    border-bottom: 2px solid {c['shadow_color']};
    border-right: 2px solid {c['shadow_color']};
    border-radius: 8px;
}}

QPushButton#collapsibleHeader {{
    background-color: {c['alt_bg']};
    border: none;
    border-radius: 6px;
    color: {c['text']};
    font-weight: bold;
    font-size: {FONT_SIZE_LARGE}px;
    padding: 10px 14px;
    text-align: left;
}}

QPushButton#collapsibleHeader:hover {{
    background-color: {c['btn_hover']};
}}

QPushButton#collapsibleHeader:checked {{
    color: {c['accent']};
}}

QListWidget#dropZone {{
    border: 2px dashed {c['card_border']};
    border-radius: 8px;
    background-color: {c['alt_bg']};
    color: {c['dim']};
    font-size: 13px;
    min-height: 80px;
}}

QListWidget#dropZone:hover {{
    border-color: {c['accent']};
}}

QWidget#filterHeader {{
    background-color: transparent;
    border-radius: 6px;
}}

QLabel {{
    color: {c['text']};
    background-color: transparent;
}}

QLabel#header {{
    color: {c['accent']};
    font-weight: bold;
    font-size: {FONT_SIZE_LARGE}px;
}}

QLabel#dim {{
    color: {c['dim']};
}}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {c['input_bg']};
    border: 1px solid {c['input_border']};
    border-radius: 4px;
    padding: 6px 10px;
    color: {c['text']};
    selection-background-color: {c['accent']};
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border-color: {c['accent']};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {c['dim']};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {c['card_bg']};
    border: 1px solid {c['card_border']};
    selection-background-color: {c['accent']};
    selection-color: {c['bg']};
}}

QPushButton {{
    background-color: {c['btn_bg']};
    border: 1px solid {c['card_border']};
    border-radius: 6px;
    padding: 8px 16px;
    color: {c['text']};
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {c['btn_hover']};
    border-color: {c['accent']};
}}

QPushButton:pressed {{
    background-color: {c['card_border']};
}}

QPushButton#primary {{
    background-color: {c['accent']};
    color: {c['bg']};
    border: none;
}}

QPushButton#primary:hover {{
    background-color: {'#e6c800' if c.get('bg') != '#ffffff' else '#8a6d00'};
}}

QPushButton#success {{
    background-color: {c['up']};
    color: {c['bg']};
    border: none;
}}

QPushButton#danger {{
    background-color: {c['down']};
    color: {'#f0f6fc' if c.get('bg') != '#ffffff' else '#ffffff'};
    border: none;
}}

QPushButton#navButton:checked {{
    background-color: transparent;
    border-bottom: 2px solid {c['accent']};
    border-radius: 0px;
    color: {c['accent']};
}}

QPushButton#navButton:!checked {{
    background-color: transparent;
    border: none;
    color: {c['dim']};
}}

QTabWidget::pane {{
    border: 1px solid {c['card_border']};
    border-radius: 8px;
    background-color: {c['card_bg']};
    padding: 10px;
}}

QTabBar::tab {{
    background-color: {c['btn_bg']};
    border: 1px solid {c['card_border']};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 12px 32px;
    margin-right: 4px;
    color: {c['dim']};
    min-width: 120px;
}}

QTabBar::tab:selected {{
    background-color: {c['card_bg']};
    color: {c['accent']};
    font-weight: bold;
}}

QTabBar::tab:hover:!selected {{
    background-color: {c['btn_hover']};
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: {c['bg']};
    width: 12px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {c['card_border']};
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {c['dim']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {c['bg']};
    height: 12px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: {c['card_border']};
    border-radius: 6px;
    min-width: 30px;
    margin: 2px;
}}

QTableWidget, QTableView {{
    background-color: {c['card_bg']};
    alternate-background-color: {c['alt_bg']};
    gridline-color: {c['card_border']};
    border: 1px solid {c['card_border']};
    border-radius: 4px;
    color: {c['text']};
}}

QTableWidget::item {{
    padding: 6px;
    color: {c['text']};
}}

QTableWidget::item:selected {{
    background-color: {c['accent']};
    color: {c['bg']};
}}

QHeaderView::section {{
    background-color: {c['btn_bg']};
    color: {c['accent']};
    font-weight: bold;
    border: none;
    border-bottom: 1px solid {c['card_border']};
    padding: 8px;
}}

QCheckBox {{
    spacing: 8px;
    color: {c['text']};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {c['card_border']};
    border-radius: 4px;
    background-color: {c['input_bg']};
}}

QCheckBox::indicator:checked {{
    background-color: {c['accent']};
    border-color: {c['accent']};
}}

QCheckBox::indicator:hover {{
    border-color: {c['accent']};
}}

QGroupBox {{
    border: 1px solid {c['card_border']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
    color: {c['accent']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {c['accent']};
}}

QTextEdit, QPlainTextEdit {{
    background-color: {c['input_bg']};
    border: 1px solid {c['card_border']};
    border-radius: 4px;
    color: {c['text']};
    font-family: {FONT_FAMILY};
    padding: 8px;
}}

QProgressBar {{
    border: 1px solid {c['card_border']};
    border-radius: 4px;
    background-color: {c['input_bg']};
    text-align: center;
    color: {c['text']};
}}

QProgressBar::chunk {{
    background-color: {c['accent']};
    border-radius: 3px;
}}

QMenuBar {{
    background-color: {c['card_bg']};
    border-bottom: 1px solid {c['card_border']};
    padding: 4px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {c['btn_hover']};
}}

QMenu {{
    background-color: {c['card_bg']};
    border: 1px solid {c['card_border']};
    border-radius: 6px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {c['accent']};
    color: {c['bg']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {c['card_border']};
    margin: 4px 8px;
}}

QStatusBar {{
    background-color: {c['card_bg']};
    border-top: 1px solid {c['card_border']};
    color: {c['dim']};
}}

QToolTip {{
    background-color: {c['card_bg']};
    border: 1px solid {c['card_border']};
    color: {c['text']};
    padding: 6px;
    border-radius: 4px;
}}

QSlider::groove:horizontal {{
    border: 1px solid {c['card_border']};
    height: 6px;
    background: {c['input_bg']};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {c['accent']};
    border: none;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: {'#e6c800' if c.get('bg') != '#ffffff' else '#8a6d00'};
}}

QListWidget {{
    background-color: {c['card_bg']};
    border: 1px solid {c['card_border']};
    border-radius: 4px;
    padding: 4px;
}}

QListWidget::item {{
    padding: 6px 8px;
    border-radius: 4px;
}}

QListWidget::item:selected {{
    background-color: {c['accent']};
    color: {c['bg']};
}}

QListWidget::item:hover:!selected {{
    background-color: {c['btn_hover']};
}}

QSplitter::handle {{
    background-color: {c['card_border']};
}}

QSplitter::handle:horizontal {{
    width: 4px;
}}

QSplitter::handle:vertical {{
    height: 4px;
}}

QDateEdit {{
    background-color: {c['input_bg']};
    border: 1px solid {c['input_border']};
    border-radius: 4px;
    padding: 6px 10px;
    color: {c['text']};
}}

QDateEdit:focus {{
    border-color: {c['accent']};
}}

QDateEdit::drop-down {{
    border: none;
    width: 20px;
}}

QCalendarWidget {{
    background-color: {c['card_bg']};
}}

QCalendarWidget QToolButton {{
    color: {c['text']};
    background-color: {c['btn_bg']};
    border-radius: 4px;
    padding: 4px;
}}

QCalendarWidget QToolButton:hover {{
    background-color: {c['btn_hover']};
}}
"""


def build_echarts_theme(colors):
    """Build ECharts theme configuration from a color palette"""
    c = colors
    return {
        "color": [c['accent'], c['up'], c['down'], c['yellow'], "#9d65c9", "#f47983", "#7cd9fd"],
        "backgroundColor": "transparent",
        "textStyle": {
            "color": c['text'],
            "fontFamily": FONT_FAMILY
        },
        "title": {
            "textStyle": {
                "color": c['text'],
                "fontFamily": FONT_FAMILY
            },
            "subtextStyle": {
                "color": c['dim']
            }
        },
        "legend": {
            "textStyle": {
                "color": c['text']
            }
        },
        "tooltip": {
            "backgroundColor": c['card_bg'],
            "borderColor": c['card_border'],
            "textStyle": {
                "color": c['text']
            }
        },
        "categoryAxis": {
            "axisLine": {
                "lineStyle": {"color": c['card_border']}
            },
            "axisTick": {
                "lineStyle": {"color": c['card_border']}
            },
            "axisLabel": {
                "color": c['dim']
            },
            "splitLine": {
                "lineStyle": {"color": c['card_border'], "type": "dashed"}
            }
        },
        "valueAxis": {
            "axisLine": {
                "lineStyle": {"color": c['card_border']}
            },
            "axisTick": {
                "lineStyle": {"color": c['card_border']}
            },
            "axisLabel": {
                "color": c['dim']
            },
            "splitLine": {
                "lineStyle": {"color": c['card_border'], "type": "dashed"}
            }
        },
        "dataZoom": {
            "backgroundColor": c['card_bg'],
            "dataBackgroundColor": c['card_border'],
            "fillerColor": f"rgba({int(c['accent'][1:3], 16)}, {int(c['accent'][3:5], 16)}, {int(c['accent'][5:7], 16)}, 0.2)",
            "handleColor": c['accent'],
            "textStyle": {
                "color": c['dim']
            }
        }
    }


# Build defaults (dark theme)
STYLESHEET = build_stylesheet(C)
ECHARTS_THEME = build_echarts_theme(C)


def apply_theme(theme_name):
    """
    Apply a theme at runtime.

    Args:
        theme_name: 'dark' or 'light'
    """
    global C, STYLESHEET, ECHARTS_THEME

    if theme_name == 'light':
        colors = LIGHT_COLORS
    else:
        colors = DARK_COLORS

    # Update the global color dict in-place so existing references still work
    C.clear()
    C.update(colors)

    STYLESHEET = build_stylesheet(colors)
    ECHARTS_THEME = build_echarts_theme(colors)

    # Apply to the running application
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        app.setStyleSheet(STYLESHEET)
