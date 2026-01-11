from PIL import Image
import os

def merge_images(image1_path, image2_path, output_path):
    try:
        img1 = Image.open(image1_path)
        img2 = Image.open(image2_path)

        # Resize images to same height
        target_height = min(img1.height, img2.height)
        
        # Calculate aspect ratios to maintain width proportionality
        img1_ratio = img1.width / img1.height
        img2_ratio = img2.width / img2.height
        
        new_width1 = int(target_height * img1_ratio)
        new_width2 = int(target_height * img2_ratio)
        
        img1 = img1.resize((new_width1, target_height), Image.Resampling.LANCZOS)
        img2 = img2.resize((new_width2, target_height), Image.Resampling.LANCZOS)

        # Create new image
        total_width = new_width1 + new_width2 + 20 # 20px padding
        new_img = Image.new('RGB', (total_width, target_height), (255, 255, 255))
        
        new_img.paste(img1, (0, 0))
        new_img.paste(img2, (new_width1 + 20, 0))
        
        new_img.save(output_path, 'WEBP', quality=90)
        print(f"Successfully saved merged image to {output_path}")

    except Exception as e:
        print(f"Error merging images: {e}")

if __name__ == "__main__":
    base_dir = r"c:\Users\INTEL\Desktop\Rithvik Foods"
    img1 = os.path.join(base_dir, "ragi_premix.webp")
    img2 = os.path.join(base_dir, "huchellu.webp")
    out = os.path.join(base_dir, "combo_ragi_huch.webp")
    
    merge_images(img1, img2, out)
