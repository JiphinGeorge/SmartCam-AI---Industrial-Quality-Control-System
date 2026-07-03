"""
QualiVision AI — Dataset Report & Visualization Generator
========================================================
Generates comprehensive dataset analysis reports and charts
after the dataset has been reorganized by prepare_dataset.py.

Outputs:
  reports/dataset_report.md        — Full markdown report
  reports/class_distribution.png   — Bar chart of class counts
  reports/dataset_split.png        — Pie chart of train/val/test
  reports/example_images.png       — Grid of sample images
  reports/image_size_distribution.png — Histogram of file sizes

Usage:
    python generate_reports.py
"""

import os
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from PIL import Image
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent
DATASET_DIR = ROOT / "dataset"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Chart styling — match QualiVision AI dark industrial theme
COLORS = {
    "Fresh":      "#16c784",  # Primary green
    "Rotten":     "#ff4d4f",  # Red/error
    "train":      "#0566d9",  # Secondary blue
    "validation": "#8b5cf6",  # Tertiary purple
    "test":       "#f59e0b",  # Amber
    "bg":         "#0b1326",  # Dark background
    "surface":    "#171f33",  # Surface
    "text":       "#dae2fd",  # On-surface text
    "grid":       "#2d3449",  # Grid lines
}

plt.rcParams.update({
    "figure.facecolor": COLORS["bg"],
    "axes.facecolor": COLORS["surface"],
    "axes.edgecolor": COLORS["grid"],
    "axes.labelcolor": COLORS["text"],
    "text.color": COLORS["text"],
    "xtick.color": COLORS["text"],
    "ytick.color": COLORS["text"],
    "grid.color": COLORS["grid"],
    "grid.alpha": 0.3,
    "font.family": "sans-serif",
    "font.size": 12,
})


# ──────────────────────────────────────────────
# Analysis Functions
# ──────────────────────────────────────────────

def analyze_dataset():
    """Scan the clean dataset and collect statistics."""
    stats = {
        "splits": {},
        "classes": defaultdict(int),
        "total": 0,
        "file_sizes": [],
        "dimensions": [],
        "issues": [],
    }

    for split_name in ["train", "validation", "test"]:
        split_path = DATASET_DIR / split_name
        if not split_path.exists():
            stats["issues"].append(f"Missing split directory: {split_name}/")
            continue

        split_stats = {}
        for class_dir in sorted(split_path.iterdir()):
            if not class_dir.is_dir():
                continue
            images = list(class_dir.glob("*"))
            count = len(images)
            split_stats[class_dir.name] = count
            stats["classes"][class_dir.name] += count
            stats["total"] += count

            # Sample file sizes and dimensions
            for img_path in images:
                stats["file_sizes"].append(img_path.stat().st_size)
                try:
                    with Image.open(img_path) as img:
                        stats["dimensions"].append(img.size)
                except Exception:
                    pass

        stats["splits"][split_name] = split_stats

    return stats


def generate_class_distribution(stats):
    """Bar chart: Fresh vs Rotten total counts."""
    fig, ax = plt.subplots(figsize=(8, 5))

    classes = list(stats["classes"].keys())
    counts = [stats["classes"][c] for c in classes]
    colors = [COLORS.get(c, "#888") for c in classes]

    bars = ax.bar(classes, counts, color=colors, edgecolor="white", linewidth=0.5,
                  width=0.5, zorder=3)

    # Add count labels on bars
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                f"{count:,}", ha="center", va="bottom", fontweight="bold",
                fontsize=14, color=COLORS["text"])

    ax.set_title("Class Distribution", fontsize=18, fontweight="bold", pad=20)
    ax.set_ylabel("Number of Images", fontsize=13)
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)

    # Balance ratio annotation
    if len(counts) == 2:
        ratio = min(counts) / max(counts) * 100
        ax.annotate(f"Balance ratio: {ratio:.1f}%",
                    xy=(0.98, 0.95), xycoords="axes fraction",
                    ha="right", va="top", fontsize=11,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor=COLORS["bg"],
                              edgecolor=COLORS["grid"], alpha=0.9))

    plt.tight_layout()
    path = REPORTS_DIR / "class_distribution.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {path.name}")


