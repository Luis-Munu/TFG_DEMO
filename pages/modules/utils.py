import base64

import altair as alt
import pandas as pd
import streamlit as st
from st_pages import Page, hide_pages, show_pages


def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = ''' <style> .stApp {background-image: url("data:image/png;base64,%s");} </style> ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

def build_markup_for_logo(png_file):
    binary_string = get_base64_of_bin_file(png_file)
    return """<style> [data-testid="stSidebarNav"] {background-image: url("data:image/png;base64,%s");} </style>""" % (binary_string)

def add_logo(png_file):
    st.markdown(build_markup_for_logo(png_file), unsafe_allow_html=True)

def manage_css_style(title, icon, layout_type, sidebar_state):
    st.set_page_config(page_title=title, page_icon=icon, layout=layout_type, initial_sidebar_state=sidebar_state)

    show_pages(
        [
            Page("pages/website.py", "Inicio"),
            Page("pages/property_finder.py", "Buscador de viviendas"),
            Page("pages/zone_finder.py", "Análisis por zonas"),
            Page("pages/user_profile.py", "Menú de usuario"),
            Page("pages/property_statistics.py","Caracteristicas de la propiedad"),
            Page("pages/zone_statistics.py","Estadisticas de la zona"),
        ]
    )
    hide_pages(["Caracteristicas de la propiedad", "Estadisticas de la zona"])

    with open('style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


    set_background("images/mtrans.png")
    add_logo("images/logon.png")

def initialize_session_state():
    if "user_name" not in st.session_state: st.session_state["user_name"] = "Pepito Perez"
    if "email" not in st.session_state: st.session_state["email"] = "pepitus@gmail.com"
    if "age" not in st.session_state: st.session_state["age"] = "35"
    if "salary" not in st.session_state: st.session_state["salary"] = "1780"
    if "savings" not in st.session_state: st.session_state["savings"] = "35000"
    if "max_amount" not in st.session_state: st.session_state["max_amount"] = "120000"
    if "bank_name" not in st.session_state: st.session_state["bank_name"] = "Santander"
    if "fixed_interest" not in st.session_state: st.session_state["fixed_interest"] = 0.0523
    if "max_mortgage_age" not in st.session_state: st.session_state["max_mortgage_age"] = 80
    if "show_filters" not in st.session_state: st.session_state["show_filters"] = True
    if "show_property" not in st.session_state: st.session_state["show_property"] = False
    if "show_zone" not in st.session_state: st.session_state["show_zone"] = False
    if "property_id" not in st.session_state: st.session_state["property_id"] = None
    if "property_url" not in st.session_state: st.session_state["property_url"] = None
    if "zone_city" not in st.session_state: st.session_state["zone_city"] = None
    if "zone_name" not in st.session_state: st.session_state["zone_name"] = None
    if "force_mortgage" not in st.session_state: st.session_state["force_mortgage"] = True

@st.cache_data
def get_property_data():
    df = pd.read_csv("properties_statistics.csv")
    df = df.rename(columns=property_translation)
    df.drop(columns=["Unnamed: 0", "Identificador"], inplace=True)
    df = df.apply(lambda col: pd.to_numeric(col, errors='ignore') if col.dtype == object else col)
    df["Precio por m²"] = df["Precio"] / df["Metros cuadrados"] if df["Metros cuadrados"] != 0 else 0
    df = df.round(2)
    df = df[["Rentabilidad", "Precio", "Metros cuadrados", "Habitaciones", "Precio por m²", "Tipo", "Zona", "Ciudad", "Grupo inter-barrio", "Percentil de barrio", "Baños", "Antigüedad", "Piso", "Ascensor", "Balcón", "Terraza", "Calefacción", "Aire acondicionado", "Parking", "Piscina", "ITP", "Seguro", "IBI", "Comunidad", "Mantenimiento", "Costos", "Cantidad a pagar", "Hipoteca total", "Hipoteca mensual", "Ingresos", "Titulo", "Enlace", "Identificacion"]]
    return df

@st.cache_data
def get_zone_data():
    df = pd.read_csv("zones_statistics.csv")
    df = df.rename(columns=zone_translation)
    df = df.apply(lambda col: pd.to_numeric(col, errors='ignore') if col.dtype == object else col)
    df = df.round(2)
    return df

@st.cache_data
def get_chart(dataframe, column):
    chart = alt.Chart(dataframe).mark_bar().encode(
        x=alt.X("Identificacion:N", title="Identificacion",
            sort=alt.EncodingSortField(field=column, order="ascending")),
        y=alt.Y(column + ":Q", title=column),
        color=alt.condition(
            alt.datum["Identificacion"] == property["Identificacion"],
            alt.value("red"),
            alt.value("blue")
        )
    ).properties(
        width=600,
        height=300
    )
    return chart

@st.cache_data
def property_to_numeric(dataset, column):
    # Data is stored as Yes or No, we need to convert it to 1 or 0
    # iterate through all the rows
    counter = 0
    for row in dataset[column]:
        if row == "Yes":
            counter+=1
    return counter/len(dataset[column])

def compare_commodities(name, col, df1, df2):
    st.metric(
        label=name,
        value="Sí" if property_to_numeric(df1, col) > 0.5 else "No",
        delta="Sí" if property_to_numeric(df2, col) > 0.5 else "No"
    )

banks = {
        "Santander": {
                "name": "Santander",
                "interest_rate": 0.0523,
                "max_mortgage_age": 80
        }, 
        "Caixabank": {
                "name": "Caixabank",
                "interest_rate": 0.0516,
                "max_mortgage_age": 75
        },
        "Sabadell": {
                "name": "Sabadell",
                "interest_rate": 0.0496,
                "max_mortgage_age": 75
        },
        "Unicaja": {
                "name": "Unicaja",
                "interest_rate": 0.0444,
                "max_mortgage_age": 70
        },
        "Bankinter": {
                "name": "Bankinter",
                "interest_rate": 0.0508,
                "max_mortgage_age": 75
        },
        "Abanca": {
                "name": "Abanca",
                "interest_rate": 0.0574,
                "max_mortgage_age": 75
        },
        "Ibercaja": {
                "name": "Ibercaja",
                "interest_rate": 0.0452,
                "max_mortgage_age": 75
        },
        "BBVA": {
                "name": "BBVA",
                "interest_rate": 0.0447,
                "max_mortgage_age": 70
        }
}

property_translation = {
    "_id": "Identificador", "price": "Precio", "type": "Tipo", "title": "Titulo", "mobile": "Móvil",
    "address": "Zona", "city": "Ciudad", "age": "Antigüedad", "url": "Enlace", "rooms": "Habitaciones",
    "bathrooms": "Baños", "m2": "Metros cuadrados", "elevator": "Ascensor", "floor": "Piso", "balcony": "Balcón",
    "terrace": "Terraza", "heating": "Calefacción", "air_conditioning": "Aire acondicionado", "parking": "Parking",
    "pool": "Piscina", "id": "Identificacion", "transfer_taxes": "ITP","insurance": "Seguro", "ibi": "IBI", 
    "community": "Comunidad", "maintenance": "Mantenimiento", "costs": "Costos", "amount_to_pay": "Cantidad a pagar", 
    "total_mortgage": "Hipoteca total", "monthly_mortgage": "Hipoteca mensual", "incomes": "Ingresos", 
    "rentability": "Rentabilidad", "group": "Grupo inter-barrio", "percentile": "Percentil de barrio"
}

zone_translation = {
    "name": "Zona",
    "parent_zone": "Zona Principal",
    "Unnamed: 0": "Nombre Completo",
    "rent": "Alquiler",
    "sell": "Venta",
    "subzones": "Subzonas",
    "rentability_sqm1rooms": "Rentabilidad m² 1 habitación",
    "rentability_sqm3rooms": "Rentabilidad m² 3 habitaciones",
    "rentability_sqm2rooms": "Rentabilidad m² 2 habitaciones",
    "rentability_sqm4rooms": "Rentabilidad m² 4 habitaciones",
    "rentability_terrace": "Rentabilidad Terraza",
    "rentability_elevator": "Rentabilidad Ascensor",
    "rentability_furnished": "Rentabilidad Amueblado",
    "rentability_parking": "Rentabilidad Parking",
    "avg_rentability": "Rentabilidad Media",
    "groups": "Tipos de vivienda por precio"
}

sell_rent_translation = {
    'sqm1rooms': 'Precio m² habitación Individual', 'sqm3rooms': 'Precio m² 3 habitaciones', 'sqm2rooms': 'Precio m² 2 habitaciones', 'sqm4rooms': 'Precio m² 4 habitaciones', 'terrace': 'Terraza',
    'elevator': 'Ascensor', 'furnished': 'Amueblado', 'parking': 'Parking', 'avgsqm': 'Promedio de m²', 'avgtype': 'Tipo promedio de casa', 'avgrooms': 'Promedio de habitaciones', 
    'avgfloors': 'Número Piso Promedio', 'pricepersqm': 'Precio promedio m²', 'price': 'Precio promedio viviendas', 'b100': 'Precio menos de 100 m²', 'a100': 'Precio más de 100 m²',
}