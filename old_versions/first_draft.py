from json import dump, load
from random import choices, choice
from typing import Any, Callable, Literal


Item = dict[str, Any]
Items = dict[str, Item]


def load_json(path: str) -> Items:
    """Load items and their ratings from JSON file."""
    with open(path, encoding='utf-8') as f:
        return load(f)


def dump_json(items: Items, path: str) -> None:
    """Save items and their ratings to JSON file."""
    with open(path, 'w', encoding='utf-8') as f:
        dump(items, f, ensure_ascii=False, indent=4)


def k_function(
        voices: int,
        k_min: float,
        k_max: float,
        target_voices: float,
        remaining_fraction: float
    ) -> float:
    """
    Calculate an individual K-factor based on the number of comparisons.

    The K-factor decreases from k_max towards k_min as the number
    of comparisons increases.

    Args:
        voices (int): Number of comparisons the item has participated in.
        k_min (float): Minimum K-factor, approached as comparisons increase.
        k_max (float): Maximum K-factor, used when there are no comparisons.
        target_voices (float): Number of comparisons at which the K-factor
            reaches the specified remaining fraction of its initial range.
        remaining_fraction (float): Fraction of the initial K-factor range
            remaining at target_voices. Must be between 0 and 1.

    Returns:
        k_factor (float): K-factor for Elo formula
    """

    s = target_voices / (1 / remaining_fraction - 1)
    k_factor = (k_min * voices + k_max * s) / (s + voices)

    return k_factor


def calculate_elo(
        winner_rating: float,
        loser_rating: float,
        winner_voices: int,
        loser_voices: int,
        scale_factor: int = 400,
        k_min: float = 15.0,
        k_max: float = 50.0,
        target_voices: float = 30.0,
        remaining_fraction: float = 0.1
    ) -> tuple[float, float]:
    """
    Calculate new Elo ratings for the winner and loser.

    Each item's K-factor is calculated individually using its
    number of previous comparisons. New ratings are rounded
    to two decimal places.

    Args:
        winner_rating (float): Current rating of winner
        loser_rating (float): Current rating of loser
        winner_voices (int): Number of comparisons the winner has participated in.
        loser_voices (int): Number of comparisons the loser has participated in.
        scale_factor (int): Controls how strongly the rating difference
            affects the predicted probability of victory.
        k_min (float): Minimum K-factor, approached as comparisons increase.
        k_max (float): Maximum K-factor, used when there are no comparisons.
        target_voices (float): Number of comparisons at which the K-factor
            reaches the specified remaining fraction of its initial range.
        remaining_fraction (float): Fraction of the initial K-factor range
            remaining at target_voices. Must be between 0 and 1.

    Returns:
        new_winner_rating (float): New rating of winner
        new_loser_rating (float): New rating of loser
    """

    winner_k_factor = k_function(winner_voices, k_min, k_max, target_voices, remaining_fraction)
    loser_k_factor = k_function(loser_voices, k_min, k_max, target_voices, remaining_fraction)

    winner_victory_probability = 1 / (1 + 10 ** ((loser_rating - winner_rating) / scale_factor))
    loser_victory_probability = 1 - winner_victory_probability

    new_winner_rating = winner_rating + winner_k_factor * (1 - winner_victory_probability)
    new_loser_rating = loser_rating - loser_k_factor * loser_victory_probability

    return round(new_winner_rating, 2), round(new_loser_rating, 2)


def choose_two_random_items(items: Items) -> list[str]:
    """
    Select two distinct items with probabilities inversely
    proportional to their number of previous comparisons.

    Args:
        items (Items): Dictionary of items with their ratings
            and comparison counts.

    Returns:
        list[str]: IDs of two distinct randomly selected items.
    """
    ids = list(items.keys())
    weights = [1 / (items[a]["voices"] + 1) for a in ids]

    id_a = choices(ids, weights=weights, k=1)[0]

    ids.remove(id_a)
    weights = [1 / (items[b]["voices"] + 1) for b in ids]

    id_b = choices(ids, weights=weights, k=1)[0]

    return [id_a, id_b]


def rating_difference(old_rating: float, new_rating: float) -> str:
    """Format the rating change with an explicit sign."""
    difference = new_rating - old_rating
    return f"{difference:+.2f}" if difference != 0 else "0.00"


