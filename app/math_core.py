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