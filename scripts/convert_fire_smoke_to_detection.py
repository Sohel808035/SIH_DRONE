import shutil
from pathlib import Path

# Define paths
source_dir = Path('datasets/fire/extracted')
destination_dir = Path('datasets/fire/cleaned_detection')

# Statistics
stats = {
    'files_processed': 0,
    'annotations_processed': 0,
    'normal_boxes_kept': 0,
    'polygons_converted': 0,
    'malformed_skipped': 0,
    'fire_count': 0,
    'smoke_count': 0,
    'train_images': 0,
    'valid_images': 0,
    'test_images': 0,
    'train_labels': 0,
    'valid_labels': 0,
    'test_labels': 0,
}

malformed_annotations = []  # [(file_name, line_number, reason), ...]

def validate_detection_format(values):
    """
    Validate YOLO detection format: class x_center y_center width height
    Returns: (is_valid, class_id, x_center, y_center, width, height, reason)
    """
    if len(values) != 5:
        return False, None, None, None, None, None, "not exactly 5 values"
    
    try:
        class_id = int(values[0])
        x_center = float(values[1])
        y_center = float(values[2])
        width = float(values[3])
        height = float(values[4])
    except ValueError:
        return False, None, None, None, None, None, "non-numeric values"
    
    # Validate class ID
    if class_id not in [0, 1]:
        return False, None, None, None, None, None, "class ID not 0 or 1"
    
    # Validate normalized coordinates
    if not (0 <= x_center <= 1 and 0 <= y_center <= 1):
        return False, None, None, None, None, None, "center coordinates outside [0,1]"
    
    if not (0 < width <= 1 and 0 < height <= 1):
        return False, None, None, None, None, None, "width or height not in (0,1]"
    
    return True, class_id, x_center, y_center, width, height, "valid"

def convert_polygon_to_detection(values):
    """
    Convert YOLO segmentation polygon to detection format.
    Input: class x1 y1 x2 y2 x3 y3 ...
    Returns: (is_valid, class_id, x_center, y_center, width, height, reason)
    """
    if len(values) < 7:
        return False, None, None, None, None, None, "less than 7 values (minimum 3 points)"
    
    try:
        class_id = int(values[0])
        coords = [float(v) for v in values[1:]]
    except ValueError:
        return False, None, None, None, None, None, "non-numeric values"
    
    # Validate class ID
    if class_id not in [0, 1]:
        return False, None, None, None, None, None, "class ID not 0 or 1"
    
    # Validate even number of coordinates
    if len(coords) % 2 != 0:
        return False, None, None, None, None, None, "odd number of coordinates"
    
    # Validate coordinates in [0, 1]
    if not all(0 <= c <= 1 for c in coords):
        return False, None, None, None, None, None, "coordinates outside [0,1]"
    
    # Extract x and y coordinates
    x_coords = [coords[i] for i in range(0, len(coords), 2)]
    y_coords = [coords[i] for i in range(1, len(coords), 2)]
    
    # Find bounding box
    xmin = min(x_coords)
    xmax = max(x_coords)
    ymin = min(y_coords)
    ymax = max(y_coords)
    
    # Convert to detection format
    width = xmax - xmin
    height = ymax - ymin
    
    if width <= 0 or height <= 0:
        return False, None, None, None, None, None, "bounding box has zero or negative dimensions"
    
    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2
    
    return True, class_id, x_center, y_center, width, height, "converted from polygon"

def process_label_file(source_file, destination_file):
    """
    Process a single label file, converting annotations as needed.
    Returns: (num_lines, num_kept, num_malformed)
    """
    global stats, malformed_annotations
    
    num_lines = 0
    num_kept = 0
    num_malformed = 0
    
    valid_lines = []
    
    with open(source_file, 'r') as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        num_lines += 1
        stats['annotations_processed'] += 1
        
        values = line.split()
        
        # Try detection format first (5 values)
        if len(values) == 5:
            is_valid, class_id, x_center, y_center, width, height, reason = validate_detection_format(values)
            if is_valid:
                valid_lines.append(f"{class_id} {x_center} {y_center} {width} {height}")
                stats['normal_boxes_kept'] += 1
                if class_id == 0:
                    stats['fire_count'] += 1
                else:
                    stats['smoke_count'] += 1
                num_kept += 1
            else:
                num_malformed += 1
                stats['malformed_skipped'] += 1
                malformed_annotations.append((source_file.name, line_num, reason))
        
        # Try polygon format (>5 values)
        elif len(values) > 5:
            is_valid, class_id, x_center, y_center, width, height, reason = convert_polygon_to_detection(values)
            if is_valid:
                valid_lines.append(f"{class_id} {x_center} {y_center} {width} {height}")
                stats['polygons_converted'] += 1
                if class_id == 0:
                    stats['fire_count'] += 1
                else:
                    stats['smoke_count'] += 1
                num_kept += 1
            else:
                num_malformed += 1
                stats['malformed_skipped'] += 1
                malformed_annotations.append((source_file.name, line_num, reason))
        
        else:
            num_malformed += 1
            stats['malformed_skipped'] += 1
            malformed_annotations.append((source_file.name, line_num, "neither 5 nor >5 values"))
    
    # Write cleaned label file
    destination_file.parent.mkdir(parents=True, exist_ok=True)
    with open(destination_file, 'w') as f:
        for line in valid_lines:
            f.write(line + '\n')
    
    return num_lines, num_kept, num_malformed

