import cv2
import numpy as np
from pathlib import Path
import random

# Define paths
dataset_dir = Path('datasets/flood/cleaned')
images_dir = dataset_dir / 'train' / 'images'
labels_dir = dataset_dir / 'train' / 'labels'
output_path = dataset_dir / 'flood_label_samples_25.jpg'

# Get all image files
image_files = sorted([f for f in images_dir.glob('*') if f.suffix.lower() in ['.jpg', '.jpeg', '.png']])

if len(image_files) < 25:
    print(f"Error: Need at least 25 images, but found only {len(image_files)}")
    exit(1)

# Select 25 random images
random_images = random.sample(image_files, 25)

# Function to draw annotations on image
def draw_annotations(image, label_file):
    """Draw segmentation polygons and class labels on image."""
    height, width = image.shape[:2]
    
    if not label_file.exists():
        return image
    
    with open(label_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        values = line.split()
        if len(values) < 7:
            continue
        
        try:
            class_id = int(values[0])
            coords = [float(v) for v in values[1:]]
            
            # Check for valid coordinates
            if not all(0 <= c <= 1 for c in coords):
                continue
            
            # Convert to pixel coordinates
            points = []
            for i in range(0, len(coords), 2):
                x = int(coords[i] * width)
                y = int(coords[i + 1] * height)
                points.append([x, y])
            
            points = np.array(points, dtype=np.int32)
            
            # Draw filled polygon with transparent green
            overlay = image.copy()
            cv2.fillPoly(overlay, [points], (0, 255, 0))
            image = cv2.addWeighted(overlay, 0.15, image, 0.85, 0)
            
            # Draw thin polygon outline
            cv2.polylines(image, [points], True, (0, 200, 0), 1)
            
            # Draw class label at centroid
            center_x = int(np.mean(coords[0::2]) * width)
            center_y = int(np.mean(coords[1::2]) * height)
            cv2.putText(image, 'floodwater', (center_x - 40, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        except (ValueError, IndexError):
            continue
    
    return image

# Load and process images
processed_images = []
for image_file in random_images:
    image = cv2.imread(str(image_file))
    if image is None:
        continue
    
    # Resize to 512x512 for consistent grid
    image = cv2.resize(image, (512, 512))
    
    # Find corresponding label file
    label_file = labels_dir / (image_file.stem + '.txt')
    
    # Draw annotations
    image = draw_annotations(image, label_file)
    
    # Add filename at top
    cv2.putText(image, image_file.name, (10, 25), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    processed_images.append(image)

# Create 5x5 grid
grid = np.vstack([
    np.hstack([processed_images[0], processed_images[1], processed_images[2], processed_images[3], processed_images[4]]),
    np.hstack([processed_images[5], processed_images[6], processed_images[7], processed_images[8], processed_images[9]]),
    np.hstack([processed_images[10], processed_images[11], processed_images[12], processed_images[13], processed_images[14]]),
    np.hstack([processed_images[15], processed_images[16], processed_images[17], processed_images[18], processed_images[19]]),
    np.hstack([processed_images[20], processed_images[21], processed_images[22], processed_images[23], processed_images[24]])
])

# Save grid
cv2.imwrite(str(output_path), grid)

print(f"Output path: {output_path}")
print(f"Grid size: 5x5 (25 images)")
print(f"Image dimensions: {grid.shape}")
