#!/usr/bin/env python
from composes.utils import io_utils
from composes.semantic_space.space import Space
import os.path
import glob
import hashlib
import os, errno
import logging
import argparse
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


#context_words_filename = './context_vocab.txt'



def load_context_vocab(context_filename):
    logging.info('Using {0} contents as context words to build a comparable'
    ' space'.format(context_filename))
    if not os.path.isfile(context_filename):
        logging.info('{0} not found: building...'.format(context_filename))
        words = []
        for space_filename in space_filenames:
            sp = io_utils.load(space_filename)
            words.append(set(sp.id2row))
        context_words = set.intersection(*words)
        with open(context_filename, 'w') as f:
            for w in context_words:
                f.write('{0}\n'.format(w))

        logging.info('File {0} created'.format(context_filename))
    return [l.strip() for l in file(context_filename)]
    

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spaces_dir')
    ap.add_argument('words_list_dir')
    args = ap.parse_args()
    spaces_dir = args.spaces_dir
    words_list_dir = args.words_list_dir
    #    '/mnt/8tera/shareclic/lucaNgrams/5grams/ITA_5grams/matrices/pkl_matrices/'
    #space_filename = '../spaces/cbow1_wind5_hs0_neg10_size400_smpl1e-05.pkl'

    output_dir = os.path.join('output', os.path.basename(words_list_dir))
    mkdir_p(output_dir)
    all_words = set(l.strip() for words_filename in glob.glob(os.path.join(words_list_dir, '*'))
        for l in file(words_filename))

    for words_filename in glob.glob(os.path.join(words_list_dir, '*')):
        space_filename = os.path.join(spaces_dir,
            os.path.splitext(os.path.basename(words_filename))[0] + '.pkl')
        if not os.path.isfile(space_filename):
            logging.error('{0} not found: ignoring'.format(space_filename ))

        context_filename = hashlib.md5(spaces_dir).hexdigest() + '.txt'
        context_words = load_context_vocab(context_filename)

        logging.debug('Processing {0}'.format(space_filename))
        sp = io_utils.load(space_filename)

        #words = [l.strip() for l in file(words_filename)]
        filtered_words = [w for w in all_words if w in sp.row2id]
        words_vectors = sp.get_rows(filtered_words)
        context_vectors = sp.get_rows(context_words)

        m = words_vectors * context_vectors.transpose()

        sp2 = Space(m, filtered_words, context_words)

        io_utils.save(sp2,
            os.path.join(output_dir,os.path.basename(space_filename)))

if __name__ == '__main__':
    main()
