"""
QualiVision AI -- Dataset Preparation Script
=========================================
Reorganizes the raw 7-class tomato dataset into a clean binary
classification dataset (Fresh / Rotten) with stratified splits.

Steps:
  1. Backup original dataset -> dataset_original/
  2. Collect all images, fixing folder-name typos
  3. Validate every image (Pillow open, convert RGB, skip corrupted)
  4. Remove exact duplicates via SHA-256 hash
  5. Stratified shuffle-split: 70% train / 15% validation / 15% test
  6. Copy validated images into clean structure

Usage:
    python prepare_dataset.py
"""

import os
import sys
import shutil
import hashlib
import random
from pathlib import Path
from collections import defaultdict

from PIL import Image

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent
ORIGINAL_DATASET = ROOT / "dataset"
BACKUP_DIR = ROOT / "dataset_original"
OUTPUT_DIR = ROOT / "dataset"  # Will overwrite after backup

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

RANDOM_SEED = 42

# Class mapping: source folder name -> target class
# All healthy tomato varieties -> "Fresh"
# Only rotten tomatoes -> "Rotten"
CLASS_MAPPING = {
    # Fresh varieties
    "freshtomato":       "Fresh",
    "freshtamto":        "Fresh",   # typo fix (Test folder)
    "maroon tomato":     "Fresh",
    "red cherry tomato": "Fresh",
    "red large tomato":  "Fresh",
    "red tomato":        "Fresh",
    "yellow tomato":     "Fresh",
    # Rotten
    "rottentomato":      "Rotten",
    "rottentamto":       "Rotten",  # typo fix (Test folder)
}

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def file_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of a file for duplicate detection."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_image(filepath: Path) -> bool:
    """
    Validate that a file is a readable image.
    Returns True if valid, False otherwise.
    """
    try:
        if filepath.stat().st_size == 0:
            return False
        with Image.open(filepath) as img:
            img.verify()
        # Re-open after verify (verify can leave file in bad state)
        with Image.open(filepath) as img:
            img.load()
            # Ensure convertible to RGB
            if img.mode not in ("RGB", "RGBA", "L", "P"):
                return False
        return True
    except Exception:
        return False


def convert_to_rgb(src: Path, dst: Path):
    """Open image, convert to RGB (strip alpha/grayscale), save as JPEG."""
    with Image.open(src) as img:
        if img.mode == "RGBA":
            # Paste onto white background to remove alpha
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")
        img.save(dst, "JPEG", quality=95)


