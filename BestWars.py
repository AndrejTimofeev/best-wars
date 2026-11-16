from typing import Callable, Literal
from app.voting import choose_two_random_items, process_voting, random_voting, Items, rating_difference
from app.database import load_json, dump_json


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
    JSON_START_PATH = 'old_versions/rating_backup_start.json'
    JSON_PATH_USER_GAME = 'old_versions/my_opinion.json'
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
