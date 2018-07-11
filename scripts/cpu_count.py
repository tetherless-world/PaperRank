import multiprocessing

print ("This script tests how many cores are visible to 'multiprocessing' in Python.")

print("It is intended to be run from inside a Docker container to ensure full CPU passthrough.")

cpus = multiprocessing.cpu_count()

print('You have', cpus, 'CPUs.')
