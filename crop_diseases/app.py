import streamlit as st
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from PIL import Image

# Image size used during training
IMG_SIZE = 150

# Load the trained model
MODEL_PATH = r"C:\Users\Pranshu Agrahari\OneDrive\Desktop\plant_disesis\Best_Plant.h5"
model = load_model(MODEL_PATH)

# Dictionary of class labels and remedies
disease_info = {
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Use resistant hybrids, crop rotation, and fungicide sprays.",
    "Corn_(maize)___Common_rust_": "Apply fungicides if severe; use resistant varieties.",
    "Corn_(maize)___healthy": "No action needed. Keep monitoring the crop.",
    "Corn_(maize)___Northern_Leaf_Blight": "Use resistant hybrids and apply fungicides early.",
    "Potato___Early_blight": "Remove infected leaves, rotate crops, and apply appropriate fungicides.",
    "Potato___healthy": "No disease detected. Maintain proper care.",
    "Potato___Late_blight": "Remove infected plants and spray systemic fungicides.",
    "Tomato___Bacterial_spot": "Use copper-based sprays and resistant varieties.",
    "Tomato___Early_blight": "Use mulch, remove infected leaves, and apply fungicides.",
    "Tomato___healthy": "No disease detected. Continue regular care.",
    "Tomato___Late_blight": "Apply fungicides and remove infected leaves immediately.",
    "Tomato___Leaf_Mold": "Improve air circulation, avoid overhead watering, and use fungicides.",
    "Tomato___Septoria_leaf_spot": "Remove infected leaves and apply chlorothalonil or copper fungicide.",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Spray with water or insecticidal soap. Introduce natural predators.",
    "Tomato___Target_Spot": "Use crop rotation, remove debris, and apply fungicides.",
    "Tomato___Tomato_mosaic_virus": "Remove infected plants and disinfect tools. Avoid handling when wet.",
    "Tomato___Yellow_Leaf_Curl_Virus": "Control whiteflies and use resistant plant varieties."
}

# Generate class labels in sorted order (same as training)
class_labels = sorted(list(disease_info.keys()))

# Streamlit UI
st.set_page_config(page_title="🌿 Plant Disease Detector", layout="centered")
st.title("🌿 Plant Disease Detection")
st.write("Upload a leaf image to detect the disease and get recommended treatment.")

# Upload image
uploaded_file = st.file_uploader("📷 Upload a plant leaf image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Show image
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # Preprocess for prediction
    img_resized = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = image.img_to_array(img_resized) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Predict
    prediction = model.predict(img_array)
    predicted_index = np.argmax(prediction)
    confidence = np.max(prediction) * 100
    predicted_label = class_labels[predicted_index]
    solution = disease_info[predicted_label]

    # Display result
    st.success(f"✅ **Predicted Disease:** `{predicted_label}`")
    st.info(f"🔍 **Confidence:** `{confidence:.2f}%`")
    st.markdown(f"🧪 **Suggested Solution:**\n\n{solution}")




