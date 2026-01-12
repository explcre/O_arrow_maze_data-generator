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
    """
    
    domain: str = Field(default="arrow_maze")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    generate_videos: bool = Field(default=True)
    video_fps: int = Field(default=10)
    
    # Grid settings
    min_grid_size: int = Field(default=4, description="Minimum grid dimension")
    max_grid_size: int = Field(default=6, description="Maximum grid dimension")
    
    # Agent settings
    agent_radius: int = Field(default=15, description="Radius of the agent marker")
    
    # Colors
    bg_color: tuple[int, int, int] = Field(default=(255, 255, 255))
    grid_color: tuple[int, int, int] = Field(default=(200, 200, 200))
    arrow_color: tuple[int, int, int] = Field(default=(100, 100, 100))
    agent_color: tuple[int, int, int] = Field(default=(50, 150, 255))
    destination_color: tuple[int, int, int] = Field(default=(50, 200, 50))
    path_color: tuple[int, int, int] = Field(default=(255, 200, 100))
