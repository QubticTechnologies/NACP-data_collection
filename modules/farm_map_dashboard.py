# census_app/modules/farm_map_dashboard.py

import streamlit as st
import pandas as pd
import pydeck as pdk
from sqlalchemy import text
from census_app.db import engine

def farm_map_dashboard(user_id=None, role="holder"):
    """
    Display an interactive farm map for a holder or admin.
    - For holder: shows only their holdings.
    - For admin: shows all holdings with owner info.
    """
    st.header("🌾 Farm Map Dashboard")

    # --- Fetch holdings data ---
    try:
        with engine.connect() as conn:
            if role == "admin":
                holdings = conn.execute(
                    text("""
                        SELECT h.holder_id, h.name AS holder_name, h.latitude, h.longitude,
                               g.holding_name, g.legal_status
                        FROM holders h
                        LEFT JOIN general_information g ON h.holder_id = g.holder_id
                        WHERE h.latitude IS NOT NULL AND h.longitude IS NOT NULL
                    """)
                ).mappings().fetchall()
            else:
                holdings = conn.execute(
                    text("""
                        SELECT h.holder_id, h.name AS holder_name, h.latitude, h.longitude,
                               g.holding_name, g.legal_status
                        FROM holders h
                        LEFT JOIN general_information g ON h.holder_id = g.holder_id
                        WHERE h.owner_id=:uid AND h.latitude IS NOT NULL AND h.longitude IS NOT NULL
                    """), {"uid": user_id}
                ).mappings().fetchall()
    except Exception as e:
        st.warning(f"Could not load holdings: {e}")
        holdings = []

    if not holdings:
        st.info("No holdings with coordinates found. Showing default map.")
        df_map = pd.DataFrame([[25.0343, -77.3963, "Default Location"]], columns=["lat", "lon", "label"])
        st.map(df_map[["lat", "lon"]])
        return

    # --- Prepare DataFrame ---
    df = pd.DataFrame(holdings)
    df["lat"] = pd.to_numeric(df["latitude"])
    df["lon"] = pd.to_numeric(df["longitude"])
    df["label"] = df.apply(lambda x: f"{x['holder_name']} ({x['holding_name'] or 'No Holding'})", axis=1)

    # --- PyDeck Layer ---
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon, lat]',
        get_color='[200, 30, 0, 160]',
        get_radius=500,
        pickable=True
    )

    # --- PyDeck View ---
    view_state = pdk.ViewState(
        longitude=df["lon"].mean(),
        latitude=df["lat"].mean(),
        zoom=7,
        pitch=0
    )

    # --- Deck ---
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "text": "{label}\nLegal Status: {legal_status}"
        }
    )

    st.pydeck_chart(r)

    # --- Holdings Table ---
    st.subheader("🏠 Holdings Details")
    display_df = df[["holder_name", "holding_name", "lat", "lon", "legal_status"]]
    st.dataframe(display_df, use_container_width=True)
