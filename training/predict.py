"""
QualiVision AI — Prediction Script
=================================
Standalone inference for testing individual images, folders,
or camera input against the trained model.

Usage:
    python -m training.predict --image path/to/tomato.jpg
    python -m training.predict --folder path/to/test_images/
    python -m training.predict --camera  (future — placeholder)

Examples:
    python training/predict.py --image dataset/test/Fresh/Fresh_00001.jpg
    python training/predict.py --folder dataset/test/Rotten/
"""

import os
import sys
import json
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import tensorflow as tf
from PIL import Image

from training.config import (
    IMAGE_SIZE, CLASS_NAMES,
    BEST_MODEL_KERAS, BEST_MODEL_H5, CONFIG_FILE,
    ROTTEN_THRESHOLD_DEFAULT,
)

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def load_model():
    """Load the best trained model."""
    if BEST_MODEL_KERAS.exists():
        model = tf.keras.models.load_model(str(BEST_MODEL_KERAS))
        print(f"[OK] Model loaded: {BEST_MODEL_KERAS.name}")
    elif BEST_MODEL_H5.exists():
        model = tf.keras.models.load_model(str(BEST_MODEL_H5))
        print(f"[OK] Model loaded: {BEST_MODEL_H5.name}")
    else:
        print("[FAIL] No trained model found! Run training/train.py first.")
        sys.exit(1)
    return model


def load_threshold():
    """Load optimal threshold from config.json."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        threshold = config.get("threshold", ROTTEN_THRESHOLD_DEFAULT)
        print(f"  Threshold: {threshold:.4f} (from config.json)")
        return threshold
    print(f"  Threshold: {ROTTEN_THRESHOLD_DEFAULT} (default)")
    return ROTTEN_THRESHOLD_DEFAULT


def preprocess_image(image_path, image_size=IMAGE_SIZE):
    """Load and preprocess a single image for prediction."""
    img = Image.open(image_path)

    # Convert to RGB (handle RGBA, grayscale, palette)
    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    img = img.resize(image_size)
    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def predict_single(model, image_path, threshold):
    """
    Predict a single image.
    Returns: (prediction_label, confidence_pct, status, raw_score)
    """
    img_array = preprocess_image(image_path)
    raw_score = model.predict(img_array, verbose=0)[0][0]

    if raw_score >= threshold:
        prediction = "Rotten"
        confidence = raw_score * 100
        status = "REJECT"
    else:
        prediction = "Fresh"
        confidence = (1 - raw_score) * 100
        status = "PASS"

    return prediction, confidence, status, float(raw_score)


def predict_image(model, image_path, threshold):
    """Predict and display result for a single image."""
    prediction, confidence, status, raw_score = predict_single(
        model, image_path, threshold
    )

    # Display result
    status_icon = "[PASS]" if status == "PASS" else "[REJECT]"
    color = "\033[92m" if status == "PASS" else "\033[91m"
    reset = "\033[0m"

    print(f"\n  {'-' * 50}")
    print(f"  Image:      {Path(image_path).name}")
    print(f"  Prediction: {color}{prediction}{reset}")
    print(f"  Confidence: {confidence:.2f}%")
    print(f"  Status:     {color}{status_icon} {status}{reset}")
    print(f"  Raw Score:  {raw_score:.6f}")
    print(f"  Threshold:  {threshold:.4f}")
    print(f"  {'-' * 50}")

    return prediction, confidence, status


def predict_folder(model, folder_path, threshold):
    """Predict all images in a folder."""
    folder = Path(folder_path)
    image_files = [f for f in folder.iterdir()
                   if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS]

    if not image_files:
        print(f"  [FAIL] No valid images found in {folder}")
        return

    print(f"\n  Processing {len(image_files)} images from {folder.name}/")
    print(f"  {'-' * 60}")
    print(f"  {'Image':<30} {'Prediction':<12} {'Confidence':>12} {'Status':>8}")
    print(f"  {'-' * 60}")

    results = {"Fresh": 0, "Rotten": 0, "total": 0}

    for img_path in sorted(image_files):
        prediction, confidence, status, _ = predict_single(
            model, img_path, threshold
        )
        results[prediction] += 1
        results["total"] += 1

        color = "\033[92m" if status == "PASS" else "\033[91m"
        reset = "\033[0m"
        status_icon = "✔" if status == "PASS" else "✘"

        print(f"  {img_path.name:<30} {color}{prediction:<12}{reset} "
              f"{confidence:>10.2f}%  {color}{status_icon}{reset}")

    print(f"  {'─' * 60}")
    print(f"  Summary: {results['total']} images | "
          f"Fresh: {results['Fresh']} | Rotten: {results['Rotten']}")
    print(f"  Pass rate: {results['Fresh']/results['total']*100:.1f}%")


def predict_camera():
    """Placeholder for camera prediction mode."""
    print("\n  📷 Camera mode")
    print("  This feature will be available in the QualiVision AI web application.")
    print("  Use the Flask app's /inspection route for live camera capture.")
    print("  For now, use --image or --folder modes.")


def main():
    parser = argparse.ArgumentParser(
        description="QualiVision AI — Tomato Quality Prediction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python training/predict.py --image dataset/test/Fresh/Fresh_00001.jpg
  python training/predict.py --folder dataset/test/Rotten/
  python training/predict.py --camera
        """
    )
    parser.add_argument("--image", type=str, help="Path to a single image file")
    parser.add_argument("--folder", type=str, help="Path to a folder of images")
    parser.add_argument("--camera", action="store_true", help="Camera mode (placeholder)")
    parser.add_argument("--threshold", type=float, default=None,
                        help="Override classification threshold (0.0-1.0)")

    args = parser.parse_args()

    if not any([args.image, args.folder, args.camera]):
        parser.print_help()
        sys.exit(0)

    print("=" * 55)
    print("  QualiVision AI — Prediction")
    print("=" * 55)

    model = load_model()
    threshold = args.threshold if args.threshold is not None else load_threshold()

    if args.image:
        img_path = Path(args.image)
        if not img_path.exists():
            print(f"  ✗ Image not found: {args.image}")
            sys.exit(1)
        predict_image(model, img_path, threshold)

    elif args.folder:
        folder_path = Path(args.folder)
        if not folder_path.is_dir():
            print(f"  ✗ Folder not found: {args.folder}")
            sys.exit(1)
        predict_folder(model, folder_path, threshold)

    elif args.camera:
        predict_camera()


if __name__ == "__main__":
    main()
