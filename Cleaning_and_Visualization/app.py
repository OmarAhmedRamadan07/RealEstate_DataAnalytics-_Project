import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(page_title="SUT - Real Estate AI Advisor", layout="wide")

# ==========================================
# 2. Data Loading & Benchmarking
# ==========================================
@st.cache_data
def load_data():
    # Force the app to look for the CSV file in the same directory as this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "airbnb_recommendations_report.csv")
    
    if not os.path.exists(file_path):
        return None
        
    return pd.read_csv(file_path)

df = load_data()

# Proceed only if the dataset is successfully loaded
if df is not None:
    # Calculate global averages to use as benchmarks for new listings
    global_avg_reviews = df['reviews_per_month'].mean()
    
    # Calculate the average price per specific neighborhood group
    neighborhood_stats = df.groupby('neighbourhood_group')['price'].mean().to_dict()

    # ==========================================
    # 3. New Feature: AI Strategy Simulator (Input Form)
    # ==========================================
    st.sidebar.divider()
    st.sidebar.header("🏠 AI Listing Advisor")
    st.sidebar.write("Enter new listing details to get a strategy:")
    
    # Form to collect new property parameters from the user
    with st.sidebar.form("prediction_form"):
        new_name = st.text_input("Listing Name", "Cozy Apartment")
        new_borough = st.selectbox("Borough", options=df['neighbourhood_group'].unique())
        new_price = st.number_input("Price per Night ($)", min_value=10, max_value=1000, value=100)
        new_nights = st.number_input("Minimum Nights", min_value=1, max_value=30, value=1)
        new_reviews = st.number_input("Expected Reviews/Month", value=1.0)
        
        submit_btn = st.form_submit_button("Analyze Listing")

    # ==========================================
    # 4. Main Dashboard Header
    # ==========================================
    st.title("🏙️ NYC Real Estate Market Optimization")
    
    # Execute the diagnosis logic if the user submits the form
    if submit_btn:
        st.header(f"📊 Strategy Diagnosis for: {new_name}")
        
        # Retrieve the average price for the selected borough (default to 100 if not found)
        avg_price_in_area = neighborhood_stats.get(new_borough, 1
