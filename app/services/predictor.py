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
        
        if fresh_prob >= 0.85 and fresh_prob > rotten_prob:
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
            "time_inference": time_inference
        }
        
        logger.info(f"Prediction: {prediction} ({confidence:.1f}%) [Prep: {time_preprocess}ms, Inf: {time_inference}ms]")
        return result