# ──────────────────────────────────────────────
# Main Pipeline
# ──────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  QualiVision AI -- Dataset Preparation")
    print("=" * 60)

    # ── Step 1: Backup original dataset ──
    if not BACKUP_DIR.exists():
        print(f"\n[1/6] Backing up dataset -> {BACKUP_DIR.name}/")
        shutil.copytree(ORIGINAL_DATASET, BACKUP_DIR)
        print(f"       [OK] Backup complete")
    else:
        print(f"\n[1/6] Backup already exists at {BACKUP_DIR.name}/ -- skipping")

    # ── Step 2: Collect all images from all splits ──
    print(f"\n[2/6] Scanning all images from original dataset...")

    # Images collected as: { "Fresh": [path, ...], "Rotten": [path, ...] }
    collected = defaultdict(list)
    skipped_folders = []
    total_scanned = 0

    # Scan both original backup and any remaining original structure
    scan_root = BACKUP_DIR if BACKUP_DIR.exists() else ORIGINAL_DATASET
    for split_dir in scan_root.iterdir():
        if not split_dir.is_dir():
            continue
        for class_dir in split_dir.iterdir():
            if not class_dir.is_dir():
                continue
            # Normalize folder name for mapping
            folder_key = class_dir.name.strip().lower()
            target_class = CLASS_MAPPING.get(folder_key)
            if target_class is None:
                skipped_folders.append(class_dir.name)
                continue
            for img_file in class_dir.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in VALID_EXTENSIONS:
                    collected[target_class].append(img_file)
                    total_scanned += 1

    print(f"       Scanned: {total_scanned} images")
    for cls, imgs in collected.items():
        print(f"       {cls}: {len(imgs)} raw images")
    if skipped_folders:
        print(f"       [!] Skipped unknown folders: {skipped_folders}")

    # ── Step 3: Validate images ──
    print(f"\n[3/6] Validating images (checking for corruption)...")

    validated = defaultdict(list)
    corrupted_count = 0

    for cls, paths in collected.items():
        for i, p in enumerate(paths):
            if validate_image(p):
                validated[cls].append(p)
            else:
                corrupted_count += 1
                print(f"       [FAIL] Corrupted: {p.name}")
            # Progress indicator
            if (i + 1) % 500 == 0:
                print(f"       ... validated {i+1}/{len(paths)} {cls} images")

    print(f"       [OK] Valid: {sum(len(v) for v in validated.values())} | "
          f"Corrupted/removed: {corrupted_count}")

    # ── Step 4: Remove duplicates ──
    print(f"\n[4/6] Removing duplicate images (SHA-256 hash)...")

    deduplicated = defaultdict(list)
    seen_hashes = set()
    duplicate_count = 0

    for cls, paths in validated.items():
        for p in paths:
            h = file_hash(p)
            if h not in seen_hashes:
                seen_hashes.add(h)
                deduplicated[cls].append(p)
            else:
                duplicate_count += 1

    print(f"       [OK] Unique: {sum(len(v) for v in deduplicated.values())} | "
          f"Duplicates removed: {duplicate_count}")
    for cls, imgs in deduplicated.items():
        print(f"       {cls}: {len(imgs)} unique images")

    # ── Step 5: Stratified split ──
    print(f"\n[5/6] Creating stratified 70/15/15 split...")

    random.seed(RANDOM_SEED)

    splits = {"train": defaultdict(list),
              "validation": defaultdict(list),
              "test": defaultdict(list)}

    for cls, paths in deduplicated.items():
        shuffled = paths.copy()
        random.shuffle(shuffled)
        n = len(shuffled)
        n_train = int(n * TRAIN_RATIO)
        n_val = int(n * VAL_RATIO)
        # Remaining goes to test
        splits["train"][cls] = shuffled[:n_train]
        splits["validation"][cls] = shuffled[n_train:n_train + n_val]
        splits["test"][cls] = shuffled[n_train + n_val:]

    for split_name, classes in splits.items():
        total = sum(len(v) for v in classes.values())
        breakdown = ", ".join(f"{c}: {len(v)}" for c, v in classes.items())
        print(f"       {split_name:>12}: {total:>5} ({breakdown})")

    # ── Step 6: Copy to clean structure ──
    print(f"\n[6/6] Building clean dataset structure...")

    # Remove old clean output if exists, write to fresh dir
    clean_output = ROOT / "dataset_clean"
    if clean_output.exists():
        shutil.rmtree(clean_output)

    for split_name, classes in splits.items():
        for cls, paths in classes.items():
            target_dir = clean_output / split_name / cls
            target_dir.mkdir(parents=True, exist_ok=True)
            for i, src_path in enumerate(paths):
                # Generate clean filename: Fresh_00001.jpg
                dst_name = f"{cls}_{i+1:05d}.jpg"
                dst_path = target_dir / dst_name
                convert_to_rgb(src_path, dst_path)
                if (i + 1) % 500 == 0:
                    print(f"       ... copied {i+1}/{len(paths)} -> {split_name}/{cls}/")

    # ── Summary ──
    print("\n" + "=" * 60)
    print("  [OK] Dataset Preparation Complete!")
    print("=" * 60)

    total_final = 0
    for split_name in ["train", "validation", "test"]:
        split_path = OUTPUT_DIR / split_name
        for cls_dir in sorted(split_path.iterdir()):
            count = len(list(cls_dir.glob("*.jpg")))
            total_final += count
            print(f"  {split_name:>12}/{cls_dir.name:<8}: {count:>5} images")

    print(f"\n  Total: {total_final} images")
    print(f"  Corrupted removed: {corrupted_count}")
    print(f"  Duplicates removed: {duplicate_count}")
    print(f"  Output: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
