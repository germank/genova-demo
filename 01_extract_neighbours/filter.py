import argparse
from composes.utils import io_utils
from collections import defaultdict
import logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--words', nargs='*')
    ap.add_argument('--spaces', nargs='*')
    ap.add_argument('-m', '--min-occurrences', type=int, default=1)
    args = ap.parse_args()

    words = set(l.strip() for words_filename in args.words for l in
        file(words_filename))

    word_reps = defaultdict(lambda: 0)
    for sp_filename in args.spaces:
        logging.info('Counting words in {0}'.format(sp_filename))
        sp = io_utils.load(sp_filename)
        for w in words:
            if w in sp.row2id:
                word_reps[w] += 1

    for filename in args.words:
        file_words = [l.strip() for l in file(filename)]
        with open(filename, 'w') as f:
            for w in file_words:
                if word_reps[w] >= args.min_occurrences:
                    f.write('{0}\n'.format(w))

if __name__ == '__main__':
    main()
