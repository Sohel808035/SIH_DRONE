import shutil
from pathlib import Path

# Define paths
source_dir = Path('datasets/debris/extracted')
destination_dir = Path('datasets/debris/cleaned_detection')

# Statistics
stats = {
    'source_images_total': 0,
    'output_images_total': 0,
    'annotations_kept': 0,
    'annotations_removed': 0,
    'train_images': 0,
    'valid_images': 0,
    'test_images': 0,
    'train_labels': 0,
    'valid_labels': 0,
    'test_labels': 0,
}

def has_rubble_annotation(label_file):
    """
    Check if label file contains at least one class-2 (Rubble) annotation.
    Returns: (has_rubble, total_annotations)
    """
    if not label_file.exists():
        return False, 0
    
    with open(label_file, 'r') as f:
        lines = f.readlines()
    
    total_annotations = 0
    has_rubble = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        values = line.split()
        if len(values) >= 1:
            total_annotations += 1
            try:
                class_id = int(values[0])
                if class_id == 2:  # Rubble class
                    has_rubble = True
            except ValueError:
                pass
    
    return has_rubble, total_annotations

def process_label_file(source_file, destination_file):
    """
    Process a single label file:
    - Keep only class 2 annotations
    - Change class ID 2 -> 0
    Returns: (annotations_kept, annotations_removed)
    """
    kept = 0
    removed = 0
    
    valid_lines = []
    
    if not source_file.exists():
        return 0, 0
    
    with open(source_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        values = line.split()
        
        if len(values) < 5:
            removed += 1
            continue
        
        try:
            class_id = int(values[0])
            
            if class_id == 2:  # Keep only Rubble
                # Remap class 2 -> 0
                new_line = f"0 {' '.join(values[1:])}"
                valid_lines.append(new_line)
                kept += 1
            else:  # Remove Person (0) and Person in Rubble (1)
                removed += 1
        
        except ValueError:
            removed += 1
    
    # Write cleaned label file only if it has annotations
    if valid_lines:
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        with open(destination_file, 'w') as f:
            for line in valid_lines:
                f.write(line + '\n')
    
    return kept, removed

# Create destination root
destination_dir.mkdir(parents=True, exist_ok=True)

print("Extracting Debris (Rubble) from Debris dataset...")
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
        
        # Find all images
        if images_source.exists():
            all_images = sorted([f for f in images_source.iterdir() if f.is_file()])
            stats[f'source_images_{split}_count'] = len(all_images)
            
            # Check each image
            for image_file in all_images:
                stats['source_images_total'] += 1
                
                # Find corresponding label file
                label_file = labels_source / (image_file.stem + '.txt')
                
                # Check if this image has rubble annotations
                has_rubble, total_annotations = has_rubble_annotation(label_file)
                
                if has_rubble:
                    # Copy image
                    shutil.copy2(str(image_file), str(images_dest / image_file.name))
                    stats['output_images_total'] += 1
                    if split == 'train':
                        stats['train_images'] += 1
                    elif split == 'valid':
                        stats['valid_images'] += 1
                    else:
                        stats['test_images'] += 1
                    
                    # Process and copy label file
                    destination_label = labels_dest / label_file.name
                    kept, removed = process_label_file(label_file, destination_label)
                    stats['annotations_kept'] += kept
                    stats['annotations_removed'] += removed
                    
                    if split == 'train':
                        stats['train_labels'] += 1
                    elif split == 'valid':
                        stats['valid_labels'] += 1
                    else:
                        stats['test_labels'] += 1
                else:
                    # Skip image (no rubble)
                    stats['annotations_removed'] += total_annotations

# Create data.yaml
print("Creating data.yaml...")
data_yaml_content = """path: ../
train: ../train/images
val: ../valid/images
test: ../test/images
nc: 1
names: ['debris']
"""

data_yaml_path = destination_dir / 'data.yaml'
with open(data_yaml_path, 'w') as f:
    f.write(data_yaml_content)

# Print report
print("\n" + "="*70)
print("DEBRIS EXTRACTION REPORT")
print("="*70)
print(f"Source: {source_dir}")
print(f"Destination: {destination_dir}")
print()

print("DATASET SUMMARY:")
print(f"  Source images (all): {stats['source_images_total']}")
print(f"  Output images (with rubble only): {stats['output_images_total']}")
print()

print("ANNOTATION STATISTICS:")
print(f"  Annotations kept (class 2 → 0): {stats['annotations_kept']}")
print(f"  Annotations removed (class 0 & 1): {stats['annotations_removed']}")
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
print("  names: ['debris']")
print()

print("="*70)
print("Extraction complete!")
print("="*70)
