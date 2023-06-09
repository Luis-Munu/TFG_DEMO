import modules.utils as utils
import streamlit as st
from PIL import Image

utils.manage_css_style("InversApp", "🏠", "wide", "expanded")

utils.initialize_session_state()

import streamlit as st
from PIL import Image

# Create a container with a semi-transparent background
st.markdown("<h1 style='text-align: center; color: #000000;'>¡Bienvenido a InversApp!</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #000000;'>La mejor herramienta de búsqueda y análisis de propiedades para invertir.</h3>", unsafe_allow_html=True)
st.image(Image.open('images/logo.png'), use_column_width=True)

property_finder_text = "Buscador de propiedades: Encuentra propiedades en función de tus criterios."
property_statistics_text = "Estadisticas de propiedad: Analiza los datos clave de una propiedad seleccionada."
zone_finder_text = "Estadisticas de zona: Descubre valiosa información de múltiples localizaciones."
user_data_text = "Datos del usuario: Gestiona tus datos, preferencias y propiedades favoritas."

first_col, second_col, third_col, forth_col = st.columns(4)

first_col.markdown(f"**{property_finder_text}**")
second_col.markdown(f"**{property_statistics_text}**")
third_col.markdown(f"**{zone_finder_text}**")
forth_col.markdown(f"**{user_data_text}**")

# Add some empty space
st.markdown("<br> </br>", unsafe_allow_html=True)
