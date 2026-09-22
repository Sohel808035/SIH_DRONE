import shutil
from pathlib import Path
from collections import defaultdict

# Define paths
destination_dir = Path('datasets/final')
report_path = destination_dir / 'merge_report.txt'

# Define source datasets with their configurations
sources = {
    'flood': {
        'path': Path('datasets/flood/cleaned_detection'),
        'class_mapping': {0: 0},
        'prefix': 'flood_',
    },
    'fire_smoke': {
        'path': Path('datasets/fire/cleaned_detection'),
        'class_mapping': {0: 2, 1: 1},
        'prefix': 'fire_',
    },
    'debris': {
        'path': Path('datasets/debris/cleaned_detection'),
        'class_mapping': {0: 3},
        'prefix': 'debris_',
    },
    'landslide': {
        'path': Path('datasets/landslide/extracted'),
        'class_mapping': {0: 4},
        'prefix': 'landslide_',
    },
    'person': {
        'path': Path('datasets/person/cleaned_detection'),
        'class_mapping': {0: 5},
        'prefix': 'person_',
    },
}

class_names = {
    0: 'flood',
    1: 'smoke',
    2: 'fire',
    3: 'debris',
    4: 'landslide',
    5: 'person',
}

# Statistics
stats = {
    'flood': {'source_images': 0, 'output_images': 0, 'annotations': 0, 'by_class': defaultdict(int)},
    'fire_smoke': {'source_images': 0, 'output_images': 0, 'annotations': 0, 'by_class': defaultdict(int)},
    'debris': {'source_images': 0, 'output_images': 0, 'annotations': 0, 'by_class': defaultdict(int)},
    'landslide': {'source_images': 0, 'output_images': 0, 'annotations': 0, 'by_class': defaultdict(int)},
    'person': {'source_images': 0, 'output_images': 0, 'annotations': 0, 'by_class': defaultdict(int)},
}

split_counts = {'train': {'images': 0, 'labels': 0}, 'valid': {'images': 0, 'labels': 0}, 'test': {'images': 0, 'labels': 0}}
used_filenames = {}  # Track filenames to detect collisions
errors = []

def process_label(label_path, class_mapping, source_name):
    """
    Process a label file, remapping class IDs.
    Expects YOLO detection format: class x_center y_center width height
    Returns: (is_valid, output_lines, annotation_count, error_msg)
    """
    if not label_path.exists():
        return True, [], 0, None
    
    output_lines = []
    annotation_count = 0
    
    try:
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            values = line.split()
            
            # Validate format: exactly 5 values
            if len(values) != 5:
                return False, [], 0, f"{label_path} line {line_num}: expected 5 values, got {len(values)}"
            
            try:
                source_class_id = int(values[0])
                x_center = float(values[1])
                y_center = float(values[2])
                width = float(values[3])
                height = float(values[4])
            except ValueError as e:
                return False, [], 0, f"{label_path} line {line_num}: invalid numeric values - {str(e)}"
            
            # Validate class ID in mapping
            if source_class_id not in class_mapping:
                return False, [], 0, f"{label_path} line {line_num}: class {source_class_id} not in mapping"
            
            # Validate coordinates
            if not all(0 <= v <= 1 for v in [x_center, y_center, width, height]):
                return False, [], 0, f"{label_path} line {line_num}: coordinates outside [0,1]"
            
            if width <= 0 or height <= 0:
                return False, [], 0, f"{label_path} line {line_num}: width and height must be > 0"
            
            # Remap class ID
            final_class_id = class_mapping[source_class_id]
            output_lines.append(f"{final_class_id} {x_center} {y_center} {width} {height}")
            annotation_count += 1
        
        return True, output_lines, annotation_count, None
    
    except Exception as e:
        return False, [], 0, f"{label_path}: {str(e)}"

