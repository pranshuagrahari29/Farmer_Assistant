from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import pickle

app = Flask(__name__)

# Load the trained model
model_path = r"C:\Users\Pranshu Agrahari\OneDrive\Desktop\crop\RandomForest.pkl"
try:
    with open(model_path, "rb") as file:
        model = pickle.load(file)
except Exception as e:
    print(f"Error loading model: {e}")

# Ideal conditions for different crops
ideal_conditions = {
    "Rice": {"N": 80, "P": 48, "K": 40, "temperature": 23.7, "humidity": 82.3, "ph": 6.4, "rainfall": 236.2},
    "Maize": {"N": 78, "P": 48, "K": 20, "temperature": 22.4, "humidity": 65.1, "ph": 6.2, "rainfall": 84.8},
    "Chickpea": {"N": 40, "P": 68, "K": 80, "temperature": 18.9, "humidity": 16.9, "ph": 7.3, "rainfall": 80.1},
    "Kidneybeans": {"N": 21, "P": 68, "K": 20, "temperature": 20.1, "humidity": 21.6, "ph": 5.7, "rainfall": 105.9},
    "Pigeonpeas": {"N": 21, "P": 68, "K": 20, "temperature": 27.7, "humidity": 48.1, "ph": 5.8, "rainfall": 149.5},
    "Mothbeans": {"N": 21, "P": 48, "K": 20, "temperature": 28.2, "humidity": 53.2, "ph": 6.8, "rainfall": 51.2},
    "Mungbean": {"N": 21, "P": 47, "K": 20, "temperature": 28.5, "humidity": 85.5, "ph": 6.7, "rainfall": 48.4},
    "Blackgram": {"N": 40, "P": 67, "K": 19, "temperature": 30.0, "humidity": 65.1, "ph": 7.1, "rainfall": 67.9},
    "Lentil": {"N": 19, "P": 68, "K": 19, "temperature": 24.5, "humidity": 64.8, "ph": 6.9, "rainfall": 45.7},
    "Pomegranate": {"N": 19, "P": 19, "K": 40, "temperature": 21.8, "humidity": 90.1, "ph": 6.4, "rainfall": 107.5},
    "Banana": {"N": 100, "P": 82, "K": 50, "temperature": 27.4, "humidity": 80.4, "ph": 6.0, "rainfall": 104.6},
    "Mango": {"N": 20, "P": 27, "K": 30, "temperature": 31.2, "humidity": 50.2, "ph": 5.8, "rainfall": 94.7},
    "Grapes": {"N": 23, "P": 133, "K": 200, "temperature": 23.8, "humidity": 81.9, "ph": 6.0, "rainfall": 69.6},
    "Watermelon": {"N": 99, "P": 17, "K": 50, "temperature": 25.6, "humidity": 85.2, "ph": 6.5, "rainfall": 50.8},
    "Muskmelon": {"N": 100, "P": 18, "K": 50, "temperature": 28.7, "humidity": 92.3, "ph": 6.4, "rainfall": 24.7},
    "Apple": {"N": 21, "P": 134, "K": 200, "temperature": 22.6, "humidity": 92.3, "ph": 5.9, "rainfall": 112.7},
    "Orange": {"N": 20, "P": 17, "K": 10, "temperature": 22.8, "humidity": 92.2, "ph": 7.0, "rainfall": 110.5},
    "Papaya": {"N": 50, "P": 59, "K": 50, "temperature": 33.7, "humidity": 92.4, "ph": 6.7, "rainfall": 142.6},
    "Coconut": {"N": 22, "P": 17, "K": 31, "temperature": 27.4, "humidity": 94.8, "ph": 6.0, "rainfall": 175.7},
    "Cotton": {"N": 118, "P": 46, "K": 20, "temperature": 24.0, "humidity": 79.8, "ph": 6.9, "rainfall": 80.4},
    "Jute": {"N": 78, "P": 47, "K": 40, "temperature": 25.0, "humidity": 79.6, "ph": 6.7, "rainfall": 174.8},
    "Coffee": {"N": 101, "P": 29, "K": 30, "temperature": 25.5, "humidity": 58.9, "ph": 6.8, "rainfall":158.1}
}
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Collect input data
        N = float(request.form['N'])
        P = float(request.form['P'])
        K = float(request.form['K'])
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # Debugging: Print input values
        print(f"Input values: N={N}, P={P}, K={K}, temperature={temperature}, humidity={humidity}, ph={ph}, rainfall={rainfall}")

        # Create DataFrame
        input_data = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]],
                                  columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])

        # Get probabilities and top 3 crops
        probabilities = model.predict_proba(input_data)[0]
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_crops = model.classes_[top_indices]
        top_probs = probabilities[top_indices]

        recommended = [f"{crop} ({prob*100:.1f}%)" for crop, prob in zip(top_crops, top_probs)]
        result_text = "Recommended Crops: " + ", ".join(recommended)

        return render_template('index.html', prediction_text=result_text)

    except Exception as e:
        print(f"Error during prediction: {e}")  # Log the error
        return render_template('index.html', prediction_text=f"Error: {e}")

@app.route('/ideal_conditions', methods=['POST'])
def ideal_conditions_route():
    crop_name = request.form['crop_name']
    conditions = ideal_conditions.get(crop_name)

    if conditions:
        result_text = (f"Ideal conditions for {crop_name}: "
                       f"N: {conditions['N']}, P: {conditions['P']}, K: {conditions['K']}, "
                       f"Temperature: {conditions['temperature']}°C, Humidity: {conditions['humidity']}%, "
                       f"pH: {conditions['ph']}, Rainfall: {conditions['rainfall']} mm")
    else:
        result_text = f"No ideal conditions found for crop: {crop_name}"

    return render_template('index.html', prediction_text=result_text)

# VERY IMPORTANT:
if __name__ == '__main__':
    print("🔥 Starting Flask app... Visit http://127.0.0.1:5000")
    app.run(debug=True)