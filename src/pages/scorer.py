# ---------------------
# Imports
# ---------------------
import streamlit as st
import pandas as pd
import matplotlib
import src.core.scoring as scoring
import src.core.default_fields as default

# ---------------------
# Page
# ---------------------
def show():
    st.image("assets/tofu.png", width=100)
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


    # Small CSS to make tables compact
    st.markdown(
        """
    <style>
    .compact-table th, .compact-table td { padding: 4px 6px; font-size: 12px; }
    .player-row { margin-bottom: 4px; }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Header row
    form_cols = [1, 1]
    r0c = st.columns(form_cols)
    r0c[0].markdown("**Player**")
    r0c[1].markdown(f"**Round {st.session_state.round}**")

    # Precompute committed totals once
    totals = scoring.current_totals()

    # Player rows: text inputs (accept comma-separated values) inside a form
    from src.core.scoring import parse_score_input

    with st.form(key=f"round_form_{st.session_state.round}"):
        # collect raw values for this form run so the submit handler reads them directly
        form_inputs = []
        for i, player in enumerate(players):
            row_cols = st.columns(form_cols)
            row_cols[0].markdown(f"**{player}**")
            key_name = f"round_input_{st.session_state.round}_{i}"
            raw = row_cols[1].text_input(
                label=f"score_{i}",
                value=str(st.session_state.current_round_inputs[i]),
                key=key_name,
                label_visibility='collapsed',
            )
            # store input as raw string; parsing happens on submit
            st.session_state.current_round_inputs[i] = raw
            form_inputs.append(raw)

        # Action buttons in the form: submitting will capture the current text inputs without needing Enter
        submitted = st.form_submit_button("Next Round ➕", use_container_width=True)
        if submitted:
            parsed_list = [parse_score_input(v) for v in form_inputs]
            scoring.commit_round(parsed_list)
            # Reset the in-memory current inputs so the next round's widgets start empty
            st.session_state.current_round_inputs = ["" for _ in st.session_state.players]
            st.rerun()

    # Restart remains outside the form (visible icon and full width)
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