def copy_source_dataset(source_name, source_config):
    """Copy and process one source dataset."""
    print(f"\nSOURCE: {source_name.upper()}")
    
    source_path = source_config['path']
    class_mapping = source_config['class_mapping']
    prefix = source_config['prefix']
    
    print(f"IMAGE DIR: {source_path / 'train' / 'images'}")
    print(f"LABEL DIR: {source_path / 'train' / 'labels'}")
    print()
    
    source_stats = stats[source_name]
    
    for split in ['train', 'valid', 'test']:
        split_source = source_path / split
        split_dest = destination_dir / split
        
        if not split_source.exists():
            continue
        
        images_source = split_source / 'images'
        labels_source = split_source / 'labels'
        
        if not images_source.exists():
            continue
        
        # Get all images
        all_images = sorted([f for f in images_source.iterdir() if f.is_file()])
        
        for image_file in all_images:
            source_stats['source_images'] += 1
            
            # IMPORTANT: Use original image stem to find SOURCE label
            original_stem = image_file.stem
            source_label_file = labels_source / (original_stem + '.txt')
            
            if not source_label_file.exists():
                errors.append(f"{source_name}: Missing source label for {image_file.name}\n  Expected: {source_label_file}")
                continue
            
            # Process label BEFORE creating destination filename
            is_valid, output_lines, annotation_count, error_msg = process_label(source_label_file, class_mapping, source_name)
            
            if not is_valid:
                errors.append(f"{source_name}\n  Source image: {image_file}\n  Source label: {source_label_file}\n  Error: {error_msg}")
                continue
            
            if annotation_count == 0:
                # Skip images with no annotations
                continue
            
            # NOW create destination filename with prefix
            destination_image_filename = prefix + image_file.name
            destination_stem = prefix + original_stem
            
            # Handle filename collision
            if destination_image_filename in used_filenames:
                errors.append(f"{source_name}: Filename collision: {destination_image_filename} (from {image_file.name})")
                continue
            
            used_filenames[destination_image_filename] = source_name
            
            # Create destination directories
            images_dest = split_dest / 'images'
            labels_dest = split_dest / 'labels'
            images_dest.mkdir(parents=True, exist_ok=True)
            labels_dest.mkdir(parents=True, exist_ok=True)
            
            # Copy image with destination filename
            destination_image_path = images_dest / destination_image_filename
            shutil.copy2(str(image_file), str(destination_image_path))
            
            source_stats['output_images'] += 1
            source_stats['annotations'] += annotation_count
            split_counts[split]['images'] += 1
            
            # Write label with destination stem
            destination_label_path = labels_dest / (destination_stem + '.txt')
            with open(destination_label_path, 'w') as f:
                for line in output_lines:
                    f.write(line + '\n')
                    # Track by final class
                    final_class = int(line.split()[0])
                    source_stats['by_class'][final_class] += 1
            
            split_counts[split]['labels'] += 1

# Create destination directories
for split in ['train', 'valid', 'test']:
    (destination_dir / split / 'images').mkdir(parents=True, exist_ok=True)
    (destination_dir / split / 'labels').mkdir(parents=True, exist_ok=True)

print("="*80)
print("BUILDING UNIFIED 6-CLASS YOLO DETECTION DATASET")
print("="*80)
print()

# Process each source dataset
for source_name in ['flood', 'fire_smoke', 'debris', 'landslide', 'person']:
    copy_source_dataset(source_name, sources[source_name])

# Check for errors
if errors:
    print("\n" + "="*80)
    print("⚠ ERRORS ENCOUNTERED:")
    print("="*80)
    for error in errors:
        print(f"\n{error}")
    print("\n" + "="*80)
    print("Abort: Cannot continue with errors.")
    print("="*80)
    exit(1)

# Create data.yaml
print("\nCreating data.yaml...")
data_yaml_content = """path: ../
train: train/images
val: valid/images
test: test/images

nc: 6

names:
  - flood
  - smoke
  - fire
  - debris
  - landslide
  - person
"""

data_yaml_path = destination_dir / 'data.yaml'
with open(data_yaml_path, 'w') as f:
    f.write(data_yaml_content)

