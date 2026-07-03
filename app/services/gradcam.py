import numpy as np
import tensorflow as tf
import cv2
from app.services.predictor import PredictorService
from app.services.preprocessing import PreprocessingService

class GradCamService:
    @staticmethod
    def find_last_conv_layer(model):
        """Finds the last convolutional layer in a Keras model."""
        # For a model wrapping EfficientNet, we need to inspect the inner layers.
        for layer in reversed(model.layers):
            # If the layer itself is a functional model (like EfficientNetV2B0 base), search inside it.
            if isinstance(layer, tf.keras.Model):
                for inner_layer in reversed(layer.layers):
                    if len(inner_layer.output_shape) == 4:
                        return layer, inner_layer.name
            if len(layer.output_shape) == 4:
                return model, layer.name
        raise ValueError("Could not find a convolutional layer.")

    @staticmethod
    def generate_heatmap(image_path_or_bytes, save_path=None):
        """Generates a Grad-CAM heatmap for the given image."""
        model = PredictorService.get_model()
        img_array = PreprocessingService.preprocess_image(image_path_or_bytes)
        
        try:
            target_model, layer_name = GradCamService.find_last_conv_layer(model)
            
            # If the last conv layer is inside the base model
            if target_model != model:
                # We need to construct a gradient model that maps from base input to base output
                grad_model = tf.keras.models.Model(
                    [target_model.inputs], 
                    [target_model.get_layer(layer_name).output, target_model.output]
                )
                
                with tf.GradientTape() as tape:
                    last_conv_layer_output, base_preds = grad_model(img_array)
                    # We pass the base predictions through the top layers (GlobalAveragePooling, Dropout, Dense)
                    x = base_preds
                    # Find index of target_model
                    base_idx = model.layers.index(target_model)
                    for layer in model.layers[base_idx + 1:]:
                        x = layer(x)
                    preds = x
                    class_channel = preds[:, 0]
            else:
                grad_model = tf.keras.models.Model(
                    [model.inputs], 
                    [model.get_layer(layer_name).output, model.output]
                )
                
                with tf.GradientTape() as tape:
                    last_conv_layer_output, preds = grad_model(img_array)
                    class_channel = preds[:, 0]
                    
            # Compute gradients
            grads = tape.gradient(class_channel, last_conv_layer_output)
            pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
            
            last_conv_layer_output = last_conv_layer_output[0]
            heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
            heatmap = tf.squeeze(heatmap)
            heatmap = tf.maximum(heatmap, 0)
            max_val = tf.math.reduce_max(heatmap)
            if max_val != 0:
                heatmap = heatmap / max_val
            heatmap = heatmap.numpy()
            heatmap = np.nan_to_num(heatmap, nan=0.0).astype(np.float32)
            
            # Overlay on original image
            original_img = cv2.imread(image_path_or_bytes) if isinstance(image_path_or_bytes, str) else cv2.imdecode(np.frombuffer(image_path_or_bytes.read(), np.uint8), cv2.IMREAD_COLOR)
            
            heatmap_resized = cv2.resize(heatmap, (original_img.shape[1], original_img.shape[0]))
            heatmap_uint8 = np.uint8(255 * heatmap_resized)
            colormap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
            
            overlay = cv2.addWeighted(original_img, 0.6, colormap, 0.4, 0)
            
            if save_path:
                cv2.imwrite(save_path, overlay)
            
            # Encode for web serving
            _, buffer = cv2.imencode('.jpg', overlay)
            return buffer.tobytes()
            
        except Exception as e:
            from app.services.logger import get_logger
            get_logger('prediction').error(f"Grad-CAM error: {e}")
            return None
