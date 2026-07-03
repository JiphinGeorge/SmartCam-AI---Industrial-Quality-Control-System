# AI Model Documentation

## Overview

The SmartCam AI predictor engine relies on a state-of-the-art convolutional neural network trained on a dataset of industrial items (e.g., tomatoes) to perform binary or multi-class classification, paired with anomaly detection for Out-Of-Distribution (OOD) objects.

## Base Architecture
- **Model**: `EfficientNetV2B0`
- **Weights**: Pre-trained on ImageNet.
- **Top Layers**: Custom GlobalAveragePooling2D -> Dropout(0.2) -> Dense(Softmax).
- **Input Shape**: `(224, 224, 3)`
- **Color Space**: RGB

## Training Parameters
- **Optimizer**: Adam (`learning_rate = 1e-4`)
- **Loss Function**: Categorical Crossentropy (or Sparse Categorical Crossentropy).
- **Metrics**: Accuracy, Precision, Recall.
- **Callbacks**: 
  - `EarlyStopping` (patience=5)
  - `ReduceLROnPlateau` (factor=0.2, patience=3)
  - `ModelCheckpoint`

## Dataset Preparation & Augmentation
The dataset was augmented during training to prevent overfitting to factory lighting conditions:
- Random Horizontal Flip
- Random Rotation (±20 degrees)
- Random Zoom (±10%)
- Brightness Adjustment

## Inference Logic & Confidence Thresholds
When an image is passed to the prediction pipeline:
1. It is resized and normalized.
2. The model outputs a probability distribution across known classes.
3. **Thresholding**:
   - If `max(probabilities) >= 65%`: The prediction is accepted.
   - If `max(probabilities) < 65%`: The image is flagged as **"REVIEW REQUIRED"** (Unknown Class Logic). This prevents the AI from confidently misclassifying an anomaly (like a wrench falling on the conveyor belt) as "Fresh".

## Explainability (Grad-CAM)
Gradient-weighted Class Activation Mapping (Grad-CAM) is implemented to provide visual explanations.
- **Target Layer**: The final convolutional block of EfficientNetV2B0.
- **Process**: The gradients of the predicted class score with respect to the feature map are computed. These gradients are pooled and used to weight the activation maps, creating a heatmap that highlights the regions of the image that contributed most to the prediction.
- **Storage**: Heatmaps are saved via OpenCV's `applyColorMap(COLORMAP_JET)` and blended with the original image at 0.4 alpha.
