import argparse
from collections import defaultdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('filenames', nargs='*')
    ap.add_argument('-m', '--min-occurrences', type=int, default=1)
    args = ap.parse_args()

    word_reps = defaultdict(lambda: 0)
    words = defaultdict(list)
    for filename in args.filenames:
        with open(filename) as f:
            for l in f:
                w = l.strip()
                word_reps[w] += 1
                words[filename].append(w)

    for filename, file_words in words.iteritems():
        with open(filename, 'w') as f:
            for w in file_words:
                if word_reps[w] >= args.min_occurrences:
                    f.write('{0}\n'.format(w))

if __name__ == '__main__':
    main()
