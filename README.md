# 📝 The Ultimate Evolutionary Playground

The Ultimate Evolutionary Playground is a fully terminal-based simulation that models a population of agents evolving over time in a dynamic environment. It’s written in Python with `curses` for real-time ASCII graphics, so it runs directly in a Unix or WSL terminal — no web front-end or GUI toolkit required. At its core, the project combines an agent-based model with a genetic algorithm to produce complex emergent behavior. You can watch as populations adapt to changing food availability, terrain, and the strategies of their peers, all from the comfort of your command line.

***
 ## ✨ Features

* **Fully Terminal-Based**: The simulation is lightweight, portable, and has minimal dependencies. It runs on any Unix-like system (Linux, macOS, WSL) without needing a graphical environment, making it easy to share and reproduce experiments. 
* **Real-Time ASCII Visualization**: Watch evolution unfold with a dynamic ASCII display. The view highlights the best-performing agent, different food types, and obstacles. It also includes a special "heatmap" mode to track and visualize population movement patterns over time.  
* **Automatic Data Logging for Research**: All key statistics—average/best fitness, and the average value for each gene per generation—are automatically saved to a `evolution_interactive.csv` file. This allows you to perform robust data analysis and create publication-quality charts to answer research questions, such as "How does mutation rate affect the evolution of the `food_seek` gene?" 
*  **Interactive Runtime Controls**: Don't just watch—interact! You can pause the simulation to observe a specific event, toggle a high-speed mode to accelerate evolution, or switch display modes on the fly. This makes the tool perfect for live demos and educational purposes.

*** 
##⚙️ How It Works

The simulation follows a classic evolutionary computation loop. Each generation introduces new environmental challenges and refines the population's genetic makeup.

1. **Initialization**: The program first prompts for key parameters like population size, number of generations, and mutation rate. It then creates a grid world with randomly placed food, obstacles, and terrain patches. The first generation of agents is spawned with a diverse set of random genes, including speed, movement bias, food-seeking tendency, and strategy (cooperative/aggressive).

2. **Simulation Loop (A Generation's Life)**: Each generation runs for a fixed number of steps. In each step, every agent makes a decision. Its movement is a combination of random drift, its innate directional bias, and its desire to move towards the nearest food source. Agents with a "cooperative" strategy may follow signals left by others, while "aggressive" agents might chase their peers. Movement costs energy, which is replenished by eating. Terrain can slow agents down or speed them up, and some food may be toxic, reducing fitness.

3. **Reproduction (Survival of the Fittest)**: At the end of a generation, agents are ranked by their fitness score. A small, elite fraction of the top performers is selected as "parents." The next generation is created by taking pairs of these parents and combining their genes through **crossover**, with a chance of **mutation** introducing new traits. This ensures that the successful genetic strategies of one generation are passed on and refined in the next.

4. **Data Logging**: After the reproduction step, key statistics for the now-complete generation are calculated and stored. Once the entire simulation is complete, this comprehensive dataset is saved to a CSV file for further analysis.

***
## 💻 Requirements

* Python 3  `numpy` library (`pip install numpy`) *. A Unix-like terminal environment that supports the `curses` library (Linux, macOS, or Windows Subsystem for Linux (WSL)). Standard Windows `cmd` or PowerShell will not work.

***
## 🚀 Usage

1. **Clone the repository and navigate to the directory.** 
2. **Run the script from your terminal:**
```
python evolution_script.py
```
3. **Enter the initial parameters when prompted:**
```
Number of agents [20]: 
Number of generations [30]: 
Mutation rate (0-1) [0.2]: 
Base food count per generation [10]: 
```
4. **The simulation will begin running in your terminal.**
***



## 🗺 Grid Legend (What Each Symbol Means)

## 🗝️ Simulation Key

| Symbol | Meaning | Details |
|:------:|---------|---------|
| `.` | Empty Cell | Walkable space; nothing currently there. |
| `#` | Obstacle / Wall | Impassable terrain; agents must move around these cells. |
| `*` | Food | Good food; increases an agent’s fitness and replenishes energy when eaten. |
| `!` | Toxic Food *(optional)* | Bad food; decreases fitness/energy when eaten — adds selective pressure. |
| `O` | Agent | A normal agent. Each `O` is one member of the population with its own genes. |
| `@` | Best Agent | The highest-fitness agent of the current generation (elite individual). |
| `1`–`9` | Heatmap Mode | When you press **`h`**, the grid switches to show visit frequency. Higher numbers = cell visited more often. |

### Display Modes
- **Normal mode:** You’ll see `.`, `#`, `*`, `O`, and `@` as described above.  
- **Heatmap mode:** Press **`h`** to toggle a heatmap view — numbers replace cells to show how frequently they’re visited.  

***
## 🎮 Runtime Controls

Interact with the simulation using these keys:

| Key | Action |
|:---:|--------|
| **`p`** | Pause or unpause the simulation. |
| **`s`** | Toggle **fast mode** for quicker steps between frames. |
| **`h`** | Toggle the **heatmap overlay** to see agent paths. |
| **`q`** | Quit the simulation early and save current results. |

---

## 📊 Data & Analysis

After the simulation completes, a file named **`evolution_interactive.csv`** is saved.  
This file contains the generational data, ready for analysis.

**Columns included:**

| Column | Description |
|--------|-------------|
| `Generation` | The generation index. |
| `AvgFitness` | Average fitness across all agents in that generation. |
| `BestFitness` | Fitness of the best agent in that generation. |
| `AvgSpeed` | Average speed gene value. |
| `AvgDirBias` | Average direction-bias gene value. |
| `AvgFoodSeek` | Average food-seeking tendency gene value. |

You can easily load this file into any data analysis tool.  
For example, using Python’s `pandas` and `matplotlib` libraries:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('evolution_interactive.csv')
plt.figure(figsize=(10, 6))
plt.plot(df['Generation'], df['AvgSpeed'], marker='o')
plt.title('Average Agent Speed Over Generations')
plt.xlabel('Generation')
plt.ylabel('Average Speed')
plt.grid(True)
plt.show()
```





