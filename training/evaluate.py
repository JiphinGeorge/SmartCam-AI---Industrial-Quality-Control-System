"""
QualiVision AI — Model Evaluation Script
========================================
Comprehensive evaluation on the test set with:
  - Confusion matrix (raw + normalized)
  - Classification report (precision, recall, F1)
  - ROC curve + AUC
  - Precision-Recall curve + AP
  - Optimal threshold determination
  - Grad-CAM heatmaps on sample images
  - Misclassified image analysis
  - Top/lowest confidence predictions
  - Example prediction cards

Usage:
    python -m training.evaluate
    # or from project root:
    python training/evaluate.py
"""

import os
import sys
import json
import pickle
import random
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_curve, auc, precision_recall_curve, average_precision_score
)

from training.config import (
    TEST_DIR, IMAGE_SIZE, BATCH_SIZE, CLASS_NAMES,
    BEST_MODEL_KERAS, BEST_MODEL_H5, CONFIG_FILE,
    REPORTS_DIR, MODELS_DIR, MODEL_VERSION,
)
from training.utils import (
    load_dataset, plot_confusion_matrix, plot_roc_curve,
    plot_precision_recall_curve, save_gradcam, save_prediction_example,
    make_gradcam_heatmap,
)


def find_last_conv_layer(model):
    """Find the last convolutional layer in the model for Grad-CAM."""
    for layer in reversed(model.layers):
        if isinstance(layer, tf.keras.Model):
            # Nested model (base model) — search inside
            for sub_layer in reversed(layer.layers):
                if len(sub_layer.output_shape) == 4:
                    return sub_layer.name
        if len(layer.output_shape) == 4:
            return layer.name
    return None


