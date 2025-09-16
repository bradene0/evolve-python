import curses
import random
import time
import numpy as np
import csv

#user Inputs 
def get_input(prompt, default, cast):
    try:
        val = cast(input(f"{prompt} [{default}]: ") or default)
        return val
    except:
        print(f"Invalid input, using default {default}")
        return default

NUM_AGENTS = get_input("Number of agents", 20, int)
GENERATIONS = get_input("Number of generations", 30, int)
MUTATION_RATE = get_input("Mutation rate (0-1)", 0.2, float)
FOOD_COUNT_BASE = get_input("Base food count per generation", 10, int)

GRID_SIZE = 20
LIFESPAN = 20
OBSTACLE_COUNT = 25
TERRAIN_SLOW = 0.5
TERRAIN_FAST = 1.5
FOOD_TYPES = [{"symbol":"*","value":5},{"symbol":"!","value":-5}]

# Global flag
PAUSED = False
FAST_MODE = False
SHOW_HEATMAP = False
QUIT_SIM = False

class Agent:
    def __init__(self, lineage=None, epigenetic_bias=None):
        self.x = random.randint(0, GRID_SIZE-1)
        self.y = random.randint(0, GRID_SIZE-1)
        self.speed = random.uniform(0.5, 2.0)
        self.dir_bias = random.uniform(-1.0,1.0)
        self.food_seek = random.uniform(0.0,1.0)
        self.energy = 20.0
        self.strategy = random.choice(["cooperative","aggressive"])
        self.fitness = 0.0
        self.lineage = lineage if lineage else []
        self.epigenetic_bias = epigenetic_bias if epigenetic_bias else 0.0

    def sense_food(self, food_positions):
        if not food_positions: return (0,0)
        nearest = min(food_positions,key=lambda f:(f['x']-self.x)**2 + (f['y']-self.y)**2)
        dx = np.sign(nearest['x'] - self.x)
        dy = np.sign(nearest['y'] - self.y)
        return dx,dy

    def sense_pheromones(self, pheromones):
        nearby = [(x,y,intensity) for x,y,intensity in pheromones if np.hypot(x-self.x,y-self.y)<5]
        if nearby:
            x,y,intensity = max(nearby,key=lambda t:t[2])
            return np.sign(x-self.x),np.sign(y-self.y)
        return 0,0

    def move(self, food_positions, obstacles, agents, terrain, pheromones):
        dx = random.choice([-1,0,1]) + self.dir_bias + self.epigenetic_bias
        dy = random.choice([-1,0,1])
        sdx,sdy = self.sense_food(food_positions)
        dx += self.food_seek*sdx
        dy += self.food_seek*sdy

        if self.strategy=="cooperative":
            pdx,pdy = self.sense_pheromones(pheromones)
            dx += 0.2*pdx
            dy += 0.2*pdy
            neighbors = [(a.x,a.y) for a in agents if a!=self and np.hypot(a.x-self.x,a.y-self.y)<5]
            if neighbors:
                cx = np.mean([n[0] for n in neighbors])
                cy = np.mean([n[1] for n in neighbors])
                dx += 0.1*(cx-self.x)
                dy += 0.1*(cy-self.y)
        elif self.strategy=="aggressive":
            others = [(a.x,a.y) for a in agents if a!=self]
            if others:
                nx,ny = min(others,key=lambda n:(n[0]-self.x)**2 + (n[1]-self.y)**2)
                dx += 0.2*(nx-self.x)
                dy += 0.2*(ny-self.y)

        dx *= self.speed
        dy *= self.speed
        terrain_multiplier = terrain[int(self.y)][int(self.x)]
        dx *= terrain_multiplier
        dy *= terrain_multiplier
        new_x = max(0,min(GRID_SIZE-1,self.x+dx))
        new_y = max(0,min(GRID_SIZE-1,self.y+dy))
        if (int(new_x),int(new_y)) not in obstacles:
            self.x = new_x
            self.y = new_y

        self.energy -= 0.5
        self.fitness += np.hypot(dx,dy)
        eaten=[]
        for f in food_positions:
            if int(self.x)==f['x'] and int(self.y)==f['y']:
                self.fitness += f['value']
                self.energy += max(f['value'],0)
                eaten.append(f)
        for f in eaten: food_positions.remove(f)

def generate_food(season):
    count = FOOD_COUNT_BASE + season
    return [{"x":random.randint(0,GRID_SIZE-1),
             "y":random.randint(0,GRID_SIZE-1),
             "symbol":random.choice(FOOD_TYPES)['symbol'],
             "value":random.choice(FOOD_TYPES)['value']} for _ in range(count)]

def generate_obstacles():
    return set((random.randint(0,GRID_SIZE-1),random.randint(0,GRID_SIZE-1)) for _ in range(OBSTACLE_COUNT))

def generate_terrain():
    terrain = np.ones((GRID_SIZE,GRID_SIZE))
    for _ in range(15): terrain[random.randint(0,GRID_SIZE-1)][random.randint(0,GRID_SIZE-1)] = TERRAIN_SLOW
    for _ in range(15): terrain[random.randint(0,GRID_SIZE-1)][random.randint(0,GRID_SIZE-1)] = TERRAIN_FAST
    return terrain

