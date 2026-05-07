import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(page_title="SUT - NYC Real Estate Analytics", layout="wide")

# ==========================================
# 2. Data Loading
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
    # --- Pre-calculations for benchmarks ---
    global_avg_reviews = df['reviews_per_month'].mean()
    neighborhood_stats = df.groupby('neighbourhood_group')['price'].mean().to_dict()

    # ==========================================
    # 3. TOP SECTION: Main Market Metrics (KPIs)
    # ==========================================
    st.title("🏙️ NYC Real Estate Market Optimization")
    st.markdown("### Market Summary Overview")
    
    # 6 Key Performance Indicators (KPIs) at the top
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        st.metric("Total Listings", f"{len(df):,}")
    with kpi2:
        st.metric("Market Avg Price", f"${df['price'].mean():.2f}")
    with kpi3:
        st.metric("Avg Reviews/Month", f"{global_avg_reviews:.2f}")
    with kpi4:
        st.metric("Occupancy Score", f"{df['occupancy_score'].mean():.1f}%")
    with kpi5:
        # Fixed: Showing the 5 main Boroughs instead of 219 small neighborhoods
        st.metric("Boroughs", f"{df['neighbourhood_group'].nunique()}")
    with kpi6:
        # Added: Showing the 3 Room Types
        st.metric("Room Types", f"{df['room_type'].nunique()}")

    st.divider()

    # ==========================================
    # 4. MIDDLE SECTION: Market Charts
    # ==========================================
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Strategy Distribution")
        fig_pie = px.pie(df, names='final_recommendation', hole=0.4, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart2:
        st.subheader("Price Range by Borough")
        fig_box = px.box(df, x="neighbourhood_group", y="price", color="neighbourhood_group")
        st.plotly_chart(fig_box, use_container_width=True)

    st.divider()

    # ==========================================
    # 5. BOTTOM SECTION: Advanced Filters & Search
    # ==========================================
    st.header("⚙️ Data Exploration & Criteria Selection")
    
    f1, f2, f3 = st.columns(3)
    
    with f1:
        selected_borough = st.multiselect("Borough Filter", 
                                          options=df['neighbourhood_group'].unique(), 
                                          default=df['neighbourhood_group'].unique())
    with f2:
        selected_room = st.multiselect("Room Type Filter", 
                                       options=df['room_type'].unique(), 
                                       default=df['room_type'].unique())
    with f3:
        price_range = st.slider("Price Range ($)", 
                                int(df['price'].min()), int(df['price'].max()), 
                                (int(df['price'].min()), int(df['price'].max())))

    filtered_df = df[
        (df['neighbourhood_group'].isin(selected_borough)) & 
        (df['room_type'].isin(selected_room)) &
        (df['price'].between(price_range[0], price_range[1]))
    ]

    st.success(f"Found {len(filtered_df):,} listings matching your selected criteria.")

    # ==========================================
    # 6. AI LISTING ADVISOR (For New Properties Only)
    # ==========================================
    st.divider()
    st.header("🤖 AI Listing Advisor (Simulator)")
    st.info("Simulate a new property listing to receive an instant, data-driven strategy based on current market averages.")
    
    # Input form for new properties only
    with st.form("new_listing_form"):
        c1, c2 = st.columns(2)
        with c1:
            in_name = st.text_input("Property Name", "My New Apartment")
            in_borough = st.selectbox("Target Borough", options=df['neighbourhood_group'].unique())
            in_price = st.number_input("Price per Night ($)", min_value=10, value=100)
        with c2:
            in_nights = st.number_input("Minimum Nights Required", min_value=1, value=1)
            in_reviews = st.number_input("Expected Monthly Reviews", min_value=0.0, value=1.0)
        
        submit = st.form_submit_button("Run AI Strategy Analysis")
        
        if submit:
            target_avg = neighborhood_stats.get(in_borough, 100)
            
            st.subheader(f"📊 Diagnosis for: '{in_name}'")
            
            # Recommendation Logic
            if in_price > (target_avg * 1.2):
                st.error(f"⚠️ **Problem:** Overpriced. Your price (${in_price}) is much higher than the '{in_borough}' average (${target_avg:.2f}). \n\n**Action:** Lower your price to increase bookings.")
            elif in_nights > 3:
                st.warning(f"⚠️ **Problem:** High Entry Barrier. Requiring {in_nights} minimum nights reduces visibility. \n\n**Action:** Reduce minimum nights to 1 or 2.")
            elif in_price <= target_avg and in_reviews < (global_avg_reviews * 0.5):
                st.info(f"💡 **Opportunity:** Competitive Price (${in_price}), but low engagement. \n\n**Action:** Improve listing photos and description to attract more guests.")
            else:
                st.success(f"✅ **Perfect Strategy:** Your price (${in_price}) and parameters are highly competitive for the '{in_borough}' market.")

else:
    st.error("🚨 Dataset not found. Please upload 'airbnb_recommendations_report.csv'.")
