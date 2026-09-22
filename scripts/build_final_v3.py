from pathlib import Path
import shutil

OLD = Path("datasets/final")
NEW = Path("datasets/final_v3")

SMOKE = Path("datasets/smoke_v3/clean")
PERSON = Path("datasets/person_v3/clean")

if NEW.exists():
    shutil.rmtree(NEW)

shutil.copytree(OLD, NEW)
print("Copied final -> final_v3")


def merge_dataset(source_root, prefix, cls):
    for split in ["train", "valid", "test"]:

        src_img = source_root / split / "images"
        src_lbl = source_root / split / "labels"

        dst_img = NEW / split / "images"
        dst_lbl = NEW / split / "labels"

        for img in src_img.glob("*.*"):
            new_name = f"{prefix}_{img.name}"
            shutil.copy2(img, dst_img / new_name)

            label = src_lbl / f"{img.stem}.txt"
            out = dst_lbl / f"{prefix}_{img.stem}.txt"

            lines = []

            if label.exists():
                for line in label.read_text().splitlines():
                    p = line.split()
                    if len(p) != 5:
                        continue
                    p[0] = str(cls)
                    lines.append(" ".join(p))

            out.write_text("\n".join(lines))

        print(f"{prefix} {split} merged")


merge_dataset(SMOKE, "smokev3", 1)
merge_dataset(PERSON, "personv3", 5)

print("\nFINAL_V3 READY")