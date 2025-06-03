from PIL import Image, ImageDraw
import os
import random

def create_avatar(size, bg_color, fg_color, pattern, filename):
    # Create new image with background color
    image = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Draw pattern
    if pattern == 'circles':
        # Concentric circles
        for i in range(0, size//2, 50):
            draw.ellipse([i, i, size-i-1, size-i-1], outline=fg_color, width=3)
    
    elif pattern == 'triangles':
        # Center triangle
        points = [(size//2, size//4), (size//4, 3*size//4), (3*size//4, 3*size//4)]
        draw.polygon(points, fill=fg_color)
    
    elif pattern == 'squares':
        # Rotated square
        center = size // 2
        square_size = size // 3
        points = [
            (center - square_size, center - square_size),
            (center + square_size, center - square_size),
            (center + square_size, center + square_size),
            (center - square_size, center + square_size)
        ]
        draw.polygon(points, fill=fg_color)
    
    elif pattern == 'dots':
        # Random dots pattern
        dot_size = 10
        for x in range(0, size, 40):
            for y in range(0, size, 40):
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                draw.ellipse([x + offset_x, y + offset_y, 
                            x + dot_size + offset_x, y + dot_size + offset_y], 
                           fill=fg_color)
    
    elif pattern == 'waves':
        # Wave pattern
        amplitude = size // 20
        for y in range(0, size, 40):
            points = []
            for x in range(-10, size + 10, 5):
                wave_y = y + amplitude * (1 + (x % 2))
                points.append((x, wave_y))
            if points:
                draw.line(points, fill=fg_color, width=3)
    
    # Create circular mask
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse([0, 0, size-1, size-1], fill=255)
    
    # Apply mask
    output = Image.new('RGB', (size, size), (255, 255, 255))
    output.paste(image, mask=mask)
    
    # Save result
    output.save(filename)

def main():
    size = 500
    avatars_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'static', 'images', 'avatars', 'default')
    
    # Create directory if it doesn't exist
    os.makedirs(avatars_dir, exist_ok=True)
    
    # Color schemes (background, foreground)
    color_schemes = [
        ('#E3F2FD', '#2196F3'),  # Blue
        ('#F3E5F5', '#9C27B0'),  # Purple
        ('#E8F5E9', '#4CAF50'),  # Green
        ('#FFF3E0', '#FF9800'),  # Orange
        ('#FFEBEE', '#F44336'),  # Red
        ('#F3E5F5', '#673AB7'),  # Deep Purple
        ('#E0F7FA', '#00BCD4'),  # Cyan
        ('#FFF8E1', '#FFC107'),  # Yellow
        ('#FAFAFA', '#607D8B'),  # Grey
        ('#E8EAF6', '#3F51B5'),  # Indigo
    ]
    
    patterns = ['circles', 'triangles', 'squares', 'dots', 'waves'] * 2
    
    # Generate avatars
    for i, (bg_color, fg_color) in enumerate(color_schemes):
        filename = os.path.join(avatars_dir, f'avatar_{i+1}.png')
        create_avatar(size, bg_color, fg_color, patterns[i], filename)
        print(f'Created avatar {i+1} of {len(color_schemes)}')

if __name__ == '__main__':
    main()
