# Distinctive words with Kullback-Leibler divergence

Find words that each friend uses more often than the others. Requires Python 3.9
or newer, with no extra packages to install.

## Try it on a Mac

1. Download or clone this repository.
2. Open Terminal and `cd` into the downloaded folder.
3. Run `mkdir -p texts`.
4. Put each friend's writing into a separate **plain-text, UTF-8** file in that
   folder, for example `texts/Alex.txt`, `texts/Blair.txt`, and `texts/Casey.txt`.
   In TextEdit, choose **Format > Make Plain Text** before saving. You need at
   least two files, and each must contain words.
5. Run:

   ```sh
   python3 distinctive_words.py
   ```

To print just five words per friend:

```sh
python3 distinctive_words.py --top 5
```

You can also supply a different folder: `python3 distinctive_words.py /path/to/texts`.
The default folder is beside the script, even if you run it from somewhere else.
Only `.txt` files directly inside the folder are read. The filename identifies
the friend; combine multiple pieces of their writing into that one file.

The `texts/` folder and everything in it are ignored by Git. Demo texts are local
only, so a fresh download needs its own files. The script processes writing
locally and does not upload it anywhere. Use writing your friends agree to share.

## What the scores mean

The script lowercases words, ignores punctuation and numbers, and keeps
contractions such as `don't` together. Common words are kept, too: they can
reveal differences in writing style.

For each friend, **P** is their word distribution and **Q** is the distribution
of everyone else's writing pooled together. Longer files contribute more words
to that pool. Both distributions get add-one smoothing over the shared vocabulary:

```text
P(word) = (friend's count + 1) / (friend's total words + vocabulary size)
Q(word) = (others' count + 1) / (others' total words + vocabulary size)
KL(P || Q) = sum over all words of P(word) * ln(P(word) / Q(word))
```

Smoothing prevents infinite scores for words nobody else uses. The displayed
words are those the friend actually used with **positive** contributions to KL,
ranked largest first. Words with negative contributions are included in the
total KL but not in the distinctive-word list. A larger word score means a
stronger contribution, not simply a larger frequency ratio. Scores use natural
logarithms (units called *nats*).

KL is directional: comparing Alex with Blair need not give the same result as
comparing Blair with Alex. Identical distributions have KL zero and no
distinctive words.

This is a fun vocabulary comparison, not a personality test or reliable author
identifier. Topics affect the results, and short samples are noisy. For a fairer
comparison, use reasonably long samples about similar topics.

## Tests

```sh
python3 -m unittest -v
```
