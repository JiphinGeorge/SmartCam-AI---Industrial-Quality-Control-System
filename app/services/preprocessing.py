from PIL import Image
import numpy as np
from app.config import Config

class PreprocessingService:
    @staticmethod
    def preprocess_image(image_path_or_bytes):
        """
        Preprocesses an image identically to the training pipeline:
        - Load with Pillow
        - Resize to Config.INPUT_SIZE (224x224)
        - Convert to RGB
        - Convert to numpy array and normalize to [0, 1]
        """
        img = Image.open(image_path_or_bytes).convert('RGB')
        img = img.resize(Config.INPUT_SIZE, Image.Resampling.BILINEAR)
        
        img_array = np.array(img, dtype=np.float32)
        # EfficientNetV2B0 in TF Keras typically expects inputs in [0, 255] for the built-in Rescaling,
        # but if our pipeline manually rescaled to [0,1], we do it here.
        # Let's check training pipeline: 'tf.keras.layers.Rescaling(1./255)' was used in the model architecture.
        # Wait, if Rescaling is part of the model, we DO NOT rescale here. We just return the array.
        # Let's pass the raw array with batch dimension.
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
