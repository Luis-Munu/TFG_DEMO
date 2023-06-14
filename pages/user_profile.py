import modules.utils as utils
import streamlit as st
from PIL import Image
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from streamlit_extras.switch_page_button import switch_page

utils.manage_css_style("Perfil de usuario", "🌍", "wide", "collapsed")

utils.initialize_session_state()

st.markdown("<h1 style='text-align: center; color: #000000;'>Perfil de usuario</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #000000;'><br><br>En esta página podrás gestionar tus datos, preferencias y propiedades favoritas.</h1>", unsafe_allow_html=True)

st.markdown("<br><br> </br>", unsafe_allow_html=True)

column1, column2, column3 = st.columns([1, 2, 0.2])
with column1:
    st.write("")
with column3:
    st.write("")
with column2:
    field1, field2 = st.columns(2)
    user_name = field1.text_input(label="Nombre de usuario", value=st.session_state["user_name"], key="user_name_input")
    st.session_state["user_name"] = user_name

    email = field2.text_input(label="Correo electrónico", value=st.session_state["email"], key="email_input")
    st.session_state["email"] = email

    field3, field4 = st.columns(2)

    age = field3.text_input(label="Edad", value=st.session_state["age"], key="age_input")
    st.session_state["age"] = age

    salary = field4.text_input(label="Salario mensual", value=st.session_state["salary"], key="salary_input")
    st.session_state["salary"] = salary

    field5, field6 = st.columns(2)
    savings_input = field5.text_input(label="Cantidad ahorrada", value=st.session_state["savings"], key="savings_input")
    st.session_state["savings"] = savings_input

    max_amount = field6.text_input(label="Límite de inversión", value=st.session_state["max_amount"], key="max_amount_input")
    st.session_state["max_amount"] = max_amount

    bank = st.selectbox(label="Banco", options=utils.banks, index=0, key="bank_select")
    st.session_state["bank_name"] = utils.banks[bank]
    st.session_state["fixed_interest"] = utils.banks[bank]["interest_rate"]
    st.session_state["max_mortgage_age"] = utils.banks[bank]["max_mortgage_age"]
    
    #first we get the index of the session state community in the utils communities dictionary
    # to get the index we can convert the dictionary to a list and then get the index of the community

    comm = st.session_state["autonomous_community"]
    index = list(utils.communities.keys()).index(comm)
    
    community = st.selectbox(label="Comunidad", options=utils.communities, index=index)
    st.session_state["autonomous_community"] = community

with column1:
    image = Image.open('images/logo.png')
    st.image(image, use_column_width=True)

# now we have to show the favorite properties of the user, it is a pandas dataframe, just create a table with the library st_aggrid
st.markdown("<h3 style='text-align: center; color: #000000;'>Propiedades favoritas</h3>", unsafe_allow_html=True)

grid_data = st.session_state["favorite_properties"]


# check if the dataframe is empty and filter all properties that are not in the autonomous community of the user
if not grid_data.empty and not grid_data[grid_data['Comunidad Autónoma'] == st.session_state["autonomous_community"]].empty:
    grid_data = grid_data[grid_data['Comunidad Autónoma'] == st.session_state["autonomous_community"]]
    zonecol, citycol, typecol = st.columns([1, 1, 1])
    with zonecol:
        zone = st.multiselect("Zona", options=grid_data['Zona'].unique())
    with citycol:
        city = st.multiselect("Ciudad", options=grid_data['Ciudad'].unique())
    with typecol:
        property_type = st.multiselect("Tipo", options=grid_data['Tipo'].unique())

    slider1, slider2 = st.columns([1, 1])
    with slider1:
        if int(grid_data['Habitaciones'].max()) != int(grid_data['Habitaciones'].min()):
            rooms = st.slider("Habitaciones", int(grid_data['Habitaciones'].min()), int(grid_data['Habitaciones'].max()), value=int(grid_data['Habitaciones'].min()))
        else: rooms = int(grid_data['Habitaciones'].max())

    with slider2:
        if int(grid_data['Baños'].max()) != int(grid_data['Baños'].min()):
            bathrooms = st.slider("Baños", int(grid_data['Baños'].min()), int(grid_data['Baños'].max()), value=int(grid_data['Baños'].min()))
        else: bathrooms = int(grid_data['Baños'].max())

    if property_type:
        grid_data = grid_data[grid_data['Tipo'].isin(property_type)]
    if zone:
        grid_data = grid_data[grid_data['Zona'].isin(zone)]
    if city:
        grid_data = grid_data[grid_data['Ciudad'].isin(city)]
    grid_data = grid_data[(grid_data['Habitaciones'] >= rooms) & (grid_data['Baños'] >= bathrooms)]

    if st.session_state["show_property"]:
        st.markdown("<a style='color: #000000;' href='{}' target='_blank'>Ver anuncio</a>".format(st.session_state["property_url"]), unsafe_allow_html=True)
        if st.button("Estudio de la vivienda"):
            st.session_state["show_property"] = False
            switch_page("Caracteristicas de la propiedad")

    # add just one line of blank space with &nbsp;
    st.markdown(" ", unsafe_allow_html=True)
    # align cell text to the left
    options = GridOptionsBuilder.from_dataframe(
        grid_data, enableRowGroup=True, enableValue=True, enablePivot=True
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
    selection = AgGrid(grid_data, custom_css=custom_css, enable_enterprise_module = True, 
                    gridOptions = options.build(), update_mode=GridUpdateMode.MODEL_CHANGED, 
                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                    reload_data= True, width=1000, allow_unsafe_jscode=True)
    if selection and len(selection["selected_rows"]) > 0:
        st.session_state["show_property"] = True
        st.session_state["property_id"] = selection["selected_rows"][0]["Identificacion"]
        st.session_state["property_url"] = "https://www.fotocasa.es" + selection["selected_rows"][0]["Enlace"]
    
else:
    st.markdown("<p style='text-align: center; color: #000000;'>Vaya, parece que aún no tienes propiedades guardadas en esta comunidad</p>", unsafe_allow_html=True)

st.markdown("<br><br> </br>", unsafe_allow_html=True)