# Create destination root
destination_dir.mkdir(parents=True, exist_ok=True)

print("Converting Fire + Smoke dataset to detection format...")
print()

# Process train, valid, test directories
for split in ['train', 'valid', 'test']:
    split_source = source_dir / split
    split_dest = destination_dir / split
    
    if split_source.exists():
        # Create directories
        (split_dest / 'images').mkdir(parents=True, exist_ok=True)
        (split_dest / 'labels').mkdir(parents=True, exist_ok=True)
        
        # Copy images
        images_source = split_source / 'images'
        images_dest = split_dest / 'images'
        if images_source.exists():
            for image_file in images_source.iterdir():
                if image_file.is_file():
                    shutil.copy2(str(image_file), str(images_dest / image_file.name))
                    if split == 'train':
                        stats['train_images'] += 1
                    elif split == 'valid':
                        stats['valid_images'] += 1
                    else:
                        stats['test_images'] += 1
        
        # Process and copy label files
        labels_source = split_source / 'labels'
        labels_dest = split_dest / 'labels'
        if labels_source.exists():
            for label_file in labels_source.iterdir():
                if label_file.is_file() and label_file.suffix == '.txt':
                    stats['files_processed'] += 1
                    destination_label = labels_dest / label_file.name
                    num_lines, num_kept, num_malformed = process_label_file(label_file, destination_label)
                    
                    if split == 'train':
                        stats['train_labels'] += 1
                    elif split == 'valid':
                        stats['valid_labels'] += 1
                    else:
                        stats['test_labels'] += 1

# Copy README files
print("Copying README files...")
for readme_file in source_dir.glob('*.txt'):
    if readme_file.is_file():
        shutil.copy2(str(readme_file), str(destination_dir / readme_file.name))

# Create data.yaml
print("Creating data.yaml...")
data_yaml_content = """path: ../
train: ../train/images
val: ../valid/images
test: ../test/images
nc: 2
names: ['fire', 'smoke']
"""

data_yaml_path = destination_dir / 'data.yaml'
with open(data_yaml_path, 'w') as f:
    f.write(data_yaml_content)

# Print report
print("\n" + "="*70)
print("FIRE + SMOKE DATASET CONVERSION REPORT")
print("="*70)
print(f"Source: {source_dir}")
print(f"Destination: {destination_dir}")
print()

print("ANNOTATION STATISTICS:")
print(f"  Files processed: {stats['files_processed']}")
print(f"  Annotations processed: {stats['annotations_processed']}")
print(f"  Normal boxes kept: {stats['normal_boxes_kept']}")
print(f"  Polygons converted: {stats['polygons_converted']}")
print(f"  Malformed annotations skipped: {stats['malformed_skipped']}")
print()

print("CLASS DISTRIBUTION:")
print(f"  Fire (class 0): {stats['fire_count']}")
print(f"  Smoke (class 1): {stats['smoke_count']}")
print()

print("IMAGES COPIED:")
print(f"  Train: {stats['train_images']}")
print(f"  Valid: {stats['valid_images']}")
print(f"  Test: {stats['test_images']}")
print()

print("LABELS CREATED:")
print(f"  Train: {stats['train_labels']}")
print(f"  Valid: {stats['valid_labels']}")
print(f"  Test: {stats['test_labels']}")
print()

print("data.yaml CREATED:")
print("  train: ../train/images")
print("  val: ../valid/images")
print("  test: ../test/images")
print("  nc: 2")
print("  names: ['fire', 'smoke']")

if malformed_annotations:
    print()
    print(f"MALFORMED ANNOTATIONS ({len(malformed_annotations)}):")
    for file_name, line_num, reason in malformed_annotations[:20]:  # Show first 20
        print(f"  {file_name} line {line_num}: {reason}")
    if len(malformed_annotations) > 20:
        print(f"  ... and {len(malformed_annotations) - 20} more")

print()
print("="*70)
print("Conversion complete!")
print("="*70)
