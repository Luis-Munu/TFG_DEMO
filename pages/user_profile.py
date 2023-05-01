import streamlit as st
from PIL import Image
import modules.utils as utils

utils.manage_css_style("Perfil de usuario", "🌍", "wide", "collapsed")

st.markdown("<h1 style='text-align: center; color: #ff9900;'>Perfil de usuario</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ff9900;'><br><br>En esta página podrás gestionar tus datos, preferencias y propiedades favoritas.</h1>", unsafe_allow_html=True)

st.markdown("<br><br> </br>", unsafe_allow_html=True)

column1, column2 = st.columns([1, 2])
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

with column1:
        image = Image.open('images/logon.png')
        st.image(image, use_column_width=True)
