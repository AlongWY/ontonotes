#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: Yunlong Feng <ylfeng@ir.hit.edu.cn>
import argparse
import os
from collections import namedtuple

import codecs
from typing import List


def iter_raw_lines(filename: str, strip=None, skip: str = '#'):
    line_num = 0
    with codecs.open(filename, encoding='utf-8') as file:
        while True:
            line = file.readline()
            line_num += 1
            if line.startswith(skip):
                continue
            if not line:  # EOF
                yield line_num, ''  # 输出空行，简化上层逻辑
                break
            line = line.strip(strip)
            yield line_num, line


def iter_lines(filename: str, split=None, strip=None):
    for line_num, raw_line in iter_raw_lines(filename=filename, strip=strip):
        if not raw_line:  # end of a sentence
            yield line_num, []  # 输出空行
        else:
            yield line_num, raw_line.split(split)


def iter_blocks(filename: str, split=None, strip=None):
    rows = []
    for line_num, line_features in iter_lines(filename, split=split, strip=strip):
        if len(line_features):
            rows.append(line_features)
        else:
            if len(rows):
                yield line_num, rows
                rows = []


OntoNotesConll = namedtuple(
    "OntoNotesConll",
    [
        'doc_id', 'part_id', 'word_id', 'word', 'pos_tag', 'bracketed',
        'predicate_lemma', 'predicate_frameset', 'word_sense', 'speaker',
        'ner_tag', 'predicate_arguments', 'co_reference'
    ]
)


def iter_ontonotes(filename: str):
    for num, block in iter_blocks(filename):
        reblock = list(list(x) for x in zip(*block))
        yield OntoNotesConll(
            doc_id=reblock[0],
            part_id=reblock[1],
            word_id=reblock[2],
            word=reblock[3],
            pos_tag=reblock[4],
            bracketed=reblock[5],
            predicate_lemma=reblock[6],
            predicate_frameset=reblock[7],
            word_sense=reblock[8],
            speaker=reblock[9],
            ner_tag=reblock[10],
            predicate_arguments=reblock[11:-1],
            co_reference=reblock[-1]
        )


def to_bio(tags: List[str]):
    res = []

    last_tag = 'O'
    for tag in tags:
        states = {}
        if tag.startswith('('):
            states['is_tag_begin'] = True
            tag = tag[1:]
        if tag.endswith(')'):
            states['is_tag_end'] = True
            tag = tag[:-1]
        if tag.endswith('*'):
            states['follow_last'] = True
            tag = tag[:-1]

        if len(tag):
            states['tag'] = tag
        else:
            states['tag'] = last_tag

        if states.get('tag') == 'O':
            res.append('O')
        elif states.get('is_tag_begin', False):
            res.append(f'B-{states["tag"]}')
        else:
            res.append(f'I-{states["tag"]}')

        last_tag = 'O' if states.get('is_tag_end', False) else states['tag']

    return res


def test_to_bio():
    assert ['B-TEST'] == to_bio(['(TEST)'])
    assert ['B-TEST', 'I-TEST'] == to_bio(['(TEST', '*)'])
    assert ['B-TEST', 'I-TEST', 'I-TEST'] == to_bio(['(TEST', '*', '*)'])

    assert ['O'] == to_bio(['*'])
    assert ['O', 'B-TEST'] == to_bio(['*', '(TEST)'])
    assert ['O', 'B-TEST', 'I-TEST'] == to_bio(['*', '(TEST', '*)'])
    assert ['O', 'B-TEST', 'I-TEST', 'I-TEST'] == to_bio(['*', '(TEST', '*', '*)'])

    assert ['O', 'B-TEST', 'O'] == to_bio(['*', '(TEST)', '*'])
    assert ['O', 'B-TEST', 'I-TEST', 'O'] == to_bio(['*', '(TEST', '*)', '*'])
    assert ['O', 'B-TEST', 'I-TEST', 'I-TEST', 'O'] == to_bio(['*', '(TEST', '*', '*)', '*'])

    assert ['O', 'B-TEST', 'I-TEST', 'B-TEST'] == to_bio(['*', '(TEST', '*)', '(TEST)'])


def to_conllu(onto: OntoNotesConll):
    id = onto.word_id
    words = onto.word
    lemma = onto.word
    upos = onto.pos_tag
    xpos = onto.pos_tag
    feats = ['_'] * len(id)
    head = list(str(x) for x in range(len(id)))
    deprel = ['_'] * len(id)
    deps = ['_'] * len(id)
    misc = ['_'] * len(id)

    sentence = f'# {"".join(words)}\n'
    conllu = [id, words, lemma, upos, xpos, feats, head, deprel, deps, misc]
    conllu = sentence + '\n'.join('\t'.join(line) for line in zip(*conllu)) + '\n\n'

    return conllu


def to_ner(onto: OntoNotesConll):
    words = onto.word
    ner_tags = to_bio(onto.ner_tag)

    sentence = f'# {"".join(words)}\n'
    ner = [words, ner_tags]
    ner = sentence + '\n'.join('\t'.join(line) for line in zip(*ner)) + '\n\n'

    return ner


def to_srl(onto: OntoNotesConll):
    words = onto.word
    predicate = ['Y' if p != '-' else '_' for p in onto.predicate_frameset]

    sentence = f'# {"".join(words)}\n'
    srl = [words, predicate]
    for srl_tags in onto.predicate_arguments:
        srl.append(to_bio(srl_tags))

    srl = sentence + '\n'.join('\t'.join(line) for line in zip(*srl)) + '\n\n'

    return srl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--language', default='chinese',
                        help='Which language to collect. support english, chinese, arabic', )
    args = parser.parse_args()
    language = args.language
    assert language in ('english', 'chinese', 'arabic')

    formats = ['conllu', 'srl', 'ner']
    src_names = ['train', 'dev', 'test']

    for format in formats:
        dir_name = os.path.join(format, language)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    for src in src_names:
        with open(f'conllu/{language}/{src}.conllu', 'w', encoding='utf-8') as conllu_file, \
                open(f'srl/{language}/{src}.txt', 'w', encoding='utf-8') as srl_file, \
                open(f'ner/{language}/{src}.bio', 'w', encoding='utf-8') as ner_file:
            for conll in iter_ontonotes(f'v4/{language}/{src}.txt'):
                conllu = to_conllu(conll)
                conllu_file.write(conllu)

                srl = to_srl(conll)
                srl_file.write(srl)

                ner = to_ner(conll)
                ner_file.write(ner)


if __name__ == '__main__':
    # test_to_bio()
    main()
