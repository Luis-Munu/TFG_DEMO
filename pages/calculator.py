from urllib.error import URLError

import modules.utils as utils
import streamlit as st

# with a math icon and a wide layout and collapsed sidebar
utils.manage_css_style("Calculator", "💸", "wide", "collapsed")

utils.initialize_session_state()

# Create a container with a semi-transparent background
st.markdown("<h1 style='text-align: center; color: #000000;'>Calculadora del inversor</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #000000;'><br><br>En esta página podrás realizar tus estimaciones rápidamente.</h1>", unsafe_allow_html=True)

try:
    property_price = st.slider("Precio de compra", 0.01, 500000.0, 36500.0, 10.0)
    column1, column2= st.columns(2)
    with column1:
        field1, field2 = st.columns(2)
        salary = field1.number_input("Salario", 0.01, 100000.0, float(st.session_state["salary"]), 10.0)
        savings = field2.number_input("Ahorros", 0.01, 1000000.0, float(st.session_state["savings"]), 10.0)
    with column2:
        field1, field2 = st.columns(2)
        years = field1.slider("Años de hipoteca", 1, 30, min(25, 80 - int(st.session_state["age"])), 1)
        interest_rate = field2.slider("Interés esperado", 0.01, 0.2, float(st.session_state["fixed_interest"]), 0.01)

    field1, field2, field3 = st.columns(3)

    building_cost = field1.slider("Gasto de obra", 0.01, 100000.0, 0.01, 10.0)
    furnishing_cost =  field2.slider("Gasto de puesta a punto", 0.01, 30000.0, 0.01, 10.0)
    rent = field3.slider("Alquiler esperado", 0.01, 3000.0, 400.0, 10.0)
        
    field1, field2, field3 = st.columns(3)
    expenses = field1.slider("Gastos anuales previstos", 0.01, 3000.0, 350.0, 10.0)
    itp = field2.slider("ITP", 0.01, 0.15, 0.08, 0.01)
    ibi = field3.slider("IBI", 0.001, 0.15, 0.04, 0.01)

    if st.button("Forzar hipoteca"):
        st.session_state["force_mortgage"] = not st.session_state["force_mortgage"]

    column1, column2, column3 = st.columns(3)

    with column1:
        buy_expenses = building_cost + furnishing_cost + (property_price * itp) + (property_price * ibi) + property_price
        mortgage = max(0, buy_expenses - savings)
        if st.session_state["force_mortgage"]:
            mortgage = max(buy_expenses * 0.2, mortgage)
        mortgage_quota = (mortgage * (interest_rate / 12)) / (1 - (1 + interest_rate / 12) ** (-years * 12))
        quota = mortgage_quota + expenses / 12
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

    st.markdown("<br> </br>", unsafe_allow_html=True)

except URLError as e:
    st.error(
        """
        This demo requires internet access.
        Connection error: %s
    """
        % e.reason
    )

