from json import dump, load
from typing import Any


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