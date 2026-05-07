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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "airbnb_recommendations_report.csv")
    
    if not os.path.exists(file_path):
        return None
        
    return pd.read_csv(file_path)

df = load_data()

if df is not None:
    # Calculate global averages to use as benchmarks for new listings
    global_avg_reviews = df['reviews_per_month'].mean()
    neighborhood_stats = df.groupby('neighbourhood_group')['price'].mean().to_dict()

    # ==========================================
    # 3. New Feature: AI Strategy Simulator (Input Form)
    # ==========================================
    st.sidebar.divider()
    st.sidebar.header("🏠 AI Listing Advisor")
    st.sidebar.write("Enter new listing details to get a strategy:")
    
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
    
    if submit_btn:
        st.header(f"📊 Strategy Diagnosis for: {new_name}")
        
        # Retrieve the average price for the selected borough (default to 100 if not found)
        avg_price_in_area = neighborhood_stats.get(new_borough, 100)
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.write(f"**Selected Borough:** {new_borough}")
            st.write(f"**Your Price:** ${new_price} (Area Avg: ${avg_price_in_area:.2f})")
            st.write(f"**Minimum Nights:** {new_nights}")
        
        with col_res2:
            if new_price > (avg_price_in_area * 1.2) and new_reviews < global_avg_reviews:
                st.error("⚠️ Problem: High Price. \n\n**Recommendation:** Lower your price to match the neighborhood average and increase demand.")
            elif new_nights > 3:
                st.warning("⚠️ Problem: High Entry Barrier. \n\n**Recommendation:** Reduce minimum nights to 1 or 2 to attract more short-stay travelers.")
            elif new_price <= avg_price_in_area and new_reviews < (global_avg_reviews * 0.5):
                st.info("💡 Opportunity: Price is Good, but engagement is low. \n\n**Recommendation:** Your price is competitive. Improve your photos and description to attract more bookings.")
            else:
                st.success("✅ Perfect Strategy! \n\n**Status:** Your listing parameters are optimal and highly competitive for the current market.")
        
        st.divider()

    # ==========================================
    # 5. Global Market Overview 
    # ==========================================
    st.subheader("📈 Market Overview (Based on 45,840 Listings)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.metric("Total Market Volume", f"{len(df):,}")
    with col2: 
        st.metric("Market Avg Price", f"${df['price'].mean():.2f}")
    with col3:
        st.metric("Avg Reviews/Month", f"{global_avg_reviews:.2f}")
    with col4:
        st.metric("Avg Occupancy Score", f"{df['occupancy_score'].mean():.1f}%")
    
    left_col, right_col = st.columns(2)

    with left_col:
        st.write("**Overall Market Strategy Distribution**")
        fig_pie = px.pie(
            df, 
            names='final_recommendation', 
            hole=0.4, 
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with right_col:
        st.write("**Price Distribution by Borough**")
        fig_box = px.box(
            df, 
            x="neighbourhood_group", 
            y="price", 
            color="neighbourhood_group"
        )
        st.plotly_chart(fig_box, use_container_width=True)

else:
    st.error("🚨 Error: The dataset file 'airbnb_recommendations_report.csv' was not found.")
