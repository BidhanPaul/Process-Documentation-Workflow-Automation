NAVY = "#1A3B5D"
NAVY_DARK = "#122A44"
BLUE = "#0070F2"
BLUE_HOVER = "#3389F4"
LIGHT_BG = "#F4F6F9"
CARD_BG = "#FFFFFF"
BORDER = "#DCE3EC"
TEXT = "#22313F"
TEXT_MUTED = "#5B6B7C"
GREEN = "#1E8E3E"
AMBER = "#E9730C"
RED = "#D0271D"
TEAL = "#0FA3A3"
PURPLE = "#8B5CF6"

STYLESHEET = f"""
QMainWindow {{
    background: {LIGHT_BG};
}}

#Sidebar {{
    background: {NAVY};
}}

#SidebarTitle {{
    color: white;
    font-size: 15px;
    font-weight: 600;
    padding: 18px 16px 4px 16px;
}}

#SidebarSubtitle {{
    color: #9FB6D1;
    font-size: 10px;
    padding: 0px 16px 16px 16px;
}}

QPushButton#NavButton {{
    background: transparent;
    color: #C9D9EC;
    text-align: left;
    padding: 11px 18px;
    border: none;
    font-size: 13px;
    border-left: 3px solid transparent;
}}
QPushButton#NavButton:hover {{
    background: {NAVY_DARK};
    color: white;
}}
QPushButton#NavButton:checked {{
    background: {NAVY_DARK};
    color: white;
    border-left: 3px solid {BLUE};
    font-weight: 600;
}}

#TopBar {{
    background: {CARD_BG};
    border-bottom: 1px solid {BORDER};
}}

#PageTitle {{
    font-size: 18px;
    font-weight: 600;
    color: {TEXT};
}}

#StatusLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}

QPushButton#PrimaryButton {{
    background: {BLUE};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#PrimaryButton:hover {{
    background: {BLUE_HOVER};
}}
QPushButton#PrimaryButton:disabled {{
    background: #A9C6EE;
}}

QPushButton#SecondaryButton {{
    background: white;
    color: {NAVY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#SecondaryButton:hover {{
    background: {LIGHT_BG};
}}

QFrame#Card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
}}

QFrame#Tile {{
    border-radius: 6px;
}}

#TileLabel {{
    color: rgba(255,255,255,0.85);
    font-size: 10px;
    font-weight: 600;
}}

#TileValue {{
    color: white;
    font-size: 26px;
    font-weight: 700;
}}

#TileSub {{
    color: rgba(255,255,255,0.75);
    font-size: 9px;
}}

#SectionLabel {{
    color: {NAVY};
    font-size: 13px;
    font-weight: 700;
}}

QTableView {{
    background: white;
    alternate-background-color: {LIGHT_BG};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    border-radius: 4px;
    font-size: 12px;
    selection-background-color: #D6E7FC;
    selection-color: {TEXT};
}}
QHeaderView::section {{
    background: {NAVY};
    color: white;
    padding: 6px;
    border: none;
    font-size: 11px;
    font-weight: 600;
}}

QLineEdit#SearchBox {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
    background: white;
}}

QProgressBar {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    background: white;
    height: 8px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: {BLUE};
    border-radius: 4px;
}}

QPlainTextEdit#LogBox {{
    background: #0F1E2E;
    color: #B9D3F0;
    border-radius: 4px;
    font-family: Consolas, monospace;
    font-size: 11px;
    padding: 8px;
}}

QLabel#Badge {{
    border-radius: 8px;
    padding: 2px 9px;
    font-size: 10px;
    font-weight: 700;
    color: white;
}}
"""
