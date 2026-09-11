from json import load, dump
from random import sample


def load_json(path: str) -> dict[int, dict]:
    with open(path, encoding='utf-8') as f:
        return load(f)


def dump_json(obj: dict[int, dict[str, str | float | int]], path: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        dump(obj, f, ensure_ascii=False, indent=4)


def calculate_elo(winner_rating: float | int, loser_rating: float | int) -> tuple[float | int, float | int]:

    scale_factor = 400
    winner_k_factor = 15 # TODO func calculation
    loser_k_factor = 15 # TODO func calculation

    winner_victory_probability = 1 / (1 + 10 ** ((loser_rating - winner_rating) / scale_factor))
    loser_victory_probability = 1 - winner_victory_probability

    new_winner_rating = winner_rating + winner_k_factor * (1 - winner_victory_probability)
    new_loser_rating = loser_rating + loser_k_factor * (0 - loser_victory_probability)

    return new_winner_rating, new_loser_rating


def choose_two_random_items(items: dict) -> list[int]:
    return sample(list(items.keys()), 2)


def rating_difference(old_rating: float | int, new_rating: float | int) -> str:
    if new_rating > old_rating:
        difference = '+' + str(new_rating - old_rating)
    elif new_rating < old_rating:
        difference = '-' + str(old_rating - new_rating)
    else:
        difference = '0'
    return difference


words = load_json('first_words.json')

print("Enter the number of the animal you consider better.\n"
      "Press any other button to exit.")
while True:
    id_a, id_b = choose_two_random_items(words)
    result = input(
        f'''What's better?\n1.{words[id_a]["word"]}\n2.{words[id_b]["word"]}\n'''
    )
    id_a_old_rating = words[id_a]["rating"]
    id_b_old_rating = words[id_b]["rating"]
    if result == "1":
        id_a_new_rating, id_b_new_rating = calculate_elo(id_a_old_rating, id_b_old_rating)
    elif result == "2":
        id_b_new_rating, id_a_new_rating = calculate_elo(id_b_old_rating, id_a_old_rating)
    else:
        print("Thanks!")
        break
    words[id_a]["rating"] = id_a_new_rating
    words[id_b]["rating"] = id_b_new_rating

    sorted_words = dict(sorted(
        words.items(), key=lambda item: item[1]["rating"], reverse=True
    ))
    dump_json(sorted_words, 'first_words.json')

    a_rating_difference = f'{words[id_a]["word"]} got {rating_difference(id_a_old_rating, id_a_new_rating)}'
    b_rating_difference = f'{words[id_b]["word"]} got {rating_difference(id_b_old_rating, id_b_new_rating)}'

    print(f'Rating updated!\n{a_rating_difference}\n{b_rating_difference}\n\n')

