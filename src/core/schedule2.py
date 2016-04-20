#!/usr/bin/env python3
import random
from collections import namedtuple

from core import multilist


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
        self.slots = multilist.MultiList(
            schedule._n_rooms,
            schedule._n_rooms,
            schedule.slots[:])
        self.allocations = schedule.allocations
        self.allocation_maps = schedule.allocation_maps.copy()
        self._fitness = schedule._fitness
        self._fitness_valid = schedule._fitness_valid
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
        self._fitness = None
        self._fitness_valid = False

    @property
    def fitness(self):
        if not self._fitness_valid:
            penalties = dict()
            penalties['clash_time_teacher'] = -1000
            penalties['clash_time_batch'] = -1000
            fitness = 0
            # teacher time clashes
            for time_slot in self.slots[(None, None): (None, None)]:
                teachers = dict()
                batches = dict()
                for allocation in time_slot:
                    if allocation is not None:
                        try:
                            teachers[allocation.teacher] += 1
                        except KeyError:
                            teachers[allocation.teacher] = 1
                        try:
                            batches[allocation.batch] += 1
                        except KeyError:
                            batches[allocation.batch] = 1
                teacher_clashes = sum((
                    (count - 1) for count in teachers.values() if count > 1))
                fitness += teacher_clashes * penalties['clash_time_teacher']
                batch_clashes = sum((
                    (count - 1) for count in batches.values() if count > 1))
                fitness += batch_clashes * penalties['clash_time_batch']
            self._fitness = fitness
            self._fitness_valid = True
        return self._fitness

    @fitness.setter
    def fitness(self):
        raise AttributeError("'fitness' is read only")

    def seed_random(self):
        """
        Randomly allocates allocations to slots
        """
        choices = list(range(self._n_slots))
        random.shuffle(choices)
        for alloc, slot in zip(self.allocations, choices):
            self.slots[slot] = alloc
            self.allocation_maps[alloc] = slot
        self._fitness_valid = False

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
        self._fitness_valid = False

    def mutate(self, count):
        """
        Swaps randomly selected slots `count` times
        """
        for swap in range(count):
            self.swap(
                random.randrange(self._n_slots),
                random.randrange(self._n_slots))
        self._fitness_valid = False

    def mutate2(self, count):
        """ Selected two points always different """
        for swap in range(count):
            swap1 = random.randrange(self._n_slots)
            swap2 = random.randrange(self._n_slots)
            while(swap2 == swap1):
                swap2 = random.randrange(self._n_slots)
            self.swap(swap1, swap2)
        self._fitness_valid = False

    def shuffle_swap(self, slot1, slot2):
        """ Need to shuffle all the slots between the two points"""
        shuffled_part = self.slots[slot1:slot2]
        random.shuffle(shuffled_part)
        self.slots[slot1:slot2] = shuffled_part
        for slot in range(slot1, slot2):
            if self.slots[slot] is not None:
                self.allocation_maps[self.slots[slot]] = slot
        self._fitness_valid = False

    def mutate3(self, count):
        """ Shuffling randomly between two points """
        for swap in range(count):
            swap1 = random.randrange(self._n_slots - 1)
            swap2 = random.randrange(swap1, self._n_slots)
            self.shuffle_swap(self, swap1, swap2)
        self._fitness_valid = False
"""
Testing old crossover
"""
def swap_between(schedule_1, schedule_2, slot):
    schedule_1.slots[slot], schedule_2.slots[slot] = (
        schedule_2.slots[slot],
        schedule_1.slots[slot])
    for schedule in (schedule_1, schedule_2):
        if schedule.slots[slot] is not None:
            schedule.allocation_maps[schedule.slots[slot]] = slot
    schedule_1._fitness_valid = False
    schedule_2._fitness_valid = False
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
    cross_point_1 = random.randrange(schedule_1._n_slots)
    cross_point_2 = random.randrange(schedule_2._n_slots)
    while ((cross_point_2 == cross_point_1) or
            (abs(cross_point_2 - cross_point_1) ==
                abs(schedule_1._n_slots - 1))):
        cross_point_2 = random.randrange(schedule_1._n_slots)
    schedule_1._fitness_valid = False
    schedule_2._fitness_valid = False
    return swap_chunk(cross_point_1, cross_point_2, schedule_1, schedule_2)
    #return swap_chunk(2, 10, schedule_1, schedule_2)
