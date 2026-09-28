import argparse
import json
from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "crop_prediction_model.pkl"
SEASON_ENCODER_PATH = BASE_DIR / "season_encoder.pkl"
SOIL_ENCODER_PATH = BASE_DIR / "soil_encoder.pkl"
CROP_ENCODER_PATH = BASE_DIR / "crop_encoder.pkl"

SEASON_ALIASES = {
    "kharif": "rainy",
    "rainy season": "rainy",
    "rainy": "rainy",
    "monsoon": "rainy",
    "rabi": "winter",
    "winter season": "winter",
    "winter": "winter",
    "zaid": "summer",
    "summer season": "summer",
    "summer": "summer",
}

SOIL_ALIASES = {
    "alluvial soil": "alluvial",
    "alluvial": "alluvial",
    "black soil": "black soil",
    "blacksoil": "black soil",
    "black": "black soil",
    "clay soil": "clay",
    "clayey soil": "clay",
    "clay": "clay",
    "laterite soil": "laterite",
    "lateritic": "laterite",
    "laterite": "laterite",
    "loamy soil": "loamy",
    "loam soil": "loamy",
    "loamy": "loamy",
    "red soil": "red soil",
    "red": "red soil",
    "sandy soil": "sandy",
    "sandy": "sandy",
}


def normalize_choice(value, aliases=None):
    text = str(value or "").strip()
    text = text.replace("_", " ").replace("-", " ")
    text = " ".join(text.split()).lower()
    if aliases and text in aliases:
        return aliases[text]
    return text


def encoder_choice(value, classes, label):
    choices = {str(choice).lower(): choice for choice in classes}
    choice = choices.get(value.lower())
    if choice is None:
        raise ValueError(   


            
            f"Invalid {label}. Use one of: " + ", ".join(map(str, classes))
        )
    return choice


def load_artifacts():
    model = joblib.load(MODEL_PATH)
    season_encoder = joblib.load(SEASON_ENCODER_PATH)
    soil_encoder = joblib.load(SOIL_ENCODER_PATH)
    crop_encoder = joblib.load(CROP_ENCODER_PATH)
    return model, season_encoder, soil_encoder, crop_encoder


def predict_crop(payload):
    model, season_encoder, soil_encoder, crop_encoder = load_artifacts()
    season = normalize_choice(payload.get("season"), SEASON_ALIASES)
    soil_type = normalize_choice(payload.get("soil_type"), SOIL_ALIASES)

    season = encoder_choice(season, season_encoder.classes_, "season")
    soil_type = encoder_choice(soil_type, soil_encoder.classes_, "soil type")
    season_encoded = season_encoder.transform([season])[0]
    soil_encoded = soil_encoder.transform([soil_type])[0]

    input_df = pd.DataFrame(
        [{
            "N": float(payload["N"]),
            "P": float(payload["P"]),
            "K": float(payload["K"]),
            "Soil_pH": float(payload["soil_ph"]),
            "Season": season_encoded,
            "SoilType": soil_encoded,
        }]
    )

    if hasattr(model, "feature_names_in_"):
        model_features = list(model.feature_names_in_)
        input_df = input_df[model_features]

    prediction = model.predict(input_df)[0]
    crop_name = crop_encoder.inverse_transform([prediction])[0]
    return {"crop": crop_name, "prediction": int(prediction)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict a crop recommendation from soil data.")
    parser.add_argument(
        "--json",
        type=str,
        help="JSON payload string, e.g. '{\"N\":80,\"P\":60,\"K\":70,\"soil_ph\":6.5,\"season\":\"Rainy\",\"soil_type\":\"Loamy Soil\"}'",
    )
    args = parser.parse_args()

    if args.json:
        raw_json = args.json
        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError:
            payload = json.loads(raw_json.replace("'", '"'))
    else:
        payload = {
            "N": 80,
            "P": 60,
            "K": 70,
            "soil_ph": 6.5,
            "season": "Rainy",
            "soil_type": "Loamy Soil",
        }

    result = predict_crop(payload)
    print(json.dumps(result, indent=2))