def reproduce(pop):
    sorted_pop = sorted(pop,key=lambda a:a.fitness,reverse=True)
    elites = sorted_pop[:max(1,len(pop)//5)]
    new_pop=[]
    while len(new_pop)<len(pop):
        p1,p2=random.sample(elites,2)
        epigenetic_bias = (p1.epigenetic_bias+p2.epigenetic_bias)/2 + random.uniform(-0.05,0.05)
        child = Agent(lineage=p1.lineage+[p1],epigenetic_bias=epigenetic_bias)
        child.speed = (p1.speed+p2.speed)/2*(1+random.uniform(-MUTATION_RATE,MUTATION_RATE))
        child.dir_bias = (p1.dir_bias+p2.dir_bias)/2*(1+random.uniform(-MUTATION_RATE,MUTATION_RATE))
        child.food_seek = (p1.food_seek+p2.food_seek)/2*(1+random.uniform(-MUTATION_RATE,MUTATION_RATE))
        child.strategy = random.choice([p1.strategy,p2.strategy])
        new_pop.append(child)
    return new_pop

def draw_grid(stdscr,pop,best_agent,food_positions,obstacles,heatmap,gen,step):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    for y in range(min(GRID_SIZE,max_y-5)):
        row=""
        for x in range(min(GRID_SIZE,(max_x//2)-1)):
            char='.'
            if (x,y) in obstacles: char='#'
            for f in food_positions:
                if f['x']==x and f['y']==y: char=f['symbol']
            for a in pop:
                if int(a.x)==x and int(a.y)==y:
                    char='@' if a==best_agent else 'O'
            if SHOW_HEATMAP and heatmap[y][x]>0:
                char=str(min(int(heatmap[y][x]),9))
            row += char + ' '
        stdscr.addstr(y, 0, row)
    info_y1 = min(GRID_SIZE+1, max_y-3)
    info_y2 = min(GRID_SIZE+2, max_y-2)
    stdscr.addstr(info_y1, 0, f"Gen {gen+1}/{GENERATIONS} Step {step}/{LIFESPAN}")
    stdscr.addstr(info_y2, 0, f"p=Pause({PAUSED}) s=Fast({FAST_MODE}) h=Heatmap({SHOW_HEATMAP}) q=Quit")
    stdscr.refresh()

def main(stdscr):
    global PAUSED, FAST_MODE, SHOW_HEATMAP, QUIT_SIM
    curses.curs_set(0)
    stdscr.nodelay(True)

    population=[Agent() for _ in range(NUM_AGENTS)]
    heatmap=np.zeros((GRID_SIZE,GRID_SIZE))
    avg_fit_history=[]
    best_fit_history=[]
    avg_speed_history=[]
    avg_dirbias_history=[]
    avg_foodseek_history=[]

    for gen in range(GENERATIONS):
        season=gen%5
        food_positions=generate_food(season)
        obstacles=generate_obstacles()
        terrain=generate_terrain()
        pheromones=[]
        for step in range(LIFESPAN):
            key = stdscr.getch()
            if key == ord('p'): PAUSED = not PAUSED
            if key == ord('s'): FAST_MODE = not FAST_MODE
            if key == ord('h'): SHOW_HEATMAP = not SHOW_HEATMAP
            if key == ord('q'): QUIT_SIM = True
            if QUIT_SIM: return
            while PAUSED:
                time.sleep(0.1)
                key = stdscr.getch()
                if key == ord('p'): PAUSED = not PAUSED
                if key == ord('q'): return

            pheromones=[(int(a.x),int(a.y),a.fitness/10) for a in population if a.strategy=="cooperative"]
            for a in population: a.move(food_positions,obstacles,population,terrain,pheromones)
            best_agent=max(population,key=lambda a:a.fitness)
            draw_grid(stdscr,population,best_agent,food_positions,obstacles,heatmap,gen,step)
            time.sleep(0.01 if FAST_MODE else 0.05)

        avg_fit=np.mean([a.fitness for a in population])
        best_fit=best_agent.fitness
        avg_speed=np.mean([a.speed for a in population])
        avg_dirbias=np.mean([a.dir_bias for a in population])
        avg_foodseek=np.mean([a.food_seek for a in population])
        avg_fit_history.append(avg_fit)
        best_fit_history.append(best_fit)
        avg_speed_history.append(avg_speed)
        avg_dirbias_history.append(avg_dirbias)
        avg_foodseek_history.append(avg_foodseek)
        population=reproduce(population)
        time.sleep(0.2)

    with open('evolution_interactive.csv','w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['Generation','AvgFitness','BestFitness','AvgSpeed','AvgDirBias','AvgFoodSeek'])
        for i,(af,bf,speed,db,fs) in enumerate(zip(avg_fit_history,best_fit_history,avg_speed_history,avg_dirbias_history,avg_foodseek_history),1):
            writer.writerow([i,af,bf,speed,db,fs])

    max_y, max_x = stdscr.getmaxyx()
    info_y3 = min(GRID_SIZE+4, max_y-1)
    stdscr.addstr(info_y3, 0, "Simulation complete! CSV saved as evolution_interactive.csv")
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)

