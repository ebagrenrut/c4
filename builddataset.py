from __future__ import print_function
import os
import sys
import random

from argparse import ArgumentParser
from itertools import chain

from c4.board import Board, DRAW
from c4.engine import PVSBookEngine


def iter_files(path):
    """Iterate all game files in a path"""

    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.game'):
                yield os.path.join(root, f)


def run():
    parser = ArgumentParser()
    parser.add_argument('paths', metavar='DIRECTORY', nargs='+')
    parser.add_argument('-s', '--seed', type=int, default=None,
                        help='Seed for random number generator.')
    parser.add_argument('-d', '--max-depth', type=int, default=10,
                        help='Maximum depth of the minimax derivative')
    parser.add_argument('-l', '--limit-moves', type=int, default=None,
                        help='Limit the number of moves to make')
    parser.add_argument('-o', '--output', default=None,
                        help='Output file (default: stdout)')
    args = parser.parse_args()

    engine = PVSBookEngine(maxdepth=args.max_depth, ordering='diff')
    random.seed(args.seed)

    fout = sys.stdout
    if args.output:
        fout = open(args.output, 'w')

    gamefiles = list(chain.from_iterable(
        iter_files(path) for path in args.paths))

    try:
        for i, filename in enumerate(gamefiles, 1):
            print(
                '=== Processing file %s/%s (%.2f%%)' % (
                    i,
                    len(gamefiles),
                    i/len(gamefiles) * 100),
                file=sys.stderr
            )
            process(engine, filename, args.limit_moves, fout)
            fout.flush()
    finally:
        fout.close()


def process(engine, filename, limit, fout):
    with open(filename, 'r') as fin:
        moves = [int(x.strip()) for x in fin.readlines() if x.strip()]
        board = Board()
        for m in moves[:random.randrange(1, len(moves))]:
            board = board.move(m)
        assert board.end is None

        move, score = evaluate(engine, board, limit)
        print('\t'.join([board.dumps(), str(move), str(score)]),
              file=fout)


def evaluate(engine, root, limit):
    moves = []
    node = root
    while node.end is None:
        m = engine.choose(node)
        moves.append(m)
        node = node.move(m)

        # truncate the game if required
        if limit is not None:
            limit -= 1
            if limit == 0:
                break

    if node.end == root.stm:
        score = '1'
    elif node.end == DRAW:
        score = '0'
    elif node.end is None:
        score = '-'
    else:
        score = '-1'

    engine.reset()
    return moves[0], score


if __name__ == '__main__':
    sys.exit(run())