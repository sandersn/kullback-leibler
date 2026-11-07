from collections import Counter
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from distinctive_words import compare, count_words, read_texts


class DistinctiveWordsTests(unittest.TestCase):
    def test_tokenization(self):
        self.assertEqual(
            count_words("Hello, HELLO! Don't don\u2019t caf\u00e9 123 co-op."),
            Counter({"hello": 2, "don't": 2, "caf\u00e9": 1, "co": 1, "op": 1}),
        )

    def test_identical_distributions(self):
        divergence, ranked = compare(Counter(cat=2, dog=2), Counter(cat=2, dog=2))
        self.assertEqual(divergence, 0)
        self.assertEqual(ranked, [])

    def test_exact_smoothed_kl_and_ranking(self):
        divergence, ranked = compare(Counter(cat=3, dog=1), Counter(dog=4))
        expected_cat = (4 / 6) * math.log(4)
        expected_dog = (2 / 6) * math.log(2 / 5)
        self.assertAlmostEqual(divergence, expected_cat + expected_dog)
        self.assertEqual([word for word, _ in ranked], ["cat"])
        self.assertAlmostEqual(ranked[0][1], expected_cat)

    def test_absent_words_contribute_to_total(self):
        divergence, ranked = compare(Counter(cat=4), Counter(dog=4))
        self.assertAlmostEqual(divergence, (5 / 6 - 1 / 6) * math.log(5))
        self.assertEqual([word for word, _ in ranked], ["cat"])

    def test_ties_sorted_alphabetically(self):
        _, ranked = compare(Counter(zebra=3, apple=3), Counter(dog=6))
        self.assertEqual([word for word, _ in ranked], ["apple", "zebra"])

    def test_read_texts_and_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            with self.assertRaisesRegex(ValueError, "at least two"):
                read_texts(directory)
            (directory / "Alex.txt").write_text("cat cat", encoding="utf-8")
            (directory / "Blair.TXT").write_text("dog dog", encoding="utf-8")
            (directory / "notes.md").write_text("ignored", encoding="utf-8")
            self.assertEqual(
                read_texts(directory),
                {"Alex.txt": Counter(cat=2), "Blair.TXT": Counter(dog=2)},
            )
            (directory / "Blair.TXT").write_text("123 !!!", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "contains no words"):
                read_texts(directory)
            (directory / "Blair.TXT").write_bytes(b"\xff")
            with self.assertRaises(UnicodeError):
                read_texts(directory)
            with self.assertRaisesRegex(ValueError, "not found"):
                read_texts(directory / "missing")

    def test_cli(self):
        script = Path(__file__).with_name("distinctive_words.py").resolve()
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for name, text in (
                ("Alex", "rocket rocket orbit"),
                ("Blair", "goal goal team"),
                ("Casey", "paint paint brush"),
            ):
                (directory / f"{name}.txt").write_text(text, encoding="utf-8")
            command = [sys.executable, str(script), folder, "--top", "1"]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.count("uses)"), 3)
            for name, word in (("Alex", "rocket"), ("Blair", "goal"), ("Casey", "paint")):
                self.assertIn(f"{name}.txt", result.stdout)
                self.assertIn(word, result.stdout)
            invalid = subprocess.run(
                [sys.executable, str(script), folder, "--top", "0"],
                capture_output=True, text=True,
            )
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("positive integer", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
