# ---------------------
# Imports
# ---------------------
import streamlit as st
import pandas as pd
import matplotlib
import src.core.scoring as scoring
import src.core.default_fields as default
from src.core.legend import render_legend

# ---------------------
# Page
# ---------------------
def show():
    # Two-column header: tofu image + legend
    header_left, header_right = st.columns([1, 3])
    with header_left:
        st.image("assets/tofu.png", width=100)
    with header_right:
        render_legend()

    st.title("Tofu's Flip Seven Scorer")
    scoring.initialize_session_state()

    if not st.session_state.game_started:
        show_player_setup()
    else:
        show_game_table()


def show_player_setup():
    # ensure player_count and players list exist
    if "player_count" not in st.session_state:
        st.session_state.player_count = 4
    if "players" not in st.session_state:
        st.session_state.players = []

    # Header with inline +/- controls (evaluate buttons before showing the count)
    minus_col, count_col, plus_col = st.columns([1, 1, 1])

    # Capture button clicks first
    dec_clicked = minus_col.button("➖", key="dec_player_count_header", use_container_width=True)
    inc_clicked = plus_col.button("➕", key="inc_player_count_header", use_container_width=True)

    # Apply changes
    if dec_clicked:
        if st.session_state.player_count > 1:
            st.session_state.player_count -= 1
            st.session_state.players = st.session_state.players[: st.session_state.player_count]
            st.rerun()
    if inc_clicked:
        st.session_state.player_count += 1
        idx = st.session_state.player_count - 1
        if idx < len(default.DEFAULT_NAMES):
            st.session_state.players.append(default.DEFAULT_NAMES[idx])
        else:
            st.session_state.players.append(f"Player {idx+1}")
        st.rerun()

    # display current count centered
    count_col.markdown(
        f"<div style='text-align: center;'><strong>Players: {st.session_state.player_count}</strong></div>",
        unsafe_allow_html=True,
    )

    # ensure players list has enough entries, but don't overwrite existing names
    while len(st.session_state.players) < st.session_state.player_count:
        idx = len(st.session_state.players)
        if idx < len(default.DEFAULT_NAMES):
            st.session_state.players.append(default.DEFAULT_NAMES[idx])
        else:
            st.session_state.players.append(f"Player {idx+1}")

    # Display player inputs in 5-column grid inside a form so clicking "Start" captures in-progress edits
    num_cols = 5
    with st.form(key="player_setup_form"):
        cols = st.columns(num_cols)
        for i in range(st.session_state.player_count):
            col_idx = i % num_cols
            with cols[col_idx]:
                st.text_input(
                    f"Player {i+1}:",
                    value=st.session_state.players[i] if i < len(st.session_state.players) else "",
                    key=f"player_input_{i}"
                )

        st.markdown("---")
        submitted = st.form_submit_button("Start game", use_container_width=True)
        if submitted:
            # Read the latest values directly from the player input widgets to ensure last edits are captured
            names = []
            for i in range(st.session_state.player_count):
                name = st.session_state.get(f"player_input_{i}", "")
                # fallback to existing list values if widget missing
                if not name and i < len(st.session_state.players):
                    name = st.session_state.players[i]
                name = name.strip()
                if name:
                    names.append(name)

            # Start if at least one non-empty name provided
            if names:
                st.session_state.players = names
                st.session_state.history = []
                st.session_state.round = 1
                st.session_state.current_round_inputs = ["" for _ in st.session_state.players]
                st.session_state.game_started = True
                st.rerun()
            else:
                st.warning("Please add at least one player name before starting the game.")


