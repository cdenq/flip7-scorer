# ---------------------
# Imports
# ---------------------
import streamlit as st
from src.core import advisor_logic

# ---------------------
# Helper Functions
# ---------------------
# Aliases for easier typing (especially on mobile)
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


def normalize_card(card):
    """Convert card aliases to their canonical form."""
    return CARD_ALIASES.get(card, card)


def parse_card_input(input_str):
    if not input_str.strip():
        return []

    cards = [card.strip().lower() for card in input_str.split(",")]
    cards = [normalize_card(card) for card in cards if card]  # Normalize aliases and filter empty
    return cards


def display_legend():
    st.markdown("##### Types of Cards: ")
    st.markdown("`0`-`12`, `+2`, `+4`, `+6`, `+8`, `+10`, `x2`, `sc`, `f3`, `fr`")
    st.markdown("`sc` = second chance, `f3` = flip 3, `fr` = freeze")
    st.markdown("---")
    st.markdown("FOR EASIER TYPING ON IPHONE, I added new aliases")
    st.markdown("`+{n}`=`-{n}` | `x2`=`!` | `sc`=`$` | `fr`=`&` | `f3`=`@`")
    st.markdown("(so instead of switching keyboards to type `+` and then back for `2` for `+2`, just type `-2`)")

# ---------------------
# Page
# ---------------------
def show():
    st.title("Tofu's Flip Seven Advisor")
    st.write("NOTE: F3 calculator not yet implemented; doesnt account for you having Second Chance.")
    st.markdown("---")

    # Display legend
    display_legend()

    st.markdown("---")

    # Input fields
    st.markdown("### Enter Your Cards")
    st.caption("Enter cards as comma-separated values (e.g., 2, 10, 8, 3, sc)")

    # Initialize session state for inputs if not present
    if "drawn_input" not in st.session_state:
        st.session_state.drawn_input = ""
    if "seen_input" not in st.session_state:
        st.session_state.seen_input = ""

    drawn_input = st.text_input(
        "**Drawn** (Your Cards):",
        value=st.session_state.drawn_input,
        placeholder="e.g., 2, 10, 1, 3, 8",
        key="drawn_text_input"
    )

    seen_input = st.text_input(
        "**Seen** (Other People's Cards):",
        value=st.session_state.seen_input,
        placeholder="e.g., 11, 12, x2, sc",
        key="seen_text_input"
    )

    # Update session state
    st.session_state.drawn_input = drawn_input
    st.session_state.seen_input = seen_input

    # Buttons
    col_advise, col_clear = st.columns(2)

    with col_advise:
        advise_clicked = st.button("Advise", type="primary", use_container_width=True)

    with col_clear:
        clear_clicked = st.button("Clear", use_container_width=True)

    # Handle Clear button
    if clear_clicked:
        st.session_state.drawn_input = ""
        st.session_state.seen_input = ""
        st.rerun()

    # Handle Advise button
    if advise_clicked:
        # Parse inputs
        drawn_cards = parse_card_input(drawn_input)
        seen_cards = parse_card_input(seen_input)

        if not drawn_cards:
            st.warning("Please enter at least one card in your hand.")
            return

        # Build deck and remove cards
        deck = advisor_logic.build_master_deck()
        deck = advisor_logic.pop_from_deck(drawn_cards, deck)
        deck = advisor_logic.pop_from_deck(seen_cards, deck)

        # Get advice
        advice = advisor_logic.check_bust(drawn_cards, deck)

        # Display results
        st.markdown("---")
        st.markdown("### Advice Results")

        # Main recommendation
        rec_color = "green" if advice["recommendation"] == "HIT" else "red"
        st.markdown(
            f"<h2 style='color: {rec_color};'>{advice['recommendation']}</h2>",
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Current Score", f"{advice['current_score']}")

        with col2:
            st.metric("Expected Value", f"{advice['expected_value']:.2f}")

        with col3:
            # Display unique numbers with special styling if flip seven achieved
            unique_label = "Numbers Until Flip7"
            unique_value = f"{advice['unique_numbers']}/7"
            if advice['has_flip_seven']:
                st.markdown(
                    f"**{unique_label}**  \n"
                    f"<span style='color: gold; font-size: 24px;'>✨ {unique_value} ✨</span>",
                    unsafe_allow_html=True
                )
            else:
                st.metric(unique_label, unique_value)

        # Expected values breakdown
        st.markdown("#### Expected Values by Card")
        ev_text = ""
        for card, perc, total, delta, ev in advice["expected_values_data"]:
            tag = f"+{delta}" if delta > 0 else str(delta)
            ev_text += f"`{card:>3}` ({perc*100:5.2f}%) → {total:>3} ({tag:>4}) | EV: {ev:>6.2f}\n\n"
        st.markdown(ev_text)

        # Bust information
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"#### Bust Chance: {advice['bust_chance']*100:.2f}%")
            if advice["bustable"]:
                bust_text = ""
                for card, perc in advice["bustable"]:
                    bust_text += f"`{card:>3}` ({perc*100:5.2f}%)\n\n"
                st.markdown(bust_text)
            else:
                st.markdown("*No bust cards remaining*")

        with col2:
            st.markdown(f"#### Event Chance: {advice['event_chance']*100:.2f}%")
            if advice["events"]:
                event_text = ""
                for card, perc in advice["events"]:
                    event_text += f"`{card:>3}` ({perc*100:5.2f}%)\n\n"
                st.markdown(event_text)
            else:
                st.markdown("*No event cards remaining*")