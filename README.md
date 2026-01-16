# O-73: Arrow Maze Navigation Data Generator

## Task Description
Given a grid with directional arrows in each cell and a starting position, follow the arrows to determine where the agent stops.

**Reasoning Type:** Navigation/Path - Deterministic path following

## Visual Elements
- **Grid**: 4x6 cells with arrow in each
- **Arrows**: Up (↑), down (↓), left (←), right (→)
- **Agent**: Semi-transparent BLUE dot (small, doesn't occlude arrows)
- **Visited Cells**: YELLOW background highlighting
- **Destination**: GREEN border on final cell

## Task Logic
- Agent follows the arrow in its current cell
- Moves one cell in arrow's direction
- **STOPS when**: Current cell's arrow points OUTSIDE the grid boundary
- Cannot stop in a loop (continues following)

## Output Format
```
data/questions/arrow_maze_task/{task_id}/
├── first_frame.png      # Grid with agent at start position
├── final_frame.png      # Path shown in yellow, destination with green border
├── prompt.txt           # Precise description with stopping condition
└── ground_truth.mp4     # Step-by-step navigation animation
```

## Animation Sequence
1. Agent at starting position
2. Agent moves one cell per step following arrows
3. Each visited cell gets yellow background
4. Step counter shows progress
5. "STOP" message when boundary condition met
6. Final destination highlighted with green border

## Usage
```bash
python examples/generate.py --num-samples 100 --seed 42
```

## Configuration
Edit `src/config.py` to customize:
- `min_grid_size` / `max_grid_size`: Grid dimensions (default: 4-6)
- `agent_radius`: Dot size (default: 10px, small)
- `agent_opacity`: Transparency (default: 150, semi-transparent)
- `visited_color`: Yellow for path (default: RGB 255,230,150)

## Sample Prompt
```
A 5x5 grid where each cell contains an arrow (↑↓←→).
A semi-transparent BLUE DOT starts at row 2, column 3.

STOPPING CONDITION:
- The blue dot STOPS when it reaches a cell whose arrow points OUTSIDE the grid boundary
...
```
