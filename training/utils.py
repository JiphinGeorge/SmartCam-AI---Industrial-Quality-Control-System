"""
QualiVision AI — Training Utilities
==================================
Shared utility functions for dataset loading, data augmentation,
Grad-CAM visualization, plotting, and metric computation.
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pathlib import Path
from datetime import datetime

import tensorflow as tf

from training.config import (
    IMAGE_SIZE, BATCH_SIZE, AUGMENTATION, CLASS_NAMES,
    REPORTS_DIR,
)

# Chart colors — QualiVision AI industrial theme
CHART_COLORS = {
    "Fresh":      "#16c784",
    "Rotten":     "#ff4d4f",
    "primary":    "#16c784",
    "secondary":  "#0566d9",
    "tertiary":   "#8b5cf6",
    "bg":         "#0b1326",
    "surface":    "#171f33",
    "text":       "#dae2fd",
    "grid":       "#2d3449",
    "accent":     "#f59e0b",
}

plt.rcParams.update({
    "figure.facecolor": CHART_COLORS["bg"],
    "axes.facecolor": CHART_COLORS["surface"],
    "axes.edgecolor": CHART_COLORS["grid"],
    "axes.labelcolor": CHART_COLORS["text"],
    "text.color": CHART_COLORS["text"],
    "xtick.color": CHART_COLORS["text"],
    "ytick.color": CHART_COLORS["text"],
    "grid.color": CHART_COLORS["grid"],
    "grid.alpha": 0.3,
    "font.family": "sans-serif",
    "font.size": 12,
})


# ──────────────────────────────────────────────
# Dataset Loading
# ──────────────────────────────────────────────

def load_dataset(directory, image_size=IMAGE_SIZE, batch_size=BATCH_SIZE, shuffle=True):
    """
    Load a dataset from a directory using tf.keras.utils.image_dataset_from_directory.
    Returns a tf.data.Dataset with labels as binary (0=Fresh, 1=Rotten).
    """
    ds = tf.keras.utils.image_dataset_from_directory(
        directory,
        image_size=image_size,
        batch_size=batch_size,
        label_mode="binary",
        class_names=CLASS_NAMES,  # Ensures Fresh=0, Rotten=1
        shuffle=shuffle,
        seed=42,
    )
    return ds


def get_class_weights(directory):
    """
    Compute class weights for imbalanced datasets.
    Returns a dict {0: weight_fresh, 1: weight_rotten}.
    """
    fresh_count = len(list(Path(directory, "Fresh").glob("*")))
    rotten_count = len(list(Path(directory, "Rotten").glob("*")))
    total = fresh_count + rotten_count

    weight_fresh = total / (2.0 * fresh_count) if fresh_count > 0 else 1.0
    weight_rotten = total / (2.0 * rotten_count) if rotten_count > 0 else 1.0

    return {0: weight_fresh, 1: weight_rotten}


# ──────────────────────────────────────────────
# Data Augmentation
# ──────────────────────────────────────────────

def create_augmentation_layer():
    """
    Create a Keras Sequential model of augmentation layers.
    Applied only during training.
    """
    augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomRotation(AUGMENTATION["rotation_factor"]),
        tf.keras.layers.RandomZoom(AUGMENTATION["zoom_factor"]),
        tf.keras.layers.RandomContrast(AUGMENTATION["contrast_factor"]),
        tf.keras.layers.RandomFlip("horizontal" if AUGMENTATION["horizontal_flip"] else "horizontal_and_vertical"),
        tf.keras.layers.RandomTranslation(
            AUGMENTATION["translation_height"],
            AUGMENTATION["translation_width"]
        ),
        tf.keras.layers.RandomBrightness(AUGMENTATION["brightness_factor"]),
    ], name="data_augmentation")

    return augmentation


# ──────────────────────────────────────────────
# Preprocessing
# ──────────────────────────────────────────────

def get_preprocessing_layer(model_name):
    """Get the correct preprocessing function for the base model."""
    if "EfficientNetV2" in model_name:
        return tf.keras.applications.efficientnet_v2.preprocess_input
    elif "EfficientNet" in model_name:
        return tf.keras.applications.efficientnet.preprocess_input
    else:
        # Generic: scale to [-1, 1]
        return lambda x: (x / 127.5) - 1.0


# ──────────────────────────────────────────────
# Grad-CAM
# ──────────────────────────────────────────────

def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    """
    Generate Grad-CAM heatmap for a given image and model.

    Args:
        img_array: Preprocessed image array (1, 224, 224, 3)
        model: Keras model
        last_conv_layer_name: Name of the last convolutional layer
        pred_index: Class index to visualize (None = predicted class)

    Returns:
        Heatmap as numpy array (0-1 normalized)
    """
    # Create a model that maps input → [last conv output, model output]
    grad_model = tf.keras.Model(
        model.inputs,
        [model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        if pred_index is None:
            pred_index = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_index] if len(predictions.shape) > 1 and predictions.shape[-1] > 1 else predictions[:, 0]

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)

    return heatmap.numpy()


def save_gradcam(img_path, model, last_conv_layer_name, output_path, image_size=IMAGE_SIZE):
    """
    Generate and save a Grad-CAM overlay for a single image.
    """
    # Load and preprocess image
    img = tf.keras.utils.load_img(img_path, target_size=image_size)
    img_array = tf.keras.utils.img_to_array(img)
    img_array_expanded = np.expand_dims(img_array, axis=0)

    # Generate heatmap
    heatmap = make_gradcam_heatmap(img_array_expanded, model, last_conv_layer_name)

    # Resize heatmap to image size
    heatmap_resized = np.uint8(255 * heatmap)
    from PIL import Image as PILImage
    heatmap_pil = PILImage.fromarray(heatmap_resized).resize(image_size)
    heatmap_resized = np.array(heatmap_pil)

    # Apply colormap
    jet_colormap = cm.get_cmap("jet")
    jet_colors = jet_colormap(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap_resized]
    jet_heatmap = np.uint8(jet_heatmap * 255)

    # Overlay
    original = np.uint8(img_array)
    superimposed = (jet_heatmap * 0.4 + original * 0.6).astype(np.uint8)

    # Save figure
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    titles = ["Original", "Grad-CAM Heatmap", "Overlay"]
    images = [original, jet_heatmap, superimposed]

    for ax, title, image in zip(axes, titles, images):
        ax.imshow(image)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xticks([])
        ax.set_yticks([])

    plt.suptitle(f"Grad-CAM Visualization", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ──────────────────────────────────────────────
# Plotting
# ──────────────────────────────────────────────

def plot_training_history(history_dict, output_dir):
    """
    Plot training/validation accuracy and loss curves.
    Handles 2-phase training (combined history dicts).
    """
    # Accuracy plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(history_dict["accuracy"], color=CHART_COLORS["primary"],
            linewidth=2, label="Train Accuracy")
    ax.plot(history_dict["val_accuracy"], color=CHART_COLORS["secondary"],
            linewidth=2, linestyle="--", label="Val Accuracy")
    ax.set_title("Model Accuracy", fontsize=18, fontweight="bold", pad=15)
    ax.set_xlabel("Epoch", fontsize=13)
    ax.set_ylabel("Accuracy", fontsize=13)
    ax.legend(fontsize=12, facecolor=CHART_COLORS["surface"], edgecolor=CHART_COLORS["grid"])
    ax.grid(True, alpha=0.2)

    # Mark phase boundary
    if "phase1_epochs" in history_dict:
        ax.axvline(x=history_dict["phase1_epochs"] - 1, color=CHART_COLORS["accent"],
                    linestyle=":", linewidth=1.5, label="Fine-tune start")
        ax.legend(fontsize=12, facecolor=CHART_COLORS["surface"], edgecolor=CHART_COLORS["grid"])

    plt.tight_layout()
    fig.savefig(output_dir / "accuracy_plot.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Loss plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(history_dict["loss"], color=CHART_COLORS["Rotten"],
            linewidth=2, label="Train Loss")
    ax.plot(history_dict["val_loss"], color=CHART_COLORS["accent"],
            linewidth=2, linestyle="--", label="Val Loss")
    ax.set_title("Model Loss", fontsize=18, fontweight="bold", pad=15)
    ax.set_xlabel("Epoch", fontsize=13)
    ax.set_ylabel("Loss", fontsize=13)
    ax.legend(fontsize=12, facecolor=CHART_COLORS["surface"], edgecolor=CHART_COLORS["grid"])
    ax.grid(True, alpha=0.2)

    if "phase1_epochs" in history_dict:
        ax.axvline(x=history_dict["phase1_epochs"] - 1, color=CHART_COLORS["accent"],
                    linestyle=":", linewidth=1.5)

    plt.tight_layout()
    fig.savefig(output_dir / "loss_plot.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Learning rate plot (if available)
    if "lr" in history_dict:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(history_dict["lr"], color=CHART_COLORS["tertiary"], linewidth=2)
        ax.set_title("Learning Rate Schedule", fontsize=18, fontweight="bold", pad=15)
        ax.set_xlabel("Epoch", fontsize=13)
        ax.set_ylabel("Learning Rate", fontsize=13)
        ax.set_yscale("log")
        ax.grid(True, alpha=0.2)
        plt.tight_layout()
        fig.savefig(output_dir / "learning_rate_plot.png", dpi=150, bbox_inches="tight")
        plt.close(fig)

    print(f"  ✓ Training plots saved to {output_dir}")


def plot_confusion_matrix(cm_array, class_names, output_path, normalize=False):
    """Plot a confusion matrix as a heatmap."""
    if normalize:
        cm_display = cm_array.astype("float") / (cm_array.sum(axis=1, keepdims=True) + 1e-8)
        fmt = ".2%"
        title = "Normalized Confusion Matrix"
    else:
        cm_display = cm_array
        fmt = "d"
        title = "Confusion Matrix"

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm_display, interpolation="nearest",
                   cmap=plt.cm.Blues if not normalize else plt.cm.Greens)

    ax.set_title(title, fontsize=18, fontweight="bold", pad=15)
    tick_marks = np.arange(len(class_names))
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(class_names, fontsize=13)
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(class_names, fontsize=13)
    ax.set_xlabel("Predicted", fontsize=14, labelpad=10)
    ax.set_ylabel("Actual", fontsize=14, labelpad=10)

    # Text annotations
    thresh = cm_display.max() / 2.0
    for i in range(cm_display.shape[0]):
        for j in range(cm_display.shape[1]):
            val = f"{cm_display[i, j]:{fmt}}" if normalize else f"{cm_display[i, j]}"
            ax.text(j, i, val, ha="center", va="center", fontsize=16, fontweight="bold",
                    color="white" if cm_display[i, j] > thresh else CHART_COLORS["text"])

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_roc_curve(fpr, tpr, auc_score, output_path):
    """Plot ROC curve."""
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.plot(fpr, tpr, color=CHART_COLORS["primary"], linewidth=2.5,
            label=f"ROC Curve (AUC = {auc_score:.4f})")
    ax.plot([0, 1], [0, 1], color=CHART_COLORS["grid"], linewidth=1.5, linestyle="--",
            label="Random (AUC = 0.5)")
    ax.fill_between(fpr, tpr, alpha=0.15, color=CHART_COLORS["primary"])
    ax.set_title("Receiver Operating Characteristic", fontsize=18, fontweight="bold", pad=15)
    ax.set_xlabel("False Positive Rate", fontsize=13)
    ax.set_ylabel("True Positive Rate", fontsize=13)
    ax.legend(fontsize=12, loc="lower right",
              facecolor=CHART_COLORS["surface"], edgecolor=CHART_COLORS["grid"])
    ax.grid(True, alpha=0.2)
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_precision_recall_curve(precision, recall, ap_score, output_path):
    """Plot Precision-Recall curve."""
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.plot(recall, precision, color=CHART_COLORS["secondary"], linewidth=2.5,
            label=f"PR Curve (AP = {ap_score:.4f})")
    ax.fill_between(recall, precision, alpha=0.15, color=CHART_COLORS["secondary"])
    ax.set_title("Precision-Recall Curve", fontsize=18, fontweight="bold", pad=15)
    ax.set_xlabel("Recall", fontsize=13)
    ax.set_ylabel("Precision", fontsize=13)
    ax.legend(fontsize=12, loc="lower left",
              facecolor=CHART_COLORS["surface"], edgecolor=CHART_COLORS["grid"])
    ax.grid(True, alpha=0.2)
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def save_prediction_example(img_path, prediction, confidence, status, output_path,
                            image_size=IMAGE_SIZE):
    """Save an annotated prediction example image."""
    img = tf.keras.utils.load_img(img_path, target_size=image_size)

    fig, ax = plt.subplots(figsize=(6, 7))
    ax.imshow(np.array(img))
    ax.set_xticks([])
    ax.set_yticks([])

    color = CHART_COLORS["Fresh"] if prediction == "Fresh" else CHART_COLORS["Rotten"]
    status_symbol = "✔ PASS" if status == "PASS" else "✘ REJECT"

    for spine in ax.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(3)

    ax.set_title(
        f"Prediction: {prediction}\n"
        f"Confidence: {confidence:.2f}%\n"
        f"{status_symbol}",
        fontsize=14, fontweight="bold", color=color, pad=15
    )

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
