from pathlib import Path

import joblib
import pandas as pd
import mysql.connector
import csv
import io

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.security import check_password_hash


# ============================================================
# FLASK APP
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)

# Used for admin login session
app.secret_key = "seasonal_crop_advisor_secret_key_2026"


# ============================================================
# MYSQL DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",

    # Replace with your MySQL ROOT password
    "password": "Vinay@53",

    "database": "seasonal_crop_advisor"
}


# ============================================================
# MYSQL CONNECTION
# ============================================================

def get_db_connection():

    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )


# ============================================================
# LOAD ML MODEL
# ============================================================

model = joblib.load(
    BASE_DIR / "crop_prediction_model.pkl"
)

season_encoder = joblib.load(
    BASE_DIR / "season_encoder.pkl"
)

soil_encoder = joblib.load(
    BASE_DIR / "soil_encoder.pkl"
)

crop_encoder = joblib.load(
    BASE_DIR / "crop_encoder.pkl"
)


# ============================================================
# SOIL ALIASES
# ============================================================

SOIL_ALIASES = {

    "alluvial soil": "Alluvial",
    "alluvial": "Alluvial",

    "black soil": "Black soil",
    "blacksoil": "Black soil",
    "black": "Black soil",

    "clay soil": "Clay",
    "clayey soil": "Clay",
    "clay": "Clay",

    "laterite soil": "Laterite",
    "lateritic": "Laterite",
    "laterite": "Laterite",

    "loamy soil": "Loamy",
    "loam soil": "Loamy",
    "loamy": "Loamy",

    "red soil": "Red soil",
    "red": "Red soil",

    "sandy soil": "Sandy",
    "sandy": "Sandy",
}


# ============================================================
# SEASON ALIASES
# ============================================================

SEASON_ALIASES = {

    "kharif": "Rainy",
    "rainy season": "Rainy",
    "rainy": "Rainy",
    "monsoon": "Rainy",

    "rabi": "Winter",
    "winter season": "Winter",
    "winter": "Winter",

    "zaid": "Summer",
    "summer season": "Summer",
    "summer": "Summer",
}


# ============================================================
# NORMALIZE ENCODER VALUE
# ============================================================

