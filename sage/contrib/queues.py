import heapq
from itertools import count

REMOVED = '<removed-task>'


class PriorityQueue(object):
    """ A basic priority queue implementation where lower integers are higher priority """

    def __init__(self):
        self.tasks = []
        self.task_map = {}
        self.counter = count()

    def clear(self):
        """ Remove all tasks from the queue """

        self.tasks = []
        self.task_map.clear()

    def get(self):
        """ Get (but don't remove) the next task from the queue """

        while self.tasks:
            task = self.tasks[0][2]
            if task is not REMOVED:
                return task

    def add(self, task, priority=0):
        """ Add a task to the queue """

        if task in self.task_map:
            remove_task(task)

        count = next(self.counter)
        entry = [priority, count, task]
        self.task_map[task] = entry
        heapq.heappush(self.tasks, entry)

    def pop(self):
        """ Pop the next task in the queue """

        while self.tasks:
            priority, count, task = heapq.heappop(self.tasks)
            if task is not REMOVED:
                del task_map[task]
                return task

        return None

    def remove(self, task):
        """ Remove a task from the queue """

        entry = task_map.pop(task)
        entry[-1] = REMOVED


class MaxPriorityQueue(PriorityQueue):
    """ PriorityQueue with a higher integer being higher priority """

    def put(self, task, priority=0):
        priority = priority * -1
        super(self, MaxPriorityQueue).put(task, priority)
