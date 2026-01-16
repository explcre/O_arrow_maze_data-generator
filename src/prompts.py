"""Arrow Maze Navigation Task Prompts - Clean version matching video exactly."""

def get_prompt(task_data: dict) -> str:
    """Generate prompt that exactly describes what happens in the video."""
    grid_size = task_data["grid_size"]
    start_row = task_data["start_row"]
    start_col = task_data["start_col"]
    end_row = task_data["end_row"]
    end_col = task_data["end_col"]
    path_length = len(task_data["path"])
    exit_direction = task_data["exit_direction"]
    
    prompt = f"""{grid_size}x{grid_size} grid with directional arrows (↑↓←→) in each cell.
A semi-transparent blue dot starts at row {start_row+1}, column {start_col+1}.

The dot follows the arrow in its current cell, moving one cell per step.
Each visited cell is highlighted with a yellow background.
The dot stops when the arrow points outside the grid boundary.

The dot stops at row {end_row+1}, column {end_col+1} (arrow points {exit_direction}, outside boundary).
Final destination has a green border. Total steps: {path_length}."""

    return prompt


def get_all_prompts() -> list[str]:
    return ["Blue dot follows arrows, yellow visited cells, stops at boundary, green border on final."]
