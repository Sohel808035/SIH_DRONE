import shutil
from pathlib import Path

# Define paths
source_dir = Path('datasets/debris/extracted')
destination_dir = Path('datasets/person/cleaned_detection')

# Statistics
stats = {
    'source_images_total': 0,
    'output_images_total': 0,
    'person_annotations_kept': 0,
    'person_in_rubble_annotations_kept': 0,
    'rubble_annotations_ignored': 0,
    'train_images': 0,
    'valid_images': 0,
    'test_images': 0,
    'train_labels': 0,
    'valid_labels': 0,
    'test_labels': 0,
}

def has_person_annotation(label_file):
    """
    Check if label file contains at least one Person (class 0) or Person in Rubble (class 1) annotation.
    Returns: (has_person, person_count, person_in_rubble_count, rubble_count)
    """
    if not label_file.exists():
        return False, 0, 0, 0
    
    with open(label_file, 'r') as f:
        lines = f.readlines()
    
    person_count = 0
    person_in_rubble_count = 0
    rubble_count = 0
    has_person = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        values = line.split()
        if len(values) >= 1:
            try:
                class_id = int(values[0])
                if class_id == 0:  # Person
                    person_count += 1
                    has_person = True
                elif class_id == 1:  # Person in Rubble
                    person_in_rubble_count += 1
                    has_person = True
                elif class_id == 2:  # Rubble
                    rubble_count += 1
            except ValueError:
                pass
    
    return has_person, person_count, person_in_rubble_count, rubble_count

def process_label_file(source_file, destination_file):
    """
    Process a single label file:
    - Keep class 0 (Person) and class 1 (Person in Rubble)
    - Map both to output class 0
    - Ignore class 2 (Rubble)
    Returns: (person_kept, person_in_rubble_kept, rubble_ignored)
    """
    person_kept = 0
    person_in_rubble_kept = 0
    rubble_ignored = 0
    
    valid_lines = []
    
    if not source_file.exists():
        return 0, 0, 0
    
    with open(source_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        values = line.split()
        
        if len(values) < 5:
            continue
        
        try:
            class_id = int(values[0])
            
            if class_id == 0:  # Person
                # Map to class 0, keep the rest
                new_line = f"0 {' '.join(values[1:])}"
                valid_lines.append(new_line)
                person_kept += 1
            
            elif class_id == 1:  # Person in Rubble
                # Map to class 0, keep the rest
                new_line = f"0 {' '.join(values[1:])}"
                valid_lines.append(new_line)
                person_in_rubble_kept += 1
            
            elif class_id == 2:  # Rubble
                # Ignore
                rubble_ignored += 1
        
        except ValueError:
            pass
    
    # Write cleaned label file only if it has annotations
    if valid_lines:
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        with open(destination_file, 'w') as f:
            for line in valid_lines:
                f.write(line + '\n')
    
    return person_kept, person_in_rubble_kept, rubble_ignored

# Create destination root
destination_dir.mkdir(parents=True, exist_ok=True)

print("Extracting Person classes from Debris dataset...")
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
            
            # Check each image
            for image_file in all_images:
                stats['source_images_total'] += 1
                
                # Find corresponding label file
                label_file = labels_source / (image_file.stem + '.txt')
                
                # Check if this image has person annotations
                has_person, person_count, person_in_rubble_count, rubble_count = has_person_annotation(label_file)
                
                if has_person:
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
                    person_kept, person_in_rubble_kept, rubble_ignored = process_label_file(label_file, destination_label)
                    
                    stats['person_annotations_kept'] += person_kept
                    stats['person_in_rubble_annotations_kept'] += person_in_rubble_kept
                    stats['rubble_annotations_ignored'] += rubble_ignored
                    
                    if split == 'train':
                        stats['train_labels'] += 1
                    elif split == 'valid':
                        stats['valid_labels'] += 1
                    else:
                        stats['test_labels'] += 1
                else:
                    # Skip image (no person annotations)
                    stats['rubble_annotations_ignored'] += rubble_count

# Create data.yaml
print("Creating data.yaml...")
data_yaml_content = """path: ../
train: ../train/images
val: ../valid/images
test: ../test/images
nc: 1
names: ['person']
"""

data_yaml_path = destination_dir / 'data.yaml'
with open(data_yaml_path, 'w') as f:
    f.write(data_yaml_content)

# Print report
print("\n" + "="*70)
print("PERSON EXTRACTION REPORT")
print("="*70)
print(f"Source: {source_dir}")
print(f"Destination: {destination_dir}")
print()

print("DATASET SUMMARY:")
print(f"  Source images (all): {stats['source_images_total']}")
print(f"  Output images (with person annotations): {stats['output_images_total']}")
print()

print("ANNOTATION STATISTICS:")
print(f"  Person (class 0) annotations kept: {stats['person_annotations_kept']}")
print(f"  Person in Rubble (class 1) annotations kept: {stats['person_in_rubble_annotations_kept']}")
print(f"  Total person annotations (both mapped to class 0): {stats['person_annotations_kept'] + stats['person_in_rubble_annotations_kept']}")
print(f"  Rubble (class 2) annotations ignored: {stats['rubble_annotations_ignored']}")
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
print("  names: ['person']")
print()

print("="*70)
print("Extraction complete!")
print("="*70)
