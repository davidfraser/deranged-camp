#!/usr/bin/env python

"""Take N students and split them up into G groups, A times (for different activities), so that no two students are in the same group more than once"""

import math
import pprint

N = 52  # number of students
S = 4   # group size
G = int(math.ceil(N/S)) # number of groups
A = 8   # number of activities

partitions = []

def simple_spread():
    for a in [1, 5, 7, 11, 17, 29]:
        map_to_group = [(n, ((a * n) % N)//S) for n in range(N)]
        partition = [{n for n, gg in map_to_group if gg == g} for g in range(G)]
        partitions.append(partition)
    return partitions

def count_overlaps(partitions):
    worked_with = {}
    for partition in partitions:
        for pp in partition:
            for n in pp:
                so_far = worked_with.setdefault(n, {})
                for i in pp.difference({n}):
                    so_far.setdefault(i, 0)
                    so_far[i] += 1
    return worked_with

def get_duplicates(worked_with):
    duplicates = {n: {k: v-1 for k, v in together.items() if v > 1} for n, together in worked_with.items()}
    return {n: dups for n, dups in duplicates.items() if dups}

def get_missing(partitions):
    for p, partition in enumerate(partitions):
        missing = set(range(N)).difference(set().union(*partition))
        if missing:
            yield p, missing

def get_badly_sized(partitions):
    for p, partition in enumerate(partitions):
        l = [len(pp) for pp in partition]
        if set(l) != {S}:
            yield p, l

def try_partitions(partitions):
    for partition in partitions:
        print(" ".join(",".join("%2d" % n for n in sorted(pp)) for pp in sorted(partition, key=min)))
    duplicates = get_duplicates(count_overlaps(partitions))
    missing = dict(get_missing(partitions))
    badly_sized = dict(get_badly_sized(partitions))
    if duplicates:
        print ("Duplicates:")
        pprint.pprint(duplicates)
    if missing:
        print ("Missing:")
        pprint.pprint(missing)
    if badly_sized:
        print ("Badly Sized:")
        pprint.pprint(badly_sized)

if __name__ == '__main__':
    try_partitions(simple_spread())

