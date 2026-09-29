from typing import Dict, Any
from ai_modules.disease_prediction import predict_tabular, predict_image


def predict_tabular_controller(features: Dict[str, Any]) -> Dict[str, Any]:
    # Controller layer can handle validation, mapping, and call AI module
    return predict_tabular(features)


def predict_image_controller(image_bytes: bytes) -> Dict[str, Any]:
    return predict_image(image_bytes)
