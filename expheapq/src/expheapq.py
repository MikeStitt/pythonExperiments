import heapq
import copy
import random


class Orderable():

    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        return self.value < other.value


def printList(name, givenlist):
    print(f"{name}=", end="")
    for i in alist:
        print(f" {i.value}", end="")
    print()

if __name__ == "__main__":

    alist = []

    for i in range(10):
        alist.append(Orderable(i))

    blist =copy.deepcopy(alist)

    random.shuffle(alist)

    printList("alist      ", alist)

    heapq.heapify(alist)

    printList("(heapified)", alist)

    print(f"type of alist: {type(alist)}")

    print(f"min of heapifiedlist= {min(alist).value}")


