<img src="assets/tofu.png" width="100">

# Tofu's Flip Seven App

Browser app for streamlining scoring for the game Flip Seven. 

Bonus advisor feature to help make informed decisions about risky plays. Never lose to your grandma again! (Probably.)

## Usage

Visit the app here: https://tofu-flip-seven-scorer.streamlit.app/.

In the sidebar:
- `Scorer`: use to track both round-by-round and total scores of players
    - will show running totals (and runway left for 200), visually indicated by an Excel-like conditional formatting
    - **can input totals or individual numbers** (if too lazy to mental math), but make sure to put in 7 individual numbers if you actually got `Flip7` to calculate the bonus
- `Advisor`: input the drawn cards (your own and others) to get info on the next draw

## Local Installation
1. Clone the repository:
```bash
git clone https://github.com/cdenq/flip-seven-scorer
cd flip-seven-scorer
```

2. Make a new envs:
```bash
conda create --name flip-seven
conda activate flip-seven
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run website locally
```bash
streamlit run app.py
```

## Project Structure

```
flip7-scorer/
├── app.py                      # Main Streamlit app entry point
├── assets/
│   └── tofu.png                # App logo
├── src/
│   ├── core/
│   │   ├── scoring.py          # Score tracking logic
│   │   ├── advisor_logic.py    # Advisor calculations and recommendations
│   │   └── default_fields.py   # Default game settings
│   └── pages/
│       ├── scorer.py           # Scorer page UI
│       └── advisor.py          # Advisor page UI
```

## Future Work?

- add to Advisor the math behind the Flip 3 action card: chances of busting someone given their hand? chances of you busting if you Flip 3 yourself?
    - idk i'll get to it eventually