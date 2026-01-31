"""Generate PNG icons for H.A.M.A.L using Pillow."""

import math
import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Icon color - dark so it shows on colored button backgrounds
ICON_COLOR = "#1e1e2e"  # Dark (matches base theme)
ICON_COLOR_LIGHT = "#cdd6f4"  # Light for dark background buttons

# Ensure we're running from project root
# Directory where icons will be saved (relative to project root)
ICONS_DIR = Path("src/hamal/ui/assets/icons")
ICONS_DIR.mkdir(parents=True, exist_ok=True)


def create_icon(name, draw_func, color, size=64):
    """Create and save an icon."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_func(draw, size, color)
    img.save(ICONS_DIR / f"{name}.png", "PNG")
    print(f"Generated {name}.png")


def draw_play(draw, s, color):
    """Play triangle."""
    pad = s * 0.2
    points = [
        (pad + s*0.05, pad),
        (pad + s*0.05, s - pad),
        (s - pad, s/2)
    ]
    draw.polygon(points, fill=color)


def draw_stop(draw, s, color):
    """Stop square."""
    pad = s * 0.25
    draw.rounded_rectangle(
        [pad, pad, s-pad, s-pad],
        radius=s*0.08,
        fill=color
    )


def draw_plus(draw, s, color):
    """Plus sign."""
    t = s * 0.18  # thickness
    # Vertical bar
    draw.rounded_rectangle(
        [s/2 - t/2, s*0.18, s/2 + t/2, s*0.82],
        radius=t/2, fill=color
    )
    # Horizontal bar
    draw.rounded_rectangle(
        [s*0.18, s/2 - t/2, s*0.82, s/2 + t/2],
        radius=t/2, fill=color
    )


def draw_settings(draw, s, color):
    """Settings gear."""
    center = (s/2, s/2)
    outer_r = s * 0.38
    inner_r = s * 0.15
    
    # Teeth
    num_teeth = 8
    for i in range(num_teeth):
        angle = (i / num_teeth) * 2 * math.pi
        x = center[0] + outer_r * math.cos(angle)
        y = center[1] + outer_r * math.sin(angle)
        tooth_size = s * 0.12
        draw.ellipse([x-tooth_size, y-tooth_size, x+tooth_size, y+tooth_size], fill=color)
    
    # Main body
    draw.ellipse(
        [center[0]-outer_r*0.85, center[1]-outer_r*0.85,
         center[0]+outer_r*0.85, center[1]+outer_r*0.85],
        fill=color
    )
    
    # Center hole (transparent)
    draw.ellipse(
        [center[0]-inner_r, center[1]-inner_r,
         center[0]+inner_r, center[1]+inner_r],
        fill=(0, 0, 0, 0)
    )


def draw_trash(draw, s, color):
    """Trash bin."""
    # Body
    body_top = s * 0.3
    body_left = s * 0.25
    body_right = s - s * 0.25
    body_bottom = s - s * 0.15
    draw.rounded_rectangle(
        [body_left, body_top, body_right, body_bottom],
        radius=s*0.05,
        fill=color
    )
    # Lid
    lid_y = s * 0.22
    draw.rounded_rectangle(
        [s*0.2, lid_y - s*0.06, s*0.8, lid_y + s*0.04],
        radius=s*0.03,
        fill=color
    )
    # Handle
    draw.rounded_rectangle(
        [s*0.38, s*0.1, s*0.62, s*0.2],
        radius=s*0.03,
        fill=color
    )


def draw_logs(draw, s, color):
    """Document/logs icon."""
    pad = s * 0.2
    # Document outline
    draw.rounded_rectangle(
        [pad, pad, s-pad, s-pad],
        radius=s*0.06,
        outline=color,
        width=int(s*0.08)
    )
    # Lines
    line_pad = s * 0.32
    line_spacing = s * 0.15
    for i in range(3):
        y = line_pad + i * line_spacing
        draw.rounded_rectangle(
            [pad + s*0.12, y, s - pad - s*0.12, y + s*0.06],
            radius=s*0.02,
            fill=color
        )


def draw_folder(draw, s, color):
    """Folder icon."""
    pad = s * 0.18
    # Main body
    draw.rounded_rectangle(
        [pad, pad + s*0.15, s-pad, s-pad],
        radius=s*0.06,
        fill=color
    )
    # Tab
    draw.polygon([
        (pad, pad + s*0.15),
        (pad, pad + s*0.05),
        (pad + s*0.25, pad + s*0.05),
        (pad + s*0.35, pad + s*0.15),
    ], fill=color)


def draw_clear(draw, s, color):
    """Clear/brush icon."""
    # Simple X
    t = s * 0.12
    # Diagonal 1
    draw.line([(s*0.25, s*0.25), (s*0.75, s*0.75)], fill=color, width=int(t))
    # Diagonal 2
    draw.line([(s*0.75, s*0.25), (s*0.25, s*0.75)], fill=color, width=int(t))


def main():
    print("Generating icons...")
    
    # Dark icons for colored buttons (play=green, stop=red, plus=blue)
    create_icon("play", draw_play, ICON_COLOR)
    create_icon("stop", draw_stop, ICON_COLOR)
    create_icon("plus", draw_plus, ICON_COLOR)
    
    # Light icons for gray/dark buttons
    create_icon("settings", draw_settings, ICON_COLOR_LIGHT)
    create_icon("trash", draw_trash, ICON_COLOR_LIGHT)
    create_icon("logs", draw_logs, ICON_COLOR_LIGHT)
    create_icon("folder", draw_folder, ICON_COLOR_LIGHT)
    create_icon("clear", draw_clear, ICON_COLOR_LIGHT)
    
    print("Done!")


if __name__ == "__main__":
    main()
