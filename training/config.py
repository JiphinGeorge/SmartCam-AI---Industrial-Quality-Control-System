"""
SmartCam AI — Training Configuration
======================================
Central configuration for all training parameters.
"""

from pathlib import Path

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "dataset"
TRAIN_DIR = DATASET_DIR / "train"
VAL_DIR = DATASET_DIR / "validation"
TEST_DIR = DATASET_DIR / "test"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
LOGS_DIR = ROOT / "logs"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "gradcam").mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "predictions").mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# Model
# ──────────────────────────────────────────────
BASE_MODEL = "EfficientNetV2B0"       # Primary choice
FALLBACK_MODEL = "EfficientNetB0"     # Fallback if V2 unavailable
IMAGE_SIZE = (224, 224)
INPUT_SHAPE = (*IMAGE_SIZE, 3)
NUM_CLASSES = 1                       # Binary classification (sigmoid)

# ──────────────────────────────────────────────
# Training — Phase 1 (Frozen backbone)
# ──────────────────────────────────────────────
PHASE1_EPOCHS = 10
PHASE1_LEARNING_RATE = 1e-3

# ──────────────────────────────────────────────
# Training — Phase 2 (Fine-tuning)
# ──────────────────────────────────────────────
PHASE2_EPOCHS = 40                    # Total = 50 with Phase 1
PHASE2_LEARNING_RATE = 1e-5
FINE_TUNE_LAYERS = 50                 # Unfreeze last N layers

# ──────────────────────────────────────────────
# Hyperparameters
# ──────────────────────────────────────────────
BATCH_SIZE = 32
OPTIMIZER = "adam"
LOSS = "binary_crossentropy"
METRICS = ["accuracy"]

# ──────────────────────────────────────────────
# Callbacks
# ──────────────────────────────────────────────
EARLY_STOPPING_PATIENCE = 8
REDUCE_LR_PATIENCE = 4
REDUCE_LR_FACTOR = 0.5
REDUCE_LR_MIN = 1e-7

# ──────────────────────────────────────────────
# Data Augmentation
# ──────────────────────────────────────────────
AUGMENTATION = {
    "rotation_factor": 0.15,          # ±15% of 360° = ±54°
    "zoom_factor": 0.15,
    "contrast_factor": 0.2,
    "brightness_factor": 0.2,
    "horizontal_flip": True,
    "vertical_flip": False,
    "translation_height": 0.1,
    "translation_width": 0.1,
}

# ──────────────────────────────────────────────
# Labels
# ──────────────────────────────────────────────
CLASS_NAMES = ["Fresh", "Rotten"]      # Index 0 = Fresh, Index 1 = Rotten
ROTTEN_THRESHOLD_DEFAULT = 0.5        # Default; overridden by optimal threshold

# ──────────────────────────────────────────────
# Output Files
# ──────────────────────────────────────────────
BEST_MODEL_KERAS = MODELS_DIR / "best_model.keras"
BEST_MODEL_H5 = MODELS_DIR / "best_model.h5"
LABELS_FILE = MODELS_DIR / "labels.txt"
CONFIG_FILE = MODELS_DIR / "config.json"
HISTORY_FILE = MODELS_DIR / "training_history.pkl"
SUMMARY_FILE = MODELS_DIR / "training_summary.json"

# ──────────────────────────────────────────────
# Version
# ──────────────────────────────────────────────
PROJECT_VERSION = "1.0.0"
MODEL_VERSION = "1.0.0"
DATASET_VERSION = "1.0"
