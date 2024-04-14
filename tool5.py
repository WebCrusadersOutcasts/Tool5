from io import BytesIO
from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64

app = Flask(__name__)
CORS(app)

# PostgreSQL database connection details
db_host = "dpg-coc79mol6cac73er920g-a.singapore-postgres.render.com"
db_name = "datathon"
db_user = "datathon_user"
db_password = "EeTXudLXaOtmBqLX0tKUhJ8kGWarqHTO"

def connect_to_db():
    """Establish connection to PostgreSQL database."""
    conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
    return conn

def get_all_district_data():
    """Retrieve data for all districts from the database."""
    conn = connect_to_db()
    try:
        query = "SELECT * FROM tool5"
        all_district_data = pd.read_sql(query, conn)
        return all_district_data
    finally:
        if conn:
            conn.close()

def preprocess_data(data):
    """Preprocess the data by creating age groups and other transformations."""
    # Create age groups
    age_bins = [0, 20, 30, 40, 50, 60, 70, np.inf]
    age_labels = ['0-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71+']
    data['AgeGroup'] = pd.cut(data['age'], bins=age_bins, labels=age_labels, right=False)

    # Update profession values
    profession_values = {
        "labourer": 1,
        "farmer": 2,
        "housewife": 3,
        "driver": 4,
        "student": 5,
        "others pi specify": 6,
        "ceo": 7,
        "businessman": 8,
        "electrician": 9,
        "bank employee": 10,
        "central govt.employee": 11
    }
    data['Profession'] = data['profession'].map(profession_values)

    return data

def generate_plots(data):
    """Generate plots based on the provided data."""
    plots = {}

    # Plot Crime Occurrence by Age Group
    plt.figure(figsize=(10, 6))
    sns.countplot(x='AgeGroup', data=data, palette='muted')
    plt.title('Crime Occurrence by Age Group')
    plt.xlabel('Age Group')
    plt.ylabel('Number of Victims')
    age_plot_buffer = BytesIO()
    plt.savefig(age_plot_buffer, format='png')
    age_plot_buffer.seek(0)
    age_plot_base64 = base64.b64encode(age_plot_buffer.getvalue()).decode('utf-8')
    plots['age'] = age_plot_base64

    # Plot Crime Occurrence by Sex
    plt.figure(figsize=(6, 4))
    sns.countplot(x='sex', data=data, palette='muted')
    plt.title('Crime Occurrence by Sex')
    plt.xlabel('Sex')
    plt.ylabel('Number of Victims')
    sex_plot_buffer = BytesIO()
    plt.savefig(sex_plot_buffer, format='png')
    sex_plot_buffer.seek(0)
    sex_plot_base64 = base64.b64encode(sex_plot_buffer.getvalue()).decode('utf-8')
    plots['sex'] = sex_plot_base64

    # Plot Crime Occurrence by Location (District)
    plt.figure(figsize=(14, 8))
    sns.countplot(x='district_name', data=data, palette='muted')
    plt.title('Crime Occurrence by Location (District)')
    plt.xlabel('District')
    plt.ylabel('Number of Victims')
    plt.xticks(rotation=90)
    location_plot_buffer = BytesIO()
    plt.savefig(location_plot_buffer, format='png')
    location_plot_buffer.seek(0)
    location_plot_base64 = base64.b64encode(location_plot_buffer.getvalue()).decode('utf-8')
    plots['location'] = location_plot_base64

    return plots

@app.route('/plots', methods=['GET'])
def generate_plots_json():
    # Retrieve data for all districts
    all_district_data = get_all_district_data()

    if all_district_data.empty:
        return jsonify({"error": "No data found in the database"}), 404

    # Preprocess the data
    processed_data = preprocess_data(all_district_data)

    # Generate plots and convert to base64 encoded strings
    plots = generate_plots(processed_data)

    # Return the plots as JSON response
    return jsonify(plots)

if __name__ == '__main__':
    app.run(debug=True)
