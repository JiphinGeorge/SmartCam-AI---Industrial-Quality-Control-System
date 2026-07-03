"""
SmartCam AI — Model Training Script
======================================
Two-phase transfer learning pipeline using EfficientNetV2B0:
  Phase 1: Train classifier head with frozen backbone (10 epochs)
  Phase 2: Fine-tune last 50 layers with low LR (40 epochs)

Features:
  - Automatic class weight computation
  - Full data augmentation pipeline
  - EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard
  - Mixed precision training (auto-detected GPU)
  - Exports: .keras, .h5, labels.txt, config.json, training_summary.json

Usage:
    python -m training.train
    # or from project root:
    python training/train.py
"""

import os
import sys
import json
import time
import pickle
from pathlib import Path
from datetime import datetime, timedelta

# Ensure project root is on the path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import tensorflow as tf

from training.config import (
    TRAIN_DIR, VAL_DIR, IMAGE_SIZE, INPUT_SHAPE, BATCH_SIZE,
    PHASE1_EPOCHS, PHASE1_LEARNING_RATE,
    PHASE2_EPOCHS, PHASE2_LEARNING_RATE, FINE_TUNE_LAYERS,
    BASE_MODEL, FALLBACK_MODEL, LOSS, METRICS,
    EARLY_STOPPING_PATIENCE, REDUCE_LR_PATIENCE, REDUCE_LR_FACTOR, REDUCE_LR_MIN,
    BEST_MODEL_KERAS, BEST_MODEL_H5, LABELS_FILE, CONFIG_FILE,
    HISTORY_FILE, SUMMARY_FILE, LOGS_DIR, MODELS_DIR,
    CLASS_NAMES, MODEL_VERSION, PROJECT_VERSION,
)
from training.utils import (
    load_dataset, get_class_weights, create_augmentation_layer,
    get_preprocessing_layer, plot_training_history,
)


def setup_mixed_precision():
    """Enable mixed precision if GPU is available."""
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        print(f"  [OK] GPU detected: {gpus[0].name}")
        try:
            tf.keras.mixed_precision.set_global_policy("mixed_float16")
            print("  [OK] Mixed precision (float16) enabled")
            return True
        except Exception as e:
            print(f"  [!] Mixed precision failed: {e}")
    else:
        print("  [INFO] No GPU detected - training on CPU")
    return False


def get_base_model(model_name, input_shape):
    """
    Load the EfficientNet base model with ImageNet weights.
    Falls back to EfficientNetB0 if V2 is unavailable.
    """
    try:
        if model_name == "EfficientNetV2B0":
            base = tf.keras.applications.EfficientNetV2B0(
                include_top=False,
                weights="imagenet",
                input_shape=input_shape,
                pooling=None,
            )
            print(f"  [OK] Loaded {model_name}")
            return base, model_name
    except (AttributeError, ImportError, Exception) as e:
        print(f"  [!] {model_name} unavailable ({e}), falling back to {FALLBACK_MODEL}")

    # Fallback
    base = tf.keras.applications.EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_shape=input_shape,
        pooling=None,
    )
    print(f"  [OK] Loaded {FALLBACK_MODEL} (fallback)")
    return base, FALLBACK_MODEL


def build_model(base_model, augmentation_layer, preprocess_fn):
    """
    Build the full model: Input → Augmentation → Preprocess → Base → Head.
    """
    inputs = tf.keras.Input(shape=INPUT_SHAPE, name="input_image")

    # Augmentation (only active during training)
    x = augmentation_layer(inputs, training=True)

    # Preprocessing for the base model
    x = tf.keras.layers.Lambda(preprocess_fn, name="preprocessing")(x)

    # Frozen base model
    x = base_model(x, training=False)

    # Classification head
    x = tf.keras.layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = tf.keras.layers.BatchNormalization(name="head_bn")(x)
    x = tf.keras.layers.Dropout(0.3, name="head_dropout_1")(x)
    x = tf.keras.layers.Dense(256, activation="relu", name="head_dense")(x)
    x = tf.keras.layers.Dropout(0.2, name="head_dropout_2")(x)

    # Binary output
    outputs = tf.keras.layers.Dense(1, activation="sigmoid", name="output",
                                     dtype="float32")(x)  # float32 for mixed precision

    model = tf.keras.Model(inputs, outputs, name="SmartCam_AI")
    return model


