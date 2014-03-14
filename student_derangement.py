#!/usr/bin/env python

"""Take N students and split them up into G groups, A times (for different activities), so that no two students are in the same group more than once"""

import math
import pprint

N = 52  # number of students
S = 4   # group size
A = 8   # number of activities

class PartitionSet(object):
    def __init__(self, N, S):
        self.N = N
        self.S = S
        self.G = int(math.ceil(N/S))
        self.partitions = []

    def add_partition(self, partition):
        self.partitions.append(partition)

    def count_overlaps(self):
        worked_with = {}
        for partition in self.partitions:
            for pp in partition:
                for n in pp:
                    so_far = worked_with.setdefault(n, {})
                    for i in pp.difference({n}):
                        so_far.setdefault(i, 0)
                        so_far[i] += 1
        return worked_with

    def get_duplicates(self):
        duplicates = {n: {k: v-1 for k, v in together.items() if v > 1} for n, together in self.count_overlaps().items()}
        return {n: dups for n, dups in duplicates.items() if dups}

    def get_missing(self):
        for p, partition in enumerate(self.partitions):
            missing = set(range(N)).difference(set().union(*partition))
            if missing:
                yield p, missing

    def get_badly_sized(self):
        for p, partition in enumerate(self.partitions):
            l = [len(pp) for pp in partition]
            if set(l) != {self.S}:
                yield p, l

    def show_and_test(self):
        for partition in self.partitions:
            print(" ".join(",".join("%2d" % n for n in sorted(pp)) for pp in sorted(partition, key=min)))
        duplicates = self.get_duplicates()
        missing = dict(self.get_missing())
        badly_sized = dict(self.get_badly_sized())
        if duplicates:
            print ("Duplicates:")
            pprint.pprint(duplicates)
        if missing:
            print ("Missing:")
            pprint.pprint(missing)
        if badly_sized:
            print ("Badly Sized:")
            pprint.pprint(badly_sized)

def simple_spread(N, S):
    G = int(math.ceil(N/S)) # number of groups
    for a in [1, 5, 7, 11, 17, 29]:
        map_to_group = [(n, ((a * n) % N)//S) for n in range(N)]
        partition = [{n for n, gg in map_to_group if gg == g} for g in range(G)]
        yield partition

if __name__ == '__main__':
    P = PartitionSet(N, S)
    for partition in simple_spread(N, S):
        P.add_partition(partition)
    P.show_and_test()

