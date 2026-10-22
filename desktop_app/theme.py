NAVY = "#16233B"
NAVY_DARK = "#0F192B"
BLUE = "#5B8CFF"
BLUE_HOVER = "#77A2FF"
LIGHT_BG = "#F5F7FB"
CARD_BG = "#FFFFFF"
BORDER = "#DCE3EC"
TEXT = "#172033"
TEXT_MUTED = "#68758A"
GREEN = "#1C9C73"
AMBER = "#E7A23B"
RED = "#D95C66"
TEAL = "#36B7B4"
PURPLE = "#8D7CFF"

STYLESHEET = f"""
QMainWindow {{
    background: {LIGHT_BG};
}}

#Sidebar {{
    background: {NAVY};
}}

#SidebarTitle {{
    color: white;
    font-size: 19px;
    font-weight: 800;
    letter-spacing: 2px;
    padding: 24px 20px 3px 20px;
}}

#SidebarSubtitle {{
    color: #9FB6D1;
    font-size: 10px;
    letter-spacing: 1.2px;
    padding: 0px 20px 28px 20px;
}}

#SidebarFooter {{
    color: #7184A3;
    font-size: 10px;
    line-height: 1.5;
    padding: 18px 20px 20px 20px;
}}

QPushButton#NavButton {{
    background: transparent;
    color: #C9D9EC;
    text-align: left;
    padding: 13px 20px;
    border: none;
    font-size: 13px;
    border-left: 3px solid transparent;
    border-radius: 0 8px 8px 0;
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
    padding: 0 4px;
}}

#PageTitle {{
    font-size: 20px;
    font-weight: 700;
    color: {TEXT};
}}

#StatusLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}

#StatusPill {{
    color: {GREEN};
    background: #E8F7F1;
    border-radius: 12px;
    padding: 6px 11px;
    font-size: 11px;
    font-weight: 600;
}}

#MutedLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}

#Eyebrow {{
    color: {BLUE};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.4px;
}}

#HeroTitle {{
    color: {TEXT};
    font-size: 24px;
    font-weight: 800;
}}

#HeroSubtitle {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}

#CardTitle {{
    color: {TEXT};
    font-size: 13px;
    font-weight: 700;
}}

#InsightValue {{
    color: {NAVY};
    font-size: 13px;
    font-weight: 700;
}}

QPushButton#PrimaryButton {{
    background: {BLUE};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
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
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 600;
}}

QPushButton#QuietButton {{
    background: transparent;
    color: {TEXT_MUTED};
    border: none;
    padding: 6px 8px;
    font-size: 11px;
}}

QPushButton#QuietButton:hover {{
    color: {BLUE};
}}
QPushButton#SecondaryButton:hover {{
    background: {LIGHT_BG};
}}

QFrame#Card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

QFrame#HeroCard {{
    background: #EAF1FF;
    border: 1px solid #D8E4FF;
    border-radius: 14px;
}}

QFrame#InsightCard {{
    background: #FFFFFF;
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

QFrame#Tile {{
    border-radius: 10px;
}}

#TileLabel {{
    color: rgba(255,255,255,0.85);
    font-size: 10px;
    font-weight: 600;
}}

#TileValue {{
    color: white;
    font-size: 28px;
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
    border-radius: 8px;
    font-size: 12px;
    selection-background-color: #E4ECFF;
    selection-color: {TEXT};
}}
QHeaderView::section {{
    background: #EEF2FA;
    color: {TEXT_MUTED};
    color: white;
    padding: 6px;
    border: none;
    font-size: 11px;
    font-weight: 700;
}}

QLineEdit#SearchBox {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
    background: white;
}}

QProgressBar {{
    border: 1px solid {BORDER};
    border-radius: 6px;
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
