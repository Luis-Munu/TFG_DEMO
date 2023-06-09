from urllib.error import URLError

import modules.utils as utils
import pandas as pd
import streamlit as st
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from streamlit_extras.switch_page_button import switch_page
from unidecode import unidecode

utils.manage_css_style("Estadisticas de la zona", "📈", "wide", "collapsed")

utils.initialize_session_state()

st.markdown("<h1 style='text-align: center; color: #000000;'>Estadisticas de la zona</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #000000;'><br><br>En esta página podrás analizar las Caracteristicas de una propiedad en detalle.</h1>", unsafe_allow_html=True)

try:
    # retrieve zone data and get the selected one, display an error if not found
    zones = utils.get_zone_data_local()
    properties = utils.get_property_data_local()

    # to get the zone, compare the zona and zona principal, also drop it from the rest of the zones
    #zone = zones.loc[(zones["Zona Principal"] == st.session_state["zone_city"]) & (zones["Zona"] == st.session_state["zone_name"])]
    zone = zones.loc[zones["Identificador"] == st.session_state["zone_id"]]
    if zone.empty:
        if st.button("Volver"):
            switch_page("Zonas")
        st.error("No se ha encontrado la zona seleccionada")

    zone = zone.iloc[0]

    st.markdown(f'### Zona seleccionada: **{zone["Nombre Completo"]}**')

    # get the properties of the zone and the parent zone
    parent_zone = zones.loc[zones["Zona"] == zone["Zona Principal"]]
    if not parent_zone.empty:
        parent_zone = parent_zone.iloc[0]
        if len(parent_zone["Propiedades"]) > 0:
            parent_properties = properties.loc[properties["DB ID"].isin(parent_zone["Propiedades"])]
        else: parent_properties = properties.copy()
    else:
        parent_zone = zone
        parent_properties = properties.copy()
    properties = properties.loc[properties["DB ID"].isin(zone["Propiedades"])]
        
    
    
    
    if properties.empty:
        st.error("No se han encontrado suficientes propiedades en la zona seleccionada")
        st.stop()
    
    # remove zone of zones
    zones = zones.loc[(zones["Zona Principal"] != st.session_state["zone_city"]) | (zones["Zona"] != st.session_state["zone_name"])]

    # display the primary attributes of the zone, comparing them with the rest of the zones
    st.write("Comparando la zona seleccionada con el resto de zonas de la ciudad:")
    # we are gonna calculate some statistics now, in essence, averages of certain metrics.
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_parent_price = float(parent_zone["Precio medio"])
        avg_price = float(zone["Precio medio"])
        st.metric(label="Precio medio", value="{:,.0f} €".format(avg_price).replace(",", "."), delta="{:,.0f} €".format(round(avg_price - avg_parent_price, 2)).replace(",", "."), delta_color="inverse")
            
    with col2:
        st.metric(label="ROI", value="{:,.0f} %".format(zone["ROI"]), delta="{:,.0f} %".format(round(zone["ROI"] - parent_zone["ROI"], 2)))
    with col3:
        avg_parent_ppsqm = float(parent_zone["Precio m²"])
        avg_ppsqm = float(zone["Precio m²"])
        st.metric(label="Precio medio por metro cuadrado", value="{:,.0f} €".format(round(avg_ppsqm, 2)).replace(",", "."), delta="{:,.0f} €".format((round(avg_ppsqm, 2) - avg_parent_ppsqm)).replace(",", "."), delta_color="inverse")
            
    with col4:
        st.metric(label="Metros cuadrados", value="{:,.0f} m²".format(float(zone["m²"])), delta="{:,.0f} m²".format(round(float(zone["m²"]) - float(parent_zone["m²"]), 2)))

    # secondary attributes
    with st.expander("Más detalles"):
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.markdown("##### Propiedades de las viviendas")
            st.metric(label="Número de propiedades", value="{:,.0f}".format(len(zone["Propiedades"])), delta="{:,.0f}".format(len(zone["Propiedades"]) - len(parent_zone["Propiedades"])))
            st.metric(label="Número de habitaciones medio", value="{:,.0f}".format(zone["Habitaciones"]), delta="{:,.0f}".format(zone["Habitaciones"] - parent_zone["Habitaciones"]))
            st.metric(label="Número de baños medio", value="{:,.0f}".format(zone["Baños"]), delta="{:,.0f}".format(zone["Baños"] - parent_zone["Baños"]))
            st.metric(label="Antigüedad media", value="{:,.0f} días".format(zone["Antigüedad anuncios"], delta="{:,.0f} días".format(zone["Antigüedad anuncios"] - parent_zone["Antigüedad anuncios"])), delta_color="inverse")
            st.metric(label="Número de plantas medio", value="{:,.0f}".format(zone["Planta media"]), delta="{:,.0f}".format(zone["Planta media"] - parent_zone["Planta media"]))
        
        with col2:
            st.markdown("##### Comodidades de las viviendas")
            utils.compare_commodities("Ascensor", "Ascensor", properties, parent_properties)
            utils.compare_commodities("Balcón", "Balcón", properties, parent_properties)
            utils.compare_commodities("Terraza", "Terraza", properties, parent_properties)
            utils.compare_commodities("Calefacción", "Calefacción", properties, parent_properties)
            utils.compare_commodities("Aire acondicionado", "Aire acondicionado", properties, parent_properties)
        with col3:
            st.write(""); st.write(""); st.write(""); st.write("")
            utils.compare_commodities("Parking", "Parking", properties, parent_properties)
            utils.compare_commodities("Piscina", "Piscina", properties, parent_properties)
            avg_parent_price = float(parent_zone["Precio medio"])
            avg_price = float(zone["Precio medio"])
            st.metric(label="Nivel del barrio", value="Bajo" if avg_price < avg_parent_price * 0.6 else "Medio" if avg_price < avg_parent_price * 1.3 else "Alto", delta="")
        with col4:
            st.markdown("##### Media impuestos")
            st.metric(label="ITP", value="{:,.0f} €".format(float(zone["ITP"])), delta="{:,.0f} €".format(float(zone["ITP"]) - float(parent_zone["ITP"])), help="Impuesto de transmisiones patrimoniales, varía según la comunidad autónoma entre un 4% y un 10%")
            st.metric(label="Seguro", value="{:,.0f} €".format(float(zone["Seguro"])), delta="{:,.0f} €".format(float(zone["Seguro"]) - float(parent_zone["Seguro"])), help="Seguro de hogar, varía según la compañía y la vivienda")
            st.metric(label="IBI", value="{:,.0f} €".format(float(zone["IBI"])), delta="{:,.0f} €".format(float(zone["IBI"]) - float(parent_zone["IBI"])), help="Impuesto de bienes inmuebles, se situa entre un 0.4% y un 1.3% según la vivienda")
        with col5:
            st.markdown("##### Media gastos anuales")
            st.metric(label="Comunidad", value="{:,.0f} €".format(float(zone["Comunidad"])), delta="{:,.0f} €".format(float(zone["Comunidad"]) - float(parent_zone["Comunidad"])), help="Gastos de comunidad de vecinos")
            st.metric(label="Mantenimiento", value="{:,.0f} €".format(float(zone["Mantenimiento"])), delta="{:,.0f} €".format(float(zone["Mantenimiento"]) - float(parent_zone["Mantenimiento"])), help="Gastos de mantenimiento de la vivienda")
            st.metric(label="Total con impuestos", value="{:,.0f} €".format(float(zone["Gastos mensuales"])*12), delta="{:,.0f} €".format(float(zone["Gastos mensuales"])*12 - float(parent_zone["Gastos mensuales"])*12))
        with col6:
            st.markdown("##### Alquiler medio")
            st.metric(label="Ingresos", value="{:,.0f} €".format(float(zone["Ingresos esperados"])), delta="{:,.0f} €".format(float(zone["Ingresos esperados"]) - float(parent_zone["Ingresos esperados"])))
            
    
    with st.expander("Mapa de la zona"):
        st.write(zone["Nombre Completo"])
        location = zone["Zona"] + ", " + zone["Zona Principal"].replace(" Capital", "").replace(" Provincia", "") + ", España"

        geolocator = Nominatim(user_agent='mytfg')
        try:
            geocode = RateLimiter(geolocator.geocode, min_delay_seconds=3)
            loc = geolocator.geocode(location)
            #st.write(loc)
            lat, lon = loc.latitude, loc.longitude
            #st.write('Latitude = {}, Longitude = {}'.format(lat, lon))
            df = pd.DataFrame({'lat': [lat], 'lon': [lon]})
            st.map(df)
        except:
            st.error('Location not found')
            st.stop()


    if st.button("Volver"):
        switch_page("Zonas")


except URLError as e:
    st.error(
        """
        This demo requires internet access.
        Connection error: %s
    """
        % e.reason
    )