def generate_split_pie(stats):
    """Pie chart: train / validation / test distribution."""
    fig, ax = plt.subplots(figsize=(7, 7))

    split_names = list(stats["splits"].keys())
    split_totals = [sum(stats["splits"][s].values()) for s in split_names]
    colors = [COLORS.get(s, "#888") for s in split_names]

    wedges, texts, autotexts = ax.pie(
        split_totals,
        labels=[f"{s.capitalize()}\n({t:,})" for s, t in zip(split_names, split_totals)],
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        textprops={"color": COLORS["text"], "fontsize": 13},
        wedgeprops={"edgecolor": COLORS["bg"], "linewidth": 2},
        pctdistance=0.75,
    )

    for at in autotexts:
        at.set_fontweight("bold")
        at.set_fontsize(12)

    ax.set_title("Dataset Split Distribution", fontsize=18, fontweight="bold", pad=20)

    plt.tight_layout()
    path = REPORTS_DIR / "dataset_split.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {path.name}")


def generate_example_images():
    """3×4 grid of sample images from the dataset."""
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle("Sample Images from Dataset", fontsize=18, fontweight="bold", y=0.98)

    gs = gridspec.GridSpec(3, 4, hspace=0.35, wspace=0.15)

    row_labels = ["Train", "Validation", "Test"]
    splits = ["train", "validation", "test"]

    for row_idx, (split, label) in enumerate(zip(splits, row_labels)):
        for col_idx, cls in enumerate(["Fresh", "Rotten"]):
            cls_dir = DATASET_DIR / split / cls
            images = sorted(cls_dir.glob("*.jpg"))[:1]
            if not images:
                continue

            # Show 2 columns per class (Fresh left pair, Rotten right pair)
            ax_idx = col_idx * 2
            for sub_idx in range(2):
                if sub_idx < len(images) or len(images) > sub_idx:
                    img_list = sorted(cls_dir.glob("*.jpg"))
                    img_idx = sub_idx * 100  # Spread samples
                    if img_idx >= len(img_list):
                        img_idx = sub_idx
                    img_path = img_list[min(img_idx, len(img_list) - 1)]

                    ax = fig.add_subplot(gs[row_idx, ax_idx + sub_idx])
                    img = Image.open(img_path)
                    ax.imshow(np.array(img))
                    ax.set_xticks([])
                    ax.set_yticks([])

                    # Border color by class
                    color = COLORS["Fresh"] if cls == "Fresh" else COLORS["Rotten"]
                    for spine in ax.spines.values():
                        spine.set_edgecolor(color)
                        spine.set_linewidth(2)

                    if sub_idx == 0:
                        ax.set_ylabel(f"{label}", fontsize=11, fontweight="bold")
                    if row_idx == 0:
                        title = f"{'🍅 Fresh' if cls == 'Fresh' else '🍅 Rotten'}"
                        ax.set_title(title, fontsize=12, fontweight="bold",
                                     color=color, pad=8)

    path = REPORTS_DIR / "example_images.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {path.name}")


def generate_size_distribution(stats):
    """Histogram of image file sizes in KB."""
    fig, ax = plt.subplots(figsize=(10, 5))

    sizes_kb = [s / 1024 for s in stats["file_sizes"]]

    ax.hist(sizes_kb, bins=50, color=COLORS["Fresh"], edgecolor=COLORS["bg"],
            alpha=0.85, zorder=3)

    avg_size = np.mean(sizes_kb)
    ax.axvline(avg_size, color=COLORS["Rotten"], linestyle="--", linewidth=2,
               label=f"Mean: {avg_size:.1f} KB")

    ax.set_title("Image File Size Distribution", fontsize=18, fontweight="bold", pad=20)
    ax.set_xlabel("File Size (KB)", fontsize=13)
    ax.set_ylabel("Count", fontsize=13)
    ax.legend(fontsize=12, facecolor=COLORS["surface"], edgecolor=COLORS["grid"])
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)

    plt.tight_layout()
    path = REPORTS_DIR / "image_size_distribution.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {path.name}")