def main():
    print("=" * 65)
    print("  QualiVision AI — Model Evaluation")
    print("=" * 65)

    # -- Load Model --
    print("\n[1/8] Loading trained model...")
    if BEST_MODEL_KERAS.exists():
        model = tf.keras.models.load_model(str(BEST_MODEL_KERAS))
        print(f"  [OK] Loaded {BEST_MODEL_KERAS.name}")
    elif BEST_MODEL_H5.exists():
        model = tf.keras.models.load_model(str(BEST_MODEL_H5))
        print(f"  [OK] Loaded {BEST_MODEL_H5.name} (fallback)")
    else:
        print("  [FAIL] No trained model found! Run train.py first.")
        sys.exit(1)

    # -- Load Test Data --
    print("\n[2/8] Loading test dataset...")
    test_ds = load_dataset(TEST_DIR, shuffle=False)

    # Get all labels and predictions
    y_true = []
    y_pred_probs = []
    image_paths = []

    # Also collect individual image paths for Grad-CAM
    test_dir_fresh = TEST_DIR / "Fresh"
    test_dir_rotten = TEST_DIR / "Rotten"
    all_test_paths = []
    all_test_labels = []

    for img_path in sorted(test_dir_fresh.glob("*")):
        all_test_paths.append(img_path)
        all_test_labels.append(0)  # Fresh = 0
    for img_path in sorted(test_dir_rotten.glob("*")):
        all_test_paths.append(img_path)
        all_test_labels.append(1)  # Rotten = 1

    # Predict on full test set
    for images, labels in test_ds:
        preds = model.predict(images, verbose=0)
        y_true.extend(labels.numpy().flatten().astype(int))
        y_pred_probs.extend(preds.flatten())

    y_true = np.array(y_true)
    y_pred_probs = np.array(y_pred_probs)

    print(f"  Test samples: {len(y_true)}")
    print(f"  Fresh: {np.sum(y_true == 0)} | Rotten: {np.sum(y_true == 1)}")

    # -- Optimal Threshold --
    print("\n[3/8] Finding optimal classification threshold...")

    fpr, tpr, thresholds_roc = roc_curve(y_true, y_pred_probs)
    roc_auc = auc(fpr, tpr)

    # Youden's J statistic for optimal threshold
    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)
    optimal_threshold = float(thresholds_roc[optimal_idx])

    print(f"  ROC AUC: {roc_auc:.4f}")
    print(f"  Optimal threshold: {optimal_threshold:.4f}")

    # Update config.json with optimal threshold
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            config = json.load(f)
    config["threshold"] = round(optimal_threshold, 4)
    config["roc_auc"] = round(roc_auc, 4)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"  [OK] Updated {CONFIG_FILE.name} with optimal threshold")

    # Apply optimal threshold
    y_pred = (y_pred_probs >= optimal_threshold).astype(int)

    # -- Confusion Matrix --
    print("\n[4/8] Generating confusion matrices...")

    cm = confusion_matrix(y_true, y_pred)
    plot_confusion_matrix(cm, CLASS_NAMES,
                          REPORTS_DIR / "confusion_matrix.png", normalize=False)
    print(f"  [OK] confusion_matrix.png")

    plot_confusion_matrix(cm, CLASS_NAMES,
                          REPORTS_DIR / "confusion_matrix_normalized.png", normalize=True)
    print(f"  [OK] confusion_matrix_normalized.png")

    # -- Classification Report --
    print("\n[5/8] Generating classification report...")

    report = classification_report(y_true, y_pred, target_names=CLASS_NAMES,
                                    digits=4, output_dict=True)
    report_text = classification_report(y_true, y_pred, target_names=CLASS_NAMES, digits=4)

    print(f"\n{report_text}")

    report_path = REPORTS_DIR / "classification_report.txt"
    with open(report_path, "w") as f:
        f.write(f"QualiVision AI — Classification Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: {MODEL_VERSION}\n")
        f.write(f"Threshold: {optimal_threshold:.4f}\n")
        f.write(f"Test samples: {len(y_true)}\n")
        f.write(f"\n{report_text}\n")
        f.write(f"\nROC AUC: {roc_auc:.4f}\n")
    print(f"  [OK] classification_report.txt")

    # -- ROC Curve --
    print("\n[6/8] Generating ROC and PR curves...")

    plot_roc_curve(fpr, tpr, roc_auc, REPORTS_DIR / "roc_curve.png")
    print(f"  [OK] roc_curve.png")

    precision, recall, _ = precision_recall_curve(y_true, y_pred_probs)
    ap_score = average_precision_score(y_true, y_pred_probs)
    plot_precision_recall_curve(precision, recall, ap_score,
                                 REPORTS_DIR / "precision_recall_curve.png")
    print(f"  [OK] precision_recall_curve.png")

    # -- Grad-CAM Heatmaps --
    print("\n[7/8] Generating Grad-CAM heatmaps...")

    gradcam_dir = REPORTS_DIR / "gradcam"
    gradcam_dir.mkdir(exist_ok=True)

    # Find last conv layer
    last_conv = None
    for layer in reversed(model.layers):
        if isinstance(layer, tf.keras.Model):
            for sub_layer in reversed(layer.layers):
                if hasattr(sub_layer, 'output_shape') and isinstance(sub_layer.output_shape, tuple) and len(sub_layer.output_shape) == 4:
                    last_conv = sub_layer.name
                    break
            if last_conv:
                break
        if hasattr(layer, 'output_shape') and isinstance(layer.output_shape, tuple) and len(layer.output_shape) == 4:
            last_conv = layer.name
            break

    if last_conv:
        print(f"  Last conv layer: {last_conv}")
        # For Grad-CAM, we need a model that can access inner layers
        # Build a fresh reference to the base model layers
        try:
            # Sample a few images for Grad-CAM
            sample_indices = random.sample(range(len(all_test_paths)),
                                            min(8, len(all_test_paths)))
            for idx, sample_idx in enumerate(sample_indices):
                img_path = all_test_paths[sample_idx]
                label = "Fresh" if all_test_labels[sample_idx] == 0 else "Rotten"
                output_path = gradcam_dir / f"gradcam_{label.lower()}_{idx+1}.png"

                try:
                    save_gradcam(img_path, model, last_conv, output_path)
                    print(f"  [OK] gradcam_{label.lower()}_{idx+1}.png")
                except Exception as e:
                    print(f"  [!] Grad-CAM failed for {img_path.name}: {e}")
        except Exception as e:
            print(f"  [!] Grad-CAM generation failed: {e}")
    else:
        print("  [!] Could not find last conv layer for Grad-CAM")

    # -- Example Predictions & Misclassified --
    print("\n[8/8] Generating prediction examples...")

    predictions_dir = REPORTS_DIR / "predictions"
    predictions_dir.mkdir(exist_ok=True)

    # Top confidence correct predictions
    correct_mask = (y_pred == y_true)
    if np.any(correct_mask):
        correct_indices = np.where(correct_mask)[0]
        correct_confidences = np.abs(y_pred_probs[correct_indices] - 0.5) * 2 * 100
        top_confident = correct_indices[np.argsort(correct_confidences)[-6:]]

        for i, idx in enumerate(top_confident):
            if idx < len(all_test_paths):
                pred_label = CLASS_NAMES[y_pred[idx]]
                conf = y_pred_probs[idx] * 100 if y_pred[idx] == 1 else (1 - y_pred_probs[idx]) * 100
                status = "PASS" if pred_label == "Fresh" else "REJECT"
                save_prediction_example(
                    all_test_paths[idx], pred_label, conf, status,
                    predictions_dir / f"top_confidence_{i+1}.png"
                )
        print(f"  ✓ {len(top_confident)} top confidence examples")

    # Lowest confidence (uncertain)
    uncertainties = np.abs(y_pred_probs - 0.5)
    most_uncertain = np.argsort(uncertainties)[:6]
    for i, idx in enumerate(most_uncertain):
        if idx < len(all_test_paths):
            pred_label = CLASS_NAMES[y_pred[idx]]
            conf = y_pred_probs[idx] * 100 if y_pred[idx] == 1 else (1 - y_pred_probs[idx]) * 100
            status = "PASS" if pred_label == "Fresh" else "REJECT"
            save_prediction_example(
                all_test_paths[idx], pred_label, conf, status,
                predictions_dir / f"lowest_confidence_{i+1}.png"
            )
    print(f"  ✓ {len(most_uncertain)} lowest confidence examples")

    # Misclassified images
    misclassified = np.where(~correct_mask)[0]
    misclass_count = min(10, len(misclassified))
    for i in range(misclass_count):
        idx = misclassified[i]
        if idx < len(all_test_paths):
            true_label = CLASS_NAMES[y_true[idx]]
            pred_label = CLASS_NAMES[y_pred[idx]]
            conf = y_pred_probs[idx] * 100 if y_pred[idx] == 1 else (1 - y_pred_probs[idx]) * 100
            save_prediction_example(
                all_test_paths[idx], f"{pred_label} (TRUE: {true_label})", conf, "MISCLASSIFIED",
                predictions_dir / f"misclassified_{i+1}.png"
            )
    print(f"  ✓ {misclass_count} misclassified examples")

    # ── Update Training Summary ──
    summary_file = MODELS_DIR / "training_summary.json"
    if summary_file.exists():
        with open(summary_file) as f:
            summary = json.load(f)
    else:
        summary = {}

    summary.update({
        "test_accuracy": round(report["accuracy"] * 100, 2),
        "precision_fresh": round(report["Fresh"]["precision"] * 100, 2),
        "recall_fresh": round(report["Fresh"]["recall"] * 100, 2),
        "f1_fresh": round(report["Fresh"]["f1-score"] * 100, 2),
        "precision_rotten": round(report["Rotten"]["precision"] * 100, 2),
        "recall_rotten": round(report["Rotten"]["recall"] * 100, 2),
        "f1_rotten": round(report["Rotten"]["f1-score"] * 100, 2),
        "roc_auc": round(roc_auc, 4),
        "average_precision": round(ap_score, 4),
        "optimal_threshold": round(optimal_threshold, 4),
        "misclassified_count": int(len(misclassified)),
        "test_samples": int(len(y_true)),
        "evaluated_at": datetime.now().isoformat(),
    })

    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    # -- Final Summary --
    print(f"\n{'=' * 65}")
    print(f"  [OK] EVALUATION COMPLETE")
    print(f"  {'-' * 61}")
    print(f"  Test Accuracy:      {report['accuracy']*100:.2f}%")
    print(f"  ROC AUC:            {roc_auc:.4f}")
    print(f"  Average Precision:  {ap_score:.4f}")
    print(f"  Optimal Threshold:  {optimal_threshold:.4f}")
    print(f"  Misclassified:      {len(misclassified)}/{len(y_true)}")
    print(f"  {'-' * 61}")
    print(f"  Fresh  - P:{report['Fresh']['precision']:.4f} R:{report['Fresh']['recall']:.4f} F1:{report['Fresh']['f1-score']:.4f}")
    print(f"  Rotten - P:{report['Rotten']['precision']:.4f} R:{report['Rotten']['recall']:.4f} F1:{report['Rotten']['f1-score']:.4f}")
    print(f"  {'-' * 61}")
    print(f"  Reports: {REPORTS_DIR}")
    print(f"{'=' * 65}")


if __name__ == "__main__":
    main()
