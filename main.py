import pygame
from algorithm import *
from PygamePlotter import Plotter

# initialize the pygame
pygame.init()

# create the screen
screenX = 790
screenY = 790
screen = pygame.display.set_mode((screenX, screenY))

# Title and Icon
pygame.display.set_caption("Smart Rockets")

# initialize Smart rockets
srs = SmartRockets(population_size=1000)
RocketVelocities.start = (200, 380)
RocketVelocities.goal = (200, 40)
RocketVelocities.size = 40
RocketVelocities.magnitude = 20
srs.initialize_population()
srs.calculate_all_fitness()

# rocket population
population = []

rect1 = pygame.Rect(10, 10, 380, 380)
best_panel = (10, 10, 380, 380)
rect2 = pygame.Rect(10, 400, 380, 380)
population_panel = (10, 400, 380, 380)
rect3 = pygame.Rect(400, 10, 380, 380)
update_panel = (400, 10, 380, 380)
rect4 = pygame.Rect(400, 400, 380, 380)
generation_panel = (400, 400, 380, 380)

pop_graph = Plotter(screen, (population_panel[0], population_panel[1]), (population_panel[2], population_panel[3]))
gen_graph = Plotter(screen, (generation_panel[0], generation_panel[1]), (generation_panel[2], generation_panel[3]))
# text
font = pygame.font.Font('freesansbold.ttf', 16)


def draw_text(s, pos, color=(0, 0, 0)):
    text = font.render(s, True, color)
    screen.blit(text, pos)


rocket_img = pygame.image.load("rocket.png")
rocket_img = pygame.transform.rotate(rocket_img, -90)


def draw_rocket(rocket, time, color=(0, 0, 0), offset=(0, 0), limit_x=(10, 380), limit_y=(10, 380)):
    x, y = rocket.path[time][:2]
    vx, vy = rocket.velocities[time]
    if limit_y[0] <= y <= limit_y[1] and limit_x[0] <= x <= limit_x[1]:
        ox, oy = (offset[0], offset[1])
        l = math.hypot(vx, vy)
        angle = 45 + 90 * math.acos(vx / l) / math.pi
        rotated_rocket = pygame.transform.rotate(rocket_img, angle)
        screen.blit(rotated_rocket, (x + ox - 8, y + oy - 8))


def draw_path(path, time, color=(255, 0, 0), offset=(0, 0), limit_x=(10, 380), limit_y=(10, 380)):
    for i in range(max(time-5, 0), time):
        x1, y1 = path[i][:2]
        x2, y2 = path[i][2:]
        if limit_x[0] <= x1 + offset[0] <= limit_x[1] and limit_x[0] <= x2 + offset[0] <= limit_x[1] and limit_y[
            0] <= y1 + offset[1] <= limit_y[1] and \
                limit_y[0] <= y1 + offset[1] <= limit_y[1]:
            pygame.draw.line(screen, color, (x1 + offset[0], y1 + offset[1]), (x2 + offset[0], y2 + offset[1]))


def draw_point(pos, color=(255, 0, 0), offset=(0, 0)):
    pygame.draw.circle(screen, color, (pos[0] + offset[0], pos[1] + offset[1]), 4)
    pygame.draw.circle(screen, color, (pos[0] + offset[0], pos[1] + offset[1]), 10, width=1)


obstacles = []


def draw_obstacle(pos, radius, color=(255, 0, 0), offset=(0, 0)):
    pygame.draw.circle(screen, color, (pos[0] + offset[0], pos[1] + offset[1]), radius)


# Properties to measure and  display
time_count = RocketVelocities.size - 1
generation_number = 0
generation_distance = []
best_fitness = None
best_distance_all = None
best_velocities_ever = None

# Game Loop
running = True
while running:
    # background
    screen.fill((127, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), rect1)
    pygame.draw.rect(screen, (255, 255, 255), rect2)
    pygame.draw.rect(screen, (255, 255, 255), rect3)
    pygame.draw.rect(screen, (255, 255, 255), rect4)
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            RocketVelocities.add_obstacles(mx, my, 30)
            obstacles = RocketVelocities.obstacles
            srs.initialize_population()
            srs.calculate_all_fitness()

            time_count = RocketVelocities.size - 1
            generation_number = 0
            generation_distance = []
            best_fitness = None
            best_distance_all = None
            best_velocities_ever = None

    if time_count == RocketVelocities.size - 1:
        # create next generation
        srs.make_generation()
        srs.calculate_all_fitness()
        population = srs.population
        generation_number += 1
        velocities = srs.get_best_gene()
        best_fitness = srs.get_best_fitness()
        if velocities:
            best_velocities = velocities
            best_distance = velocities.distance
            generation_distance.append(best_distance)
            if best_distance_all is None:
                best_distance_all = best_distance
                best_velocities_ever = best_velocities
            elif best_distance_all is not None and best_distance_all >= best_distance:
                best_distance_all = best_distance
                best_velocities_ever = best_velocities
    # display progress
    draw_point(RocketVelocities.goal, color=(0, 255, 0))
    draw_point(RocketVelocities.start, color=(0, 0, 255))
    for i in range(len(population)):
        draw_path(population[i].path, time_count, color=(169, 169, 169))
        if not population[i].collided:
            draw_rocket(population[i], time_count)
    for i in obstacles:
        draw_obstacle((i[0], i[1]), i[2])
    draw_text(" Generation:" + str(generation_number) + " Time:" + str(time_count), (best_panel[0], best_panel[1]))

    # display best ever
    draw_point(RocketVelocities.goal, color=(0, 255, 0), offset=(update_panel[0], 0))
    draw_point(RocketVelocities.start, color=(0, 0, 255), offset=(update_panel[0], 0))
    if best_velocities_ever:
        draw_text(" Best ever  Distance:" + str(best_distance_all), (update_panel[0], update_panel[1]))
        draw_path(best_velocities_ever.path, time_count, offset=(update_panel[0], 0), limit_y=(10, 390),
                  limit_x=(400, 780))
        draw_rocket(best_velocities_ever, time_count, offset=(update_panel[0], 0))
    else:
        draw_text(" Best ever", (update_panel[0], update_panel[1]))
    for i in obstacles:
        draw_obstacle((i[0], i[1]), i[2], offset=(update_panel[0], 0))

    time_count = (time_count + 1) % RocketVelocities.size
    # display graph
    pop_graph.clear()
    pop_graph.ax.hist(srs.parent_fitness, bins=20)
    pop_graph.ax.set_title("Frequency distribution of parents")
    pop_graph.ax.set_xlabel("Distance")
    pop_graph.ax.set_ylabel("Frequency")
    pop_graph.show()

    # display graph
    gen_graph.clear()
    gen_graph.ax.plot(list(range(1, len(generation_distance) + 1)), generation_distance)
    gen_graph.ax.set_title("Best distance (y) vs generation(x)")
    gen_graph.ax.set_xlabel("Generation")
    gen_graph.ax.set_ylabel("Best Distance")
    gen_graph.show()

    pygame.display.update()