def get_callbacks(phase, log_subdir="phase1"):
    """Create training callbacks for a given phase."""
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=EARLY_STOPPING_PATIENCE,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=REDUCE_LR_FACTOR,
            patience=REDUCE_LR_PATIENCE,
            min_lr=REDUCE_LR_MIN,
            verbose=1,
        ),
        tf.keras.callbacks.ModelCheckpoint(
            str(BEST_MODEL_KERAS),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        tf.keras.callbacks.TensorBoard(
            log_dir=str(LOGS_DIR / log_subdir),
            histogram_freq=1,
            write_graph=True,
        ),
    ]
    return callbacks


def main():
    start_time = time.time()

    print("=" * 65)
    print("  SmartCam AI — Model Training Pipeline")
    print("  " + "-" * 61)
    print(f"  Version: {PROJECT_VERSION} | Model: {MODEL_VERSION}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    # -- Setup --
    print("\n[1/7] Setting up environment...")
    use_mixed = setup_mixed_precision()

    # -- Load Data --
    print("\n[2/7] Loading datasets...")
    train_ds = load_dataset(TRAIN_DIR, shuffle=True)
    val_ds = load_dataset(VAL_DIR, shuffle=False)

    # Class weights
    class_weights = get_class_weights(TRAIN_DIR)
    print(f"  Class weights: Fresh={class_weights[0]:.4f}, Rotten={class_weights[1]:.4f}")

    # Optimize pipeline
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(AUTOTUNE)
    val_ds = val_ds.cache().prefetch(AUTOTUNE)

    # -- Build Model --
    print("\n[3/7] Building model architecture...")
    base_model, actual_model_name = get_base_model(BASE_MODEL, INPUT_SHAPE)
    augmentation_layer = create_augmentation_layer()
    preprocess_fn = get_preprocessing_layer(actual_model_name)

    # Freeze backbone
    base_model.trainable = False

    model = build_model(base_model, augmentation_layer, preprocess_fn)
    model.summary(print_fn=lambda x: print(f"  {x}") if "param" in x.lower() or "layer" in x.lower()[:10] else None)

    total_params = model.count_params()
    trainable_params = sum(tf.keras.backend.count_params(w) for w in model.trainable_weights)
    print(f"\n  Total parameters: {total_params:,}")
    print(f"  Trainable parameters: {trainable_params:,}")
    print(f"  Base model: {actual_model_name}")

    # ===========================================
    # PHASE 1: Train classifier head (frozen backbone)
    # ===========================================
    print(f"\n{'=' * 65}")
    print(f"  PHASE 1: Training Classifier Head ({PHASE1_EPOCHS} epochs)")
    print(f"  Backbone: FROZEN | LR: {PHASE1_LEARNING_RATE}")
    print(f"{'=' * 65}")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=PHASE1_LEARNING_RATE),
        loss=LOSS,
        metrics=METRICS,
    )

    phase1_callbacks = get_callbacks("phase1", log_subdir="phase1")

    history1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=PHASE1_EPOCHS,
        callbacks=phase1_callbacks,
        class_weight=class_weights,
        verbose=1,
    )

    phase1_epochs_actual = len(history1.history["loss"])
    print(f"\n  [OK] Phase 1 complete: {phase1_epochs_actual} epochs")
    print(f"    Train Accuracy: {history1.history['accuracy'][-1]:.4f}")
    print(f"    Val Accuracy:   {history1.history['val_accuracy'][-1]:.4f}")

    # ===========================================
    # PHASE 2: Fine-tune top layers
    # ===========================================
    print(f"\n{'=' * 65}")
    print(f"  PHASE 2: Fine-Tuning ({PHASE2_EPOCHS} epochs)")
    print(f"  Unfreezing last {FINE_TUNE_LAYERS} layers | LR: {PHASE2_LEARNING_RATE}")
    print(f"{'=' * 65}")

    # Unfreeze last N layers of the backbone
    base_model.trainable = True
    total_layers = len(base_model.layers)
    freeze_until = max(0, total_layers - FINE_TUNE_LAYERS)

    for layer in base_model.layers[:freeze_until]:
        layer.trainable = False

    unfrozen = sum(1 for l in base_model.layers if l.trainable)
    print(f"  Base model layers: {total_layers}")
    print(f"  Unfrozen layers: {unfrozen}")

    # Re-compile with lower learning rate
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=PHASE2_LEARNING_RATE),
        loss=LOSS,
        metrics=METRICS,
    )

    trainable_params_p2 = sum(tf.keras.backend.count_params(w) for w in model.trainable_weights)
    print(f"  Trainable parameters: {trainable_params_p2:,}")

    phase2_callbacks = get_callbacks("phase2", log_subdir="phase2")

    history2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=PHASE1_EPOCHS + PHASE2_EPOCHS,
        initial_epoch=phase1_epochs_actual,
        callbacks=phase2_callbacks,
        class_weight=class_weights,
        verbose=1,
    )

    phase2_epochs_actual = len(history2.history["loss"])

    # -- Combine histories --
    combined_history = {}
    for key in history1.history:
        combined_history[key] = history1.history[key] + history2.history[key]
    combined_history["phase1_epochs"] = phase1_epochs_actual
    total_epochs = phase1_epochs_actual + phase2_epochs_actual

    print(f"\n  [OK] Phase 2 complete: {phase2_epochs_actual} epochs")
    print(f"    Final Train Accuracy: {combined_history['accuracy'][-1]:.4f}")
    print(f"    Final Val Accuracy:   {combined_history['val_accuracy'][-1]:.4f}")

    # -- Save Outputs --
    print(f"\n[5/7] Saving model and artifacts...")

    # .keras (primary format)
    model.save(str(BEST_MODEL_KERAS))
    print(f"  [OK] {BEST_MODEL_KERAS.name}")

    # .h5 (compatibility format)
    model.save(str(BEST_MODEL_H5))
    print(f"  [OK] {BEST_MODEL_H5.name}")

    # labels.txt
    with open(LABELS_FILE, "w") as f:
        for i, name in enumerate(CLASS_NAMES):
            f.write(f"{i} {name}\n")
    print(f"  [OK] {LABELS_FILE.name}")

    # training_history.pkl
    with open(HISTORY_FILE, "wb") as f:
        pickle.dump(combined_history, f)
    print(f"  [OK] {HISTORY_FILE.name}")

    # -- Generate Plots --
    print(f"\n[6/7] Generating training plots...")
    from training.config import REPORTS_DIR
    plot_training_history(combined_history, REPORTS_DIR)

    # -- Training Summary --
    print(f"\n[7/7] Saving training summary...")

    elapsed = time.time() - start_time
    elapsed_str = str(timedelta(seconds=int(elapsed)))

    model_size_mb = BEST_MODEL_KERAS.stat().st_size / (1024 * 1024) if BEST_MODEL_KERAS.exists() else 0

    summary = {
        "project": "SmartCam AI",
        "project_version": PROJECT_VERSION,
        "model_version": MODEL_VERSION,
        "model": actual_model_name,
        "tensorflow_version": tf.__version__,
        "total_epochs": total_epochs,
        "phase1_epochs": phase1_epochs_actual,
        "phase2_epochs": phase2_epochs_actual,
        "best_train_accuracy": round(max(combined_history["accuracy"]) * 100, 2),
        "best_val_accuracy": round(max(combined_history["val_accuracy"]) * 100, 2),
        "final_train_accuracy": round(combined_history["accuracy"][-1] * 100, 2),
        "final_val_accuracy": round(combined_history["val_accuracy"][-1] * 100, 2),
        "final_train_loss": round(combined_history["loss"][-1], 4),
        "final_val_loss": round(combined_history["val_loss"][-1], 4),
        "training_time": elapsed_str,
        "training_time_seconds": round(elapsed, 1),
        "model_size_mb": round(model_size_mb, 2),
        "image_size": list(IMAGE_SIZE),
        "batch_size": BATCH_SIZE,
        "class_names": CLASS_NAMES,
        "class_weights": {str(k): round(v, 4) for k, v in class_weights.items()},
        "mixed_precision": use_mixed,
        "trained_at": datetime.now().isoformat(),
        "output_files": {
            "keras": str(BEST_MODEL_KERAS),
            "h5": str(BEST_MODEL_H5),
            "labels": str(LABELS_FILE),
        }
    }

    with open(SUMMARY_FILE, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  [OK] {SUMMARY_FILE.name}")

    # config.json (threshold — will be updated by evaluate.py)
    config = {
        "threshold": 0.5,
        "model": actual_model_name,
        "image_size": list(IMAGE_SIZE),
        "class_names": CLASS_NAMES,
        "model_version": MODEL_VERSION,
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"  [OK] {CONFIG_FILE.name}")

    # -- Final Summary --
    print(f"\n{'=' * 65}")
    print(f"  [OK] TRAINING COMPLETE")
    print(f"  {'-' * 61}")
    print(f"  Model:            {actual_model_name}")
    print(f"  Total Epochs:     {total_epochs}")
    print(f"  Best Val Accuracy: {max(combined_history['val_accuracy'])*100:.2f}%")
    print(f"  Training Time:    {elapsed_str}")
    print(f"  Model Size:       {model_size_mb:.1f} MB")
    print(f"  {'-' * 61}")
    print(f"  Output: {MODELS_DIR}")
    print(f"  TensorBoard: tensorboard --logdir {LOGS_DIR}")
    print(f"{'=' * 65}")


if __name__ == "__main__":
    main()
