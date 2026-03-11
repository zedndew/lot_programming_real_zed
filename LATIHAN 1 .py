import streamlit as st
import pd as pd
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

# ================== CSS CUSTOM (AESTHETIC & STABLE CENTER) ==================
def local_css():
    st.markdown("""
        <style>
        /* Tetapan latar belakang global */
        .stApp {
            background-color: #1b1714 !important;
        }

        /* Hilangkan header dan footer asal Streamlit */
        header, footer {visibility: hidden;}
        
        /* Container untuk kotak login */
        .login-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding-top: 50px;
        }

        /* Kotak Login (Card) */
        .login-card {
            background-color: #2c2420;
            padding: 40px;
            border-radius: 25px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.6);
            border: 1px solid #3d332d;
            width: 100%;
            max-width: 450px;
            text-align: center;
            margin-bottom: 20px;
        }

        /* Styling Input Box */
        div[data-baseweb="input"] {
            background-color: #3d332d !important;
            border-radius: 12px !important;
            border: 1px solid #5a4a42 !important;
        }
        
        input {
            color: #dcd0c0 !important;
        }

        /* Styling Butang */
        .stButton > button {
            background-color: #634e42 !important;
            color: #f5f5f5 !important;
            border-radius: 12px !important;
            border: none !important;
            height: 3.5em !important;
            font-weight: bold !important;
            width: 100% !important;
            transition: 0.4s !important;
        }
        
        .stButton > button:hover {
            background-color: #8a6d5d !important;
            border: 1px solid #dcd0c0 !important;
            transform: translateY(-2px);
        }

        /* Teks dan Tajuk */
        h2 { color: #dcd0c0 !important; font-family: 'Arial', sans-serif; margin-bottom: 10px; }
        p { color: #a89081 !important; }
        label { color: #a89081 !important; font-weight: bold !important; }
        
        /* Hilangkan ruang kosong berlebihan di atas */
        .block-container {
            padding-top: 2rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

local_css()

# ================== FUNGSI TUKAR DMS ==================
def format_dms(decimal_degree):
    d = int(decimal_degree)
    m = int((decimal_degree - d) * 60)
    s = round((((decimal_degree - d) * 60) - m) * 60, 0)
    return f"{d}°{abs(m):02d}'{abs(int(s)):02d}\""

# ================== FUNGSI LOGIN & KEMASKINI ==================
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
        # Menggunakan columns untuk centering secara horizontal
        _, col_mid, _ = st.columns([1, 1.5, 1])
        
        with col_mid:
            st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
            st.markdown("""
                <div class="login-card">
                    <img src="https://cdn-icons-png.flaticon.com/512/6195/6195696.png" width="80">
                    <h2>Sistem Survey Lot PUO</h2>
                    <p>Sila masukkan kredential anda</p>
                </div>
            """, unsafe_allow_html=True)
            
            user_id = st.text_input("ID Pengguna", key="user_id", placeholder="Contoh: zed")
            password = st.text_input("Kata Laluan", type="password", key="user_pass", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
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

# ================== MAIN APP (SELEPAS LOGIN) ==================
if check_password():
    # Override CSS untuk main app supaya putih/cerah balik atau ikut tema asal
    st.markdown("""<style>.stApp { background-color: #ffffff !important; }</style>""", unsafe_allow_html=True)

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
            <div>
                <h1 style="font-family: 'Arial Black'; font-size: 45px; margin-bottom: -10px;">SISTEM SURVEY LOT</h1>
                <p style="font-size: 18px; color: #555;">Politeknik Ungku Omar | Jabatan Kejuruteraan Awam</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    # ================== SIDEBAR SETTINGS ==================
    st.sidebar.header("⚙️ Tetapan Paparan")
    uploaded_file = st.sidebar.file_uploader("Upload fail CSV", type=["csv"])

    st.sidebar.markdown("---")
    show_interactive_map = st.sidebar.toggle("On/Off Peta Satelit", value=False)
    map_provider = st.sidebar.radio("Pilih Jenis Peta:", ["Satelit (Hybrid)", "Standard Map"], disabled=not show_interactive_map)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Pilihan Warna")
    poly_color = st.sidebar.color_picker("Warna Kawasan", "#6036AF") 
    line_color = st.sidebar.color_picker("Warna Sempadan", "#FFFF00") 
    poly_opacity = st.sidebar.slider("Kelegapan", 0.0, 1.0, 0.3)

    plot_theme = st.sidebar.selectbox("Tema Matplotlib", ["Light Mode", "Dark Mode", "Blueprint"])
    show_bg_grid = st.sidebar.checkbox("Papar Grid", value=True)
    grid_interval = st.sidebar.slider("Jarak Grid", 5, 50, 10)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🖋️ Gaya Label")
    show_luas_label = st.sidebar.checkbox("Papar Label LUAS", value=True)
    label_size_stn = st.sidebar.slider("Saiz Stesen", 15, 30, 22) 
    label_size_data = st.sidebar.slider("Saiz Data", 5, 12, 7)
    label_size_luas = st.sidebar.slider("Saiz Luas", 8, 30, 14) 

    # ================== BACA DATA ==================
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if all(col in df.columns for col in ['STN', 'E', 'N']):
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
                geojson_dict = {
                    "type": "FeatureCollection",
                    "features": [{
                        "type": "Feature",
                        "geometry": mapping(poly_ll),
                        "properties": {"Area_sqm": round(area, 2), "Stations": len(df)}
                    }]
                }
                st.sidebar.download_button(label="🚀 Export to QGIS", data=json.dumps(geojson_dict), file_name="survey_lot.geojson", mime="application/json", use_container_width=True)

                # Metrik
                st.markdown("### 📊 Ringkasan Lot")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Luas (m²)", f"{area:.2f}")
                c2.metric("Luas (Ekar)", f"{area/4046.856:.4f}")
                c3.metric("Stesen", len(df))
                c4.metric("Status", "Tutup" if poly_geom.is_valid else "Ralat")

                st.markdown("---")

                if show_interactive_map:
                    google_url = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}' if map_provider == "Satelit (Hybrid)" else 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}'
                    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=20, tiles=google_url, attr='Google')
                    points = [[r['lat'], r['lon']] for _, r in df.iterrows()]
                    folium.Polygon(locations=points, color=line_color, fill=True, fill_color=poly_color, fill_opacity=poly_opacity).add_to(m)
                    
                    if show_luas_label:
                        folium.Marker([df['lat'].mean(), df['lon'].mean()], icon=folium.DivIcon(html=f'<div style="font-size: {label_size_luas}pt; color: white; font-weight: bold; text-shadow: 2px 2px 4px black;">{area:.2f} m²</div>')).add_to(m)
                    folium_static(m, width=900, height=550)
                else:
                    if plot_theme == "Dark Mode": bg, gr = "#121212", "#555"
                    elif plot_theme == "Blueprint": bg, gr = "#003366", "#004080"
                    else: bg, gr = "#ffffff", "#aaa"

                    fig, ax = plt.subplots(figsize=(10, 8))
                    fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
                    ax.plot(*(line_geom.xy), color=line_color, linewidth=2)
                    ax.fill(*(poly_geom.exterior.xy), color=poly_color, alpha=poly_opacity)
                    if show_bg_grid: ax.grid(True, color=gr, linestyle='--')
                    
                    if show_luas_label:
                        ax.text(centroid_m.x, centroid_m.y, f"{area:.2f} m²", fontsize=label_size_luas, fontweight='bold', ha='center', bbox=dict(boxstyle='round', fc='white', ec='green'))
                    
                    for i in range(len(df)):
                        p1 = df.iloc[i]
                        ax.scatter(p1['E'], p1['N'], color='white', edgecolor='red', s=200, zorder=5)
                        ax.text(p1['E'], p1['N'], str(int(p1['STN'])), fontsize=label_size_stn/2, ha='center', va='center', fontweight='bold')
                    
                    ax.set_aspect("equal"); st.pyplot(fig)

                st.dataframe(df[['STN', 'E', 'N', 'lat', 'lon']], use_container_width=True)
            else: st.error("❌ Kolum STN, E, N tidak dijumpai.")
        except Exception as e: st.error(f"❌ Ralat: {e}")
