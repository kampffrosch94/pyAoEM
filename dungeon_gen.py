import random

def seed(s=None):
    random.seed(a=s)

def cellular_automaton(w,h,wall_chance=42,iterations=3,spawn_walls=True):
    """Walls are True."""
    weighted_choices = [(True,wall_chance),(False,100-wall_chance)]
    choices = [x for x,p in weighted_choices for i in range(p)]
    g_map = {} #generator_map
    for x in range(w):
        for y in range(w):
            g_map[(x,y)] = random.choice(choices)

    def block_walls(pos,g_map):
        """How many walls are in a 3x3 block."""
        mx,my = pos
        result = 0
        for x in range(mx-1,mx+2):
            for y in range(my-1,my+2):
                try:
                    result += g_map[(x,y)]
                except KeyError:
                    result += 10
        return result

    for step in range(iterations):
        new_map = g_map.copy()
        for pos in g_map:
            sur_walls = block_walls(pos,new_map)
            if  sur_walls < 5 :
                new_map[pos] = False
            elif spawn_walls and sur_walls == 0:
                new_map[pos] = random.choice(choices)
            else:
                new_map[pos] = True
        g_map = new_map
    return g_map

def check_map(g_map):
    pos_neighbors = {}
    def neighbors(pos):
        mx,my = pos
        result = set()
        for x in range(mx-1,mx+2):
            for y in range(my-1,my+2):
                if (x,y) in g_map and g_map[(x,y)] == False:
                    result.add((x,y))
        return result

    for pos in g_map:
        if g_map[pos] == False:
            pos_neighbors[pos] = neighbors(pos)

    keys = [x for x in pos_neighbors.keys()]
    pos  = keys[0]
    while True:
        cp = pos_neighbors[pos].copy()
        for neighbor in pos_neighbors[pos]:
            cp.update(pos_neighbors[neighbor])
        if pos_neighbors[pos] == cp:
            break
        pos_neighbors[pos] = cp

    result = (pos_neighbors[pos] == set(pos_neighbors.keys()))
    return result

def checked_cellular_automaton(x,y,wall_chance = 42,iterations = 3,
        seeed=None,spawn_walls=True):
    m = cellular_automaton(x,y,wall_chance,iterations,spawn_walls)
    while not check_map(m):
        m = cellular_automaton(x,y,wall_chance,iterations,spawn_walls)
    return m

def quick_display(wall_chance = 42,iterations = 3,seeed=None,
        spawn_walls=True):
    seed(seeed)
    m = checked_cellular_automaton(20,20,wall_chance,
            iterations,spawn_walls)

    for y in range(20):
        s = ""
        for x in range(20):
            if m[(x,y)]:
                s += "#"
            else:
                s += "."
        print(s)
    return m 
