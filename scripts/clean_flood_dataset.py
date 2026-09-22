import shutil
from pathlib import Path

# Define paths
source_dir = Path('datasets/flood/extracted')
destination_dir = Path('datasets/flood/cleaned')

# Statistics
total_label_files = 0
total_annotation_lines = 0
valid_lines_kept = 0
invalid_lines_removed = 0
invalid_entries = []  # [(file_name, line_number, reason), ...]

def validate_label_line(line):
    """
    Validate a single label line.
    Returns: (is_valid, reason)
    """
    values = line.split()
    
    # Check: at least 7 values
    if len(values) < 7:
        return False, "less than 7 values"
    
    # Check: class ID is numeric
    try:
        class_id = int(values[0])
    except ValueError:
        return False, "class ID not numeric"
    
    # Check: class ID must be 0
    if class_id != 0:
        return False, "class ID is not 0"
    
    # Extract coordinates
    coord_values = values[1:]
    
    # Check: even number of coordinates
    if len(coord_values) % 2 != 0:
        return False, "odd number of coordinate values after class_id"
    
    # Check: all coordinates are numeric
    try:
        coords = [float(v) for v in coord_values]
    except ValueError:
        return False, "non-numeric coordinate values"
    
    # Check: all coordinates in [0, 1]
    if not all(0 <= c <= 1 for c in coords):
        return False, "coordinates outside [0,1]"
    
    return True, "valid"

def process_label_file(source_file, destination_file):
    """
    Process a single label file, keeping only valid lines.
    Returns: (num_lines, num_valid, num_invalid)
    """
    global total_annotation_lines, valid_lines_kept, invalid_lines_removed, invalid_entries
    
    num_lines = 0
    num_valid = 0
    num_invalid = 0
    
    valid_lines = []
    
    with open(source_file, 'r') as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        num_lines += 1
        total_annotation_lines += 1
        
        is_valid, reason = validate_label_line(line)
        
        if is_valid:
            valid_lines.append(line)
            num_valid += 1
            valid_lines_kept += 1
        else:
            num_invalid += 1
            invalid_lines_removed += 1
            invalid_entries.append((source_file.name, line_num, reason))
    
    # Write cleaned label file
    destination_file.parent.mkdir(parents=True, exist_ok=True)
    with open(destination_file, 'w') as f:
        for line in valid_lines:
            f.write(line + '\n')
    
    return num_lines, num_valid, num_invalid

# Create destination root
destination_dir.mkdir(parents=True, exist_ok=True)

# Copy directory structure and files
print("Copying dataset structure...")

# Copy train, valid, test directories
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
        
        # Process and copy label files
        labels_source = split_source / 'labels'
        labels_dest = split_dest / 'labels'
        if labels_source.exists():
            for label_file in labels_source.iterdir():
                if label_file.is_file() and label_file.suffix == '.txt':
                    total_label_files += 1
                    destination_label = labels_dest / label_file.name
                    process_label_file(label_file, destination_label)

# Copy README files
print("Copying README files...")
for readme_file in source_dir.glob('*.txt'):
    if readme_file.is_file():
        shutil.copy2(str(readme_file), str(destination_dir / readme_file.name))

# Create and update data.yaml
print("Creating data.yaml...")
data_yaml_content = """path: ../
train: ../train/images
val: ../valid/images
test: ../test/images
nc: 1
names: ['floodwater']
"""

data_yaml_path = destination_dir / 'data.yaml'
with open(data_yaml_path, 'w') as f:
    f.write(data_yaml_content)

# Print report
print("\n" + "="*60)
print("FLOOD DATASET CLEANING REPORT")
print("="*60)
print(f"Source directory: {source_dir}")
print(f"Destination directory: {destination_dir}")
print(f"\nTotal label files processed: {total_label_files}")
print(f"Total annotation lines processed: {total_annotation_lines}")
print(f"Valid lines kept: {valid_lines_kept}")
print(f"Invalid lines removed: {invalid_lines_removed}")

if invalid_entries:
    print(f"\nInvalid lines details:")
    for file_name, line_num, reason in invalid_entries:
        print(f"  {file_name} line {line_num}: {reason}")

print("\ndata.yaml created with:")
print("  train: ../train/images")
print("  val: ../valid/images")
print("  test: ../test/images")
print("  nc: 1")
print("  names: ['floodwater']")
print("="*60)