# Generate merge report
print("Generating merge_report.txt...")
report_lines = []

report_lines.append("="*80)
report_lines.append("UNIFIED 6-CLASS YOLO DETECTION DATASET - MERGE REPORT")
report_lines.append("="*80)
report_lines.append("")

report_lines.append("FINAL CLASSES:")
report_lines.append("  0 = flood")
report_lines.append("  1 = smoke")
report_lines.append("  2 = fire")
report_lines.append("  3 = debris")
report_lines.append("  4 = landslide")
report_lines.append("  5 = person")
report_lines.append("")

report_lines.append("="*80)
report_lines.append("SOURCE DATASET STATISTICS")
report_lines.append("="*80)
report_lines.append("")

for source_name in ['flood', 'fire_smoke', 'debris', 'landslide', 'person']:
    source_stat = stats[source_name]
    report_lines.append(f"SOURCE: {source_name.upper()}")
    report_lines.append(f"  Source directory: {sources[source_name]['path']}")
    report_lines.append(f"  Source images found: {source_stat['source_images']}")
    report_lines.append(f"  Output images copied: {source_stat['output_images']}")
    report_lines.append(f"  Annotations copied: {source_stat['annotations']}")
    report_lines.append(f"  Annotations by final class:")
    for class_id in sorted(source_stat['by_class'].keys()):
        count = source_stat['by_class'][class_id]
        class_name = class_names[class_id]
        report_lines.append(f"    {class_id} ({class_name}): {count}")
    report_lines.append("")

report_lines.append("="*80)
report_lines.append("FINAL DATASET STATISTICS")
report_lines.append("="*80)
report_lines.append("")

total_images = sum(split_counts[split]['images'] for split in ['train', 'valid', 'test'])
total_labels = sum(split_counts[split]['labels'] for split in ['train', 'valid', 'test'])

report_lines.append(f"Total images copied: {total_images}")
report_lines.append(f"Total labels created: {total_labels}")
report_lines.append("")

report_lines.append("SPLIT BREAKDOWN:")
for split in ['train', 'valid', 'test']:
    report_lines.append(f"  {split.upper()}:")
    report_lines.append(f"    Images: {split_counts[split]['images']}")
    report_lines.append(f"    Labels: {split_counts[split]['labels']}")

report_lines.append("")
report_lines.append("FILENAME PREFIXES:")
report_lines.append("  flood_")
report_lines.append("  fire_")
report_lines.append("  debris_")
report_lines.append("  landslide_")
report_lines.append("  person_")

report_lines.append("")
report_lines.append("="*80)
report_lines.append("DATA.YAML CREATED")
report_lines.append("="*80)
report_lines.append("")
report_lines.append("path: ../")
report_lines.append("train: train/images")
report_lines.append("val: valid/images")
report_lines.append("test: test/images")
report_lines.append("")
report_lines.append("nc: 6")
report_lines.append("names:")
report_lines.append("  - flood")
report_lines.append("  - smoke")
report_lines.append("  - fire")
report_lines.append("  - debris")
report_lines.append("  - landslide")
report_lines.append("  - person")

report_lines.append("")
report_lines.append("="*80)
report_lines.append("Merge complete!")
report_lines.append("="*80)

# Write report
with open(report_path, 'w') as f:
    f.write('\n'.join(report_lines))

# Print summary
print("\n" + "="*80)
print("UNIFIED 6-CLASS YOLO DETECTION DATASET - SUMMARY")
print("="*80)
print()
print("DATASET STATISTICS:")
print(f"  Total images: {total_images}")
print(f"  Total labels: {total_labels}")
print()
print("SPLIT BREAKDOWN:")
for split in ['train', 'valid', 'test']:
    print(f"  {split.upper()}: {split_counts[split]['images']} images, {split_counts[split]['labels']} labels")
print()
print(f"Report saved to: {report_path}")
print()
print("="*80)
print("Merge complete!")
print("="*80)
