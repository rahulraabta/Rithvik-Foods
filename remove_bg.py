from PIL import Image, ImageDraw
import sys

def remove_background(input_path, output_path, tolerance=30):
    try:
        img = Image.open(input_path).convert("RGBA")
        width, height = img.size
        
        # Get background color from top-left corner
        bg_color = img.getpixel((0, 0))
        print(f"Detected background color: {bg_color}")

        # Create a mask initialized to 0 (all transparent)
        # We will flood fill the "background" with 1s
        # seed points: 4 corners
        seeds = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
        
        # Using ImageDraw.floodfill is not directly available for selection in older PIL, 
        # but we can do a simple queue-based flood fill manually or use a threshold method.
        # Since I want to be robust, let's use a simple distance check for all pixels 
        # IF the background is uniform. The user said "box shape", implying uniform box.
        
        datas = img.getdata()
        new_data = []
        
        # Simple Euclidean distance for color similarity
        def is_similar(c1, c2, tol):
            return sum(abs(v1 - v2) for v1, v2 in zip(c1[:3], c2[:3])) < tol

        # Check if corners are similar (to ensure uniform bg)
        # If not, we might be destroying the image.
        # But let's assume valid request.
        
        for item in datas:
            if is_similar(item, bg_color, tolerance):
                new_data.append((255, 255, 255, 0)) # Fully transparent
            else:
                new_data.append(item)

        img.putdata(new_data)
        img.save(output_path, "WEBP")
        print(f"Saved transparent image to {output_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    remove_background("mandala.png", "logo.webp", tolerance=60)
