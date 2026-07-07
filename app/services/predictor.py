import tensorflow as tf
import time
from app.config import Config
from app.services.preprocessing import PreprocessingService
from app.services.logger import get_logger

logger = get_logger('prediction')

class PredictorService:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            try:
                logger.info(f"Loading model from {Config.MODEL_PATH}...")
                cls._model = tf.keras.models.load_model(Config.MODEL_PATH)
                logger.info("Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise e
        return cls._model

    @staticmethod
    def predict(image_path_or_bytes):
        """
        Runs inference on an image and returns the prediction result.
        """
        model = PredictorService.get_model()
        
        # Preprocess
        start_preprocess = time.time()
        input_tensor = PreprocessingService.preprocess_image(image_path_or_bytes)
        time_preprocess = int((time.time() - start_preprocess) * 1000)
        
        # Inference
        start_inference = time.time()
        prediction_scores = model.predict(input_tensor, verbose=0)
        time_inference = int((time.time() - start_inference) * 1000)
        
        # Format results
        if len(prediction_scores[0]) > 1:
            fresh_prob = float(prediction_scores[0][0])
            rotten_prob = float(prediction_scores[0][1])
        else:
            rotten_prob = float(prediction_scores[0][0])
            fresh_prob = 1.0 - rotten_prob
            
        # OOD Heuristic: Use OpenCV to check if image has tomato-like colors (Red, Green, Yellow/Orange)
        import cv2
        import numpy as np
        img_rgb = input_tensor[0].astype(np.uint8)
        img_bgr = img_rgb[:, :, ::-1]
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        mask_red1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
        mask_red2 = cv2.inRange(hsv, np.array([170, 50, 50]), np.array([180, 255, 255]))
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)
        mask_green = cv2.inRange(hsv, np.array([35, 40, 40]), np.array([85, 255, 255]))
        mask_yellow = cv2.inRange(hsv, np.array([11, 50, 50]), np.array([34, 255, 255]))
        combined = cv2.bitwise_or(mask_red, mask_green)
        combined = cv2.bitwise_or(combined, mask_yellow)
        ratio = cv2.countNonZero(combined) / (img_bgr.shape[0] * img_bgr.shape[1])
        
        is_ood = ratio < 0.02 # If less than 2% of the image is tomato-colored, flag as Unknown.

        if is_ood:
            prediction = "Unknown"
            confidence = max(fresh_prob, rotten_prob) * 100
            status = "REVIEW"
            explanation = "Out-of-Distribution Detected. The object does not match the visual color profile of a tomato. Flagged for manual review."
        elif fresh_prob >= 0.85 and fresh_prob > rotten_prob:
            prediction = "Fresh"
            confidence = fresh_prob * 100
            status = "PASS"
            explanation = "The AI model classified this tomato as Fresh with high confidence. The decision is based on visual patterns learned during training. The highlighted regions show the image areas that most influenced the prediction."
        elif rotten_prob >= 0.85 and rotten_prob > fresh_prob:
            prediction = "Rotten"
            confidence = rotten_prob * 100
            status = "FAIL"
            explanation = "The AI model classified this tomato as Rotten with high confidence. The highlighted regions contributed most strongly to the model's decision and resemble decay-related patterns learned during training."
        else:
            prediction = "Unknown"
            confidence = max(fresh_prob, rotten_prob) * 100
            status = "REVIEW"
            explanation = "The AI could not confidently classify this image. Manual inspection is recommended before making a quality-control decision."

        # Confidence Level
        if confidence >= 95:
            conf_level = "Very High"
        elif confidence >= 85:
            conf_level = "High"
        elif confidence >= 70:
            conf_level = "Medium"
        else:
            conf_level = "Low"
            
        result = {
            "prediction": prediction,
            "confidence": confidence,
            "confidence_level": conf_level,
            "status": status,
            "explanation": explanation,
            "time_preprocess": time_preprocess,
            "time_inference": time_inference,
            "probabilities": {
                "Fresh": fresh_prob,
                "Rotten": rotten_prob
            },
            "tensor_data": {
                "model_version": "v2.1",
                "tensor_shape": [1, 224, 224, 3],
                "latency_ms": time_inference,
                "raw_logits": [round(fresh_prob, 3), round(rotten_prob, 3)],
                "activations": "softmax" if len(prediction_scores[0]) > 1 else "sigmoid"
            }
        }
        
        logger.info(f"Prediction: {prediction} ({confidence:.1f}%) [Prep: {time_preprocess}ms, Inf: {time_inference}ms]")
        return result
