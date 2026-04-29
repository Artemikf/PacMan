import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Pac-Man Game")
    parser.add_argument("--difficulty", choices=["easy", "normal", "hard"],
                        default="normal", help="Game difficulty")
    parser.add_argument("--bg-color", type=str, default="black",
                        help="Background color (name or hex, e.g., 'darkblue' or '#001133')")
    return parser.parse_args()

def get_bg_color(color_str):
    import pygame
    if color_str.startswith("#") and len(color_str) == 7:
        return tuple(int(color_str[i:i+2], 16) for i in (1,3,5))
    return pygame.Color(color_str)