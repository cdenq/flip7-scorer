# ---------------------
# Imports
# ---------------------
from . import default_fields as default
import streamlit as st
from typing import List
import re


# ---------------------
# Scoring Functions
# ---------------------
def initialize_session_state(session_state=None):
    ss = session_state or st.session_state
    if ss.get("players") is None:
        ss["players"] = default.DEFAULT_NAMES  # default four players
    if ss.get("player_count") is None:
        ss["player_count"] = 4
    if ss.get("round") is None:
        ss["round"] = 1
    if ss.get("history") is None:
        ss["history"] = []  # list of rounds, each is list of floats
    if ss.get("game_started") is None:
        ss["game_started"] = False
    return ss


def add_player(name: str, session_state=None):
    ss = session_state or st.session_state
    players = ss.get("players", [])
    players.append(name)
    ss["players"] = players


def restart_game(session_state=None):
    ss = session_state or st.session_state
    # Preserve current players, just reset the game state
    current_players = ss.get("players")
    if current_players is None:
        current_players = ["", "", ""]
    ss["round"] = 1
    ss["history"] = []
    ss["game_started"] = False
    ss["current_round_inputs"] = ["" for _ in current_players]


def commit_round(scores: List[float], session_state=None):
    ss = session_state or st.session_state
    players = ss.get("players", [])
    n = len(players)
    if len(scores) < n:
        scores = scores + [0.0] * (n - len(scores))
    # store as floats
    scores = [float(x) for x in scores]
    history = ss.get("history", [])
    history.append(scores)
    ss["history"] = history
    ss["round"] = ss.get("round", 1) + 1


def current_totals(session_state=None):
    ss = session_state or st.session_state
    players = ss.get("players", [])
    n = len(players)
    totals = [0.0] * n
    for r in ss.get("history", []):
        for i in range(n):
            if i < len(r):
                totals[i] += float(r[i])
    return totals


def parse_score_input(s: str) -> float:
    from src.core.advisor_logic import calc_score

    if s is None:
        return 0.0
    if isinstance(s, (int, float)):
        return float(s)
    txt = str(s).strip()
    if txt == "":
        return 0.0

    # Aliases for easier typing
    CARD_ALIASES = {
        "-2": "+2",
        "-4": "+4",
        "-6": "+6",
        "-8": "+8",
        "-10": "+10",
        "!": "x2",
        "$": "sc",
        "&": "fr",
        "@": "f3",
    }

    # Try to parse as card tokens (comma-separated)
    tokens = [t.strip().lower() for t in txt.split(",")]
    tokens = [CARD_ALIASES.get(t, t) for t in tokens if t]

    # Check if all tokens look like valid cards
    valid_cards = set(
        [str(i) for i in range(13)]
        + ["+2", "+4", "+6", "+8", "+10"]
        + ["x2", "sc", "f3", "fr"]
    )
    if all(t in valid_cards for t in tokens):
        return float(calc_score(tokens))

    # Fallback: treat as plain number(s)
    nums = re.findall(r"[-+]?\d*\.?\d+", txt)
    if nums:
        if len(nums) == 1:
            return float(nums[0])
        return sum(float(n) for n in nums)
    return 0.0
