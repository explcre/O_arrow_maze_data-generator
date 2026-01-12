"""Arrow Maze Navigation Task Prompts."""

import random

PROMPTS = {
    "default": [
        "Follow the arrows from the starting position. Where does the agent end up?",
        "The agent follows the direction of the arrow in each cell. Trace the path and show the destination.",
        "Starting from the marked cell, follow the arrows step by step. Highlight the final cell.",
    ],
}

def get_prompt(task_type: str = "default") -> str:
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)

def get_all_prompts(task_type: str = "default") -> list[str]:
    return PROMPTS.get(task_type, PROMPTS["default"])
