import batch
import teacher
import room
import subject
import allocation
import schedule

import evolution

import pickle
import pprint
from schedule import crossover
from schedule import swap_chunk
from schedule import swap_between

import unittest
import collections

class InequalityTest(unittest.TestCase):

    def testEqual(self):
        self.assertDictEqual(chi1.allocation_maps, chi2.allocation_maps)

    #def testNotEqual(self):
    #    self.assertEqual(2, 3-2)

if __name__ == '__main__':


    """ Creating a list of batches """
    batch_list = [  batch.Batch('IT1', 20), batch.Batch('IT2', 20), batch.Batch('IT3', 20), batch.Batch('IT4', 20),
                    batch.Batch('CS1', 20), batch.Batch('CS2', 20), batch.Batch('CS3', 20), batch.Batch('CS4', 20)]
    #print batch_list
    """ Creating a list of teachers """
    teacher_list = [teacher.Teacher('T1'), teacher.Teacher('T2'), teacher.Teacher('T3'), teacher.Teacher('T4')]
    #print teacher_list
    """ Creating a list of rooms """
    room_list = [room.Room('R1', 30, 0), room.Room('R2', 40, 1), room.Room('R3', 30, 2), room.Room('R4', 40, 3)]
    #print room_list
    """ Creating a list of subject """
    subject_list = [subject.Subject('Sub1'), subject.Subject('Sub2'), subject.Subject('Sub3'), subject.Subject('Sub4')]
    #print subject_list
    """ Creating a list of allocation (batch-subjct-teacher) """
    #allocation_list = [allocation.Allocation(batch_list[alloc], subject_list[alloc], teacher_list[alloc]) for alloc in range(8)]
    #print allocation_list
    #pprint.pprint(allocation_list)

    allocation_list = []
    for number in range(8):
        allocation_list.append((subject_list[0], teacher_list[0], batch_list[number]))

    for number in range(8):
        allocation_list.append((subject_list[1], teacher_list[1], batch_list[number]))

    for number in range(8):
        allocation_list.append((subject_list[2], teacher_list[2], batch_list[number]))

    for number in range(8):
        allocation_list.append((subject_list[3], teacher_list[3], batch_list[number]))

    """ Creating a schedule """
    sched1 = schedule.Schedule(8, 8, allocation_list)
    sched1.seed_random()
    fitness = sched1.fitness()
    print 'sched1 ', fitness
    sched2 = schedule.Schedule(0, 0, [])
    sched2 = sched2.from_Schedule(sched1)
    fitness = sched2.fitness()
    print 'sched2 ', fitness
    #sched1 = sched1.from_Schedule(sched1)
    #sched1.display_sched()
    #pprint.pprint(sched1.slots, width=2)
    print '---------------------------------------------------------------------'
    #pprint.pprint((sched1.allocation_maps))
    print sched1
    print '---------------------------------------------------------------------'
    sched1.mutate2(100)
    print 'Sched1 mutated'
    fitness = sched1.fitness()
    print 'sched1 ', fitness
    sched2 = sched2.from_Schedule(sched1)
    fitness = sched2.fitness()
    print 'sched2 ', fitness
    sched2.mutate2(100)
    print 'Sched2 mutated'
    fitness = sched2.fitness()
    print 'sched2 ', fitness
    fitness = sched1.fitness()
    print 'sched1 ', fitness
    #pprint.pprint(sched1.allocation_maps)
    #pprint.pprint(sched2.allocation_maps)
    print '************************************'
    chi1, chi2 = crossover(sched1, sched2)
    print 'Crossover done'
    fitness = sched1.fitness()
    print 'sched1 ', fitness
    print sched1.slots is sched2.slots
    fitness = sched2.fitness()
    print 'sched2 ', fitness
    fitness = chi1.fitness()
    print 'chi1 ', fitness
    fitness = chi2.fitness()
    print 'chi2 ', fitness
    """print '************************************'
    pprint.pprint(sched1.slots)
    print '************************************'
    pprint.pprint(sched2.slots)
    print '************************************'
    pprint.pprint(chi1.slots)
    #pprint.pprint(chi1.allocation_maps)
    print '************************************'
    pprint.pprint(chi2.slots)
    #pprint.pprint(chi2.allocation_maps)
    print '************************************'
    #print (schedule.fintess(sched1))
    """

    #sched1.display_sched()
    #pprint.pprint(sched1.slots)
    #print '---------------------------------------------------------------------'
    #sched1.mutate(3)
    #pprint.pprint(sched1.allocation_maps)
    #print '---------------------------------------------------------------------'
    #unittest.main()

    print ("Testing EVOLUTION")


