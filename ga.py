import numpy as np

class GeneticAlgorithm:
    def __init__(self, pop_size, genome_length,
                 mutation_rate=0.1, mutation_strength=0.2):
        self.pop_size = pop_size
        self.genome_length = genome_length
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.population = [np.random.randn(genome_length) * 0.5
                           for _ in range(pop_size)]

    def evolve(self, fitnesses):
        paired = sorted(zip(fitnesses, self.population),
                        key=lambda x: x[0], reverse=True)
        survivors = [g for _, g in paired[:self.pop_size // 2]]

        new_pop = survivors.copy()  # elites carry over unchanged
        while len(new_pop) < self.pop_size:
            p1 = survivors[np.random.randint(len(survivors))]
            p2 = survivors[np.random.randint(len(survivors))]
            child = self._crossover(p1, p2)
            child = self._mutate(child)
            new_pop.append(child)

        self.population = new_pop
        return self.population

    def _crossover(self, p1, p2):
        mask = np.random.rand(self.genome_length) > 0.5
        return np.where(mask, p1, p2)

    def _mutate(self, genome):
        mask = np.random.rand(self.genome_length) < self.mutation_rate
        noise = np.random.randn(self.genome_length) * self.mutation_strength
        return genome + mask * noise