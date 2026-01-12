"""
Arrow Maze Navigation Task Generator.

Generates grids with directional arrows where the agent follows arrows
until reaching a cell pointing outside or a loop.
"""

import random
import tempfile
import math
from pathlib import Path
from typing import List, Tuple, Set
from PIL import Image, ImageDraw, ImageFont

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class TaskGenerator(BaseGenerator):
    """Arrow maze navigation task generator."""
    
    DIRECTIONS = {
        'up': (0, -1),
        'down': (0, 1),
        'left': (-1, 0),
        'right': (1, 0),
    }
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one task pair."""
        task_data = self._generate_task_data()
        
        first_image = self._render_initial_state(task_data)
        final_image = self._render_final_state(task_data)
        
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(first_image, final_image, task_id, task_data)
        
        prompt = get_prompt(task_data.get("type", "default"))
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    def _generate_task_data(self) -> dict:
        """Generate arrow grid and compute path."""
        grid_size = random.randint(self.config.min_grid_size, self.config.max_grid_size)
        
        # Generate random arrows for each cell
        directions = list(self.DIRECTIONS.keys())
        grid = [[random.choice(directions) for _ in range(grid_size)] for _ in range(grid_size)]
        
        # Choose starting position
        start_col = random.randint(0, grid_size - 1)
        start_row = random.randint(0, grid_size - 1)
        
        # Trace the path
        path = self._trace_path(grid, start_row, start_col, grid_size)
        
        # The destination is the last cell in the path
        end_row, end_col = path[-1]
        
        return {
            "grid_size": grid_size,
            "grid": grid,
            "start_row": start_row,
            "start_col": start_col,
            "end_row": end_row,
            "end_col": end_col,
            "path": path,
            "type": "default",
        }
    
    def _trace_path(self, grid: List[List[str]], start_row: int, start_col: int, 
                    grid_size: int) -> List[Tuple[int, int]]:
        """Trace path following arrows until exit or loop."""
        path = [(start_row, start_col)]
        visited: Set[Tuple[int, int]] = {(start_row, start_col)}
        
        current_row, current_col = start_row, start_col
        max_steps = grid_size * grid_size + 1  # Prevent infinite loops
        
        for _ in range(max_steps):
            direction = grid[current_row][current_col]
            dx, dy = self.DIRECTIONS[direction]
            
            next_col = current_col + dx
            next_row = current_row + dy
            
            # Check if out of bounds
            if not (0 <= next_row < grid_size and 0 <= next_col < grid_size):
                break  # Exits the grid
            
            # Check for loop
            if (next_row, next_col) in visited:
                path.append((next_row, next_col))
                break
            
            path.append((next_row, next_col))
            visited.add((next_row, next_col))
            current_row, current_col = next_row, next_col
        
        return path
    
    def _draw_arrow(self, draw: ImageDraw.Draw, cx: int, cy: int, 
                    direction: str, size: int, color: tuple):
        """Draw an arrow pointing in the given direction."""
        half = size // 2
        shaft_width = size // 6
        head_size = size // 3
        
        if direction == 'up':
            # Shaft
            draw.rectangle([cx - shaft_width, cy - half + head_size, 
                           cx + shaft_width, cy + half], fill=color)
            # Head
            draw.polygon([
                (cx, cy - half),
                (cx - head_size, cy - half + head_size),
                (cx + head_size, cy - half + head_size)
            ], fill=color)
        elif direction == 'down':
            draw.rectangle([cx - shaft_width, cy - half, 
                           cx + shaft_width, cy + half - head_size], fill=color)
            draw.polygon([
                (cx, cy + half),
                (cx - head_size, cy + half - head_size),
                (cx + head_size, cy + half - head_size)
            ], fill=color)
        elif direction == 'left':
            draw.rectangle([cx - half + head_size, cy - shaft_width, 
                           cx + half, cy + shaft_width], fill=color)
            draw.polygon([
                (cx - half, cy),
                (cx - half + head_size, cy - head_size),
                (cx - half + head_size, cy + head_size)
            ], fill=color)
        elif direction == 'right':
            draw.rectangle([cx - half, cy - shaft_width, 
                           cx + half - head_size, cy + shaft_width], fill=color)
            draw.polygon([
                (cx + half, cy),
                (cx + half - head_size, cy - head_size),
                (cx + half - head_size, cy + head_size)
            ], fill=color)
    
    def _render_grid(self, task_data: dict, agent_pos: Tuple[int, int] = None,
                     show_path: bool = False, highlight_end: bool = False) -> Image.Image:
        """Render the arrow grid."""
        width, height = self.config.image_size
        img = Image.new('RGB', (width, height), self.config.bg_color)
        draw = ImageDraw.Draw(img)
        
        grid_size = task_data["grid_size"]
        grid = task_data["grid"]
        
        # Calculate cell size
        margin = 50
        available = min(width, height) - 2 * margin
        cell_size = available // grid_size
        
        # Calculate grid start position
        start_x = (width - grid_size * cell_size) // 2
        start_y = (height - grid_size * cell_size) // 2
        
        # Draw path highlight if requested
        if show_path:
            path = task_data["path"]
            for row, col in path:
                cx = start_x + col * cell_size + cell_size // 2
                cy = start_y + row * cell_size + cell_size // 2
                draw.rectangle(
                    [cx - cell_size // 2 + 2, cy - cell_size // 2 + 2,
                     cx + cell_size // 2 - 2, cy + cell_size // 2 - 2],
                    fill=self.config.path_color
                )
        
        # Draw grid lines
        for i in range(grid_size + 1):
            x = start_x + i * cell_size
            draw.line([(x, start_y), (x, start_y + grid_size * cell_size)], 
                     fill=self.config.grid_color, width=2)
        for i in range(grid_size + 1):
            y = start_y + i * cell_size
            draw.line([(start_x, y), (start_x + grid_size * cell_size, y)], 
                     fill=self.config.grid_color, width=2)
        
        # Draw arrows
        arrow_size = int(cell_size * 0.5)
        for row in range(grid_size):
            for col in range(grid_size):
                cx = start_x + col * cell_size + cell_size // 2
                cy = start_y + row * cell_size + cell_size // 2
                self._draw_arrow(draw, cx, cy, grid[row][col], arrow_size, self.config.arrow_color)
        
        # Highlight destination
        if highlight_end:
            end_row = task_data["end_row"]
            end_col = task_data["end_col"]
            cx = start_x + end_col * cell_size + cell_size // 2
            cy = start_y + end_row * cell_size + cell_size // 2
            
            # Draw highlight circle
            radius = cell_size // 2 - 5
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                        outline=self.config.destination_color, width=4)
        
        # Draw agent
        if agent_pos:
            row, col = agent_pos
            cx = start_x + col * cell_size + cell_size // 2
            cy = start_y + row * cell_size + cell_size // 2
            
            radius = self.config.agent_radius
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                        fill=self.config.agent_color, outline=(0, 0, 0), width=2)
        
        return img
    
    def _render_initial_state(self, task_data: dict) -> Image.Image:
        """Render initial state with agent at start."""
        agent_pos = (task_data["start_row"], task_data["start_col"])
        return self._render_grid(task_data, agent_pos=agent_pos)
    
    def _render_final_state(self, task_data: dict) -> Image.Image:
        """Render final state with agent at destination."""
        agent_pos = (task_data["end_row"], task_data["end_col"])
        return self._render_grid(task_data, agent_pos=agent_pos, 
                                show_path=True, highlight_end=True)
    
    def _generate_video(self, first_image: Image.Image, final_image: Image.Image,
                        task_id: str, task_data: dict) -> str:
        """Generate video showing agent following arrows."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        frames = []
        hold_frames = 5
        frames_per_step = 5
        
        path = task_data["path"]
        
        # Hold initial
        for _ in range(hold_frames):
            frames.append(first_image.copy())
        
        # Animate each step
        for i, (row, col) in enumerate(path):
            # Show current position
            partial_path = path[:i+1]
            frame = self._render_grid(task_data, agent_pos=(row, col), show_path=False)
            
            # Highlight visited cells
            width, height = self.config.image_size
            grid_size = task_data["grid_size"]
            margin = 50
            available = min(width, height) - 2 * margin
            cell_size = available // grid_size
            start_x = (width - grid_size * cell_size) // 2
            start_y = (height - grid_size * cell_size) // 2
            
            draw = ImageDraw.Draw(frame)
            for pr, pc in partial_path[:-1]:
                cx = start_x + pc * cell_size + cell_size // 2
                cy = start_y + pr * cell_size + cell_size // 2
                draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5],
                            fill=self.config.path_color)
            
            for _ in range(frames_per_step):
                frames.append(frame.copy())
        
        # Hold final
        for _ in range(hold_frames * 2):
            frames.append(final_image.copy())
        
        result = self.video_generator.create_video_from_frames(frames, video_path)
        return str(result) if result else None
