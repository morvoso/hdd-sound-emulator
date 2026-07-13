#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw

ICONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

def draw_hdd_icon(state="idle", filename="icon_idle.png"):
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Outer HDD chassis casing (silver/grey rounded rect)
    if state == "disabled":
        chassis_color = (120, 120, 120, 230)
        border_color = (80, 80, 80, 255)
        platter_color = (100, 100, 100, 255)
    else:
        chassis_color = (210, 215, 220, 255)
        border_color = (140, 145, 150, 255)
        platter_color = (180, 185, 190, 255)
        
    # Draw chassis box
    draw.rounded_rectangle([8, 6, 56, 58], radius=6, fill=chassis_color, outline=border_color, width=2)
    
    # Inner platter recess (circle at top half)
    draw.ellipse([14, 10, 50, 46], fill=platter_color, outline=(130, 135, 140, 255), width=1)
    # Spindle hub
    draw.ellipse([27, 23, 37, 33], fill=(80, 85, 90, 255), outline=(60, 65, 70, 255), width=1)
    
    # Actuator arm
    draw.line([46, 42, 33, 27], fill=(90, 90, 95, 255), width=3)
    draw.ellipse([43, 39, 49, 45], fill=(70, 70, 75, 255)) # arm pivot
    
    # Bottom logic board / bezel section
    draw.rectangle([8, 46, 56, 58], fill=(50, 55, 60, 255), outline=border_color, width=1)
    
    # Activity LED / Status light on bezel
    # Left LED: Power (Green)
    if state == "disabled":
        draw.ellipse([14, 49, 20, 55], fill=(80, 90, 80, 255)) # dim green
    else:
        draw.ellipse([14, 49, 20, 55], fill=(40, 220, 60, 255)) # bright green
        
    # Right LED: HDD Activity (Red / Orange when active)
    if state == "active":
        # Bright pulsing red/orange activity LED with glow
        draw.ellipse([25, 49, 31, 55], fill=(255, 60, 20, 255), outline=(255, 180, 50, 255))
    elif state == "idle":
        # Dim/off activity LED
        draw.ellipse([25, 49, 31, 55], fill=(90, 40, 40, 255))
    else:
        # Disabled state
        draw.ellipse([25, 49, 31, 55], fill=(60, 60, 60, 255))
        
    # If disabled, draw a red diagonal strike or cross
    if state == "disabled":
        draw.line([12, 12, 52, 52], fill=(220, 40, 40, 230), width=4)
        draw.line([52, 12, 12, 52], fill=(220, 40, 40, 230), width=4)
        
    filepath = os.path.join(ICONS_DIR, filename)
    img.save(filepath, "PNG")
    print(f"Generated {filepath}")

if __name__ == "__main__":
    draw_hdd_icon("idle", "icon_idle.png")
    draw_hdd_icon("active", "icon_active.png")
    draw_hdd_icon("disabled", "icon_disabled.png")
