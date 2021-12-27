import numpy as np
import math

def Xavier(n):
  return math.sqrt(1/n)

def Sigmoid(x):
  return 1 / (1 + math.exp(-4.9 * x))

class Basic:
  def __init__(self, n_in, n_out, n_hl):
    self.dims = n_hl.copy()
    self.dims.append(n_out)

    self.weights = np.array([])
    prev = n_in
    for i in self.dims:
      self.weights = np.hstack((self.weights, np.random.normal(100, 5, prev * i)))
      prev = i
    self.dims.insert(0, n_in)

    self.indices = [self.dims[i] * self.dims[i+1] for i in range(len(self.dims) - 1)]
    self.fitness = 0

  def eval(self, inp):
    start = 0
    current = inp.copy()
    for i in range(len(self.dims) - 1):
      step = self.dims[i] * self.dims[i + 1]
      matrix = np.reshape(self.weights[start:(start+step)], (self.dims[i], self.dims[i + 1]))
      current = np.dot(current, matrix)
      for j in range(len(current)):
        current[j] = current[j]
      start += step
    
    return current

  # Obsoleted by CMA-ES
  def mutate(self, m_rate, m_range):
    # TODO: Redo with modulo
    for i in range(len(self.dims) - 1):
      n_in = self.dims[i]
      p_range = m_range * 6 / n_in
      for j in range(n_in * self.dims[i + 1]):
        if np.random.uniform() < m_rate:
          perturb = (np.random.uniform() - 0.5) * p_range
          self.weights[j] += perturb