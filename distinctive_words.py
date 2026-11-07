#!/usr/bin/env python3
"""Find distinctive words in friends' writing using KL divergence."""

import argparse
from collections import Counter
import math
from pathlib import Path
import re
from typing import Dict, List, Tuple


def count_words(text: str) -> Counter[str]:
    """Count Unicode words, keeping internal apostrophes but ignoring numbers."""
    text = text.casefold().replace("\u2019", "'")
    return Counter(re.findall(r"[^\W\d_]+(?:'[^\W\d_]+)*", text))


def read_texts(directory: Path) -> Dict[str, Counter[str]]:
    if not directory.is_dir():
        raise ValueError(
            f"Text folder not found: {directory}. "
            "Create it and add a .txt file for each friend."
        )
    paths = sorted(
        path for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() == ".txt"
    )
    if len(paths) < 2:
        raise ValueError("Add at least two .txt files, one per friend.")
    texts: Dict[str, Counter[str]] = {}
    for path in paths:
        words = count_words(path.read_text(encoding="utf-8"))
        if not words:
            raise ValueError(f"{path.name} contains no words. Add some writing.")
        texts[path.name] = words
    return texts


def compare(
    words: Counter[str], others: Counter[str]
) -> Tuple[float, List[Tuple[str, float]]]:
    """Return smoothed KL in nats and positive contributions of observed words."""
    vocabulary = words.keys() | others.keys()
    word_total = sum(words.values()) + len(vocabulary)
    other_total = sum(others.values()) + len(vocabulary)
    divergence = 0.0
    distinctive: List[Tuple[str, float]] = []
    for word in sorted(vocabulary):
        p = (words[word] + 1) / word_total
        q = (others[word] + 1) / other_total
        contribution = p * math.log(p / q)
        divergence += contribution
        if words[word] and contribution > 0:
            distinctive.append((word, contribution))
    distinctive.sort(key=lambda item: (-item[1], item[0]))
    return divergence, distinctive


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory", nargs="?", type=Path,
        default=Path(__file__).resolve().parent / "texts",
        help="folder of UTF-8 .txt files (default: texts/ beside this script)",
    )
    parser.add_argument(
        "--top", type=int, default=10, help="maximum words per friend (default: 10)"
    )
    args = parser.parse_args()
    if args.top < 1:
        parser.error("--top must be a positive integer")
    try:
        texts = read_texts(args.directory)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))

    combined: Counter[str] = Counter()
    for words in texts.values():
        combined.update(words)
    print("Each friend compared with all the other friends combined.")
    print("Scores are positive contributions to KL divergence (natural-log units).")
    for filename, words in texts.items():
        divergence, distinctive = compare(words, combined - words)
        print(f"\n{filename} ({sum(words.values())} words; KL = {divergence:.4f})")
        if not distinctive:
            print("  No distinctive words: the word distributions are identical.")
        for word, score in distinctive[:args.top]:
            print(f"  {word:<20} {score:.4f}  ({words[word]} uses)")


if __name__ == "__main__":
    main()
