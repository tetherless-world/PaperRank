# Script to test the `multiprocessing` package behavior
# Intended to be used with Dockerfile to test behavior
# GOAL: Create Processes in a process pool of a fixed size,
#       corresponding to the number of cores on the target machine.
#       The processes will pop an item from a list, and when complete
#       will reduce the number of active threads. There can at most be
#       n processes, where n is the number of processes in the Pool.

from multiprocessing import Pool, Manager
import os
from time import sleep


# Function to decrement counter, this is analogous
# to a Query thread.
def decrementFunction(x, p, lock):
    # (Do stuff here)
    sleep(1)
    # Acquire lock
    lock.acquire()
    # Decrement counter
    p.value -= 1
    # Release lock
    lock.release()


if __name__ == '__main__':
    # Process model for farmer thread
    # Let this list be the EXPLORE
    explore = list(range(100))

    # Setting pool size
    pool_size = os.cpu_count()

    # Global iteration counter
    n = 1

    # Creating process pool of size `pool_size`, and limiting the maximum
    # number of tasks before new process is spawned. This is done to
    # streamline memory management (with regard to redis connections).
    pool = Pool(processes=pool_size, maxtasksperchild=10)

    # Creating manager object and shared counter value
    m = Manager()
    p = m.Value('i', 0)

    # Creating lock (using same manager)
    lock = m.Lock()

    # Iterate until EXPLORE is empty
    while len(explore) is not 0:

        # Only create a new process if the current number of active
        # threads is below total number of workers in pool.
        if p.value < pool_size:
            # Acquire lock for counter
            lock.acquire()
            # Create asynchronous process (non-blocking here)
            pool.apply_async(decrementFunction, (explore.pop(), p, lock, ))
            # Incremenet process counter
            p.value += 1
            # Release lock
            lock.release()
        # Print update
        print('on run', n, 'with explore size', len(explore),
              'and', p.value, 'active processes')
        n += 1
    pool.close()
    print('reached the end!')
