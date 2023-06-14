import time
from urllib.error import URLError

import modules.utils as utils
import pandas as pd
import streamlit as st
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from streamlit_extras.switch_page_button import switch_page
from unidecode import unidecode

utils.manage_css_style("Caracteristicas de la propiedad", "📈", "wide", "collapsed")

utils.initialize_session_state()


try:
    st.markdown("<h1 style='text-align: center; color: #000000;'>Caracteristicas de la propiedad</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #000000;'><br><br>En esta página podrás analizar las Caracteristicas de una propiedad en detalle.</h1>", unsafe_allow_html=True)

    # Retrieve property and zone data, filter property based on identifier, and display error if not found
    properties = utils.get_property_data_local()
    zones = utils.get_zone_data_local()

    property = properties[properties["DB ID"] == st.session_state["property_id"]]
    if property.empty or zones.empty:
        st.error("No se ha encontrado la vivienda")
        st.stop()
    property = property.iloc[0]
    
    
    # Get the properies of the zone. on the right of this first markdown, add a button with the shape of a heart. When clicked, add the property to the favorites list
    coltitle, colheart = st.columns([10, 1])
    with coltitle:
        st.markdown(f"## {property['Titulo']}")
    with colheart:
        if st.button("❤️"):
            # add row to favorite properties in session state pandas dataset
            # also show a message that the property has been added to favorites and make the message fade over 3 seconds
            if "favorite_properties" in st.session_state and not st.session_state["favorite_properties"].empty:
                if "DB ID" not in st.session_state["favorite_properties"].columns:
                    st.session_state["favorite_properties"] = st.session_state["favorite_properties"].append(property)
                    alert = st.warning("Propiedad añadida a favoritos")
                elif property["DB ID"] not in st.session_state["favorite_properties"]["DB ID"].values:
                    st.session_state["favorite_properties"] = st.session_state["favorite_properties"].append(property)
                    alert = st.warning("Propiedad añadida a favoritos")
                else:
                    alert = st.warning("Propiedad ya añadida a favoritos")
            else:
                st.session_state["favorite_properties"] = st.session_state["favorite_properties"].append(property)
                alert = st.warning("Propiedad añadida a favoritos")
            
            
            time.sleep(3)
            alert.empty()
    st.markdown("<a style='color: #000000; font-weight: bold;' href='{}' target='_blank'>Ver anuncio</a>".format(st.session_state["property_url"]), unsafe_allow_html=True)
    #st.write(property["Zona"], ", ", property["Ciudad"])
    #zone_id = unidecode(property["Zona"] + ", " + property["Ciudad"])
    #zone = zones[zones["Nombre Completo"].apply(lambda x: unidecode(x)) == zone_id].iloc[0]
    zone = zones[zones["Identificador"] == property["ID zona"]].iloc[0]
    
    # This is necessary to calculate the average profitability of the zone
    zone_properties = properties[(properties["Zona"] == property["Zona"]) & (properties["Ciudad"] == property["Ciudad"])]
    if len(zone_properties) > 1: zone_properties = zone_properties[zone_properties["Identificacion"] != property["Identificacion"]]
    property = property.apply(pd.to_numeric, errors='ignore')
    # Compare property with zone, primary attributes
    st.write("Comparación de la vivienda con la media de la zona")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        st.metric("Rentabilidad", value = "{:,.0f} %".format(property["Rentabilidad"]), delta = "{:,.0f} %".format(property["Rentabilidad"] - zone_properties["Rentabilidad"].mean().round(2)))
    with col2:
        st.metric("Precio", value = "{:,.0f} €".format(property["Precio"]), delta = "{:,.0f} €".format(property["Precio"] - zone["Precio medio"]), delta_color = "inverse")
    with col3:
        st.metric("Metros cuadrados", value = "{:,.0f} m²".format(property["Metros cuadrados"]), delta = "{:,.0f} m²".format(property["Metros cuadrados"] - zone_properties["Metros cuadrados"].mean().round(2)))
    with col4:
        st.metric("Habitaciones", value="{:,.0f}".format(int(property["Habitaciones"])), delta="{:,.0f}".format(int(property["Habitaciones"] - zone["Habitaciones"])))

    # Secondary attributes
    with st.expander("Más detalles"):

            col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

            with col1:
                st.markdown("##### Características de la vivienda")
                st.metric("Precio por m²", value = "{:,.0f} €".format(property["Precio por m²"]), delta = "{:,.0f} €".format(property["Precio por m²"] - zone["Precio m²"]), delta_color = "inverse")
                st.metric("Baños", value = "{:,.0f}".format(property["Baños"]), delta = "{:,.0f}".format(property["Baños"] - zone["Baños"]))
                st.metric("Antigüedad anuncio", value = "{:,.0f} días".format(property["Antigüedad anuncio"]), delta = "{:,.0f} días".format(property["Antigüedad anuncio"] - zone["Antigüedad anuncios"]), delta_color = "inverse")
                st.metric("Planta", value = "{:,.0f}".format(property["Planta"]), delta = "{:,.0f}".format(property["Planta"] - zone["Planta media"]), delta_color = "inverse")
            
            with col2:
                st.markdown("##### Comodidades")
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
                st.markdown("##### Impuestos")
                st.metric("ITP", value = "{:,.0f} €".format(property["ITP"]), delta = "{:,.0f} €".format(property["ITP"] - zone["ITP"]).replace(",", "."), delta_color = "inverse", help="Impuesto de transmisiones patrimoniales, varía según la comunidad autónoma entre un 4% y un 10%")
                st.metric("Seguro", value = "{:,.0f} €".format(property["Seguro"]), delta = "{:,.0f} €".format(property["Seguro"] - zone["Seguro"]).replace(",", "."), delta_color = "inverse", help="Seguro de hogar, varía según la compañía y la vivienda")
                st.metric("IBI", value = "{:,.0f} €".format(property["IBI"]), delta = "{:,.0f} €".format(property["IBI"] - zone["IBI"]).replace(",", "."), delta_color = "inverse", help="Impuesto de bienes inmuebles, se situa entre un 0.4% y un 1.3% según la vivienda")
                
            with col5:
                st.markdown("##### Gastos anuales")
                st.metric("Comunidad", value = "{:,.0f} €".format(property["Comunidad"]), delta = "{:,.0f} €".format(property["Comunidad"] - zone_properties["Comunidad"].mean().round(2)).replace(",", "."), delta_color = "inverse", help="Gastos de comunidad de vecinos")
                st.metric("Mantenimiento", value = "{:,.0f} €".format(property["Mantenimiento"]), delta = "{:,.0f} €".format(property["Mantenimiento"] - zone_properties["Mantenimiento"].mean().round(2)).replace(",", "."), delta_color = "inverse", help="Gastos de mantenimiento de la vivienda")
                st.metric("Total con impuestos", value = "{:,.0f} €".format(property["Gastos mensuales"]*12), delta = "{:,.0f} €".format(property["Gastos mensuales"]*12 - zone["Gastos mensuales"]*12).replace(",", "."), delta_color = "inverse", help= "Suma de mantenimiento, comunidad, IBI y seguro")
            with col6:
                st.markdown("##### Entradas y salidas")
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
            salary = field2.number_input("Salario", 0.1, 100000.0, float(st.session_state["salary"]), 100.0)
        with column2:
            field1, field2 = st.columns(2)
            savings = field1.number_input("Ahorros", 0.1, 1000000.0, float(st.session_state["savings"]), 100.0)
            interest_rate = field2.slider("Interés esperado", 0.1, 0.2, float(st.session_state["fixed_interest"]), 0.01)

        field1, field2, field3 = st.columns(3)
        building_cost = field1.slider("Gasto de obra", 0.1, 100000.0, 0.1, 100.0)
        furnishing_cost =  field2.slider("Gasto de puesta a punto", 0.1, 30000.0, 0.1, 100.0)
        rent = field3.slider("Alquiler esperado", 0.1, float(property["Ingresos"] * 3), float(property["Ingresos"]), 25.0)
            
        field1, field2, field3 = st.columns(3)
        expenses = field1.slider("Gastos anuales previstos", 0.1, 
                                    float(property["Seguro"] + property["IBI"] + property["Comunidad"] + property["Mantenimiento"]) * 3, 
                                    float(property["Seguro"] + property["IBI"] + property["Comunidad"] + property["Mantenimiento"]), 
                                    10.0)
        itp = field2.slider("ITP", 0.01, 0.15, 0.08, 0.01)
        ibi = field3.slider("IBI", 0.01, 0.15, 0.04, 0.01)
        ibi = ibi /10

        if st.button("Forzar hipoteca"):
            st.session_state["force_mortgage"] = not st.session_state["force_mortgage"]

        column1, column2, column3 = st.columns(3)

        with column1:
            buy_expenses = building_cost + furnishing_cost + property["Precio"] * (1.0085 + itp)
            mortgage = max(0, buy_expenses - savings)
            if st.session_state["force_mortgage"]:
                mortgage = max(buy_expenses * 0.2, mortgage)
            mortgage_quota = (mortgage * (interest_rate / 12)) / (1 - (1 + interest_rate / 12) ** (-years * 12))
            #mortgage_quota = mortgage * (interest_rate / 12) / (1 - (1 + interest_rate / 12) ** (-years * 12))
            quota = mortgage_quota + (expenses / 12) + (property["Precio"] * ibi / 12)
            st.metric("Inversión total de compra y preparación", value = "{:,.0f} €".format(buy_expenses).replace(",", "."))

        with column2:
            col1, col2 = st.columns(2)
            col1.metric("Cuota mensual con gastos", value = "{:,.0f} €".format(quota).replace(",", "."))
            total_mortgage = mortgage_quota * years * 12 + savings
            col2.metric("Hipoteca total", value = "{:,.0f} €".format(total_mortgage).replace(",", "."))

        with column3:
            col1, col2 = st.columns(2)
            col1.metric("Porcentaje del salario", value = "{:,.0f} %".format((quota / salary) * 100).replace(",", "."))
            net_profit = (rent * 12) - mortgage_quota * 12 - expenses - property["Precio"] * ibi
            net_profit_rate = (net_profit / buy_expenses) * 100
            col2.metric("Rentabilidad neta", value = "{:,.2f} %".format(net_profit_rate).replace(",", "."))


    with st.expander("Mapa de la zona"):

        location = property["Zona"] + ", " + property["Ciudad"].replace(" Capital", "").replace(" Provincia", "") + ", España"
        st.write(location)
        geolocator = Nominatim(user_agent='mytfg')
        try:
            geocode = RateLimiter(geolocator.geocode, min_delay_seconds=3)
            loc = geolocator.geocode(location)
            df = pd.DataFrame({'lat': [loc.latitude], 'lon': [loc.longitude]})
            st.map(df)
        except:
            st.error('Location not found')
            st.stop()


    zonecol, backcol, _ = st.columns([1, 1, 4])
    with zonecol:
        if st.button("Ver zona"):
            st.session_state["zone_city"] = zone["Zona Principal"]
            st.session_state["zone_name"] = zone["Zona"]
            st.session_state["zone_id"] = zone["Identificador"]
            switch_page("Estadisticas de la zona")
    with backcol:
        if st.button("Búsqueda de viviendas"):
            switch_page("Viviendas")
    
    st.write("")


    

        

except URLError as e:
    st.error(
        """
        This demo requires internet access.
        Connection error: %s
    """
        % e.reason
    )
