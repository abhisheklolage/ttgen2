#!usr/bin/env python3
import random
from collections import namedtuple

import multilist
import pprint
import pickle

class Schedule(object):
    SlotIndex = namedtuple('SlotIndex', ['time', 'room'])

    @classmethod
    def from_Schedule(cls, schedule):
        """
        Clone a Schedule
        """
        self = cls.__new__(cls)
        self._n_rooms = schedule._n_rooms
        self._n_times = schedule._n_times
        self._n_slots = schedule._n_slots
        #self.slots = multilist.MultiList(schedule._n_rooms, schedule._n_times)
        self.slots = schedule.slots
        self.allocations = schedule.allocations
        self.allocation_maps = schedule.allocation_maps.copy()
        return self

    def __init__(self, n_times, n_rooms, allocations):
        if n_times * n_rooms < len(allocations):
            raise Exception("Too few slots")
        self._n_rooms = n_rooms
        self._n_times = n_times
        self._n_slots = n_times * n_rooms
        self.slots = multilist.MultiList(n_rooms, n_times)
        self.allocations = allocations
        self.allocation_maps = dict()

    def seed_random(self):
        """
        Randomly allocates allocations to slots
        """
        choices = list(range(self._n_slots))
        random.shuffle(choices)
        for alloc, slot in zip(self.allocations, choices):
            self.slots[slot] = alloc
            self.allocation_maps[alloc] = slot


    def __str__(self):
        string = ""
        count = 0
        for key in self.allocation_maps:
            b, t, s = key
            string = string + str(b.name) + " " + str(t.name) + " " + str(s.name) + " " +  str(self.allocation_maps[key]) + "|"
            count = count + 1
            if (count % self._n_rooms == 0):
                string = string + "\n"
        return string

    def slot_indices(self, slot):
        """
        Gives the indices for self.slots[][] as a tuple of (time, room)
        """
        return self.SlotIndex(
            time=(slot // self._n_rooms),
            room=(slot % self._n_rooms))

    def swap(self, slot1, slot2):
        """
        Swaps the allocations between two slots
        """
        self.slots[slot1], self.slots[slot2] = (
            self.slots[slot2],
            self.slots[slot1])
        for slot in (slot1, slot2):
            if self.slots[slot] is not None:
                self.allocation_maps[self.slots[slot]] = slot

    def mutate(self, count):
        """
        Swaps randomly selected slots `count` times
        """
        for swap in range(count):
            self.swap(
                random.randrange(self._n_slots),
                random.randrange(self._n_slots))

    def fitness(self):
        penalties = dict()
        penalties['clash_time_teacher'] = -1000
        penalties['clash_time_batch'] = -1000
        fitness = 0
        # teacher time clashes
        for time_slot in self.slots[(None, None):(None, None)]:
        #for time_slot in self.slots:
            #print (type(time_slot))
            #print time_slot

            teachers = dict()
            for allocation in time_slot:
                #print allocation
                if(allocation is not None):
                    try:
                        teachers[allocation[1]] += 1
                    except KeyError:
                        teachers[allocation[1]] = 1
            violations = sum((
                (count - 1) for count in teachers.values() if count > 1))
            fitness += violations * penalties['clash_time_teacher']
        # batches time clashes
        for time_slot in self.slots[(None, None): (None, None)]:
            batches = dict()
            for allocation in time_slot:
                if(allocation is not None):
                    try:
                        batches[allocation[2]] += 1
                    except KeyError:
                        batches[allocation[2]] = 1
            violations = sum((
                (count - 1) for count in batches.values() if count > 1))
            fitness += violations * penalties['clash_time_batch']
        return fitness

    def mutate2(self, count):
        """ Selected two points always different """
        for swap in range(count):
            swap1 = random.randrange(self._n_slots)
            swap2 = random.randrange(self._n_slots)
            while(swap2 == swap1):
                swap2 = random.randrange(self._n_slots)
            self.swap(swap1, swap2)

    def shuffle_swap(self, slot1, slot2):
        """ Need to shuffle all the slots between the two points"""
        shuffled_part = self.slots[slot1:slot2]
        random.shuffle(shuffled_part)
        self.slots[slot1:slot2] = shuffled_part
        for slot in range(slot1, slot2):
            if self.slots[slot] is not None:
                self.allocation_maps[self.slots[slot]] = slot

    def mutate3(self, count):
        """ Shuffling randomly between two points """
        for swap in range(count):
            swap1 = random.randrange(self._n_slots - 1)
            swap2 = random.randrange(swap1, self._n_slots)
            self.shuffle_swap(self, swap1, swap2)


def swap_between(schedule_1, schedule_2, slot):
    schedule_1.slots[slot], schedule_2.slots[slot] = (
        schedule_2.slots[slot],
        schedule_1.slots[slot])
    for schedule in (schedule_1, schedule_2):
        if schedule.slots[slot] is not None:
            schedule.allocation_maps[schedule.slots[slot]] = slot
    return schedule_1, schedule_2

def swap_chunk(cross_point_1, cross_point_2, schedule_1, schedule_2):
    """
    Swap the chunk of allocations between the two
    indices crossover1(slot1) & crossover2(slot2)
    of two parent allocations.

    The parents are cloned to form the children.
    """

    child_1 = Schedule.from_Schedule(schedule_1)
    child_2 = Schedule.from_Schedule(schedule_2)
    cross_point_1, cross_point_2 = (
        min(cross_point_1, cross_point_2),
        max(cross_point_1, cross_point_2))
    for slot_number in range(cross_point_1, cross_point_2 + 1):
            child_1, child_2 = swap_between(child_1, child_2, slot_number)
    return child_1, child_2

def crossover(schedule_1, schedule_2):
    """
    Combine two parent allocations into two offsprings
    by swapping randomly determined chunk.
    """
    cross_point_1 = random.randrange(schedule_1._n_slots - 1)
    cross_point_2 = random.randrange(cross_point_1 + 1, schedule_1._n_slots)
    print "Crosspoints are: ", cross_point_1, " ", cross_point_2
    return swap_chunk(cross_point_1, cross_point_2, schedule_1, schedule_2)
    #return swap_chunk(2, 10, schedule_1, schedule_2)
