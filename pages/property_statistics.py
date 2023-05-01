from urllib.error import URLError

import modules.utils as utils
import pandas as pd
import streamlit as st
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from streamlit_extras.switch_page_button import switch_page

utils.manage_css_style("Caracteristicas de la propiedad", "📈", "wide", "collapsed")

utils.initialize_session_state()

st.markdown("<h1 style='text-align: center; color: #ff9900;'>Caracteristicas de la propiedad</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ff9900;'><br><br>En esta página podrás analizar las Caracteristicas de una propiedad en detalle.</h1>", unsafe_allow_html=True)

try:
    # Retrieve property and zone data, filter property based on identifier, and display error if not found
    properties = utils.get_property_data()
    zones = utils.get_zone_data()

    property = properties[properties["Identificacion"] == st.session_state["property_id"]]
    if property.empty:
        st.error("No se ha encontrado la vivienda")
        st.stop()
    property = property.iloc[0]

    # Get the properies of the zone.
    st.markdown(f"## {property['Titulo']}")
    st.markdown("<a style='color: #ff9900;' href='{}' target='_blank'>Ver propiedad</a>".format(st.session_state["property_url"]), unsafe_allow_html=True)
    zone = zones[(zones["Zona"] == property["Zona"]) & (zones["Zona Principal"] == property["Ciudad"])].iloc[0]
    zone_properties = properties[(properties["Zona"] == property["Zona"]) & (properties["Ciudad"] == property["Ciudad"])]
    zone_properties = zone_properties[zone_properties["Identificacion"] != property["Identificacion"]]

    # Compare property with zone, primary attributes
    st.write("Comparación de la vivienda con la media de la zona")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        st.metric("Rentabilidad", value = "{:,.0f} %".format(property["Rentabilidad"]), delta = "{:,.0f} %".format(property["Rentabilidad"] - zone_properties["Rentabilidad"].mean().round(2)))
    with col2:
        st.metric("Precio", value = "{:,.0f} €".format(property["Precio"]), delta = "{:,.0f} €".format(property["Precio"] - zone_properties["Precio"].mean().round(2)), delta_color = "inverse")
    with col3:
        st.metric("Metros cuadrados", value = "{:,.0f} m²".format(property["Metros cuadrados"]), delta = "{:,.0f} m²".format(property["Metros cuadrados"] - zone_properties["Metros cuadrados"].mean().round(2)))
    with col4:
        st.metric("Habitaciones", value = "{:,.0f}".format(property["Habitaciones"]), delta = "{:,.0f}".format(property["Habitaciones"] - zone_properties["Habitaciones"].mean().round(2)))

    # Secondary attributes
    with st.expander("Más detalles"):

            col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

            with col1:
                st.write("Características de la vivienda")
                st.metric("Precio por m²", value = "{:,.0f} €".format(property["Precio por m²"]), delta = "{:,.0f} €".format(property["Precio por m²"] - zone_properties["Precio por m²"].mean().round(2)), delta_color = "inverse")
                st.metric("Baños", value = "{:,.0f}".format(property["Baños"]), delta = "{:,.0f}".format(property["Baños"] - zone_properties["Baños"].mean().round(2)))
                st.metric("Antigüedad", value = "{:,.0f} días".format(property["Antigüedad"]), delta = "{:,.0f} días".format(property["Antigüedad"] - zone_properties["Antigüedad"].mean().round(2)), delta_color = "inverse")
                st.metric("Piso", value = "{:,.0f}".format(property["Piso"]), delta = "{:,.0f}".format(property["Piso"] - zone_properties["Piso"].mean().round(2)), delta_color = "inverse")
            
            with col2:
                st.write("Comodidades")
                st.metric("Ascensor :elevator:", value = property["Ascensor"])
                st.metric("Balcón ☀️", value = property["Balcón"])
                st.metric("Terraza 🏡", value = property["Terraza"])
                st.metric("Calefacción 🛢️", value = property["Calefacción"])
                st.metric("Aire acondicionado 🌶️", value = property["Aire acondicionado"])

            with col3:
                st.write(""); st.write(""); st.write("")
                st.metric("Parking 🚗", value = property["Parking"])
                st.metric("Piscina 🏊‍♂️", value = property["Piscina"])
                st.metric("Zona del barrio", value = property["Grupo inter-barrio"])
                st.metric("Percentil en el barrio", value = property["Percentil de barrio"])
                
            with col4:
                st.write("Impuestos")
                st.metric("ITP", value = "{:,.0f} €".format(property["ITP"]), delta = "{:,.0f} €".format(property["ITP"] - zone_properties["ITP"].mean().round(2)).replace(",", "."), delta_color = "inverse", help="Impuesto de transmisiones patrimoniales, varía según la comunidad autónoma entre un 4% y un 10%")
                st.metric("Seguro", value = "{:,.0f} €".format(property["Seguro"]), delta = "{:,.0f} €".format(property["Seguro"] - zone_properties["Seguro"].mean().round(2)).replace(",", "."), delta_color = "inverse", help="Seguro de hogar, varía según la compañía y la vivienda")
                st.metric("IBI", value = "{:,.0f} €".format(property["IBI"]), delta = "{:,.0f} €".format(property["IBI"] - zone_properties["IBI"].mean().round(2)).replace(",", "."), delta_color = "inverse", help="Impuesto de bienes inmuebles, se situa entre un 0.4% y un 1.3% según la vivienda")
                
            with col5:
                st.write("Costos anuales")
                st.metric("Comunidad", value = "{:,.0f} €".format(property["Comunidad"]), delta = "{:,.0f} €".format(property["Comunidad"] - zone_properties["Comunidad"].mean().round(2)).replace(",", "."), delta_color = "inverse", help="Gastos de comunidad de vecinos")
                st.metric("Mantenimiento", value = "{:,.0f} €".format(property["Mantenimiento"]), delta = "{:,.0f} €".format(property["Mantenimiento"] - zone_properties["Mantenimiento"].mean().round(2)).replace(",", "."), delta_color = "inverse", help="Gastos de mantenimiento de la vivienda")
                st.metric("Otros costos", value = "{:,.0f} €".format(property["Costos"]), delta = "{:,.0f} €".format(property["Costos"] - zone_properties["Costos"].mean().round(2)).replace(",", "."), delta_color = "inverse")
            with col6:
                st.write("Entradas y salidas")
                st.metric("Cantidad a pagar", value = "{:,.0f} €".format(property["Cantidad a pagar"]), delta = "{:,.0f} €".format(property["Cantidad a pagar"] - zone_properties["Cantidad a pagar"].mean().round(2)).replace(",", "."), delta_color = "inverse", help="Cantidad a pagar por la vivienda una vez descontada la inversión inicial")
                st.metric("Hipoteca total", value = "{:,.0f} €".format(property["Hipoteca total"]), delta = "{:,.0f} €".format(property["Hipoteca total"] - zone_properties["Hipoteca total"].mean().round(2)).replace(",", "."), delta_color = "inverse")
                st.metric("Hipoteca mensual", value = "{:,.0f} €".format(property["Hipoteca mensual"]), delta = "{:,.0f} €".format(property["Hipoteca mensual"] - zone_properties["Hipoteca mensual"].mean().round(2)).replace(",", "."), delta_color = "inverse")
                st.metric("Ingresos", value = "{:,.0f} €".format(property["Ingresos"]), delta = "{:,.0f} €".format(property["Ingresos"] - zone_properties["Ingresos"].mean().round(2)).replace(",", "."))

    # Calculadora del inversor
    with st.expander("Calculadora del inversor"):
        st.write("Esta calculadora te permite estimar la rentabilidad de una inversión en una vivienda.")
        column1, column2 = st.columns(2)
        with column1:
            field1, field2 = st.columns(2)
            years = field1.slider("Años de hipoteca", 1, 30, min(25, 80 - int(st.session_state["age"])), 1)
            salary = field2.number_input("Salario", 0.0, 100000.0, float(st.session_state["salary"]), 100.0)
        with column2:
            field1, field2 = st.columns(2)
            savings = field1.number_input("Ahorros", 0.0, 1000000.0, float(st.session_state["savings"]), 100.0)
            interest_rate = field2.slider("Interés esperado", 0.0, 0.2, float(st.session_state["fixed_interest"]), 0.01)

        field1, field2, field3 = st.columns(3)
        building_cost = field1.slider("Gasto de obra", 0.0, 100000.0, 0.0, 100.0)
        furnishing_cost =  field2.slider("Gasto de puesta a punto", 0.0, 30000.0, 0.0, 100.0)
        rent = field3.slider("Alquiler esperado", 0.0, float(property["Ingresos"] * 3), float(property["Ingresos"]), 25.0)
            
        field1, field2, field3 = st.columns(3)
        expenses = field1.slider("Gastos anuales previstos", 0.0, 
                                    float(property["Comunidad"] + property["Mantenimiento"] + property["Costos"]) * 3, 
                                    float(property["Comunidad"] + property["Mantenimiento"] + property["Costos"]), 
                                    10.0)
        itp = field2.slider("ITP", 0.01, 0.15, 0.08, 0.01)
        ibi = field3.slider("IBI", 0.01, 0.15, 0.04, 0.01)

        if st.button("Forzar hipoteca"):
            st.session_state["force_mortgage"] = not st.session_state["force_mortgage"]

        column1, column2, column3 = st.columns(3)

        with column1:
            buy_expenses = building_cost + furnishing_cost + (property["Precio"] * itp) + (property["Precio"] * ibi) + property["Precio"]
            mortgage = max(0, buy_expenses - savings)
            if st.session_state["force_mortgage"]:
                mortgage = max(buy_expenses * 0.2, mortgage)
            mortgage_quota = (mortgage * (interest_rate / 12)) / (1 - (1 + interest_rate / 12) ** (-years * 12))
            quota = mortgage_quota + (property["Comunidad"] + property["Mantenimiento"] + property["Costos"] + property["Seguro"] + property["IBI"]) / 12
            st.metric("Inversión total de compra y preparación", value = "{:,.0f} €".format(buy_expenses).replace(",", "."))

        with column2:
            col1, col2 = st.columns(2)
            col1.metric("Cuota mensual con gastos", value = "{:,.0f} €".format(quota).replace(",", "."))
            total_mortgage = mortgage_quota * years * 12
            col2.metric("Hipoteca total", value = "{:,.0f} €".format(total_mortgage).replace(",", "."))

        with column3:
            col1, col2 = st.columns(2)
            col1.metric("Porcentaje del salario", value = "{:,.0f} %".format((quota / salary) * 100).replace(",", "."))
            net_profit = (rent * 12) - quota - expenses
            net_profit_rate = (net_profit / buy_expenses) * 100
            col2.metric("Rentabilidad neta", value = "{:,.2f} %".format(net_profit_rate).replace(",", "."))


    with st.expander("Mapa de la zona"):
        st.write(property["Ciudad"])
        location = property["Zona"] + ", " + property["Ciudad"].replace(" Capital", "").replace(" Provincia", "") + ", España"

        geolocator = Nominatim(user_agent='mytfg')
        try:
            geocode = RateLimiter(geolocator.geocode, min_delay_seconds=3)
            loc = geolocator.geocode(location)
            st.write(loc)
            lat, lon = loc.latitude, loc.longitude
            st.write('Latitude = {}, Longitude = {}'.format(lat, lon))
            df = pd.DataFrame({'lat': [lat], 'lon': [lon]})
            st.map(df)
        except:
            st.error('Location not found')
            st.stop()



    if st.button("Volver al buscador de viviendas"):
        switch_page("Buscador de viviendas")

        

except URLError as e:
    st.error(
        """
        This demo requires internet access.
        Connection error: %s
    """
        % e.reason
    )
