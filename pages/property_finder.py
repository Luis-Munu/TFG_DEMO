from urllib.error import URLError

import modules.utils as utils
import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from streamlit_extras.switch_page_button import switch_page

for k, v in st.session_state.items():
    st.session_state[k] = v

utils.manage_css_style("Viviendas", "🏠", "wide", "collapsed")

utils.initialize_session_state()

try:
    st.markdown("<h1 style='text-align: center; color: #000000;'>Buscador de viviendas</h1>", unsafe_allow_html=True)
    st.markdown("")
    properties = utils.get_property_data_local()
    if properties.empty:
        st.markdown("<h3 style='text-align: center; color: #000000;'><br><br>Actualmente no hay viviendas disponibles en la zona</h3>", unsafe_allow_html=True)
        st.stop()
    st.markdown("<h3 style='text-align: center; color: #000000;'><br><br>Busca rápidamente las viviendas más rentables entre más de {} propiedades</h3>".format(properties.shape[0]), unsafe_allow_html=True)
    properties = properties.sort_values(by="Rentabilidad", ascending=False)
    filtercol, datacol = st.columns((3, 10))

    with filtercol:
        if st.session_state["show_property"]:
            if st.button("Estudio de la vivienda"):
                st.session_state["show_property"] = False
                switch_page("Caracteristicas de la propiedad")
            st.markdown("<a style='color: #000000; font-weight: bold;' href='{}' target='_blank'>Ver anuncio</a>".format(st.session_state["property_url"]), unsafe_allow_html=True)
            
        if "ps_rooms" not in st.session_state:
            st.session_state["ps_rooms"] = [int(properties['Habitaciones'].min()), int(properties['Habitaciones'].max())]
        if "ps_m2" not in st.session_state:
            st.session_state["ps_m2"] = [int(properties['Metros cuadrados'].min()), int(properties['Metros cuadrados'].max())]
        if "ps_price" not in st.session_state:
            st.session_state["ps_price"] = [int(properties['Precio'].min()), 300000]
        if "ps_floor" not in st.session_state:
            st.session_state["ps_floor"] = [int(properties['Planta'].min()), int(properties['Planta'].max())]
        
            
        city = st.multiselect("Ciudad", options=properties['Ciudad'].unique(), key="ps_city")
        if city:
            subzones = properties[properties['Ciudad'].isin(city)]['Zona'].unique()
            zone = st.multiselect("Zona", options=subzones, key="ps_zone")
        else:
            zone = st.multiselect("Zona", options=properties['Zona'].unique(), key="ps_zone")

        property_type = st.multiselect("Tipo", options=properties['Tipo'].unique(), key="ps_property_type")
        rooms = st.slider("Habitaciones", int(properties['Habitaciones'].min()), int(properties['Habitaciones'].max()), key="ps_rooms")
        m2 = st.slider("Metros cuadrados", int(properties['Metros cuadrados'].min()), int(properties['Metros cuadrados'].max()), key="ps_m2")
        price = st.slider("Precio", int(properties['Precio'].min()), 300000, key="ps_price")
        max_floor = properties['Planta'].replace('[^0-9]', '0', regex=True).astype(float).max()
        floor = st.slider("Planta", int(properties['Planta'].min()), int(max_floor), key="ps_floor")
        elevator = st.checkbox("Ascensor", key="ps_elevator")
        
        
        if property_type:
            properties = properties[properties['Tipo'].isin(property_type)]
        if zone:
            properties = properties[properties['Zona'].isin(zone)]
        if city:
            properties = properties[properties['Ciudad'].isin(city)]
        if price:
            properties = properties[(properties['Precio'] >= price[0]) & (properties['Precio'] <= price[1])]
        if m2:
            properties = properties[(properties['Metros cuadrados'] >= m2[0]) & (properties['Metros cuadrados'] <= m2[1])]
        if rooms:
            properties = properties[(properties['Habitaciones'] >= rooms[0]) & (properties['Habitaciones'] <= rooms[1])]
        if floor:
            properties = properties[(properties['Planta'] >= floor[0]) & (properties['Planta'] <= floor[1])]
        if elevator:
            properties = properties[properties['Ascensor'] == 'Yes']
            

    with datacol:
        # align cell text to the left
        options = GridOptionsBuilder.from_dataframe(
            properties, enableRowGroup=True, enableValue=True, enablePivot=True
        )
        options.configure_selection("single")
        options.configure_columns(cellStyle={"textAlign": "left"})
        custom_css ="""
        <style>
            .ag-header-cell-label {
                justify-content: left !important;
            }

            .ag-cell {
                justify-content: left !important;
                align-items: left !important;
            }

            .col_heading   {text-align: left !important}

            #gridToolBar {
                display: none !important;
            }
        """
        selection = AgGrid(properties, custom_css=custom_css, height=3000, enable_enterprise_module = True, 
                        gridOptions = options.build(), update_mode=GridUpdateMode.MODEL_CHANGED, 
                        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                        reload_data= True, width=1000, allow_unsafe_jscode=True)
        if selection and len(selection["selected_rows"]) > 0:
            st.session_state["show_property"] = True
            st.session_state["property_id"] = selection["selected_rows"][0]["DB ID"]
            st.write(st.session_state["property_id"])
            st.session_state["property_url"] = "https://www.fotocasa.es" + selection["selected_rows"][0]["Enlace"]
        
        

except URLError as e:
    st.error(
        """
        This demo requires internet access.
        Connection error: %s
    """
        % e.reason
    )