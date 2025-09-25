import streamlit as st
import pickle
import numpy as np

# ---------------------------
# Load the saved model & scaler
# ---------------------------
try:
    with open("../saved_models/scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open("../saved_models/kmeans_model.pkl", "rb") as f:
        kmeans_model = pickle.load(f)
except Exception as e:
    st.error(f"Error loading model files: {e}")
    st.stop()

# ---------------------------
# Mapping from model clusters to original classes
# ---------------------------
mapping = {2: 1, 1: 3, 0: 2}

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("Wine Cluster Prediction App")
st.write("Enter the chemical composition of wine to predict its cluster.")

# Feature names
features = [
    'Alcohol', 'Malic acid', 'Ash', 'Alkanility of ash',
    'Magnesium', 'Total phenols', 'Flavanoids', 'Nonflavanoid phenols',
    'Proanthocyanins', 'Color intensity', 'Hue',
    'OD280/OD315 of diluted wines', 'Proline'
]

# Input fields for all features
inputs = {}
for feature in features:
    try:
        inputs[feature] = st.number_input(f"{feature}", value=0.0, format="%.3f")
    except Exception as e:
        st.error(f"Error with input for {feature}: {e}")
        st.stop()

# Prediction button
if st.button("Predict Cluster"):
    try:
        # Convert to array
        input_array = np.array([list(inputs.values())]).reshape(1, -1)

        input_scaled = scaler.transform(input_array)

        cluster_pred = kmeans_model.predict(input_scaled)[0]

        # Map cluster to original class
        class_pred = mapping.get(cluster_pred, "Unknown")

        st.success(f"✅ Predicted Cluster: {cluster_pred} → Original Wine Class: {class_pred}")

    except Exception as e:
        st.error(f"Prediction failed: {e}")
