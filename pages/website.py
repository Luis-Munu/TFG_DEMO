import streamlit as st
from PIL import Image
import modules.utils as utils

utils.manage_css_style("InversApp", "🏠", "wide", "expanded")

utils.initialize_session_state()

st.markdown("<h1 style='text-align: center; color: #ff9900;'>¡Bienvenido a InversApp!</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ff9900;'><br><br>InversApp te ofrece las mejores herramientas de análisis y búsqueda de propiedades para invertir.</h1>", unsafe_allow_html=True)

# Background images and logo
image = Image.open('images/logon.png')
st.image(image, use_column_width=True)

property_finder_text = "Buscador de propiedades: Encuentra propiedades en función de tus criterios."
property_statistics_text = "Estadisticas de propiedad: Analiza los datos clave de una propiedad seleccionada."
zone_finder_text = "Estadisticas de zona: Descubre valiosa información de múltiples localizaciones."
user_data_text = "Datos del usuario: Gestiona tus datos, preferencias y propiedades favoritas."

left_col, right_col = st.columns(2)

left_col.markdown(f"- **{property_finder_text}**")
left_col.markdown(f"- **{property_statistics_text}**")

right_col.markdown(f"- **{zone_finder_text}**")
right_col.markdown(f"- **{user_data_text}**")

# add some empty space
st.markdown("<br> </br>", unsafe_allow_html=True)
