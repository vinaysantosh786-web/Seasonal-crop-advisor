import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# =====================================================
# LOAD DATASET
# =====================================================

df = pd.read_csv(
    r"C:\Users\swamy\Downloads\crop_dataset_40k (1).csv"
)


# =====================================================
# REMOVE UNNECESSARY COLUMNS
# =====================================================

df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
df = df.dropna(axis=1, how="all")


print("\nDataset Columns:")
print(df.columns.tolist())

print("\nFirst 5 Rows:")
print(df.head())


# =====================================================
# CLEAN CATEGORICAL VALUES
# =====================================================

df["Season"] = df["Season"].astype(str).str.strip().str.lower()
df["SoilType"] = df["SoilType"].astype(str).str.strip().str.lower()

# Crop names
df["Predicted_Crop"] = (
    df["Predicted_Crop"]
    .astype(str)
    .str.strip()
)


# =====================================================
# ENCODE CATEGORICAL COLUMNS
# =====================================================

season_encoder = LabelEncoder()
soil_encoder = LabelEncoder()
crop_encoder = LabelEncoder()


df["Season"] = season_encoder.fit_transform(
    df["Season"]
)

df["SoilType"] = soil_encoder.fit_transform(
    df["SoilType"]
)

df["Predicted_Crop"] = crop_encoder.fit_transform(
    df["Predicted_Crop"]
)


# =====================================================
# FEATURES AND TARGET
# =====================================================

X = df.drop("Predicted_Crop", axis=1)

y = df["Predicted_Crop"]


print("\nFeatures used by model:")
print(X.columns.tolist())

print("\nSeason values:")
print(season_encoder.classes_)

print("\nSoil Type values:")
print(soil_encoder.classes_)

print("\nCrop values:")
print(crop_encoder.classes_)


# =====================================================
# TRAIN TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# =====================================================
# RANDOM FOREST MODEL
# =====================================================

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=20,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42
)


# =====================================================
# TRAIN MODEL
# =====================================================

model.fit(X_train, y_train)


# =====================================================
# TEST MODEL
# =====================================================

y_pred = model.predict(X_test)


accuracy = accuracy_score(
    y_test,
    y_pred
)


print("\n===================================")
print("Model Accuracy:", f"{accuracy * 100:.2f}%")
print("===================================")


print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred
    )
)


# =====================================================
# SAVE MODEL AND ENCODERS
# =====================================================

joblib.dump(
    model,
    "crop_prediction_model.pkl"
)

joblib.dump(
    season_encoder,
    "season_encoder.pkl"
)

joblib.dump(
    soil_encoder,
    "soil_encoder.pkl"
)

joblib.dump(
    crop_encoder,
    "crop_encoder.pkl"
)


print("\n===================================")
print("Model Saved Successfully!")
print("===================================")

print("\nFiles created:")
print("1. crop_prediction_model.pkl")
print("2. season_encoder.pkl")
print("3. soil_encoder.pkl")
print("4. crop_encoder.pkl")


# =====================================================
# FIRST 10 PREDICTIONS
# =====================================================

print("\nFirst 10 Predictions:")

for i in range(min(10, len(y_pred))):

    predicted_crop = crop_encoder.inverse_transform(
        [y_pred[i]]
    )[0]

    actual_crop = crop_encoder.inverse_transform(
        [y_test.iloc[i]]
    )[0]

    print(
        f"Predicted: {predicted_crop} | "
        f"Actual: {actual_crop}"
    )