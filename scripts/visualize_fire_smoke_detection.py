import cv2
import numpy as np
from pathlib import Path
import random

# Define paths
dataset_dir = Path('datasets/fire/extracted')
images_dir = dataset_dir / 'train' / 'images'
labels_dir = dataset_dir / 'train' / 'labels'
output_dir = dataset_dir / 'verification'
output_path = output_dir / 'fire_smoke_samples.jpg'

# Class names
class_names = {0: 'fire', 1: 'smoke'}

# Create output directory
output_dir.mkdir(parents=True, exist_ok=True)

# Get all image files
image_files = sorted([f for f in images_dir.glob('*') if f.suffix.lower() in ['.jpg', '.jpeg', '.png']])

if len(image_files) < 12:
    print(f"Error: Need at least 12 images, but found only {len(image_files)}")
    exit(1)

# Select 12 random images
random_images = random.sample(image_files, 12)

def get_bbox_from_annotation(line_values, width, height):
    """
    Parse annotation line and return bounding box coordinates.
    
    Supports two formats:
    A) Detection (5 values): class x_center y_center width height
    B) Polygon (>5 values): class x1 y1 x2 y2 x3 y3 ...
    
    Returns: (class_id, x1, y1, x2, y2) in pixel coordinates or None if invalid
    """
    try:
        if len(line_values) < 2:
            return None
        
        class_id = int(line_values[0])
        
        # Format A: YOLO detection (5 values)
        if len(line_values) == 5:
            x_center = float(line_values[1])
            y_center = float(line_values[2])
            box_width = float(line_values[3])
            box_height = float(line_values[4])
            
            # Validate normalized coordinates
            if not all(0 <= v <= 1 for v in [x_center, y_center, box_width, box_height]):
                return None
            
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
            
            return (class_id, x1, y1, x2, y2)
        
        # Format B: Polygon (>5 values)
        elif len(line_values) > 5:
            coords = [float(v) for v in line_values[1:]]
            
            # Must have even number of coordinates
            if len(coords) % 2 != 0:
                return None
            
            # Validate coordinates are in [0, 1]
            if not all(0 <= c <= 1 for c in coords):
                return None
            
            # Extract polygon points and find bounding box
            x_coords = [coords[i] * width for i in range(0, len(coords), 2)]
            y_coords = [coords[i] * height for i in range(1, len(coords), 2)]
            
            x1 = max(0, int(min(x_coords)))
            y1 = max(0, int(min(y_coords)))
            x2 = min(width - 1, int(max(x_coords)))
            y2 = min(height - 1, int(max(y_coords)))
            
            return (class_id, x1, y1, x2, y2)
        
        else:
            return None
    
    except (ValueError, IndexError):
        return None

def draw_annotations(image, label_file):
    """Draw bounding boxes and class labels on image."""
    height, width = image.shape[:2]
    
    if not label_file.exists():
        return image
    
    with open(label_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        line_values = line.split()
        bbox = get_bbox_from_annotation(line_values, width, height)
        
        if bbox is None:
            continue
        
        class_id, x1, y1, x2, y2 = bbox
        
        # Validate class ID
        if class_id not in class_names:
            continue
        
        # Draw bounding box
        color = (0, 255, 0) if class_id == 0 else (255, 0, 0)  # Green for fire, Blue for smoke
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # Draw class label
        class_name = class_names[class_id]
        cv2.putText(image, class_name, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
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
