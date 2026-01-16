"""
Arrow Maze Navigation Task Configuration.
"""

from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Arrow Maze Navigation task configuration.
    
    Task: Given a grid with directional arrows in each cell and a starting position,
    follow the arrows to determine the final destination.
    The agent stops when it reaches a cell whose arrow points outside the grid.
    """
    
    domain: str = Field(default="arrow_maze")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    generate_videos: bool = Field(default=True)
    video_fps: int = Field(default=10)
    
    # Grid settings
    min_grid_size: int = Field(default=4, description="Minimum grid dimension")
    max_grid_size: int = Field(default=6, description="Maximum grid dimension")
    
    # Agent settings
    agent_radius: int = Field(default=10, description="Radius of the agent dot (smaller)")
    agent_opacity: int = Field(default=150, description="Agent opacity (0-255, semi-transparent)")
    
    # Colors
    bg_color: tuple[int, int, int] = Field(default=(255, 255, 255))
    grid_color: tuple[int, int, int] = Field(default=(200, 200, 200))
    arrow_color: tuple[int, int, int] = Field(default=(80, 80, 80))
    agent_color: tuple[int, int, int] = Field(default=(50, 150, 255))  # Blue
    visited_color: tuple[int, int, int] = Field(default=(255, 230, 150))  # Yellow for visited
    destination_color: tuple[int, int, int] = Field(default=(50, 200, 50))  # Green for destination
