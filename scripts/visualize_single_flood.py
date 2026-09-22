import cv2
import numpy as np
from pathlib import Path

# Define paths
image_path = Path('datasets/flood/extracted/train/images/flood_1123_jpg.rf.fc6f96f20b92709e993671be08376c7d.jpg')
label_path = Path('datasets/flood/extracted/train/labels/flood_1123_jpg.rf.fc6f96f20b92709e993671be08376c7d.txt')
output_dir = Path('datasets/flood/extracted/verification')
output_path = output_dir / 'flood_1123_visualized.jpg'

# Create output directory
output_dir.mkdir(parents=True, exist_ok=True)

# Read image
image = cv2.imread(str(image_path))
if image is None:
    print(f"Error: Could not read image from {image_path}")
    exit(1)

height, width = image.shape[:2]

# Create overlay for semi-transparent fills
overlay = image.copy()

# Track statistics
valid_polygons = 0
invalid_lines = 0
invalid_line_numbers = []

# Read and process label file
if label_path.exists():
    with open(label_path, 'r') as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        values = line.split()
        
        # Check: at least 7 values (class_id + 3 coordinates minimum)
        if len(values) < 7:
            print(f"INVALID LINE: {line_num} less than 7 values")
            invalid_lines += 1
            invalid_line_numbers.append(line_num)
            continue
        
        # Check: class_id is numeric
        try:
            class_id = int(values[0])
        except ValueError:
            print(f"INVALID LINE: {line_num} class ID not numeric")
            invalid_lines += 1
            invalid_line_numbers.append(line_num)
            continue
        
        # Extract coordinates
        coord_values = values[1:]
        
        # Check: odd number of coordinates (must be pairs)
        if len(coord_values) % 2 != 0:
            print(f"INVALID LINE: {line_num} odd number of coordinate values after class_id")
            invalid_lines += 1
            invalid_line_numbers.append(line_num)
            continue
        
        # Parse and validate coordinates
        try:
            coords = [float(v) for v in coord_values]
        except ValueError:
            print(f"INVALID LINE: {line_num} non-numeric coordinate values")
            invalid_lines += 1
            invalid_line_numbers.append(line_num)
            continue
        
        # Check: coordinates in [0, 1]
        if not all(0 <= c <= 1 for c in coords):
            print(f"INVALID LINE: {line_num} coordinates outside [0,1]")
            invalid_lines += 1
            invalid_line_numbers.append(line_num)
            continue
        
        # Convert normalized coordinates to pixel coordinates
        points = []
        for i in range(0, len(coords), 2):
            x = int(coords[i] * width)
            y = int(coords[i + 1] * height)
            points.append([x, y])
        
        points = np.array(points, dtype=np.int32)
        
        # Draw filled polygon on overlay (light fill)
        cv2.fillPoly(overlay, [points], (0, 255, 0))
        
        # Draw polygon outline on image (solid outline)
        cv2.polylines(image, [points], True, (0, 255, 0), 2)
        
        # Draw class ID on image
        center_x = int(np.mean(coords[0::2]) * width)
        center_y = int(np.mean(coords[1::2]) * height)
        cv2.putText(image, str(class_id), (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        valid_polygons += 1
else:
    print(f"Warning: Label file not found at {label_path}")

# Blend overlay with image for light fill effect
alpha = 0.3  # 30% opacity for the light fill
image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

# Save visualization
cv2.imwrite(str(output_path), image)

# Print summary statistics
print(f"Image path: {image_path}")
print(f"Label path: {label_path}")
print(f"Number of valid polygons: {valid_polygons}")
print(f"Number of invalid lines: {invalid_lines}")
if invalid_line_numbers:
    print(f"Invalid line numbers: {invalid_line_numbers}")
print(f"Output path: {output_path}")
