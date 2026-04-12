import streamlit as st
import joblib

# Load model
model = joblib.load("model.pkl")
le_drug = joblib.load("le_drug.pkl")
le_side = joblib.load("le_side.pkl")

st.title("💊 MediPredict - Side Effect Predictor")

st.write("Enter a medicine name to predict possible side effects")

# Input box
drug = st.text_input("Medicine Name")

if st.button("Predict"):
    try:
        drug_encoded = le_drug.transform([drug])
        prediction = model.predict([drug_encoded])
        side_effect = le_side.inverse_transform(prediction)

        st.success(f"Predicted Side Effect: {side_effect[0]}")

    except:
        st.error("Invalid medicine name or not in dataset")
