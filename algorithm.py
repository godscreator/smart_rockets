import random
import math


def get_random_velocity(magnitude):
    x = random.uniform(-1, 1)
    y = random.choice([-1, 1]) * math.sqrt(1 - math.pow(x, 2))
    return x * magnitude, y * magnitude


def get_distance(start, end):
    return math.sqrt(math.pow(end[0] - start[0], 2) + math.pow(end[1] - start[1], 2))


class RocketVelocities:
    # class properties
    goal = (0, 0)
    start = (0, 0)
    magnitude = 1
    size = 20
    obstacles = []

    @classmethod
    def add_obstacles(cls, x, y, r):
        cls.obstacles.append((x, y, r))

    # instance properties
    def __init__(self, velocities=None, randomized=False):
        if velocities is not None:
            self.velocities = velocities
        else:
            self.velocities = [(0, 0) for _ in range(RocketVelocities.size)]
        if randomized:
            self.velocities = []
            for i in range(RocketVelocities.size):
                self.velocities.append(get_random_velocity(RocketVelocities.magnitude))
        self.path = []
        self.distance = get_distance(RocketVelocities.start, RocketVelocities.goal)
        self.calculate_distance()
        self.collided = False

    def calculate_distance(self):
        self.path = []
        sum_x, sum_y = RocketVelocities.start
        not_collided = 1
        for i in self.velocities:
            line = [sum_x, sum_y]
            sum_x += i[0] * not_collided
            sum_y += i[1] * not_collided
            for j in RocketVelocities.obstacles:
                collision_distance = get_distance([sum_x, sum_y],(j[0],j[1]))
                if collision_distance <= j[2] + 8:
                    not_collided = 0
                    self.collided = True
                    break
            line.extend([sum_x, sum_y])
            self.path.append(line)
        self.distance = get_distance((sum_x, sum_y), RocketVelocities.goal)
        if not_collided == 0:
            self.distance = get_distance(RocketVelocities.start,RocketVelocities.goal)

    def mutate(self, mutate_rate):
        if random.random() < mutate_rate:
            a = random.randrange(RocketVelocities.size)
            self.velocities[a] = get_random_velocity(RocketVelocities.magnitude)
            self.calculate_distance()

    @staticmethod
    def crossover(parent_a, parent_b):
        a = random.randint(0, RocketVelocities.size)
        return RocketVelocities(velocities=parent_a.velocities[:a] + parent_b.velocities[a:])


class SmartRockets:
    def __init__(self, population_size=10):
        self.population_size = population_size
        self.population = []
        self.fitness = []
        self.current_distances = []
        self.parent_fitness = []
        self.initialize_population()

    def initialize_population(self):
        self.population = []
        for i in range(self.population_size):
            v = RocketVelocities(randomized=True)
            self.population.append(v)

    def calculate_all_fitness(self):
        fitness = []
        total_inverse_distances = []
        self.current_distances = []
        for i in self.population:
            d = i.distance
            self.current_distances.append(d)
        d_min = min(self.current_distances)
        for i in self.current_distances:
            total_inverse_distances.append(1 / (i*i))
        total_inverse_distance = sum(total_inverse_distances)
        for i in range(len(self.population)):
            x = total_inverse_distances[i] / total_inverse_distance
            fitness.append(x)
        self.fitness = fitness

    def pick_one(self):
        x = random.random()
        s = 0
        for i in range(len(self.population)):
            s += self.fitness[i]
            if x < s:
                return self.population[i]
        return self.population[-1]

    def make_generation(self):
        new_population = []
        self.parent_fitness = []
        for i in range(len(self.population)):
            parent_a = self.pick_one()
            parent_b = self.pick_one()
            self.parent_fitness.append(parent_a.distance)
            self.parent_fitness.append(parent_b.distance)
            child = RocketVelocities.crossover(parent_a, parent_b)
            child.mutate(mutate_rate=0.1)
            new_population.append(child)
        self.population = new_population

    def get_best_index(self):
        if self.fitness:
            return self.fitness.index(max(self.fitness))
        else:
            return None

    def get_best_gene(self):
        ind = self.get_best_index()
        if ind is not None:
            return self.population[ind]
        else:
            return None

    def get_best_fitness(self):
        ind = self.get_best_index()
        if ind is not None:
            return self.fitness[ind]
        else:
            return None
