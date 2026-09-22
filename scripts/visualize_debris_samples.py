import cv2
import numpy as np
from pathlib import Path
import random

# Define paths
dataset_dir = Path('datasets/debris/cleaned_detection')
images_dir = dataset_dir / 'train' / 'images'
labels_dir = dataset_dir / 'train' / 'labels'
output_path = dataset_dir / 'debris_samples.jpg'

# Get all image files
image_files = sorted([f for f in images_dir.glob('*') if f.suffix.lower() in ['.jpg', '.jpeg', '.png']])

if len(image_files) < 12:
    print(f"Error: Need at least 12 images, but found only {len(image_files)}")
    exit(1)

# Select 12 random images
random_images = random.sample(image_files, 12)

def draw_annotations(image, label_file):
    """Draw bounding boxes and 'debris' labels on image."""
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
        
        # Expected format: class x_center y_center width height
        if len(values) != 5:
            continue
        
        try:
            class_id = int(values[0])
            x_center = float(values[1])
            y_center = float(values[2])
            box_width = float(values[3])
            box_height = float(values[4])
            
            # Validate normalized coordinates
            if not all(0 <= v <= 1 for v in [x_center, y_center, box_width, box_height]):
                continue
            
            # Convert to pixel coordinates
            x1 = int((x_center - box_width / 2) * width)
            y1 = int((y_center - box_height / 2) * height)
            x2 = int((x_center + box_width / 2) * width)
            y2 = int((y_center + box_height / 2) * height)
            
            # Clamp to image bounds
            x1 = max(0, min(x1, width - 1))
            y1 = max(0, min(y1, height - 1))
            x2 = max(0, min(x2, width - 1))
            y2 = max(0, min(y2, height - 1))
            
            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            cv2.putText(image, 'debris', (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        except (ValueError, IndexError):
            continue
    
    return image

# Load and process images
processed_images = []
for image_file in random_images:
    image = cv2.imread(str(image_file))
    if image is None:
        continue
    
    # Resize to 320x320 for consistent grid
    image = cv2.resize(image, (320, 320))
    
    # Find corresponding label file
    label_file = labels_dir / (image_file.stem + '.txt')
    
    # Draw annotations
    image = draw_annotations(image, label_file)
    
    # Add filename at top
    cv2.putText(image, image_file.name, (5, 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    processed_images.append(image)

# Create 3x4 grid
grid = np.vstack([
    np.hstack([processed_images[0], processed_images[1], processed_images[2], processed_images[3]]),
    np.hstack([processed_images[4], processed_images[5], processed_images[6], processed_images[7]]),
    np.hstack([processed_images[8], processed_images[9], processed_images[10], processed_images[11]])
])

# Save grid
cv2.imwrite(str(output_path), grid)

print(f"Output path: {output_path}")
print(f"Grid size: 3x4 (12 images)")
print(f"Image dimensions: {grid.shape}")