def show_game_table():
    players = st.session_state.players
    n = len(players)

    # ensure current_round_inputs exist and match player count
    if "current_round_inputs" not in st.session_state or len(st.session_state.current_round_inputs) != n:
        st.session_state.current_round_inputs = ["" for _ in players]

    from src.core.scoring import parse_score_input

    # Callback to clear a single player's input
    def clear_input(idx):
        round_num = st.session_state.round
        key_name = f"round_input_{round_num}_{idx}"
        if key_name in st.session_state:
            st.session_state[key_name] = ""
        st.session_state.current_round_inputs[idx] = ""

    # Precompute committed totals
    totals = scoring.current_totals()

    # Column layout: Player | Total Score | Running Total | Round N | Clear
    col_weights = [2, 2, 2, 3, 1]

    # Header row
    header = st.columns(col_weights)
    header[0].markdown("**Player**")
    header[1].markdown("**Total Score**")
    header[2].markdown("**Running Total**")
    header[3].markdown(f"**Round {st.session_state.round}**")
    header[4].markdown("")

    # Player rows (no form — Enter just recalculates, doesn't commit)
    for i, player in enumerate(players):
        row = st.columns(col_weights)

        # Player name
        row[0].markdown(f"**{player}**")

        # Total Score: "120 (80)"
        total = totals[i]
        left = max(0, 200 - total)
        row[1].markdown(f"{total:.0f} ({left:.0f})")

        # Round input
        key_name = f"round_input_{st.session_state.round}_{i}"
        if key_name not in st.session_state:
            st.session_state[key_name] = str(st.session_state.current_round_inputs[i])
        raw = row[3].text_input(
            label=f"score_{i}",
            key=key_name,
            label_visibility="collapsed",
        )
        st.session_state.current_round_inputs[i] = raw

        # Running Total: "+34 (154)" coloured
        parsed = parse_score_input(raw)
        projected = total + parsed
        if parsed > 0:
            color = "green"
            display = f"+{parsed:.0f} ({projected:.0f})"
        else:
            color = "red"
            display = f"{parsed:.0f} ({projected:.0f})"
        row[2].markdown(
            f"<span style='color: {color};'>{display}</span>",
            unsafe_allow_html=True,
        )

        # Clear button
        row[4].button("✕", key=f"clear_btn_{i}", on_click=clear_input, args=(i,))

    # Action buttons: Next Round (primary) | Restart — same row
    btn_left, btn_right = st.columns(2)
    with btn_left:
        if st.button("Next Round ➕", type="primary", use_container_width=True):
            parsed_list = [parse_score_input(st.session_state.current_round_inputs[j]) for j in range(n)]
            scoring.commit_round(parsed_list)
            # Clear current inputs so next round starts fresh
            st.session_state.current_round_inputs = ["" for _ in players]
            st.rerun()
    with btn_right:
        if st.button("Restart 🔄", use_container_width=True):
            scoring.restart_game()
            st.rerun()

    # Combined scores & totals table
    st.markdown("---")
    st.subheader("Totals")

    # Recompute totals after any possible round commit above
    totals = scoring.current_totals()

    # Build history frame: rows=players, cols=R1..Rn; fill missing with 0
    rounds = len(st.session_state.history)
    if rounds > 0:
        hist = pd.DataFrame(st.session_state.history).T
        hist.columns = [f"R{r+1}" for r in range(rounds)]
        hist.insert(0, "Player", players)
        hist_df = hist.set_index("Player")
        hist_df = hist_df.fillna(0)
    else:
        hist_df = pd.DataFrame({"Player": players}).set_index("Player")

    # Add Total column
    hist_df["Total"] = totals

    # Add Left column (amount needed to reach 200)
    hist_df["Left"] = [max(0, 200 - t) for t in totals]

    # Order columns: Total, Left, then rounds
    round_cols = [c for c in hist_df.columns if c.startswith("R")]
    cols_order = ["Total", "Left"] + round_cols if round_cols else ["Total", "Left"]
    hist_df = hist_df[cols_order]

    # Styling: white -> dark green on Total
    styled = hist_df.style.background_gradient(cmap="Greens", subset=["Total"]).format("{:.0f}")
    st.write(styled)

