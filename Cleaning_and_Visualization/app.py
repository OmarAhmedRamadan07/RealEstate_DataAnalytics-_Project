import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(page_title="NYC Real Estate Optimization", layout="wide")

# ==========================================
# 2. Data Loading with Error Handling
# ==========================================
@st.cache_data
def load_data():
    file_name = "airbnb_recommendations_report.csv"
    
    # Check if the file exists before trying to read it
    if not os.path.exists(file_name):
        st.error(f"🚨 Error: The file '{file_name}' was not found!")
        st.warning("Please make sure you uploaded the CSV file to the exact same folder as this app.py file on GitHub.")
        return None
        
    return pd.read_csv(file_name)

df = load_data()

# Only run the dashboard if the data is successfully loaded
if df is not None:
    
    # ==========================================
    # 3. Sidebar Filters
    # ==========================================
    st.sidebar.header("Filter Options")
    borough = st.sidebar.multiselect(
        "Select Borough", 
        options=df['neighbourhood_group'].unique(), 
        default=df['neighbourhood_group'].unique()
    )
    room = st.sidebar.multiselect(
        "Room Type", 
        options=df['room_type'].unique(), 
        default=df['room_type'].unique()
    )

    mask = df['neighbourhood_group'].isin(borough) & df['room_type'].isin(room)
    filtered_df = df[mask]

    # ==========================================
    # 4. Main Dashboard Title
    # ==========================================
    st.title("🏙️ NYC Real Estate Market Optimization")
    st.markdown("### Strategic Analysis & AI-Driven Recommendations")

    # ==========================================
    # 5. KPI Metrics (Top Row)
    # ==========================================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Listings", f"{len(filtered_df):,}")
    with col2:
        st.metric("Average Price", f"${filtered_df['price'].mean():.2f}")
    with col3:
        st.metric("Avg Reviews/Month", f"{filtered_df['reviews_per_month'].mean():.2f}")
    with col4:
        st.metric("Avg Occupancy Score", f"{filtered_df['occupancy_score'].mean():.1f}%")

    st.divider()

    # ==========================================
    # 6. Visualizations (Middle Row)
    # ==========================================
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Strategy Distribution")
        fig_pie = px.pie(
            filtered_df, 
            names='final_recommendation', 
            hole=0.4, 
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with right_col:
        st.subheader("Price Distribution by Borough")
        fig_box = px.box(
            filtered_df, 
            x="neighbourhood_group", 
            y="price", 
            color="neighbourhood_group"
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.divider()

    # ==========================================
    # 7. Listing Deep-Dive (Search specific apartment)
    # ==========================================
    st.header("🔍 Individual Listing Diagnosis")
    st.info("Search for a specific listing to see its performance issues and recommendations.")

    search_query = st.selectbox(
        "Select or Search for an Apartment Name:", 
        options=filtered_df['name'].unique()
    )

    if search_query:
        listing_data = filtered_df[filtered_df['name'] == search_query].iloc[0]
        
        d_col1, d_col2 = st.columns([1, 2])
        
        with d_col1:
            st.write(f"**Neighborhood:** {listing_data['neighbourhood']}")
            st.write(f"**Host:** {listing_data['host_name']}")
            st.write(f"**Price:** ${listing_data['price']}")
            st.write(f"**Min Nights:** {listing_data['minimum_nights']}")
            st.write(f"**Current Reviews:** {listing_data['number_of_reviews']}")
        
        with d_col2:
            st.subheader("Strategic Diagnosis")
            rec = listing_data['final_recommendation']
            
            # Highlighting the specific Problem and Solution
            if "Lower price" in rec:
                st.error(f"⚠️ **Problem:** Overpriced for its specific area.\n\n**Solution:** {rec}")
            elif "Reduce minimum nights" in rec:
                st.warning(f"⚠️ **Problem:** High entry barrier for short-stay guests.\n\n**Solution:** {rec}")
            elif "Improve listing" in rec:
                st.info(f"💡 **Opportunity:** Competitive price, but marketing is weak.\n\n**Solution:** {rec}")
            else:
                st.success(f"✅ **Performance:** This listing is performing optimally.\n\n**Status:** {rec}")
