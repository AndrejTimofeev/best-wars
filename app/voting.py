from random import choices,choice
from .math_core import calculate_elo
from .database import Items


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


def rating_difference(old_rating: float, new_rating: float) -> str:
    """Format the rating change with an explicit sign."""
    difference = new_rating - old_rating
    return f"{difference:+.2f}" if difference != 0 else "0.00"