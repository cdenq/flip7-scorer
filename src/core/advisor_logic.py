# ---------------------
# Imports
# ---------------------

# ---------------------
# Advisor Functions
# ---------------------
def build_master_deck():
    deck = []
    for i in range(13):
        if i > 1:
            for j in range(i):
                deck.append(str(i))
        else:
            deck.append(str(i))
    for card in ["sc", "f3", "fr"]:
        for _ in range(3):
            deck.append(card)
    for i in range(2, 11, 2):
        deck.append(f"+{i}")
    deck.append("x2")
    return deck


def pop_from_deck(ls, deck):
    for item in ls:
        try:
            deck.remove(str(item))
        except ValueError:
            # Ignore cards not found in deck
            pass
    return deck


def calc_score(drawn):
    relevant_nums = [item for item in drawn if item not in ["sc", "f3", "fr"]]

    flip_seven = []
    sum_score = 0
    mod = 0
    double = 1
    flipped = 0

    for item in relevant_nums:
        if "x" in item:
            double = 2
        elif "+" in item:
            mod += int(item.strip("+"))
        else:
            if item in flip_seven:
                return 0
            else:
                flip_seven.append(item)
            sum_score += int(item)

    if len(flip_seven) == 7:
        flipped = 1

    final = (sum_score * double) + mod + (flipped * 15)
    return final


def check_bust(drawn, deck):
    drawn = [str(item) for item in drawn]

    # Current score
    curr_score = calc_score(drawn)

    # Count unique base numbers (not +n, x2, or events)
    unique_nums = set()
    for item in drawn:
        if item not in ["sc", "f3", "fr"] and "x" not in item and "+" not in item:
            unique_nums.add(item)
    unique_count = len(unique_nums)
    has_flip_seven = unique_count == 7

    # Counting cards left
    cards_left = len(deck)
    deck_counter = {}
    for item in deck:
        if item not in deck_counter.keys():
            deck_counter[item] = 1
        else:
            deck_counter[item] += 1

    # Finding expected value
    expected_values_data = []
    total_expected_value = 0
    for k, v in deck_counter.items():
        temp = drawn.copy()
        temp.append(k)
        temp_perc = v / cards_left
        temp_total = calc_score(temp)
        delta = temp_total - curr_score
        expected_value = temp_perc * delta
        total_expected_value += expected_value
        expected_values_data.append((k, temp_perc, temp_total, delta, expected_value))

    expected_values_data = sorted(expected_values_data, key=lambda x: x[4], reverse=True)
    recommendation = "HIT" if total_expected_value > 0 else "STAY"

    # Checking busts
    bustable = []
    bust_total = 0
    for item in drawn:
        if item not in ["sc", "f3", "fr"]:
            try:
                perc = deck_counter[item] / cards_left
                bustable.append((item, perc))
                bust_total += perc
            except:
                pass

    bustable = sorted(bustable, key=lambda x: x[1], reverse=True)

    # Checking events
    events = []
    event_total = 0
    for item in ["sc", "f3", "fr"]:
        try:
            perc = deck_counter[item] / cards_left
            events.append((item, perc))
            event_total += perc
        except:
            continue

    return {
        "current_score": curr_score,
        "recommendation": recommendation,
        "expected_value": total_expected_value,
        "expected_values_data": expected_values_data,
        "bust_chance": bust_total,
        "bustable": bustable,
        "event_chance": event_total,
        "events": events,
        "unique_numbers": unique_count,
        "has_flip_seven": has_flip_seven,
    }
