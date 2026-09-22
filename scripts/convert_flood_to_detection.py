import shutil
from pathlib import Path

# Define paths
source_dir = Path('datasets/flood/cleaned')
destination_dir = Path('datasets/flood/cleaned_detection')

# Statistics
stats = {
    'images_processed': 0,
    'annotation_lines_processed': 0,
    'boxes_created': 0,
    'malformed_annotations': 0,
    'train_images': 0,
    'valid_images': 0,
    'test_images': 0,
    'train_labels': 0,
    'valid_labels': 0,
    'test_labels': 0,
}

errors = []

def convert_polygon_to_detection(line, line_num, file_name):
    """
    Convert segmentation polygon line to detection format.
    Input: class x1 y1 x2 y2 x3 y3 ...
    Output: (is_valid, output_line, error_msg)
    """
    values = line.split()
    
    # Minimum: class + 3 points (6 values)
    if len(values) < 7:
        return False, None, f"{file_name} line {line_num}: less than 7 values"
    
    try:
        class_id = int(values[0])
        coords = [float(v) for v in values[1:]]
    except ValueError as e:
        return False, None, f"{file_name} line {line_num}: non-numeric values"
    
    # Class should be 0
    if class_id != 0:
        return False, None, f"{file_name} line {line_num}: class is not 0 (segmentation)"
    
    # Must have even number of coordinates (pairs)
    if len(coords) % 2 != 0:
        return False, None, f"{file_name} line {line_num}: odd number of coordinates"
    
    # Validate coordinates in [0, 1]
    if not all(0 <= c <= 1 for c in coords):
        return False, None, f"{file_name} line {line_num}: coordinates outside [0,1]"
    
    # Extract x and y coordinates
    x_coords = [coords[i] for i in range(0, len(coords), 2)]
    y_coords = [coords[i] for i in range(1, len(coords), 2)]
    
    # Find bounding box
    xmin = min(x_coords)
    xmax = max(x_coords)
    ymin = min(y_coords)
    ymax = max(y_coords)
    
    # Calculate center and dimensions
    width = xmax - xmin
    height = ymax - ymin
    
    if width <= 0 or height <= 0:
        return False, None, f"{file_name} line {line_num}: bounding box has zero or negative dimensions"
    
    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2
    
    # Validate final output
    if not all(0 <= v <= 1 for v in [x_center, y_center, width, height]):
        return False, None, f"{file_name} line {line_num}: final coordinates outside [0,1]"
    
    if width <= 0 or height <= 0:
        return False, None, f"{file_name} line {line_num}: final width or height <= 0"
    
    output_line = f"0 {x_center} {y_center} {width} {height}"
    return True, output_line, None

def process_label_file(source_file, destination_file):
    """
    Process a single label file, converting polygons to boxes.
    Returns: (boxes_created, is_valid)
    """
    global stats, errors
    
    boxes_created = 0
    output_lines = []
    
    with open(source_file, 'r') as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        stats['annotation_lines_processed'] += 1
        
        # Try to convert polygon to detection
        is_valid, output_line, error_msg = convert_polygon_to_detection(line, line_num, source_file.name)
        
        if not is_valid:
            stats['malformed_annotations'] += 1
            errors.append(error_msg)
            continue
        
        output_lines.append(output_line)
        boxes_created += 1
        stats['boxes_created'] += 1
    
    # Write label file
    destination_file.parent.mkdir(parents=True, exist_ok=True)
    with open(destination_file, 'w') as f:
        for line in output_lines:
            f.write(line + '\n')
    
    return boxes_created

# Create destination root
destination_dir.mkdir(parents=True, exist_ok=True)

print("Converting Flood segmentation dataset to detection format...")
print()

# Process train, valid, test directories
for split in ['train', 'valid', 'test']:
    split_source = source_dir / split
    split_dest = destination_dir / split
    
    if split_source.exists():
        # Create directories
        (split_dest / 'images').mkdir(parents=True, exist_ok=True)
        (split_dest / 'labels').mkdir(parents=True, exist_ok=True)
        
        images_source = split_source / 'images'
        labels_source = split_source / 'labels'
        images_dest = split_dest / 'images'
        labels_dest = split_dest / 'labels'
        
        # Copy images and process labels
        if images_source.exists():
            for image_file in images_source.iterdir():
                if image_file.is_file():
                    # Copy image
                    shutil.copy2(str(image_file), str(images_dest / image_file.name))
                    stats['images_processed'] += 1
                    
                    if split == 'train':
                        stats['train_images'] += 1
                    elif split == 'valid':
                        stats['valid_images'] += 1
                    else:
                        stats['test_images'] += 1
                    
                    # Find and process label file
                    label_file = labels_source / (image_file.stem + '.txt')
                    if label_file.exists():
                        destination_label = labels_dest / label_file.name
                        boxes_created = process_label_file(label_file, destination_label)
                        
                        if split == 'train':
                            stats['train_labels'] += 1
                        elif split == 'valid':
                            stats['valid_labels'] += 1
                        else:
                            stats['test_labels'] += 1

# Check for errors
if errors:
    print("\n⚠ ERRORS ENCOUNTERED:")
    for error in errors:
        print(f"  {error}")
    print("\nAbort: Cannot continue with errors.")
    exit(1)

# Create data.yaml
print("Creating data.yaml...")
data_yaml_content = """path: ../
train: ../train/images
val: ../valid/images
test: ../test/images
nc: 1
names: ['flood']
"""

data_yaml_path = destination_dir / 'data.yaml'
with open(data_yaml_path, 'w') as f:
    f.write(data_yaml_content)

# Print report
print("\n" + "="*70)
print("FLOOD SEGMENTATION TO DETECTION CONVERSION REPORT")
print("="*70)
print(f"Source: {source_dir}")
print(f"Destination: {destination_dir}")
print()

print("PROCESSING STATISTICS:")
print(f"  Images processed: {stats['images_processed']}")
print(f"  Annotation lines processed: {stats['annotation_lines_processed']}")
print(f"  Boxes created: {stats['boxes_created']}")
print(f"  Malformed annotations: {stats['malformed_annotations']}")
print()

print("OUTPUT STRUCTURE:")
print(f"  Train images: {stats['train_images']}")
print(f"  Train labels: {stats['train_labels']}")
print(f"  Valid images: {stats['valid_images']}")
print(f"  Valid labels: {stats['valid_labels']}")
print(f"  Test images: {stats['test_images']}")
print(f"  Test labels: {stats['test_labels']}")
print()

print("data.yaml CREATED:")
print("  train: ../train/images")
print("  val: ../valid/images")
print("  test: ../test/images")
print("  nc: 1")
print("  names: ['flood']")
print()

print("="*70)
print("Conversion complete!")
print("="*70)
