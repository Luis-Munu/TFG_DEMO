from urllib.error import URLError

import altair as alt
import modules.utils as utils
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from streamlit_extras.switch_page_button import switch_page

utils.manage_css_style("Comparador de zonas", "🌍", "wide", "collapsed")

utils.initialize_session_state()



try:
    st.markdown("<h1 style='text-align: center; color: #000000;'>Comparador de zonas</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #000000;'><br><br>En esta página podrás comparar dos zonas fácilmente.</h1>", unsafe_allow_html=True)

    left, content, right = st.columns((1, 20, 1))

    with left:
        st.write("")
    with right:
        st.write("")
    with content:
        # Get zone data and sort by "Zona" column
        zones = utils.get_zone_data_local()
        zones = zones.sort_values(by="Zona", ascending=False)
        # Create two columns layout
        drop1, drop2 = st.columns([2, 2])

        # Add a dropdown to select view option
        display_option = drop1.selectbox(
            "Elige una opción de visualización", options=['General', 'Alquiler', 'Venta']
        )
        # Filter dataframe based on display option
        if display_option != 'General':
            zones = zones.reset_index()
            zones2 = zones[display_option].astype(str).apply(lambda x: eval(x))
            zones2 = pd.json_normalize(zones2)
            zones2 = zones2.rename(columns=utils.sell_rent_translation)
            zones = pd.concat([zones[['Zona', 'Zona Principal', 'Nombre Completo', 'ROI', 'Identificador']], zones2], axis=1)
        else:
            zones = zones.drop(columns=['Alquiler', 'Venta', 'Subzonas', 'Propiedades'])

        zones.set_index("Zona", inplace=True)
        # Add a multi-select box for specific zones
        zone_list = st.multiselect("Busca una zona en concreto", options=zones.index)

        # Add a dropdown to select a statistic to compare
        columns = list(zones.select_dtypes(include='number').columns)
        sort_column = drop2.selectbox("Selecciona una estadística a comparar", options=columns, index=0)

        # Show navigation button if show zone
        if st.session_state["show_zone"]:
            if st.button("Comparar la zona seleccionada"):
                switch_page("Estadisticas de la zona")

        # Show data based on the selected zones and sort by chosen statistic
        data = zones.loc[zone_list] if zone_list else zones
        #data = utils.filter_df_by_zones(df, zones)
        data = data.sort_values(by=sort_column, ascending=False)
        data.reset_index(inplace=True)
        options = GridOptionsBuilder.from_dataframe(
            data, enableRowGroup=True, enableValue=True, enablePivot=True, suppressToolBar=True
        )
        options.configure_columns(cellStyle={"textAlign": "left"})
        options.configure_selection("single")
        selection = AgGrid(data, enable_enterprise_module=True,
                        gridOptions=options.build(), update_mode=GridUpdateMode.MODEL_CHANGED,
                        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                        reload_data=True, width=1000, allow_unsafe_jscode=True)
        if selection and len(selection["selected_rows"]) > 0:
            st.session_state["show_zone"] = True
            st.session_state["zone_id"] = selection["selected_rows"][0]["Identificador"]
            st.session_state["zone_city"] = selection["selected_rows"][0]["Zona Principal"]
            st.session_state["zone_name"] = selection["selected_rows"][0]["Zona"]


        # Plot comparison data as a bar chart
        data = data.reset_index().melt(id_vars=["Zona"], value_vars=[sort_column])
        st.write("### Comparación en gráfico")
        chart = (
            alt.Chart(data.head(10))
            .mark_bar()
            .encode(
                x=alt.X("Zona:N", sort='-y'),
                y=alt.Y("value:Q", title=sort_column),
                color="Zona:N",
            )
        )
        st.altair_chart(chart, use_container_width=True)


except URLError as e:
    st.error(
        """
        This demo requires internet access.
        Connection error: %s
    """
        % e.reason
    )