def process_voting(
        winner_id: str,
        loser_id: str,
        word_list: Items,
        scale_factor: int,
        k_min: float,
        k_max: float,
        target_voices: float,
        remaining_fraction: float
    ) -> tuple[float, float, float, float]:
    """
    Apply a vote and update the ratings and comparison counts
    of the winner and loser.

    Args:
        winner_id (str): ID of the winning item.
        loser_id (str): ID of the losing item.
        word_list (Items): Dictionary containing all items and their data.
        scale_factor (int): Controls the effect of rating differences
            on predicted victory probability.
        k_min (float): Minimum K-factor.
        k_max (float): Maximum K-factor.
        target_voices (float): Number of comparisons at which the K-factor
            reaches the specified remaining fraction of its initial range.
        remaining_fraction (float): Fraction of the initial K-factor range
            remaining at target_voices.

    Returns:
        tuple[float, float, float, float]: Old winner rating,
            old loser rating, new winner rating, new loser rating.
    """
    winner = word_list[winner_id]
    loser = word_list[loser_id]

    old_winner_rating = winner["rating"]
    old_loser_rating = loser["rating"]

    new_winner_rating, new_loser_rating = calculate_elo(
        winner_rating=winner["rating"],
        loser_rating=loser["rating"],
        winner_voices=winner["voices"],
        loser_voices=loser["voices"],
        scale_factor=scale_factor,
        k_min=k_min,
        k_max=k_max,
        target_voices=target_voices,
        remaining_fraction=remaining_fraction
    )

    winner["rating"] = new_winner_rating
    loser["rating"] = new_loser_rating

    winner["voices"] += 1
    loser["voices"] += 1

    return old_winner_rating, old_loser_rating, new_winner_rating, new_loser_rating


def random_voting(id_a: str, id_b: str) -> tuple[str, str]:
    """Randomly select a winner and loser from a pair."""
    winner_id = choice([id_a, id_b])
    loser_id = id_b if winner_id == id_a else id_a
    return winner_id, loser_id


def run(
        mode: Literal["user_infinite_loop", "votes_simulate"],
        scale_factor: int,
        k_min: float,
        k_max: float,
        target_voices: float,
        remaining_fraction: float,
        load_json_path: str,
        save_json_path: str,
        votes_quantity: int=0,
        choose_pair_func: Callable[[Items], list[str]] = choose_two_random_items,
        voting_func: Callable[..., tuple[float, float, float, float]] = process_voting,
        select_winner_func: Callable[[str, str], tuple[str, str]] = random_voting,
    ) -> Items:
    """
    Run the interactive voting loop or a voting simulation.

    Interactive mode saves the updated ratings after every vote.
    Simulation mode returns the updated items without saving them.
    """
    words = load_json(load_json_path)

    if mode == "user_infinite_loop":

        print("Enter the number of the animal you consider better.\n"
              "Enter 0 to exit.")
        i = 0

        while True:
            i += 1
            id_a, id_b = choose_pair_func(words)

            print(f"Vote number {i}")
            result = input(
                f'''What's better?\n1.{words[id_a]["word"]}\n2.{words[id_b]["word"]}\n'''
            )
            if result == "1":
                winner_id = id_a
                loser_id = id_b
            elif result == "2":
                winner_id = id_b
                loser_id = id_a
            elif result =='0':
                print("Thanks!")
                break
            else:
                continue

            old_winner, old_loser, new_winner, new_loser = voting_func(
                winner_id=winner_id,
                loser_id=loser_id,
                word_list=words,
                scale_factor=scale_factor,
                k_min=k_min,
                k_max=k_max,
                target_voices=target_voices,
                remaining_fraction=remaining_fraction
            )

            sorted_words = dict(sorted(
                words.items(), key=lambda item: item[1]["rating"], reverse=True
            ))
            dump_json(sorted_words, save_json_path)


            winner_rating_difference = (f'{words[winner_id]["word"]} '
                                   f'{rating_difference(old_rating=old_winner, new_rating=new_winner)}')
            loser_rating_difference = (f'{words[loser_id]["word"]} '
                                   f'{rating_difference(old_rating=old_loser, new_rating=new_loser)}')

            print(f'Rating updated!\n{winner_rating_difference}\n{loser_rating_difference}\n\n')


    elif mode == "votes_simulate":
        for _ in range(votes_quantity):
            id_a, id_b = choose_pair_func(words)

            winner_id, loser_id = select_winner_func(id_a, id_b)

            voting_func(
                winner_id=winner_id,
                loser_id=loser_id,
                word_list=words,
                scale_factor=scale_factor,
                k_min=k_min,
                k_max=k_max,
                target_voices=target_voices,
                remaining_fraction=remaining_fraction
            )
    else:
        raise ValueError(f"Invalid mode: {mode}")

    return words



if __name__ == "__main__":
    SCALE_FACTOR = 400
    K_MIN = 15.0
    K_MAX = 50.0
    TARGET_VOICES = 30
    REMAINING_FRACTION = 0.1
    JSON_START_PATH = 'rating_backup_start.json'
    JSON_PATH_USER_GAME = 'my_opinion.json'
    JSON_RANDOM_SIMULATED = 'random_simulated.json'


    run(mode="user_infinite_loop",
        scale_factor=SCALE_FACTOR,
        k_min=K_MIN,
        k_max=K_MAX,
        target_voices=TARGET_VOICES,
        remaining_fraction=REMAINING_FRACTION,
        load_json_path=JSON_PATH_USER_GAME,
        save_json_path=JSON_PATH_USER_GAME
        )
