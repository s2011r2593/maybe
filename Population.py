import numpy as np

from Basic import Basic

'''POP FILE'''
class Population:
  def __init__(self, n, t, i, o, h):
    self.type = t
    self.n_in = i
    self.n_out = o
    self.n_hl = h.copy()

    self.size = n
    self.genomes = [t(i, o, self.n_hl) for _ in range(n)]

  # Obsoleted by CMA-ES
  def next_gen(self, m_rate, m_range):
    next_gen = [self.type(self.n_in, self.n_out, self.n_hl) for _ in range(self.size)]

    lottery = []
    total = 0
    for i in self.genomes:
      total += i.fitness
    for i in self.genomes:
      i.fitness /= total
      lottery.append(i.fitness)

    for i in range(self.size):
      p1 = np.random.choice(self.genomes, p=lottery)
      p2 = np.random.choice(self.genomes, p=lottery)
      for j in range(len(p1.weights)):
        if np.random.uniform() > 0.5:
          next_gen[i].weights[j] = p1.weights[j]
        else:
          next_gen[i].weights[j] = p2.weights[j]
      next_gen[i].mutate(m_rate, m_range)

    self.genomes = next_gen

  def cma_es(self):
    param_count = len(self.genomes[0].weights)
    sorted_pop = sorted(self.genomes, key=lambda x: x.fitness, reverse=True)
    n_best = int(np.ceil(.25 * self.size))
    μ_g = [(1/self.size) * sum(i.weights[j] for i in sorted_pop) for j in range(param_count)]
    μ_gplus1 = [(1/self.size) * sum(i.weights[j] for i in sorted_pop[:n_best]) for j in range(param_count)]

    var_gplus1 = [[(1/n_best) * sum([(c.weights[i] - μ_g[i]) * (c.weights[j] - μ_g[j]) for c in sorted_pop[:n_best]]) for i in range(param_count)] for j in range(param_count)]

    next_gen = [self.type(self.n_in, self.n_out, self.n_hl) for _ in range(self.size)]
    for i in range(self.size):
      next_gen[i].weights = np.random.multivariate_normal(μ_gplus1, var_gplus1)
    
    self.genomes = next_gen