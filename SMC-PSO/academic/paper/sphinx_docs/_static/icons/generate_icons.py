#!/usr/bin/env python3
"""
============================================================================
PWA Icon Generator - Simple Placeholder Icons
============================================================================

Generates 192x192 and 512x512 PNG icons for the PWA manifest.
Uses PIL/Pillow to create basic gradient background with text overlay.

For production, replace with custom SVG converted to PNG.

Usage:
    python generate_icons.py

Output:
    - icon-192x192.png
    - icon-512x512.png
============================================================================
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Brand colors
COLOR_PRIMARY = (102, 126, 234)  # #667eea
COLOR_SECONDARY = (118, 75, 162)  # #764ba2
COLOR_WHITE = (255, 255, 255)
COLOR_TEXT_SHADOW = (40, 40, 60)

def create_gradient_background(size):
    """Create a radial gradient background"""
    image = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(image)

    # Create radial gradient from center
    center_x, center_y = size // 2, size // 2
    max_radius = int((size / 2) * 1.414)  # diagonal

    for radius in range(max_radius, 0, -1):
        # Interpolate between primary and secondary colors
        ratio = radius / max_radius
        r = int(COLOR_PRIMARY[0] * ratio + COLOR_SECONDARY[0] * (1 - ratio))
        g = int(COLOR_PRIMARY[1] * ratio + COLOR_SECONDARY[1] * (1 - ratio))
        b = int(COLOR_PRIMARY[2] * ratio + COLOR_SECONDARY[2] * (1 - ratio))

        # Draw concentric circles
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            fill=(r, g, b)
        )

    return image

def draw_pendulum_simple(draw, size):
    """Draw a simplified pendulum representation"""
    center_x, center_y = size // 2, size // 2
    scale = size / 512  # Scale factor for different sizes

    # Base/cart
    cart_y = int(center_y + 120 * scale)
    cart_w = int(60 * scale)
    cart_h = int(20 * scale)
    draw.rectangle(
        [center_x - cart_w // 2, cart_y - cart_h // 2,
         center_x + cart_w // 2, cart_y + cart_h // 2],
        fill=COLOR_WHITE
    )

    # First pendulum
    p1_x = int(center_x + 30 * scale)
    p1_y = int(center_y - 20 * scale)
    draw.line([center_x, cart_y, p1_x, p1_y], fill=COLOR_WHITE, width=int(6 * scale))
    draw.ellipse(
        [p1_x - int(15 * scale), p1_y - int(15 * scale),
         p1_x + int(15 * scale), p1_y + int(15 * scale)],
        fill=COLOR_WHITE
    )

    # Second pendulum
    p2_x = int(center_x + 10 * scale)
    p2_y = int(center_y - 100 * scale)
    draw.line([p1_x, p1_y, p2_x, p2_y], fill=COLOR_WHITE, width=int(5 * scale))
    draw.ellipse(
        [p2_x - int(12 * scale), p2_y - int(12 * scale),
         p2_x + int(12 * scale), p2_y + int(12 * scale)],
        fill=COLOR_WHITE
    )

def add_text(image, size):
    """Add text overlay to icon"""
    draw = ImageDraw.Draw(image)

    # Try to use a nice font, fall back to default if not available
    try:
        # Try common system fonts
        font_size = size // 8
        font = ImageFont.truetype("arial.ttf", font_size)
        font_small = ImageFont.truetype("arial.ttf", font_size // 2)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size // 8)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size // 16)
        except (OSError, IOError):
            # Fall back to default font
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()

    # Draw text with shadow for depth
    text = "DIP"
    text_small = "SMC"

    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2
    y = size // 2 + int(size * 0.25)

    # Shadow
    shadow_offset = max(2, size // 150)
    draw.text((x + shadow_offset, y + shadow_offset), text, fill=COLOR_TEXT_SHADOW, font=font)
    # Main text
    draw.text((x, y), text, fill=COLOR_WHITE, font=font)

    # Small text
    bbox_small = draw.textbbox((0, 0), text_small, font=font_small)
    text_small_width = bbox_small[2] - bbox_small[0]
    x_small = (size - text_small_width) // 2
    y_small = y + text_height + int(size * 0.05)

    # Shadow
    draw.text((x_small + shadow_offset // 2, y_small + shadow_offset // 2),
              text_small, fill=COLOR_TEXT_SHADOW, font=font_small)
    # Main text
    draw.text((x_small, y_small), text_small, fill=COLOR_WHITE, font=font_small)

def generate_icon(size, filename):
    """Generate a single icon"""
    print(f"Generating {size}x{size} icon: {filename}")

    # Create gradient background
    image = create_gradient_background(size)

    # Draw pendulum
    draw = ImageDraw.Draw(image)
    draw_pendulum_simple(draw, size)

    # Add text
    add_text(image, size)

    # Save with optimization
    image.save(filename, 'PNG', optimize=True, quality=95)
    print(f"  [OK] Saved {filename} ({os.path.getsize(filename) / 1024:.1f} KB)")

def main():
    """Generate all required icon sizes"""
    print("=" * 70)
    print("PWA Icon Generator - DIP SMC Documentation")
    print("=" * 70)

    # Ensure output directory exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Generate icons
    sizes = [
        (192, 'icon-192x192.png'),
        (512, 'icon-512x512.png'),
    ]

    for size, filename in sizes:
        generate_icon(size, filename)

    print("\n" + "=" * 70)
    print("[OK] Icon generation complete!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - icon-192x192.png (for mobile home screens)")
    print("  - icon-512x512.png (for app splash screens)")
    print("\nNext steps:")
    print("  1. Review the generated icons")
    print("  2. Replace with custom SVG-based icons if desired")
    print("  3. Update manifest.json icon paths if needed")
    print("=" * 70)

if __name__ == '__main__':
    main()
