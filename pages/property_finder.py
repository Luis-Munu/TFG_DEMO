from urllib.error import URLError

import modules.utils as utils
import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from streamlit_extras.switch_page_button import switch_page
import modules.utils as utils

utils.manage_css_style("Buscador de viviendas", "🏠", "wide", "collapsed")

utils.initialize_session_state()

try:
    left, content, right = st.columns((1, 20, 1))

    with left:
        st.write("")
    with right:
        st.write("")

    with content:
        st.write("""<div class='PortMarker'/>""", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #ff9900;'>Buscador de viviendas</h1>", unsafe_allow_html=True)
        df = utils.get_property_data()
        st.markdown("<h3 style='text-align: center; color: #ff9900;'><br><br>Busca rápidamente las viviendas más rentables entre más de {} propiedades</h3>".format(df.shape[0]), unsafe_allow_html=True)
        st.markdown("")

        df = df.sort_values(by="Rentabilidad", ascending=False)
        datacol, filtercol = st.columns((10, 3))

        with filtercol:
            if st.session_state["show_property"]:
                if st.button("Estudio de la vivienda"):
                    st.session_state["show_property"] = False
                    switch_page("Caracteristicas de la propiedad")

            zone = st.multiselect("Zona", options=df['Zona'].unique())
            city = st.multiselect("Ciudad", options=df['Ciudad'].unique())
            property_type = st.multiselect("Tipo", options=df['Tipo'].unique())
            rooms = st.slider("Habitaciones", int(df['Habitaciones'].min()), int(df['Habitaciones'].max()), value=int(df['Habitaciones'].min()))
            bathrooms = st.slider("Baños", int(df['Baños'].min()), int(df['Baños'].max()), value=int(df['Baños'].min()))

            if property_type:
                df = df[df['Tipo'].isin(property_type)]
            if zone:
                df = df[df['Zona'].isin(zone)]
            if city:
                df = df[df['Ciudad'].isin(city)]
            df = df[(df['Habitaciones'] >= rooms) & (df['Baños'] >= bathrooms)]

            if st.session_state["show_property"]:
                st.markdown("<a style='color: #ff9900;' href='{}' target='_blank'>Ver propiedad</a>".format(st.session_state["property_url"]), unsafe_allow_html=True)

        with datacol:
            # align cell text to the left
            options = GridOptionsBuilder.from_dataframe(
                df, enableRowGroup=True, enableValue=True, enablePivot=True
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
            selection = AgGrid(df, custom_css=custom_css, height=3000, enable_enterprise_module = True, 
                            gridOptions = options.build(), update_mode=GridUpdateMode.MODEL_CHANGED, 
                            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                            reload_data= True, width=1000, allow_unsafe_jscode=True)
            if selection and len(selection["selected_rows"]) > 0:
                st.session_state["show_property"] = True
                st.session_state["property_id"] = selection["selected_rows"][0]["Identificacion"]
                st.session_state["property_url"] = "https://www.fotocasa.es" + selection["selected_rows"][0]["Enlace"]
            
        

except URLError as e:
    st.error(
        """
        This demo requires internet access.
        Connection error: %s
    """
        % e.reason
    )