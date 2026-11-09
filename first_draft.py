from json import load, dump
from random import sample,choice
from typing import Literal


def load_json(path: str) -> dict[str, dict]:
    with open(path, encoding='utf-8') as f:
        return load(f)


def dump_json(obj: dict[str, dict[str, str | float]], path: str) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        dump(obj, f, ensure_ascii=False, indent=4)


def calculate_elo(
        winner_rating: float,
        loser_rating: float,
        winner_voices: int,
        loser_voices: int,
        k_min: float=15.0, # TODO не хранить их тут, а вынести потом в какую-нибудь конфигу или вроде того
        k_max: float=50.0,
        target_voices: float=30,
        remaining_fraction: float=0.1
) -> tuple[float, float]:

    scale_factor = 400 # TODO тоже как-то что-то с этим придумать
    winner_k_factor = k_function(winner_voices, k_min, k_max, target_voices, remaining_fraction)
    loser_k_factor = k_function(loser_voices, k_min, k_max, target_voices, remaining_fraction)

    winner_victory_probability = 1 / (1 + 10 ** ((loser_rating - winner_rating) / scale_factor))
    loser_victory_probability = 1 - winner_victory_probability

    new_winner_rating = winner_rating + winner_k_factor * (1 - winner_victory_probability)
    new_loser_rating = loser_rating + loser_k_factor * (0 - loser_victory_probability)

    return new_winner_rating, new_loser_rating


def choose_two_random_items(items: dict) -> list[str]:
    return sample(list(items.keys()), 2)


def k_function(voices, k_min, k_max, target_voices, remaining_fraction):

    s = target_voices / (1 / remaining_fraction - 1)
    k_factor = (k_min * voices + k_max * s) / (s + voices)

    return k_factor


def rating_difference(old_rating: float, new_rating: float) -> str:
    if new_rating > old_rating:
        difference = '+' + str(new_rating - old_rating)
    elif new_rating < old_rating:
        difference = '-' + str(old_rating - new_rating)
    else:
        difference = '0'
    return difference


def process_voting(winner_id: str, loser_id: str, word_list: dict):
    winner = word_list[winner_id]
    loser = word_list[loser_id]

    old_winner_rating = winner["rating"]
    old_loser_rating = loser["rating"]

    new_winner_rating, new_loser_rating = calculate_elo(
        winner_rating=winner["rating"],
        loser_rating=loser["rating"],
        winner_voices=winner["voices"],
        loser_voices=loser["voices"],
    )

    winner["rating"] = new_winner_rating
    loser["rating"] = new_loser_rating

    winner["voices"] += 1
    loser["voices"] += 1

    return old_winner_rating, old_loser_rating, new_winner_rating, new_loser_rating


def random_voting(id_a: str, id_b: str):
    winner_id = choice([id_a, id_b])
    loser_id = id_b if winner_id == id_a else id_a
    return winner_id, loser_id


def run(
        mode: Literal["user_infinite_loop", "votes_simulate"],
        votes_quantity: int=0,
        choose_pair_func=choose_two_random_items,
        voting_func=process_voting,
        select_winner_func=random_voting,
        load_json_path: str= 'rating_backup_start.json',
        save_json_path: str= 'first_words.json'
):
    words = load_json(load_json_path)

    if mode == "user_infinite_loop":

        print("Enter the number of the animal you consider better.\n"
              "Press any other button to exit.")

        while True:
            id_a, id_b = choose_pair_func(words)

            # честная пользовательская игра
            result = input(
                f'''What's better?\n1.{words[id_a]["word"]}\n2.{words[id_b]["word"]}\n'''
            )
            if result == "1":
                winner_id = id_a
                loser_id = id_b
            elif result == "2":
                winner_id = id_b
                loser_id = id_a
            else:
                print("Thanks!")
                break

            old_winner, old_loser, new_winner, new_loser = voting_func(
                winner_id=winner_id,
                loser_id=loser_id,
                word_list=words
            )

            sorted_words = dict(sorted(
                words.items(), key=lambda item: item[1]["rating"], reverse=True
            ))
            dump_json(sorted_words, save_json_path)


            winner_rating_difference = (f'{words[winner_id]["word"]} got '
                                   f'{rating_difference(old_rating=old_winner, new_rating=new_winner)}')
            loser_rating_difference = (f'{words[loser_id]["word"]} got '
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
            )

    return words



if __name__ == "__main__":
    run(mode="user_infinite_loop")