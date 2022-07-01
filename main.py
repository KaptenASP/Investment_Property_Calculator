import streamlit as st
import constants
import plotly.graph_objects as go
import pandas as pd


@st.cache(allow_output_mutation=True)
def get_data():
    return []


st.header("Investment Property Profitability Calculator")
st.sidebar.header("Calculation Results:")

st.write("---------------------------------------------------------------------")
st.subheader("Calculating Upfront Costs")
st.sidebar.subheader("Costs:")

property_price = st.slider('Enter the property price?', 0, 2000000, 500000, 10000)
deposit_percent = st.slider("Enter (in %) how much you want to deposit", 5, 30, 10, 1)
st.write(
    f"Currently, you want to deposit {deposit_percent}% equating to ${round(deposit_percent / 100 * property_price, 2)}")

deposit_amount = round(deposit_percent / 100 * property_price, 2)

rate = 0
# Calculating LMI
if deposit_percent < 20:
    key_1 = str(100 - deposit_percent)
    if property_price <= 300000:
        rate = constants.LMI_RATES[key_1]["300000"]
    elif property_price <= 500000:
        rate = constants.LMI_RATES[key_1]["500000"]
    elif property_price <= 600000:
        rate = constants.LMI_RATES[key_1]["600000"]
    elif property_price <= 750000:
        rate = constants.LMI_RATES[key_1]["750000"]
    else:
        rate = constants.LMI_RATES[key_1]["1000000"]

lmi_transfer_duty = round(0.09 * rate, 2)
lmi = round(rate / 100 * property_price, 2)

# Calculating transfer duty as of July 2022
# Based on tables from: https://www.revenue.nsw.gov.au/taxes-duties-levies-royalties/transfer-duty
transfer_duty = 0
if property_price < 15000:
    transfer_duty = 1.25 * (property_price / 100)
elif property_price < 32000:
    transfer_duty = 187 + 1.50 * (property_price - 15000) / 100
elif property_price < 87000:
    transfer_duty = 442 + 1.75 * (property_price - 32000) / 100
elif property_price < 327000:
    transfer_duty = 1405 + 3.5 * (property_price - 87000) / 100
elif property_price < 1089000:
    transfer_duty = 9805 + 4.5 * (property_price - 300000) / 100
else:
    transfer_duty = 44095 + 5.5 * (property_price - 1089000) / 100

transfer_duty = round(lmi_transfer_duty + transfer_duty, 2)

with st.expander("Click for a more advanced input"):
    mortgage_registration_fee = float(st.text_input("Enter the mortgage registration fees", 154.00))
    legal_fees = float(st.text_input("Enter the legal fees related with property purchase", 2000.00))
    inspection_fees = float(st.text_input("Enter the inspection fees", 900))

upfront_costs = deposit_amount + transfer_duty + mortgage_registration_fee + lmi + legal_fees + inspection_fees
st.sidebar.write(f"Upfront costs = ${round(upfront_costs, 2)}")

upfront_cost_breakdown = st.checkbox("Click to view breakdown of upfront expenses")
if upfront_cost_breakdown:
    upfront_cost_labels = [
        'Deposit Amount',
        'Transfer Duty',
        'Mortgage Registration Fees',
        'Lenders Mortgage Insurance',
        'Legal Fees',
        'Inspection Fees'
    ]

    upfront_cost_values = [
        deposit_amount,
        transfer_duty,
        mortgage_registration_fee,
        lmi,
        legal_fees,
        inspection_fees
    ]

    upfront_cost_fig = go.Figure(data=[go.Pie(labels=upfront_cost_labels, values=upfront_cost_values)])
    st.plotly_chart(upfront_cost_fig, use_container_width=True)

    upfront_cost_table = go.Figure(data=[go.Table(
        header=dict(values=['Name', 'Amount ($)'],
                    line_color='#656a7a',
                    fill_color='#0e1117',
                    font_size=16,
                    align='center'),
        cells=dict(values=[
            upfront_cost_labels,
            upfront_cost_values],
            font_size=14,
            height=30,
            line_color='#656a7a',
            fill_color='#0e1117',
            align='center')
    )
    ])

    st.plotly_chart(upfront_cost_table)

st.write("---------------------------------------------------------------------")
st.subheader("Calculating Long Term Costs")

loan_interest_rate = st.slider('Loan Interest Rate', 0.00, 7.00, 3.00, 0.01)
loan_term = st.slider("Loan Term", 1, 50, 30, 1)

loan_amount = property_price - deposit_amount
monthly_repayment_amount = (loan_amount * (loan_interest_rate / 1200) * (1 + (loan_interest_rate / 1200)) ** (
        loan_term * 12)) / ((1 + (loan_interest_rate / 1200)) ** (loan_term * 12) - 1)
yearly_repayment_amount = monthly_repayment_amount * 12

agent_fees = st.slider("Enter agent fees (%)", 0, 15, 8, 1)

col1, col2, col3 = st.columns(3)
council_fees = 0
maintenance_fees = 0
insurance_fees = 0

with col1:
    council_fees = st.text_input("Enter council fees:", 3000)
    council_fees = float(council_fees)
with col2:
    maintenance_fees = st.text_input("Enter maintenance fees:", 2000)
    maintenance_fees = float(maintenance_fees)
with col3:
    insurance_fees = st.text_input("Enter insurance fees", 1500)
    insurance_fees = float(insurance_fees)

st.write("---------------------------------------------------------------------")
st.subheader("Calculating Long Term Income")

rent = st.slider("Enter property's rental income (weekly)", 0.00, 0.003 * property_price, 0.001 * property_price, 50.00)

long_term_fees = yearly_repayment_amount + (agent_fees * rent / 100) + council_fees + maintenance_fees + insurance_fees

long_term_expenses_breakdown = st.checkbox("Click to view breakdown of long term expenses")
if long_term_expenses_breakdown:
    long_term_expense_labels = [
        'yearly loan repayment amount',
        'agent fees',
        'council fees',
        'maintenance fees',
        'insurance fees'
    ]

    long_term_expense_values = [
        yearly_repayment_amount,
        agent_fees * rent / 100,
        council_fees,
        maintenance_fees,
        insurance_fees
    ]

    upfront_cost_fig = go.Figure(data=[go.Pie(labels=long_term_expense_labels, values=long_term_expense_values)])
    st.plotly_chart(upfront_cost_fig, use_container_width=True)

st.sidebar.write(f"long term expenses = ${round(long_term_fees, 2)}")
st.sidebar.subheader("Income:")
st.sidebar.write(f"gross income = ${rent * 52}")

st.sidebar.subheader("NET (excl. upfront costs):")
net_income = round(rent * 52 - long_term_fees, 2)
if net_income > 0:
    st.sidebar.success(f"Net Income = ${net_income}")
elif net_income is 0:
    st.sidebar.warning(f"Net Income = $0")
else:
    st.sidebar.error(f"Net Income = -${abs(net_income)}")

# Creating SNAPSHOTS
property_snapshots = []
st.subheader("Snapshots:")
snapshot_name = st.text_input("Enter Snapshot Name:")

if st.button("Save Snapshot:"):
    get_data().append({
        "snapshot_name": snapshot_name,
        "gross_income": rent*52,
        "net_income": rent*52 - long_term_fees,
    })

st._legacy_table(pd.DataFrame(get_data()))
