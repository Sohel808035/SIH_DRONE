from pathlib import Path
import shutil

OLD = Path("datasets/final")
NEW = Path("datasets/final_v2")

SMOKE = Path("datasets/smoke_v2/extracted")
PERSON = Path("datasets/person_v2/extracted")

# --------------------------
# Copy V1 dataset
# --------------------------
if NEW.exists():
    shutil.rmtree(NEW)

shutil.copytree(OLD, NEW)
print("Copied final -> final_v2")

# --------------------------
# Merge function
# --------------------------
def merge_dataset(source_root, prefix, target_class):
    for split in ["train", "valid", "test"]:

        src_img = source_root / split / "images"
        src_lbl = source_root / split / "labels"

        dst_img = NEW / split / "images"
        dst_lbl = NEW / split / "labels"

        for img in src_img.iterdir():
            if not img.is_file():
                continue

            new_name = f"{prefix}_{img.name}"
            shutil.copy2(img, dst_img / new_name)

            label = src_lbl / f"{img.stem}.txt"
            out_label = dst_lbl / f"{prefix}_{img.stem}.txt"

            lines = []

            if label.exists():
                for line in label.read_text().splitlines():
                    p = line.split()
                    if len(p) != 5:
                        continue
                    p[0] = str(target_class)
                    lines.append(" ".join(p))

            out_label.write_text("\n".join(lines))

        print(f"{prefix} {split} merged")

# Smoke = class 1
merge_dataset(SMOKE, "smokev2", 1)

# Person = class 5
merge_dataset(PERSON, "personv2", 5)

print("\nFINAL_V2 READY")