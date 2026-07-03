# SmartCam AI — Dataset Documentation

## Dataset Source

The original dataset was sourced externally and contains approximately **7,900 images** of tomatoes across 7 categories.

### Original Structure

```
dataset/
├── Train/
│   ├── freshtomato/        (1,858 images)
│   ├── rottentomato/       (1,825 images)
│   ├── Maroon Tomato/      (546 images)
│   ├── Red Cherry Tomato/  (657 images)
│   ├── Red Large Tomato/   (711 images)
│   ├── Red Tomato/         (567 images)
│   └── Yellow Tomato/      (657 images)
├── Test/
│   ├── freshtamto/         (255 images) ← typo
│   ├── rottentamto/        (353 images) ← typo
│   ├── Maroon Tomato/      (32 images)
│   ├── Red Cherry Tomato/  (36 images)
│   ├── Red Large Tomato/   (25 images)
│   ├── Red Tomato/         (24 images)
│   └── Yellow Tomato/      (34 images)
└── valid/
    ├── Maroon Tomato/      (59 images)
    ├── Red Cherry Tomato/  (74 images)
    ├── Red Large Tomato/   (74 images)
    ├── Red Tomato/         (52 images)
    └── Yellow Tomato/      (59 images)
```

### Issues Found

1. **7 classes** instead of required 2 (binary classification)
2. **Validation split incomplete** — missing freshtomato and rottentomato
3. **Spelling errors** — `freshtamto`, `rottentamto` in Test folder
4. **Inconsistent splits** — uneven distribution across train/test/valid
5. **Images already augmented** — filenames suggest rotation/crop augmentation applied

---

## Transformation Rules

### Class Mapping

| Original Category | → Target Class | Reasoning |
|---|---|---|
| `freshtomato` | **Fresh** | Healthy tomatoes |
| `Maroon Tomato` | **Fresh** | Healthy variety |
| `Red Cherry Tomato` | **Fresh** | Healthy variety |
| `Red Large Tomato` | **Fresh** | Healthy variety |
| `Red Tomato` | **Fresh** | Healthy variety |
| `Yellow Tomato` | **Fresh** | Healthy variety |
| `rottentomato` | **Rotten** | Spoiled/defective tomatoes |

### Typo Corrections

| Original | → Corrected Mapping |
|---|---|
| `freshtamto` | → Fresh |
| `rottentamto` | → Rotten |

### Pipeline

1. Backup original dataset → `dataset_original/`
2. Collect all images from all splits (Train + Test + valid)
3. Fix folder-name typos
4. Validate every image (Pillow open, verify, convert to RGB)
5. Remove corrupted/empty files
6. Remove exact duplicates (SHA-256 hash)
7. Stratified random shuffle split: **70% / 15% / 15%**
8. Copy validated images with clean filenames (`Fresh_00001.jpg`)

---

## Clean Dataset Structure

```
dataset/
├── train/
│   ├── Fresh/      (N images)
│   └── Rotten/     (N images)
├── validation/
│   ├── Fresh/      (N images)
│   └── Rotten/     (N images)
└── test/
    ├── Fresh/      (N images)
    └── Rotten/     (N images)
```

*(Exact counts are in `reports/dataset_report.md` after running `prepare_dataset.py`)*

---

## Data Augmentation (Training)

Applied during training only via Keras augmentation layers:

| Augmentation | Parameter |
|---|---|
| Random Rotation | ±15% |
| Random Zoom | ±15% |
| Random Contrast | ±20% |
| Random Brightness | ±20% |
| Horizontal Flip | Yes |
| Random Translation | ±10% H/W |

---

## Training Methodology

- **Architecture**: EfficientNetV2B0 (ImageNet pre-trained)
- **Transfer Learning**: Two-phase
  - Phase 1: Frozen backbone, train head (10 epochs, LR=1e-3)
  - Phase 2: Unfreeze last 50 layers, fine-tune (40 epochs, LR=1e-5)
- **Optimizer**: Adam
- **Loss**: Binary Crossentropy
- **Class Weights**: Computed automatically
- **Callbacks**: EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard
- **Image Size**: 224×224 RGB

---

## Evaluation Metrics

Generated automatically by `training/evaluate.py`:

- Confusion Matrix (raw + normalized)
- Classification Report (Precision, Recall, F1-Score)
- ROC Curve + AUC Score
- Precision-Recall Curve + Average Precision
- Optimal Classification Threshold (Youden's J)
- Grad-CAM Heatmaps
- Misclassified Image Analysis
- Top/Lowest Confidence Predictions

All outputs saved to `reports/`.

---

*Dataset version: 1.0 | Prepared by SmartCam AI Pipeline*
