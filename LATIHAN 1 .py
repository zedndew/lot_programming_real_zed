import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, Point, LineString, mapping
import json
import os
import folium 
from streamlit_folium import folium_static 
from pyproj import Transformer

# Set page configuration
st.set_page_config(page_title="Sistem Survey Lot PUO", page_icon="🔐", layout="wide")

# ================== CSS CUSTOM (AESTHETIC & PETAK KECIK) ==================
def local_css():
    st.markdown("""
        <style>
        .stApp { background-color: #1b1714 !important; }
        header, footer { visibility: hidden; }
        
        /* Container untuk kotak login supaya jadi petak kecik */
        .login-card {
            background-color: #2c2420;
            padding: 35px;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.6);
            border: 1px solid #3d332d;
            text-align: center;
        }

        /* Input & Button Styling */
        div[data-baseweb="input"] { background-color: #3d332d !important; border-radius: 10px !important; }
        input { color: #dcd0c0 !important; }
        label { color: #a89081 !important; font-weight: bold !important; }
        
        .stButton > button {
            background-color: #634e42 !important;
            color: white !important;
            border-radius: 10px !important;
            height: 3.5em !important;
            width: 100% !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ================== FUNGSI ASAL (DMS & DIALOG) ==================
def format_dms(decimal_degree):
    d = int(decimal_degree)
    m = int((decimal_degree - d) * 60)
    s = round((((decimal_degree - d) * 60) - m) * 60, 0)
    return f"{d}°{abs(m):02d}'{abs(int(s)):02d}\""

@st.dialog("🔑 Kemaskini Kata Laluan")
def reset_password_dialog():
    st.info("Sila sahkan ID untuk menetapkan semula kata laluan.")
    id_sah = st.text_input("Sahkan ID Pengguna:")
    pass_baru = st.text_input("Kata Laluan Baharu:", type="password")
    pass_sah = st.text_input("Sahkan Kata Laluan Baharu:", type="password")
    if st.button("Simpan Kata Laluan", use_container_width=True):
        if id_sah == "zed" and pass_baru == pass_sah and pass_baru != "":
            st.success("✅ Kata laluan berjaya dikemaskini!")
            st.rerun()
        else:
            st.error("❌ Maklumat tidak sepadan.")

def check_password():
    if "password_correct" not in st.session_state:
        local_css()
        # Gunakan columns untuk buat petak login jadi kecik kat tengah
        _, col_mid, _ = st.columns([1, 1.2, 1])
        with col_mid:
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            st.markdown("""
                <img src="https://cdn-icons-png.flaticon.com/512/6195/6195696.png" width="70">
                <h2 style="color: #dcd0c0;">Sistem Survey Lot PUO</h2>
                <p style="color: #a89081;">Log masuk untuk mulakan tugasan</p>
            """, unsafe_allow_html=True)
            
            user_id = st.text_input("ID Pengguna", key="user_id")
            password = st.text_input("Kata Laluan", type="password", key="user_pass")
            
            if st.button("Log Masuk", use_container_width=True):
                if user_id == "zed" and password == "admin123":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("😕 ID atau Kata Laluan salah.")
            
            if st.button("❓ Lupa Kata Laluan?", use_container_width=True):
                reset_password_dialog()
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# ================== MAIN APP (KOD ASAL PENUH 100%) ==================
if check_password():
    # Unlock background asal
    st.markdown("""<style>.stApp { background-color: #ffffff !important; } header {visibility: visible;}</style>""", unsafe_allow_html=True)

    # --- 👤 PROFIL PENGGUNA (SIDEBAR) ---
    st.sidebar.markdown(
        """
        <div style="background: linear-gradient(135deg, #634e42, #3d332d); padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; border: 1px solid #8a6d5d;">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="80" style="border-radius: 50%; border: 3px solid #dcd0c0;">
            <h3 style="color: white; margin-top: 10px;">Hai, Zed!</h3>
            <p style="color: #dcd0c0; font-size: 0.8em;">Surveyor Berdaftar</p>
        </div>
        """, unsafe_allow_html=True
    )

    # --- HEADER UTAMA ---
    col_logo, col_text = st.columns([1.2, 4])
    with col_logo:
        if os.path.exists("Poli_Logo.png"):
            st.image("Poli_Logo.png", width=180)
        else:
            st.warning("⚠️ Logo 'Poli_Logo.png' tidak dijumpai.")

    with col_text:
        st.markdown("""
            <style>
                .main-title { font-family: 'Arial Black'; font-size: 50px; font-weight: 900; line-height: 1; color: #1b1714; }
                .sub-title { font-size: 18px; color: #555; }
            </style>
            <div>
                <h1 class="main-title">SISTEM SURVEY LOT</h1>
                <p class="sub-title">Politeknik Ungku Omar | Jabatan Kejuruteraan Awam</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)

    # ================== SIDEBAR SETTINGS (ASAL) ==================
    st.sidebar.header("⚙️ Tetapan Paparan")
    uploaded_file = st.sidebar.file_uploader("Upload fail CSV", type=["csv"])

    st.sidebar.markdown("---")
    show_interactive_map = st.sidebar.toggle("On/Off Peta Satelit", value=False)
    map_provider = st.sidebar.radio("Pilih Jenis Peta:", ["Satelit (Hybrid)", "Standard Map"], disabled=not show_interactive_map)

    st.sidebar.markdown("---")
    poly_color = st.sidebar.color_picker("Warna Kawasan (Poligon)", "#6036AF") 
    line_color = st.sidebar.color_picker("Warna Garisan Sempadan", "#FFFF00") 
    poly_opacity = st.sidebar.slider("Kelegapan Kawasan", 0.0, 1.0, 0.3)

    st.sidebar.markdown("---")
    plot_theme = st.sidebar.selectbox("Tema Warna Pelan Matplotlib", ["Light Mode", "Dark Mode", "Blueprint"])
    show_bg_grid = st.sidebar.checkbox("Papar Grid Latar", value=True)
    grid_interval = st.sidebar.slider("Jarak Selang Grid", 5, 50, 10)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🖋️ Gaya Label")
    show_luas_label = st.sidebar.checkbox("Papar Label LUAS", value=True)
    label_size_stn = st.sidebar.slider("Saiz Bulatan Stesen", 15, 30, 22) 
    label_size_data = st.sidebar.slider("Saiz Bearing/Jarak", 5, 12, 7)
    label_size_luas = st.sidebar.slider("Saiz Tulisan LUAS", 8, 30, 14) 
    dist_offset = st.sidebar.slider("Jarak Label Stesen ke Luar", 0.5, 5.0, 1.5)

    # ================== BACA DATA & PENGIRAAN (ASAL) ==================
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if all(col in df.columns for col in ['STN', 'E', 'N']):
                
                # Transformer koordinat
                transformer = Transformer.from_crs("EPSG:4390", "EPSG:4326", always_xy=True)
                df['lon'], df['lat'] = transformer.transform(df['E'].values, df['N'].values)
                
                coords_en = list(zip(df['E'], df['N']))
                coords_ll = list(zip(df['lon'], df['lat']))
                poly_geom = Polygon(coords_en)
                poly_ll = Polygon(coords_ll) 
                line_geom = LineString(coords_en + [coords_en[0]])
                centroid_m = poly_geom.centroid
                area = poly_geom.area

                # Eksport QGIS
                geojson_dict = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": mapping(poly_ll), "properties": {"Area_sqm": round(area, 2)}}]}
                st.sidebar.download_button(label="🚀 Export to QGIS (.geojson)", data=json.dumps(geojson_dict), file_name="survey_lot.geojson", mime="application/json", use_container_width=True)

                # Metrik
                st.markdown("### 📊 Ringkasan Lot")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Luas (m²)", f"{area:.2f}")
                col2.metric("Luas (Ekar)", f"{area/4046.856:.4f}")
                col3.metric("Bilangan Stesen", len(df))
                col4.metric("Status", "Tutup" if poly_geom.is_valid else "Ralat")

                st.markdown("---")

                if show_interactive_map:
                    # Logic Folium
                    google_map_url = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}' if map_provider == "Satelit (Hybrid)" else 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}'
                    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=20, max_zoom=22, tiles=google_map_url, attr='Google')
                    points_map = [[r['lat'], r['lon']] for _, r in df.iterrows()]
                    folium.Polygon(locations=points_map, color=line_color, weight=3, fill=True, fill_color=poly_color, fill_opacity=poly_opacity).add_to(m)
                    
                    for i in range(len(df)):
                        p1 = df.iloc[i]
                        folium.Marker([p1['lat'], p1['lon']], icon=folium.DivIcon(html=f'<div style="background-color: white; border: 2px solid red; border-radius: 50%; width: 20px; height: 20px; text-align: center; font-weight: bold;">{int(p1["STN"])}</div>')).add_to(m)
                    
                    folium_static(m, width=900, height=550)

                else:
                    # Logic Matplotlib
                    if plot_theme == "Dark Mode": bg_color, grid_color = "#121212", "#555555"
                    elif plot_theme == "Blueprint": bg_color, grid_color = "#003366", "#004080"
                    else: bg_color, grid_color = "#ffffff", "#aaaaaa"

                    fig, ax = plt.subplots(figsize=(10, 8))
                    fig.patch.set_facecolor(bg_color); ax.set_facecolor(bg_color)
                    ax.plot(*(line_geom.xy), linewidth=2, color=line_color, zorder=4)
                    ax.fill(*(poly_geom.exterior.xy), color=poly_color, alpha=poly_opacity)

                    if show_bg_grid:
                        ax.grid(True, color=grid_color, linestyle='--', alpha=0.5)
                        ax.xaxis.set_major_locator(plt.MultipleLocator(grid_interval))
                        ax.yaxis.set_major_locator(plt.MultipleLocator(grid_interval))

                    if show_luas_label:
                        ax.text(centroid_m.x, centroid_m.y, f"{area:.2f} m²", fontsize=label_size_luas, fontweight='bold', color='darkgreen', ha='center', bbox=dict(boxstyle='round', fc='white', alpha=0.9), zorder=10)

                    for i in range(len(df)):
                        p1, p2 = df.iloc[i], df.iloc[(i + 1) % len(df)]
                        dE, dN = p2['E'] - p1['E'], p2['N'] - p1['N']
                        dist, bear = np.sqrt(dE**2 + dN**2), (np.degrees(np.arctan2(dE, dN)) + 360) % 360
                        txt_angle = np.degrees(np.arctan2(dN, dE))
                        if txt_angle > 90: txt_angle -= 180
                        elif txt_angle < -90: txt_angle += 180
                        ax.text((p1['E']+p2['E'])/2, (p1['N']+p2['N'])/2, f"{format_dms(bear)}\n{dist:.2f}m", fontsize=label_size_data, color='brown', fontweight='bold', ha='center', rotation=txt_angle)
                        ax.scatter(p1['E'], p1['N'], color='white', edgecolor='red', s=300, zorder=5)
                        ax.text(p1['E'], p1['N'], str(int(p1['STN'])), fontsize=label_size_stn/2, color='black', fontweight='bold', ha='center', va='center')

                    ax.set_aspect("equal"); st.pyplot(fig)

                st.subheader("📋 Jadual Data Koordinat")
                st.dataframe(df[['STN', 'E', 'N', 'lat', 'lon']], use_container_width=True)

            else: st.error("❌ Kolum STN, E, N tak jumpa dalam CSV!")
        except Exception as e: st.error(f"❌ Ada ralat: {e}")