def generate_markdown_report(stats):
    """Generate comprehensive dataset_report.md."""

    total = stats["total"]
    fresh_total = stats["classes"].get("Fresh", 0)
    rotten_total = stats["classes"].get("Rotten", 0)
    balance_ratio = min(fresh_total, rotten_total) / max(fresh_total, rotten_total) * 100 if max(fresh_total, rotten_total) > 0 else 0

    sizes_kb = [s / 1024 for s in stats["file_sizes"]]
    avg_size = np.mean(sizes_kb) if sizes_kb else 0
    min_size = np.min(sizes_kb) if sizes_kb else 0
    max_size = np.max(sizes_kb) if sizes_kb else 0

    dims = stats["dimensions"]
    if dims:
        widths = [d[0] for d in dims]
        heights = [d[1] for d in dims]
        avg_w, avg_h = np.mean(widths), np.mean(heights)
        min_w, min_h = np.min(widths), np.min(heights)
        max_w, max_h = np.max(widths), np.max(heights)
    else:
        avg_w = avg_h = min_w = min_h = max_w = max_h = 0

    report = f"""# QualiVision AI — Dataset Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Project:** QualiVision AI Industrial Quality Control
**Classification:** Binary (Fresh Tomato / Rotten Tomato)

---

## Summary

| Metric | Value |
|---|---|
| **Total Images** | {total:,} |
| **Fresh Images** | {fresh_total:,} |
| **Rotten Images** | {rotten_total:,} |
| **Class Balance** | {balance_ratio:.1f}% |
| **Image Format** | JPEG (RGB) |

---

## Dataset Split

| Split | Fresh | Rotten | Total | Percentage |
|---|---|---|---|---|
"""

    for split_name in ["train", "validation", "test"]:
        s = stats["splits"].get(split_name, {})
        f = s.get("Fresh", 0)
        r = s.get("Rotten", 0)
        t = f + r
        pct = (t / total * 100) if total > 0 else 0
        report += f"| {split_name.capitalize()} | {f:,} | {r:,} | {t:,} | {pct:.1f}% |\n"

    report += f"| **Total** | **{fresh_total:,}** | **{rotten_total:,}** | **{total:,}** | **100%** |\n"

    report += f"""
---

## Image Statistics

| Metric | Value |
|---|---|
| Average File Size | {avg_size:.1f} KB |
| Min File Size | {min_size:.1f} KB |
| Max File Size | {max_size:.1f} KB |
| Average Dimensions | {avg_w:.0f} × {avg_h:.0f} px |
| Min Dimensions | {min_w:.0f} × {min_h:.0f} px |
| Max Dimensions | {max_w:.0f} × {max_h:.0f} px |
| Color Mode | RGB (converted) |

---

## Class Mapping

The original 7-class dataset was merged into 2 classes:

### Fresh (Healthy Tomatoes)
- `freshtomato` — General fresh tomatoes
- `Maroon Tomato` — Maroon variety
- `Red Cherry Tomato` — Cherry variety
- `Red Large Tomato` — Large red variety
- `Red Tomato` — Standard red variety
- `Yellow Tomato` — Yellow variety

### Rotten (Defective Tomatoes)
- `rottentomato` — Rotten/spoiled tomatoes

### Typo Corrections
- `freshtamto` → mapped to **Fresh**
- `rottentamto` → mapped to **Rotten**

---

## Visualizations

- ![Class Distribution](class_distribution.png)
- ![Dataset Split](dataset_split.png)
- ![Example Images](example_images.png)
- ![Image Size Distribution](image_size_distribution.png)

---

## Potential Issues

"""
    if stats["issues"]:
        for issue in stats["issues"]:
            report += f"- [!] {issue}\n"
    else:
        report += "- ✅ No issues detected\n"

    report += f"""
---

## Data Pipeline

1. Images collected from all original splits (Train/Test/valid)
2. Folder-name typos corrected automatically
3. All images validated with Pillow (corrupted files removed)
4. Duplicate images removed via SHA-256 hash
5. All images converted to RGB JPEG format
6. Stratified random split: 70% train / 15% validation / 15% test
7. Class balance maintained across all splits

---

*Report generated by QualiVision AI Dataset Pipeline v1.0.0*
"""

    path = REPORTS_DIR / "dataset_report.md"
    path.write_text(report, encoding="utf-8")
    print(f"  [OK] {path.name}")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  QualiVision AI — Dataset Report Generator")
    print("=" * 60)

    print("\n[1/6] Analyzing dataset...")
    stats = analyze_dataset()

    print(f"\n[2/6] Generating class distribution chart...")
    generate_class_distribution(stats)

    print(f"\n[3/6] Generating dataset split pie chart...")
    generate_split_pie(stats)

    print(f"\n[4/6] Generating example images grid...")
    generate_example_images()

    print(f"\n[5/6] Generating image size distribution...")
    generate_size_distribution(stats)

    print(f"\n[6/6] Generating markdown report...")
    generate_markdown_report(stats)

    print("\n" + "=" * 60)
    print("  [OK] All reports generated in reports/")
    print("=" * 60)


if __name__ == "__main__":
    main()
