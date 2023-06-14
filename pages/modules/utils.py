import base64
import time
import json
import io

import altair as alt
import pandas as pd
from pandas import json_normalize 
import requests
import streamlit as st
from st_pages import Page, hide_pages, show_pages
import logging
from unidecode import unidecode
import ast

logging.basicConfig(level=logging.ERROR)

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
            Page("pages/property_finder.py", "Viviendas"),
            Page("pages/zone_finder.py", "Zonas"),
            Page("pages/user_profile.py", "Menú de usuario"),
            Page("pages/calculator.py", "Calculadora"),
            Page("pages/property_statistics.py","Caracteristicas de la propiedad"),
            Page("pages/zone_statistics.py","Estadisticas de la zona"),
        ]
    )
    hide_pages(["Caracteristicas de la propiedad", "Estadisticas de la zona"])

    with open('style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


    set_background("images/background.jpg")
    add_logo("images/logo.png")
    # create a div of class content that will contain nothing
    st.markdown("<div class='content'></div>", unsafe_allow_html=True)

def filter_df_by_zones(df, zones):

    if not zones:
        return df
    selected_rows = []
    st.write(df.columns)
    for zone in zones:
        zone_rows = df.loc[df["Zona"] == zone]
        selected_rows.append(zone_rows)
        subzones = zone_rows["Subzonas"].unique()
        if len(subzones) > 0:
            selected_rows.append(filter_df_by_zones(df, subzones))

    return pd.concat(selected_rows).drop_duplicates().dropna()


def initialize_session_state():
    if "user_name" not in st.session_state: st.session_state["user_name"] = "Pepito Perez"
    if "email" not in st.session_state: st.session_state["email"] = "pepitus@gmail.com"
    if "age" not in st.session_state: st.session_state["age"] = "35"
    if "salary" not in st.session_state: st.session_state["salary"] = "1780"
    if "savings" not in st.session_state: st.session_state["savings"] = "35000"
    if "max_amount" not in st.session_state: st.session_state["max_amount"] = 1200000
    if "bank_name" not in st.session_state: st.session_state["bank_name"] = "Santander"
    if "fixed_interest" not in st.session_state: st.session_state["fixed_interest"] = 0.0523
    if "max_mortgage_age" not in st.session_state: st.session_state["max_mortgage_age"] = 80
    if "show_property" not in st.session_state: st.session_state["show_property"] = False
    if "show_zone" not in st.session_state: st.session_state["show_zone"] = False
    if "property_id" not in st.session_state: st.session_state["property_id"] = None
    if "property_url" not in st.session_state: st.session_state["property_url"] = None
    if "zone_city" not in st.session_state: st.session_state["zone_city"] = None
    if "zone_name" not in st.session_state: st.session_state["zone_name"] = None
    if "force_mortgage" not in st.session_state: st.session_state["force_mortgage"] = True
    if "autonomous_community" not in st.session_state: st.session_state["autonomous_community"] = "Extremadura"
    if "favorite_properties" not in st.session_state: 
        columns = ["Rentabilidad", "Precio", "Metros cuadrados", "Habitaciones", "Precio por m²", "Tipo", "Zona", "Ciudad", "Grupo inter-barrio", "Percentil de barrio", "Baños", "Antigüedad anuncio", "Planta", "Ascensor", "Balcón", "Terraza", "Calefacción", "Aire acondicionado", "Parking", "Piscina", "ITP", "Seguro", "IBI", "Comunidad", "Mantenimiento", "Gastos mensuales", "Cantidad a pagar", "Hipoteca total", "Hipoteca mensual", "Ingresos", "Titulo", "Enlace", "Identificacion"]
        st.session_state["favorite_properties"] = pd.DataFrame(columns=columns)
        
### Metodos usados para actualizar las propiedades en la DEMO copiados de Django.

def update_properties(properties, age, savings, max_age, interest_rate, autonomous_community):
    # remove all duplicates by url
    properties = properties.drop_duplicates(subset=['url'])
    # filter the properties by salary, currently disabled.
    # Filter the properties by the autonomous community, use check_community
    properties = community_filter(properties, autonomous_community)
    if properties.empty:
        return properties
    properties["amount_to_pay"] = properties.apply(lambda x: max(0, x["price"] - savings), axis=1)
    properties["total_mortgage"] = properties.apply(lambda x: total_mortgage(x, age, max_age, interest_rate, savings), axis=1)
    properties['monthly_mortgage'] = properties.apply(lambda x: mortgage(x, age, max_age, interest_rate), axis=1)
    properties['profitability'] = properties.apply(lambda x: profitability(x), axis=1)
    properties = properties.sort_values(by=['profitability'], ascending=False)
    

    return properties

def filter_by_mortgage(house, age, initial_amount):
    """Calculate the minimum amount required for a down payment based on the house price and the buyer's age"""
    if initial_amount < house["price"] * (0.2 + 0.015 * age):
        return False
    return True

def monthly_payment(amount, interest_rate, years):
    """Calculate the monthly payment for a mortgage based on the amount, interest rate, and number of years"""
    return max(0, (amount * (interest_rate / 12)) / (1 - (1 + interest_rate / 12) ** (-years * 12)))

def total_mortgage(house, age, max_age, interest_rate, savings):
    """Calculate the total mortgage payment for a house based on the amount left to pay, the buyer's age, and the interest rate"""
    years = min(abs(max_age - age), 30)
    return monthly_payment(house["amount_to_pay"], interest_rate, years) * 12 * years + savings

def mortgage(house, age, max_age, interest_rate):
    """Calculate the monthly mortgage payment for a house based on the amount left to pay, the buyer's age, and the interest rate"""
    years = min(abs(max_age - age), 30)
    return monthly_payment(house["amount_to_pay"], interest_rate, years)

def profitability(house):
    """Calculate the profitability of a house based on expected income, monthly mortgage payment, external costs, price, transfer taxes, and initial amount"""
    net_monthly_income = house['exp_income'] - (house['monthly_mortgage'] + house['ext_costs'])
    return net_monthly_income * 12 / (house["price"] + house["transfer_taxes"]) * 100

def community_filter(properties, autonomous_community):
    zones = get_zone_data_local()
    if zones.empty:
        # return an empty dataframe if there are no zones
        return pd.DataFrame()
    # now we have to get the list of all properties that are contained in these zones
    property_ids = [id for zone in zones['Propiedades'] for id in zone]
    properties = properties[properties['_id'].isin(property_ids)]
    
    properties["Comunidad Autónoma"] = autonomous_community

    return properties

def get_property_data_local():
    df = pd.read_csv("properties_statistics.csv")
    df.drop(columns=["Unnamed: 0"], inplace=True)
    
    df = update_properties(df, int(st.session_state["age"]), int(st.session_state["savings"]), st.session_state["max_mortgage_age"], st.session_state["fixed_interest"], st.session_state["autonomous_community"])
    if df.empty:
        return df
    df = df.rename(columns=property_translation)

    df = df[(df["Metros cuadrados"] != 0) & (df["Metros cuadrados"] < 1000)]
    df["Precio por m²"] = df["Precio"] / df["Metros cuadrados"]
    df = df.round(2)
    df = df[["Rentabilidad", "Precio", "Metros cuadrados", "Habitaciones", "Precio por m²", "Tipo", "Zona", 
             "Ciudad", "Comunidad Autónoma", "Grupo inter-barrio", "Percentil de barrio", "Baños", "Antigüedad anuncio", 
             "Planta", "Ascensor", "Balcón", "Terraza", "Calefacción", "Aire acondicionado", "Parking", 
             "Piscina", "ITP", "Seguro", "IBI", "Comunidad", "Mantenimiento", "Gastos mensuales", "Cantidad a pagar", 
             "Hipoteca total", "Hipoteca mensual", "Ingresos", "Titulo", "Enlace", "Identificacion", "DB ID", "ID zona"]]
    # replace all non-numeric values of "Planta" with 0
    df["Planta"] = df["Planta"].replace(to_replace=r'^\D+$', value=0, regex=True)
    df = df.apply(lambda col: pd.to_numeric(col, errors='ignore') if col.dtype == object else col)
    df["ID zona"] = df["ID zona"].astype(str)
    #df = df[df["Rentabilidad"] < 50]
    df = df[df["Precio"] < int(st.session_state["max_amount"])]
    return df

def get_property_data():
    url = 'http://localhost:8000/get_property_data'
    params = {'salary': st.session_state["salary"], 
              'age': st.session_state["age"], 
              'savings': st.session_state["savings"],
              'autonomous_community': st.session_state["autonomous_community"],
              'max_mortgage_age': st.session_state["max_mortgage_age"],
              'fixed_interest': st.session_state["fixed_interest"]
              }

    response = requests.get(url, params=params)
    data = json.loads(response.text)
    df = pd.DataFrame.from_dict(data, orient='index').T
    if df.empty: return df
    df.drop_duplicates(subset="url", inplace=True)
    df = df.rename(columns=property_translation)
    df = df.apply(lambda col: pd.to_numeric(col, errors='ignore') if col.dtype == object else col)
    
    # drop where metros cuadrados is 0
    df = df[df["Metros cuadrados"] != 0]
    df["Precio por m²"] = df["Precio"] / df["Metros cuadrados"]
    df = df.round(2)
    df = df[["Rentabilidad", "Precio", "Metros cuadrados", "Habitaciones", "Precio por m²", "Tipo", "Zona", 
             "Ciudad", "Grupo inter-barrio", "Percentil de barrio", "Baños", "Antigüedad anuncio", 
             "Planta", "Ascensor", "Balcón", "Terraza", "Calefacción", "Aire acondicionado", "Parking", 
             "Piscina", "ITP", "Seguro", "IBI", "Comunidad", "Mantenimiento", "Gastos mensuales", "Cantidad a pagar", 
             "Hipoteca total", "Hipoteca mensual", "Ingresos", "Titulo", "Enlace", "Identificacion", "DB ID", "ID zona"]]
    df = df.apply(lambda col: pd.to_numeric(col, errors='ignore') if col.dtype == object else col)
    # change ID zona to string in order to avoid reaching int64 limit
    df["ID zona"] = df["ID zona"].astype(str)
    #df = df[df["Rentabilidad"] < 50]
    df = df[df["Precio"] < int(st.session_state["max_amount"])]
    return df

def get_zone_data_local():
    df = pd.read_csv("zones_statistics.csv")

    df = df[df['autonomous_community'] == st.session_state["autonomous_community"]]
    if df.empty: return df
    df = df.drop(columns=["Unnamed: 0"])
    df = df.rename(columns=zone_translation)
    # Propiedades is a list but it is read as a string, so we have to convert it to a list
    df["Propiedades"] = df["Propiedades"].apply(lambda x: ast.literal_eval(x))
    df["Nombre Completo"] = df["Zona"] + ", " + df["Zona Principal"]
    df["Número de propiedades"] = df["Propiedades"].apply(lambda x: len(x))
    df = df.apply(lambda col: pd.to_numeric(col, errors='ignore') if col.dtype == object else col)
    df = df.round(2)
    df["Identificador"] = df["Identificador"].astype(str)
    df = df[df["Número de propiedades"] > 0]
    return df

def get_zone_data():
    # get the csv from doing a request to the django server
    url = 'http://localhost:8000/get_zone_data'
    params = {
        'autonomous_community': st.session_state["autonomous_community"],
    }
    response = requests.get(url, params=params)
    data = json.loads(response.text)
    df = pd.DataFrame.from_dict(data, orient='index').T
    df = df.rename(columns=zone_translation)
    df["Nombre Completo"] = df["Zona"] + ", " + df["Zona Principal"]
    df["Número de propiedades"] = df["Propiedades"].apply(lambda x: len(x))
    df = df.apply(lambda col: pd.to_numeric(col, errors='ignore') if col.dtype == object else col)
    df = df.round(2)
    # change Identificador to string
    df["Identificador"] = df["Identificador"].astype(str)
    df = df[df["Número de propiedades"] > 0]

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
    return sum(1 for row in dataset[column] if row == "Yes") / len(dataset[column])

def compare_commodities(name, col, df1, df2):
    val1, val2 = property_to_numeric(df1, col), property_to_numeric(df2, col)
    val1, val2 = int(val1 > 0.5), int(val2 > 0.5)
    
    st.metric(
        label=name,
        value="Sí" if val1 == 1 else "No",
        delta="Sí" if val2 == 1 else "No",
        delta_color="normal" if val1 != val2 else "off"
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

communities = {
    "Andalucía": "Andalucía", "Illes Balears": "Illes Balears",
    "Cantabria": "Cantabria", "Castilla y León": "Castilla y León",
    "Comunitat Valenciana": "Comunitat Valenciana", "Extremadura": "Extremadura",
    "Murcia": "Murcia", "País Vasco": "País Vasco"
}

property_translation = {
    "price": "Precio", "type": "Tipo", "title": "Titulo", "mobile": "Móvil",
    "address": "Zona", "city": "Ciudad", "Comunidad Autónoma": "Comunidad Autónoma", "age": "Antigüedad anuncio", "url": "Enlace", "rooms": "Habitaciones",
    "bathrooms": "Baños", "m2": "Metros cuadrados", "elevator": "Ascensor", "floor": "Planta", "balcony": "Balcón",
    "terrace": "Terraza", "heating": "Calefacción", "air_conditioning": "Aire acondicionado", "parking": "Parking",
    "pool": "Piscina", "id": "Identificacion", "itp": "ITP", "transfer_taxes": "Impuestos de transferencia",
    "insurance": "Seguro", "ibi": "IBI", "community": "Comunidad", "maintenance": "Mantenimiento",
    "ext_costs": "Gastos mensuales", "exp_income": "Ingresos", "group": "Grupo inter-barrio",
    "percentile": "Percentil de barrio", "amount_to_pay": "Cantidad a pagar", "total_mortgage": "Hipoteca total",
    "monthly_mortgage": "Hipoteca mensual", "profitability": "Rentabilidad", "_id": "DB ID", "zone": "ID zona"
}

zone_translation = {
    "name": "Zona", "parent_zone": "Zona Principal", "properties": "Propiedades", "id": "Identificador",
    "rent": "Alquiler", "sell": "Venta", "subzones": "Subzonas", "autonomous_community": "Comunidad Autónoma",
    "roi_sqm1rooms": "ROI m² 1 habitación", "roi_sqm3rooms": "ROI m² 3 habitaciones",
    "roi_sqm2rooms": "ROI m² 2 habitaciones", "roi_sqm4rooms": "ROI m² 4 habitaciones",
    "roi_terrace": "ROI Terraza", "roi_elevator": "ROI Ascensor",
    "roi_furnished": "ROI Amueblado", "roi_parking": "ROI Parking",
    "avg_roi": "ROI", "avg_price": "Precio medio", "avg_ppsqm": "Precio m²", "avg_rooms": "Habitaciones",
    "avg_bathrooms": "Baños", "avg_age": "Antigüedad anuncios", "avg_floor": "Planta media",
    "avg_itp": "ITP", "avg_insurance": "Seguro", "avg_ibi": "IBI", "avg_community": "Comunidad",
    "avg_maintenance": "Mantenimiento", "avg_exp_income": "Ingresos esperados", "avg_elevator": "Ascensor",
    "avg_balcony": "Balcón", "avg_terrace": "Terraza", "avg_heating": "Calefacción",
    "avg_air_conditioning": "Aire acondicionado", "avg_parking": "Parking", "avg_pool": "Piscina",
    "groups": "Tipos de vivienda por precio", "avg_m2": "m²", "avg_transfer_taxes": "Impuestos de transmisión",
    "avg_ext_costs": "Gastos mensuales"
}

sell_rent_translation = {
    'sqm1rooms': 'Precio m² habitación Individual', 'sqm3rooms': 'Precio m² 3 habitaciones', 'sqm2rooms': 'Precio m² 2 habitaciones', 'sqm4rooms': 'Precio m² 4 habitaciones', 'terrace': 'Terraza',
    'elevator': 'Ascensor', 'furnished': 'Amueblado', 'parking': 'Parking', 'avgsqm': 'Promedio de m²', 'avgtype': 'Tipo promedio de casa', 'avgrooms': 'Promedio de habitaciones', 
    'avgfloors': 'Número Piso Promedio', 'pricepersqm': 'Precio promedio m²', 'price': 'Precio promedio viviendas', 'b100': 'Precio menos de 100 m²', 'a100': 'Precio más de 100 m²',
}