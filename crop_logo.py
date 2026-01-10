from PIL import Image, ImageDraw, ImageOps

def crop_to_circle(input_path, output_path, zoom_factor=0.8):
    try:
        img = Image.open(input_path).convert("RGBA")
        width, height = img.size
        
        # 1. Zoom/Crop to Center (to remove outer text/cream)
        # Calculate new dimensions
        new_width = int(width * zoom_factor)
        new_height = int(height * zoom_factor)
        
        # Calculate coordinate to crop centered
        left = (width - new_width) // 2
        top = (height - new_height) // 2
        right = (width + new_width) // 2
        bottom = (height + new_height) // 2
        
        img_cropped = img.crop((left, top, right, bottom))
        
        # 2. Create Circle Mask
        mask = Image.new('L', img_cropped.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img_cropped.size[0], img_cropped.size[1]), fill=255)
        
        # 3. Apply Mask
        result = ImageOps.fit(img_cropped, mask.size, centering=(0.5, 0.5))
        result.putalpha(mask)
        
        result.save(output_path, "WEBP")
        print(f"Saved circular cropped logo to {output_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Zoom factor 0.7 means we keep the inner 70%, 
    # effectively cutting off the outer 15% from all sides.
    # This should remove the edge text while keeping the center peacock.
    crop_to_circle("mandala.png", "logo_v3.webp", zoom_factor=0.75)
