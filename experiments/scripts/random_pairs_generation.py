from statistics import pstdev, mean
from csv import DictWriter
from os import remove, makedirs
from random import choices
import pandas as pd
import matplotlib.pyplot as plt

from first_draft import (
    load_json,
    dump_json,
    choose_two_random_items,
    run
)


def generate_datasets(
    source_json: str,
    sizes: list[int],
    output_dir: str,
) -> dict[int, str]:

    source_words = load_json(source_json)
    makedirs(output_dir, exist_ok=True)

    datasets = {}

    for size in sizes:
        selected_words = choices(
            list(source_words.values()),
            k=size
        )

        words = {
            f"word_{i}": {
                **word_data,
                "rating": 1000,
                "voices": 0,
            }
            for i, word_data in enumerate(selected_words)
        }

        output_path = f"{output_dir}/words_{size}.json"
        dump_json(words, output_path)

        datasets[size] = output_path

    return datasets


def visualize_experiments(sizes: list[int], results_dir: str) -> None:

    metrics = [
        ("cv", "Coefficient of variation"),
        ("relative_spread", "Relative spread"),
    ]

    for size in sizes:
        baseline = pd.read_csv(
            f"{results_dir}/random_{size}.csv"
        )
        inverse = pd.read_csv(
            f"{results_dir}/inverse_voices_{size}.csv"
        )

        baseline["relative_spread"] = baseline["spread"] / baseline["mean"]
        inverse["relative_spread"] = inverse["spread"] / inverse["mean"]

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        for ax, (metric, title) in zip(axes, metrics):
            ax.plot(
                baseline["mean"],
                baseline[metric],
                label="Random baseline"
            )

            ax.plot(
                inverse["mean"],
                inverse[metric],
                label="Inverse voting"
            )

            ax.set_title(title)
            ax.set_xlabel("Average votes per word")
            ax.set_ylabel("Normalized value")
            ax.legend()
            ax.grid()

        fig.suptitle(f"Comparison — {size} words")
        plt.tight_layout()

        plt.savefig(f"{results_dir}/comparison_{size}.png")
        plt.close(fig)


def collect_statistics(words: dict) -> dict:
    voices = [item["voices"] for item in words.values()]

    average = mean(voices)
    std = pstdev(voices)

    return {
        "mean": average,
        "std": std,
        "cv": std / average if average else 0,
        "spread": max(voices) - min(voices),
    }


def choose_pair_inverse_voting(words: dict) -> list[str]:
    ids = list(words.keys())
    weights = [1 / (words[id]["voices"] + 1) for id in ids]

    id_a = choices(ids, weights=weights, k=1)[0]

    ids.remove(id_a)
    weights = [1 / (words[id]["voices"] + 1) for id in ids]

    id_b = choices(ids, weights=weights, k=1)[0]

    return [id_a, id_b]


def run_experiment(
    initial_json: str,
    total_votes: int,
    snapshot_interval: int,
    output_csv: str,
    choose_pair_func
) -> None:

    current_json = initial_json
    results = []

    for votes in range(snapshot_interval, total_votes + 1, snapshot_interval):
        words = run(
            mode="votes_simulate",
            votes_quantity=snapshot_interval,
            load_json_path=current_json,
            choose_pair_func=choose_pair_func
        )

        current_json = "experiments/_experiment_temp.json"
        dump_json(words, current_json)

        stats = collect_statistics(words)
        stats["votes"] = votes
        results.append(stats)

    with open(output_csv, "w", newline="", encoding="utf-8") as file:
        writer = DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    remove(current_json)


if __name__ == "__main__":
    sizes = [100, 500, 2000]

    datasets = generate_datasets(
        source_json="experiments/base_rating.json",
        sizes=sizes,
        output_dir="experiments/datasets",
    )

    for size, dataset_path in datasets.items():
        votes_quantity = 50000
        snapshot = 100

        for algorithm_name, algorithm in [
            ("random", choose_two_random_items),
            ("inverse_voices", choose_pair_inverse_voting),
        ]:
            output_csv = (
                f"experiments/results/random_pair_generation/"
                f"{algorithm_name}_{size}.csv"
            )

            run_experiment(
                initial_json=dataset_path,
                total_votes=votes_quantity,
                snapshot_interval=snapshot,
                output_csv=output_csv,
                choose_pair_func=algorithm,
            )

    visualize_experiments(
        sizes=sizes,
        results_dir="experiments/results/random_pair_generation"
    )