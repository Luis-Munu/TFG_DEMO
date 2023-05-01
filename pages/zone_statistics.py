from urllib.error import URLError

import modules.utils as utils
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
import pandas as pd

utils.manage_css_style("Estadisticas de la zona", "📈", "wide", "collapsed")

utils.initialize_session_state()

st.markdown("<h1 style='text-align: center; color: #ff9900;'>Estadisticas de la zona</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ff9900;'><br><br>En esta página podrás analizar las Caracteristicas de una propiedad en detalle.</h1>", unsafe_allow_html=True)

try:
    # retrieve zone data and get the selected one, display an error if not found
    zones = utils.get_zone_data()
    properties = utils.get_property_data()

    # to get the zone, compare the zona and zona principal, also drop it from the rest of the zones
    zone = zones.loc[(zones["Zona Principal"] == st.session_state["zone_city"]) & (zones["Zona"] == st.session_state["zone_name"])]
    if zone.empty:
        if st.button("Volver al buscador de viviendas"):
            switch_page("Buscador de viviendas")
        st.error("No se ha encontrado la zona seleccionada")

    zone = zone.iloc[0]

    st.markdown(f'### Zona seleccionada: **{zone["Nombre Completo"]}**')

    # get the properties of the zone
    parent_properties = properties.loc[properties["Ciudad"] == zone["Zona Principal"]]
    properties = parent_properties.loc[parent_properties["Zona"] == zone["Zona"]]
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
        avg_parent_price = parent_properties["Precio"].mean()
        avg_price = properties["Precio"].mean()
        st.metric(label="Precio medio", value="{:,.0f} €".format(avg_price).replace(",", "."), delta="{:,.0f} €".format((avg_price - avg_parent_price).round(2)).replace(",", "."), delta_color="inverse" if avg_price < avg_parent_price else "normal")
    
    with col2:
        st.metric(label="Rentabilidad Media", value="{:,.0f} %".format(zone["Rentabilidad Media"]), delta="{:,.0f} %".format((zone["Rentabilidad Media"] - zones["Rentabilidad Media"].mean()).round(2)))
    
    with col3:
        avg_parent_ppsqm = parent_properties.apply(lambda row: 0 if row["Precio"] == 0 or row["Metros cuadrados"] == 0 
                                                   else row["Precio"] / row["Metros cuadrados"], axis=1).mean()

        avg_ppsqm = properties.apply(lambda row: 0 if row["Precio"] == 0 or row["Metros cuadrados"] == 0
                                                    else row["Precio"] / row["Metros cuadrados"], axis=1).mean()
        st.metric(label="Precio medio por metro cuadrado", value="{:,.0f} €".format(avg_ppsqm).replace(",", "."), delta="{:,.0f} €".format((avg_ppsqm - avg_parent_ppsqm).round(2)).replace(",", "."), delta_color="inverse" if avg_ppsqm < avg_parent_ppsqm else "normal")
    
    with col4:
        st.metric(label="Metros cuadrados", value="{:,.0f} m²".format(properties["Metros cuadrados"].mean()), delta="{:,.0f} m²".format((properties["Metros cuadrados"].mean() - parent_properties["Metros cuadrados"].mean()).round(2)))

    # secondary attributes
    with st.expander("Más detalles"):
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.write("Propiedades de las viviendas")
            st.metric(label="Número de propiedades", value="{:,.0f}".format(properties["Precio"].count()), delta="{:,.0f}".format(properties["Precio"].count() - parent_properties["Precio"].count()))
            st.metric(label="Número de habitaciones medio", value="{:,.0f}".format(properties["Habitaciones"].mean()), delta="{:,.0f}".format(properties["Habitaciones"].mean() - parent_properties["Habitaciones"].mean()))
            st.metric(label="Número de baños medio", value="{:,.0f}".format(properties["Baños"].mean()), delta="{:,.0f}".format(properties["Baños"].mean() - parent_properties["Baños"].mean()))
            st.metric(label="Antigüedad media", value="{:,.0f} años".format(properties["Antigüedad"].mean()), delta="{:,.0f} años".format(properties["Antigüedad"].mean() - parent_properties["Antigüedad"].mean()))
            st.metric(label="Número de plantas medio", value="{:,.0f}".format(properties["Piso"].mean()), delta="{:,.0f}".format(properties["Piso"].mean() - parent_properties["Piso"].mean()))
        with col2:
            st.write("Comodidades de las viviendas")
            utils.compare_commodities("Ascensor", "Ascensor", properties, parent_properties)
            utils.compare_commodities("Balcón", "Balcón", properties, parent_properties)
            utils.compare_commodities("Terraza", "Terraza", properties, parent_properties)
            utils.compare_commodities("Calefacción", "Calefacción", properties, parent_properties)
            utils.compare_commodities("Aire acondicionado", "Aire acondicionado", properties, parent_properties)
        with col3:
            st.write(""); st.write(""); st.write("")
            utils.compare_commodities("Parking", "Parking", properties, parent_properties)
            utils.compare_commodities("Piscina", "Piscina", properties, parent_properties)
            avg_parent_price = parent_properties["Precio"].mean()
            avg_price = properties["Precio"].mean()
            st.metric(label="Nivel del barrio", value="Bajo" if avg_price < avg_parent_price * 0.33 else "Medio" if avg_price < avg_parent_price * 0.66 else "Alto", delta="")
        with col4:
            st.write("Impuestos")
            st.metric(label="ITP", value="{:,.0f} €".format(properties["ITP"].mean()), delta="{:,.0f} €".format(properties["ITP"].mean() - parent_properties["ITP"].mean()))
            st.metric(label="Seguro", value="{:,.0f} €".format(properties["Seguro"].mean()), delta="{:,.0f} €".format(properties["Seguro"].mean() - parent_properties["Seguro"].mean()))
            st.metric(label="IBI", value="{:,.0f} €".format(properties["IBI"].mean()), delta="{:,.0f} €".format(properties["IBI"].mean() - parent_properties["IBI"].mean()))
        with col5:
            st.write("Costos anuales")
            st.metric(label="Comunidad", value="{:,.0f} €".format(properties["Comunidad"].mean()), delta="{:,.0f} €".format(properties["Comunidad"].mean() - parent_properties["Comunidad"].mean()))
            st.metric(label="Mantenimiento", value="{:,.0f} €".format(properties["Mantenimiento"].mean()), delta="{:,.0f} €".format(properties["Mantenimiento"].mean() - parent_properties["Mantenimiento"].mean()))
            st.metric(label="Otros costos", value="{:,.0f} €".format(properties["Costos"].mean()), delta="{:,.0f} €".format(properties["Costos"].mean() - parent_properties["Costos"].mean()))
        with col6:
            st.write("Alquiler medio")
            st.metric(label="Ingresos", value="{:,.0f} €".format(properties["Ingresos"].mean()), delta="{:,.0f} €".format(properties["Ingresos"].mean() - parent_properties["Ingresos"].mean()))
    
    with st.expander("Mapa de la zona"):
        st.write(zone["Nombre Completo"])
        location = zone["Zona"] + ", " + zone["Zona Principal"].replace(" Capital", "").replace(" Provincia", "") + ", España"

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