def normalize_encoder_value(value, encoder, aliases):

    text = str(value).strip()

    normalized = aliases.get(
        text.lower(),
        text
    )

    for choice in encoder.classes_:

        if choice.lower() == normalized.lower():
            return choice

    raise ValueError(
        f"Invalid value '{value}'. "
        f"Available values: {list(encoder.classes_)}"
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# CROP PREDICTION
# ============================================================
@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json(silent=True)

        if not data:
            raise ValueError("No JSON data received")

        # ====================================================
        # PREPARE INPUT
        # ====================================================

        input_data = pd.DataFrame([{

            "N": float(data["N"]),

            "P": float(data["P"]),

            "K": float(data["K"]),

            "Soil_pH": float(data["soil_ph"]),

            "Season": season_encoder.transform([

                normalize_encoder_value(
                    data["season"],
                    season_encoder,
                    SEASON_ALIASES
                )

            ])[0],

            "SoilType": soil_encoder.transform([

                normalize_encoder_value(
                    data.get(
                        "soil_type",
                        data.get("soilType")
                    ),
                    soil_encoder,
                    SOIL_ALIASES
                )

            ])[0]

        }])


        # ====================================================
        # MATCH FEATURE ORDER
        # ====================================================

        if hasattr(model, "feature_names_in_"):

            input_data = input_data[
                list(model.feature_names_in_)
            ]


        # ====================================================
        # PREDICTION
        # ====================================================

        prediction = model.predict(input_data)

        predicted_crop = crop_encoder.inverse_transform(
            prediction
        )[0]


        # ====================================================
        # GET ALL CROP PROBABILITIES
        # ====================================================

        probabilities = model.predict_proba(
            input_data
        )[0]

        model_classes = list(model.classes_)


        # ====================================================
        # CREATE CROP + PROBABILITY LIST
        # ====================================================

        crop_probabilities = []

        for class_value, probability in zip(
            model_classes,
            probabilities
        ):

            crop_name = crop_encoder.inverse_transform(
                [class_value]
            )[0]

            crop_probability = round(
                float(probability * 100),
                2
            )

            crop_probabilities.append({

                "crop": crop_name,

                "percentage": crop_probability

            })


        # ====================================================
        # SORT BY HIGHEST PROBABILITY
        # ====================================================

        crop_probabilities.sort(
            key=lambda x: x["percentage"],
            reverse=True
        )


        # ====================================================
        # TOP 3 RECOMMENDATIONS
        # ====================================================

        recommendations = crop_probabilities[:3]


        # ====================================================
        # MAKE SURE PREDICTED CROP IS FIRST
        # ====================================================

        for item in recommendations:

            if item["crop"] == predicted_crop:

                recommendations.remove(item)

                recommendations.insert(
                    0,
                    item
                )

                break


        # ====================================================
        # TOP CROP CONFIDENCE
        # ====================================================

        confidence = recommendations[0]["percentage"]


        # ====================================================
        # SAVE TOP CROP TO MYSQL
        # ====================================================

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            sql = """
                INSERT INTO predictions
                (
                    nitrogen,
                    phosphorus,
                    potassium,
                    soil_ph,
                    season,
                    soil_type,
                    recommended_crop
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """

            values = (

                float(data["N"]),

                float(data["P"]),

                float(data["K"]),

                float(data["soil_ph"]),

                str(data["season"]),

                str(
                    data.get(
                        "soil_type",
                        data.get("soilType")
                    )
                ),

                predicted_crop

            )

            cursor.execute(
                sql,
                values
            )

            connection.commit()

            print(
                "Prediction saved to MySQL."
            )

        except mysql.connector.Error as db_error:

            print(
                "MySQL Error:",
                db_error
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()


        # ====================================================
        # SEND RESPONSE
        # ====================================================

        return jsonify({

            "success": True,

            "crop": predicted_crop,

            "confidence": confidence,

            "recommendations": recommendations

        })


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except KeyError as error:

        return jsonify({

            "success": False,

            "error":
                f"Missing field: {error}"

        }), 400


    except (TypeError, ValueError) as error:

        return jsonify({

            "success": False,

            "error":
                str(error)

        }), 400


    except Exception as error:

        app.logger.exception(
            "Prediction failed"
        )

        return jsonify({

            "success": False,

            "error":
                f"Prediction failed: {error}"

        }), 500


# ============================================================
# ADMIN LOGIN PAGE
# ============================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    # Already logged in
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    # Login form submitted
    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Check empty fields
        if not username or not password:
            return render_template(
                "admin_login.html",
                error="Please enter username and password."
            )

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT admin_id, username, password_hash
                FROM admins
                WHERE username = %s
                """,
                (username,)
            )

            admin = cursor.fetchone()

            # Check password
            if admin and check_password_hash(
                admin["password_hash"],
                password
            ):

                session["admin_logged_in"] = True

                session["admin_id"] = admin["admin_id"]

                session["admin_username"] = admin["username"]

                return redirect(
                    url_for("admin_dashboard")
                )

            # Wrong username/password
            return render_template(
                "admin_login.html",
                error="Invalid username or password."
            )

        except mysql.connector.Error as error:

            return render_template(
                "admin_login.html",
                error=f"Database error: {error}"
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    # Normal GET request
    return render_template("admin_login.html",  
                error=""
            )  

      
    

# ============================================================
# ADMIN DASHBOARD
@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ALL PREDICTION RECORDS
        cursor.execute("""
            SELECT
                prediction_id,
                nitrogen,
                phosphorus,
                potassium,
                soil_ph,
                season,
                soil_type,
                recommended_crop,
                prediction_date
            FROM predictions
            ORDER BY prediction_id DESC
        """)

        predictions = cursor.fetchall()

        # TOTAL PREDICTIONS
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM predictions
        """)

        total_predictions = cursor.fetchone()["total"]

        # UNIQUE CROPS
        cursor.execute("""
            SELECT COUNT(DISTINCT recommended_crop) AS total
            FROM predictions
        """)

        total_crops = cursor.fetchone()["total"]

        # TODAY'S PREDICTIONS
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM predictions
            WHERE DATE(prediction_date) = CURDATE()
        """)

        today_predictions = cursor.fetchone()["total"]

        # MOST PREDICTED CROP
        cursor.execute("""
            SELECT
                recommended_crop,
                COUNT(*) AS crop_count
            FROM predictions
            GROUP BY recommended_crop
            ORDER BY crop_count DESC
            LIMIT 1
        """)

        top_crop_result = cursor.fetchone()

        if top_crop_result:
            top_crop = top_crop_result["recommended_crop"]
        else:
            top_crop = "No Data"

                 # CROP-WISE COUNTS
        cursor.execute("""
            SELECT recommended_crop, COUNT(*) AS count
            FROM predictions
            GROUP BY recommended_crop
            ORDER BY count DESC
        """)

        crop_results = cursor.fetchall()

        crop_names = [row["recommended_crop"] for row in crop_results]
        crop_counts = [row["count"] for row in crop_results]


        # SEASON-WISE COUNTS
        cursor.execute("""
            SELECT season, COUNT(*) AS count
            FROM predictions
            GROUP BY season
            ORDER BY count DESC
        """)

        season_results = cursor.fetchall()

        season_names = [row["season"] for row in season_results]
        season_counts = [row["count"] for row in season_results]   

        return render_template(
            "admin_dashboard.html",
            predictions=predictions,
            total_predictions=total_predictions,
            total_crops=total_crops,
            today_predictions=today_predictions,
            top_crop=top_crop,
            crop_names=crop_names,
            crop_counts=crop_counts,
            season_names=season_names,
            season_counts=season_counts,
            admin_username=session.get("admin_username")
        )

    except mysql.connector.Error as error:
        print("MySQL Error:", error)

        return render_template(
            "admin_dashboard.html",
            predictions=[],
            total_predictions=0,
            total_crops=0,
            today_predictions=0,
            top_crop="No Data",
            admin_username=session.get("admin_username")
        )

    except Exception as error:
        print("Error:", error)

        return render_template(
            "admin_dashboard.html",
            predictions=[],
            total_predictions=0,
            total_crops=0,
            today_predictions=0,
            top_crop="No Data",
            admin_username=session.get("admin_username")
        )

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()
   

# ============================================================
# DELETE PREDICTION
# ============================================================

@app.route(
    "/admin/delete/<int:prediction_id>",
    methods=["POST"]
)
def delete_prediction(prediction_id):

    # --------------------------------------------------------
    # SECURITY CHECK
    # --------------------------------------------------------

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )


    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM predictions
            WHERE prediction_id = %s
            """,
            (prediction_id,)
        )

        connection.commit()


    except mysql.connector.Error as error:

        print(
            "Delete error:",
            error
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


    return redirect(
        url_for("admin_dashboard")
    )
@app.route("/admin/delete/<int:prediction_id>", methods=["POST"])
def admin_delete(prediction_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM predictions WHERE prediction_id = %s",
        (prediction_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("admin_dashboard"))


@app.route("/admin/export")
def admin_export():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            prediction_id,
            nitrogen,
            phosphorus,
            potassium,
            soil_ph,
            season,
            soil_type,
            recommended_crop,
            prediction_date
        FROM predictions
        ORDER BY prediction_id DESC
    """)

    predictions = cursor.fetchall()

    cursor.close()
    conn.close()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Prediction ID",
        "Nitrogen",
        "Phosphorus",
        "Potassium",
        "Soil pH",
        "Season",
        "Soil Type",
        "Recommended Crop",
        "Prediction Date"
    ])

    for prediction in predictions:
        writer.writerow([
            prediction["prediction_id"],
            prediction["nitrogen"],
            prediction["phosphorus"],
            prediction["potassium"],
            prediction["soil_ph"],
            prediction["season"],
            prediction["soil_type"],
            prediction["recommended_crop"],
            prediction["prediction_date"]
        ])

    response = app.response_class(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers["Content-Disposition"] = \
        "attachment; filename=seasonal_crop_predictions.csv"

    return response


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )