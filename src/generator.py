"""
Arrow Maze Navigation Task Generator - Clean version.

Features:
- Semi-transparent blue dot (small, doesn't occlude arrows)
- Yellow background on visited cells
- Green border on final destination
- No text overlays in video
"""

import random
import tempfile
from pathlib import Path
from typing import List, Tuple, Set
from PIL import Image, ImageDraw, ImageFont

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class TaskGenerator(BaseGenerator):
    """Arrow maze navigation task generator."""
    
    DIRECTIONS = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        task_data = self._generate_task_data()
        
        first_image = self._render_initial_state(task_data)
        final_image = self._render_final_state(task_data)
        
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(first_image, final_image, task_id, task_data)
        
        prompt = get_prompt(task_data)
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    def _generate_task_data(self) -> dict:
        grid_size = random.randint(self.config.min_grid_size, self.config.max_grid_size)
        directions = list(self.DIRECTIONS.keys())
        grid = [[random.choice(directions) for _ in range(grid_size)] for _ in range(grid_size)]
        
        start_col = random.randint(0, grid_size - 1)
        start_row = random.randint(0, grid_size - 1)
        
        path = self._trace_path(grid, start_row, start_col, grid_size)
        end_row, end_col = path[-1]
        exit_direction = grid[end_row][end_col]
        
        return {
            "grid_size": grid_size,
            "grid": grid,
            "start_row": start_row,
            "start_col": start_col,
            "end_row": end_row,
            "end_col": end_col,
            "path": path,
            "exit_direction": exit_direction,
        }
    
    def _trace_path(self, grid, start_row, start_col, grid_size):
        path = [(start_row, start_col)]
        visited = {(start_row, start_col)}
        current_row, current_col = start_row, start_col
        
        for _ in range(grid_size * grid_size + 1):
            direction = grid[current_row][current_col]
            dx, dy = self.DIRECTIONS[direction]
            next_col, next_row = current_col + dx, current_row + dy
            
            if not (0 <= next_row < grid_size and 0 <= next_col < grid_size):
                break
            
            if (next_row, next_col) in visited:
                path.append((next_row, next_col))
                break
            
            path.append((next_row, next_col))
            visited.add((next_row, next_col))
            current_row, current_col = next_row, next_col
        
        return path
    
    def _draw_arrow(self, draw, cx, cy, direction, size, color):
        half = size // 2
        shaft_width = size // 6
        head_size = size // 3
        
        if direction == 'up':
            draw.rectangle([cx - shaft_width, cy - half + head_size, cx + shaft_width, cy + half], fill=color)
            draw.polygon([(cx, cy - half), (cx - head_size, cy - half + head_size), 
                         (cx + head_size, cy - half + head_size)], fill=color)
        elif direction == 'down':
            draw.rectangle([cx - shaft_width, cy - half, cx + shaft_width, cy + half - head_size], fill=color)
            draw.polygon([(cx, cy + half), (cx - head_size, cy + half - head_size),
                         (cx + head_size, cy + half - head_size)], fill=color)
        elif direction == 'left':
            draw.rectangle([cx - half + head_size, cy - shaft_width, cx + half, cy + shaft_width], fill=color)
            draw.polygon([(cx - half, cy), (cx - half + head_size, cy - head_size),
                         (cx - half + head_size, cy + head_size)], fill=color)
        elif direction == 'right':
            draw.rectangle([cx - half, cy - shaft_width, cx + half - head_size, cy + shaft_width], fill=color)
            draw.polygon([(cx + half, cy), (cx + half - head_size, cy - head_size),
                         (cx + half - head_size, cy + head_size)], fill=color)
    
    def _render_grid(self, task_data: dict, agent_pos=None, visited_cells=None,
                     highlight_end: bool = False) -> Image.Image:
        width, height = self.config.image_size
        img = Image.new('RGBA', (width, height), (*self.config.bg_color, 255))
        draw = ImageDraw.Draw(img)
        
        grid_size = task_data["grid_size"]
        grid = task_data["grid"]
        
        margin = 50
        available = min(width, height) - 2 * margin
        cell_size = available // grid_size
        
        start_x = (width - grid_size * cell_size) // 2
        start_y = (height - grid_size * cell_size) // 2
        
        # Draw visited cells (yellow)
        if visited_cells:
            for row, col in visited_cells:
                cx = start_x + col * cell_size + cell_size // 2
                cy = start_y + row * cell_size + cell_size // 2
                draw.rectangle([cx - cell_size // 2 + 2, cy - cell_size // 2 + 2,
                               cx + cell_size // 2 - 2, cy + cell_size // 2 - 2],
                              fill=(*self.config.visited_color, 200))
        
        # Highlight destination
        if highlight_end:
            end_row, end_col = task_data["end_row"], task_data["end_col"]
            cx = start_x + end_col * cell_size + cell_size // 2
            cy = start_y + end_row * cell_size + cell_size // 2
            draw.rectangle([cx - cell_size // 2 + 1, cy - cell_size // 2 + 1,
                           cx + cell_size // 2 - 1, cy + cell_size // 2 - 1],
                          outline=self.config.destination_color, width=4)
        
        # Grid lines
        for i in range(grid_size + 1):
            x = start_x + i * cell_size
            draw.line([(x, start_y), (x, start_y + grid_size * cell_size)],
                     fill=(*self.config.grid_color, 255), width=2)
            y = start_y + i * cell_size
            draw.line([(start_x, y), (start_x + grid_size * cell_size, y)],
                     fill=(*self.config.grid_color, 255), width=2)
        
        # Arrows
        arrow_size = int(cell_size * 0.5)
        for row in range(grid_size):
            for col in range(grid_size):
                cx = start_x + col * cell_size + cell_size // 2
                cy = start_y + row * cell_size + cell_size // 2
                self._draw_arrow(draw, cx, cy, grid[row][col], arrow_size,
                               (*self.config.arrow_color, 255))
        
        # Agent (semi-transparent blue dot)
        if agent_pos:
            row, col = agent_pos
            cx = start_x + col * cell_size + cell_size // 2
            cy = start_y + row * cell_size + cell_size // 2
            radius = self.config.agent_radius
            
            agent_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            agent_draw = ImageDraw.Draw(agent_layer)
            agent_draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                             fill=(*self.config.agent_color, self.config.agent_opacity),
                             outline=(0, 0, 0, 200), width=1)
            img = Image.alpha_composite(img, agent_layer)
        
        return img.convert('RGB')
    
    def _render_initial_state(self, task_data: dict) -> Image.Image:
        return self._render_grid(task_data, agent_pos=(task_data["start_row"], task_data["start_col"]))
    
    def _render_final_state(self, task_data: dict) -> Image.Image:
        return self._render_grid(task_data, agent_pos=(task_data["end_row"], task_data["end_col"]),
                                visited_cells=task_data["path"], highlight_end=True)
    
    def _generate_video(self, first_image, final_image, task_id: str, task_data: dict) -> str:
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        frames = []
        hold_frames = 8
        frames_per_step = 6
        
        path = task_data["path"]
        
        for _ in range(hold_frames):
            frames.append(first_image.copy())
        
        for i, (row, col) in enumerate(path):
            visited_so_far = path[:i+1]
            is_last = (i == len(path) - 1)
            
            frame = self._render_grid(task_data, agent_pos=(row, col),
                                      visited_cells=visited_so_far, highlight_end=is_last)
            
            for _ in range(frames_per_step):
                frames.append(frame.copy())
        
        for _ in range(hold_frames * 2):
            frames.append(final_image.copy())
        
        result = self.video_generator.create_video_from_frames(frames, video_path)
        return str(result) if result else None
