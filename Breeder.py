from NeuralNetwork import _random_weight
import random
from random import randint


class Breeder(object):
    """Handles finding and breeding two Creatures"""

    MAX_MUTATIONS = 3
    # Chance is x/1000, so 500 is a 50% chance
    MUTATION_CHANCE = 10

    def __init__(self, tournament_size=3):
        super().__init__()
        self.tournament_size = tournament_size

    def breed(self, creatures):
        """
            Find best creatures, breed them, and mutate the genes

            Returns the new NN weights
        """

        first = self._tournament(creatures)
        second = self._tournament(creatures)

        new_weights = self._recombine_weights(first, second)

        mutated_weights = self._mutate(new_weights)

        return mutated_weights

    def _tournament(self, creatures):
        """Finds the best of 'size' creatures chosen at random"""
        size = self.tournament_size
        return max((random.choice(creatures) for _ in range(size)), key=lambda c: c.total_food_eaten)

    def _recombine_weights(self, first, second):
        first_weights = first.nn.get_network()
        second_weights = second.nn.get_network()

        # Recombine NN weights
        split_index = randint(0, len(first_weights))
        new_weights = first_weights[:split_index] + second_weights[split_index:]

        return new_weights
        
    def _mutate(self, weights):
        mutated_weights = weights[:]
        chance = self.MUTATION_CHANCE

        mutation_count = 0

        for index in range(len(weights)):
            if randint(0, 1000) < chance:
                mutated_weights[index] = _random_weight()
                mutation_count += 1

                if mutation_count >= self.MAX_MUTATIONS:
                    break

        return mutated_weights
