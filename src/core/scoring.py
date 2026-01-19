# ---------------------
# Imports
# ---------------------
from . import default_fields as default
import streamlit as st
from typing import List, Any
import re

# ---------------------
# Scoring Functions
# ---------------------
def _get(ss: Any, name: str, default=None):
    try:
        return ss[name]
    except Exception:
        return getattr(ss, name, default)


def _set(ss: Any, name: str, value):
    try:
        ss[name] = value
    except Exception:
        setattr(ss, name, value)


def initialize_session_state(session_state=None):
    ss = session_state or st.session_state
    if _get(ss, "players", None) is None:
        # sensible defaults for quick start
        _set(ss, "players", default.DEFAULT_NAMES)  # default four players
    if _get(ss, "player_count", None) is None:
        _set(ss, "player_count", 4)
    if _get(ss, "round", None) is None:
        _set(ss, "round", 1)
    if _get(ss, "history", None) is None:
        _set(ss, "history", [])  # list of rounds, each is list of floats
    if _get(ss, "game_started", None) is None:
        _set(ss, "game_started", False)
    return ss


def add_player(name: str, session_state=None):
    ss = session_state or st.session_state
    players = _get(ss, "players", [])
    players.append(name)
    _set(ss, "players", players)


def restart_game(session_state=None):
    ss = session_state or st.session_state
    # Preserve current players, just reset the game state
    current_players = _get(ss, "players", None)
    if current_players is None:
        current_players = ["", "", ""]
    _set(ss, "round", 1)
    _set(ss, "history", [])
    _set(ss, "game_started", False)
    _set(ss, "current_round_inputs", ["" for _ in current_players])


def commit_round(scores: List[float], session_state=None):
    ss = session_state or st.session_state
    players = _get(ss, "players", [])
    n = len(players)
    if len(scores) < n:
        scores = scores + [0.0] * (n - len(scores))
    # store as floats
    scores = [float(x) for x in scores]
    history = _get(ss, "history", [])
    history.append(scores)
    _set(ss, "history", history)
    _set(ss, "round", _get(ss, "round", 1) + 1)


def current_totals(session_state=None):
    ss = session_state or st.session_state
    players = _get(ss, "players", [])
    n = len(players)
    totals = [0.0] * n
    for r in _get(ss, "history", []):
        for i in range(n):
            if i < len(r):
                totals[i] += float(r[i])
    return totals


def parse_score_input(s: str) -> float:
    if s is None:
        return 0.0
    if isinstance(s, (int, float)):
        return float(s)
    txt = str(s).strip()
    if txt == "":
        return 0.0
    
    # If there's a comma, split and sum tokens
    if "," in txt:
        parts = [p.strip() for p in txt.split(",")]
        total = 0.0
        for p in parts:
            if p == "":
                continue
            # find numeric substrings inside token
            nums = re.findall(r"[-+]?\d*\.?\d+", p)
            if nums:
                for n in nums:
                    try:
                        total += float(n)
                    except Exception:
                        continue
            else:
                try:
                    total += float(p)
                except Exception:
                    continue
        return total
    
    # otherwise try to parse a single number, or extract numbers
    nums = re.findall(r"[-+]?\d*\.?\d+", txt)
    if nums:
        try:
            if len(nums) == 1:
                return float(nums[0])
            # if multiple found, sum them
            return sum(float(n) for n in nums)
        except Exception:
            return 0.0
    try:
        return float(txt)
    except Exception:
        return 0.0
