#!/usr/bin/env python

"""Take N students and split them up into G groups, A times (for different activities), so that no two students are in the same group more than once"""

# Copyright 2014 David Fraser <https://github.com/davidfraser/> and Matthew Hampton <https://github.com/matthewhampton/>
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not 
# use this file except in compliance with the License. You may obtain a copy 
# of the License at 
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT 
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the 
# License for the specific language governing permissions and limitations 
# under the License. 

import math
import pprint
import random
import csv
import sys

ORDINAL_SUFFIXES = ["th", "st", "nd", "rd"] + ["th"]*16

def ordinal(n):
    return "%d%s" % (n, ORDINAL_SUFFIXES[n%20])

rand_instance  = random.Random()

class PartitionSet(object):
    def __init__(self, N, S, students, leaders):
        """Sets up a partition set for N students divided into groups of S"""
        self.N = N
        self.S = S
        self.G = int(math.ceil(N/S))
        self.partitions = []
        self.students = students
        self.leaders = leaders

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
            missing = set(range(self.N)).difference(set().union(*partition))
            if missing:
                yield p, missing

    def get_badly_sized(self):
        for p, partition in enumerate(self.partitions):
            l = [len(pp) for pp in partition]
            if set(l) != {self.S}:
                yield p, l

    def get_leaders_with_duplicate_students(self):
        leaders_kids = {}
        for p, partition in enumerate(self.partitions):
            for i, group in enumerate(partition):
                kidset = leaders_kids.setdefault(i, set())
                for n in group:
                    if n in kidset:
                        yield self.leaders[i], self.students[n]
                    kidset.add(n)

    def get_groups_with_only_one_gender(self):
        for p, partition in enumerate(self.partitions):
            for i, group in enumerate(partition):
                genders = set([self.students[gn]['Gender'] for gn in group])
                if len(genders) < 2:
                    yield self.group_to_string(i, group)

    def group_to_string(self, leader_num, group):
        return '%(First Name)s %(Surname)s: ' % self.leaders[leader_num] + ", ".join('%(First Name)s %(Surname)s (%(Gender)s)' % self.students[n] for n in group)

    def group_to_row(self, leader_num, group):
        return ['%(First Name)s %(Surname)s' % self.leaders[leader_num]] + ['%(First Name)s %(Surname)s' % self.students[n] for n in group]

    def show_partition(self, partition):
        print("\n".join(self.group_to_string(i, pp) for i, pp in enumerate(partition)))

    def save_de_rangement(self):
        with open('derangement.csv', 'wb') as f:
            csv_file = csv.writer(f)
            for p, partition in enumerate(self.partitions):
                csv_file.writerow(['Exercise %02d'%(p+1)] + ['']*self.S)
                for i, group in enumerate(partition):
                    csv_file.writerow(self.group_to_row(i, group))
                csv_file.writerow(['']*(self.S+1))

    def show_and_test(self):

        for i, partition in enumerate(self.partitions):
            print '\nExercise %02d\n' % (i+1)
            self.show_partition(partition)

        duplicates = self.get_duplicates()
        missing = dict(self.get_missing())
        badly_sized = dict(self.get_badly_sized())
        leaders_with_duplicates = list(self.get_leaders_with_duplicate_students())
        groups_with_one_gender = list(self.get_groups_with_only_one_gender())
        if duplicates:
            print ("Duplicates:")
            pprint.pprint(duplicates)
        if missing:
            print ("Missing:")
            pprint.pprint(missing)
        if badly_sized:
            print ("Badly Sized:")
            pprint.pprint(badly_sized)
        if leaders_with_duplicates:
            print ("Leaders with duplicates:")
            pprint.pprint(leaders_with_duplicates)
        if groups_with_one_gender:
            print ("Groups with one gender:")
            pprint.pprint(groups_with_one_gender)
        if not (duplicates or missing or badly_sized or leaders_with_duplicates):
            print ("Valid solution")
            return True
        return False

class PartitionMaker(PartitionSet):
    def __init__(self, N, S, students, leaders):
        super(PartitionMaker, self).__init__(N, S, students, leaders)
        self.worked_with = {}
        self.worked_with_leaders = {}


    def add_partition(self, partition):
        super(PartitionMaker, self).add_partition(partition)
        for i, group in enumerate(partition):
            for n in group:
                self.worked_with.setdefault(n, set()).update(group.difference({n}))
                a = self.worked_with_leaders.setdefault(n, set())
                a.add(i)

    def clear(self):
        self.partitions = []
        self.worked_with = {}
        self.worked_with_leaders = {}

    def pop_partition(self):
        new_partitions = self.partitions[:-1]
        self.clear()
        for partition in new_partitions:
            self.add_partition(partition)

    def add_initial_partition(self):
        self.add_partition([{n for n in range(self.N) if n/self.S == g} for g in range(self.G)])

    def find_next_partition(self, n_sequence=None):
        """simple partition generation that just slots the given numbers into the first place it can find for them"""
        partition = [set() for g in range(self.G)]
        n_sequence = n_sequence or range(self.N)
        for n in n_sequence:
            avoid = self.worked_with.get(n, set())
            avoid_leader = self.worked_with_leaders.get(n, set())
            for i, group in enumerate(sorted(partition, key=len)):
                group = partition[i]
                genders = set([self.students[gn]['Gender'] for gn in group])
                if (len(group) < (self.S-1) or (len(group) < self.S and (len(genders)>1 or self.students[n]['Gender'] not in genders))) and not group.intersection(avoid) and not i in avoid_leader:
                    group.add(n)
                    break
            else:
                # self.show_and_test()
                # self.show_partition(partition)
                raise ValueError("No place for %d in %s partition" % (n, ordinal(len(self.partitions)+1)))
        self.add_partition(partition)

    def try_random_order(self, max_tries=5000):
        for i in range(max_tries):
            n_sequence = range(self.N)
            rand_instance.shuffle(n_sequence)
            try:
                self.find_next_partition(n_sequence)
                print "! (%d tries)" % i
                return True
            except ValueError, e:
                if i % 100 == 0:
                    sys.stdout.write(".")
                    sys.stdout.flush()
        else:
            raise ValueError("Could not find solution to add to %d items" % len(self.partitions))

def simple_spread(N, S):
    G = int(math.ceil(N/S)) # number of groups
    for a in [1, 5, 7, 11, 17, 29]:
        map_to_group = [(n, ((a * n) % N)//S) for n in range(N)]
        partition = [{n for n, gg in map_to_group if gg == g} for g in range(G)]
        yield partition

if __name__ == '__main__':

    with open('students.csv') as f:
        students = list(sorted(csv.DictReader(f), key=lambda s:(s['Gender'],s['Race'])))

    with open('leaders.csv') as f:
        leaders = list(csv.DictReader(f))

    if len(students) % len(leaders) != 0:
        raise ValueError("Students must be an exact multiple of the number of leaders")
    A = 6   # number of activities
    P = PartitionMaker(len(students), len(students)/len(leaders), students, leaders)
    repeated_failures = 0
    while len(P.partitions) < A:
        try:
            P.try_random_order()
            repeated_failures = 0
        except ValueError:
            repeated_failures += 1
            items_to_pop = 1 + (repeated_failures // 5)
            print ("Going back %d..." % items_to_pop)
            for i in range(items_to_pop):
                P.pop_partition()
    print
    P.show_and_test()
    P.save_de_rangement()


