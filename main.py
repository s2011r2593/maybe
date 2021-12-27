import numpy as np
import matplotlib.pyplot as plt

from Population import Population
from Basic import Basic

# Number, Type, Inputs, Outputs, Hidden Layers
pop = Population(500, Basic, 1, 2, [])

def Rastrigin(x, n=2):
  temp = 0
  for i in range(n):
    temp += (x[i] * x[i]) - (10 * np.cos(2 * np.pi * x[i]))
  return (10 * n) + temp

for g in range(40):
  points = []
  for i in pop.genomes:
    # eval takes an input array and returns an output array
    res = i.eval([1])

    # Rastrigin stuff
    points.append(res)
    score = 1 / (1 + Rastrigin(res)) # Avoid division by zero

    i.fitness = score

  # Plot Rastrigin
  xy = np.transpose(points)
  plt.plot(xy[0], xy[1], 'o', color='black')
  plt.show()

  # Get next gen
  pop.cma_es()