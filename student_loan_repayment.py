import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("💰 Student Loan Payoff Calculator")

# ------------------------------
# User Guide Section
# ------------------------------
with st.expander("📘 Student Loan Payoff User Guide"):
    st.markdown(f"""
    ## 📘 How to Use This App

    ### 1️⃣ Step 1 – Understand Your Loan
    - **Loan Amount:** `${0:,.2f}` (updates after you enter it below)
    - **Interest Rate:** `{0:.2f}%` (updates after you enter it below)
    - **Minimum Monthly Payment:** Auto-calculated for a 10-year plan
    - **Extra Payment Example:** Enter any amount to see payoff speed-up

    **Why this matters:** Knowing your exact loan balance, interest rate, and minimum payment is the foundation for building a smart payoff plan.

    ---

    ### 2️⃣ Step 2 – Choose a Payoff Strategy
    #### **Option A – Minimum Payment**
    - **Pros:** Frees up cash for other needs, lower immediate risk.
    - **Cons:** Longest payoff time, highest total interest paid.

    #### **Option B – Aggressive Payoff (+Extra Monthly Payment)**
    - **Pros:** Shorter payoff period, less interest paid overall.
    - **Cons:** Higher monthly commitment, less flexibility.

    #### **Option C – Lump-Sum Payment**
    - **Pros:** Instant reduction in balance, significant interest savings.
    - **Cons:** Requires large upfront cash, risk if emergency arises.

    ---

    ### 3️⃣ Step 3 – Use the App's Features
    1. **Loan Calculator Table** – Compare payoff timelines & interest savings.
    2. **Balance Chart** – See how fast each strategy pays off your loan.
    3. **Extra Payment Planner** – Test different amounts.

    ---

    ### 4️⃣ Step 4 – Pro Tips for Paying Off Faster
    - Make biweekly payments instead of monthly (13 full payments per year).
    - Apply tax refunds or bonuses directly to your loan.
    - Refinance if you qualify for a lower rate (but check federal benefits first).
    - Track progress visually to stay motivated.

    ---

    **💡 Financial Reminder:** Always keep an emergency fund before going too aggressive on loan payoff.
    """)

# ------------------------------
# User Inputs
# ------------------------------
loan_amount = st.number_input("Loan Amount ($)", value=0.0, min_value=0.0, step=1000.0, format="%.2f")
annual_interest_rate = st.number_input("Annual Interest Rate (%)", value=0.0, min_value=0.0, step=0.1, format="%.2f") / 100
extra_payment = st.number_input("Extra Monthly Payment ($)", value=0.0, min_value=0.0, step=50.0, format="%.2f")
lump_sum = st.number_input("Lump Sum Payment ($)", value=0.0, min_value=0.0, step=1000.0, format="%.2f")

calculate = st.button("Calculate Loan Payoff")

monthly_interest_rate = annual_interest_rate / 12

# ------------------------------
# Loan schedule calculator
# ------------------------------
def loan_schedule(balance, monthly_payment, extra_payment=0):
    months = 0
    total_interest = 0
    balances = [balance]
    while balance > 0:
        interest = balance * monthly_interest_rate
        principal_payment = monthly_payment + extra_payment - interest
        if principal_payment > balance:
            principal_payment = balance
        balance -= principal_payment
        total_interest += interest
        months += 1
        balances.append(balance)
        if months > 1000:  # safety break
            break
    return months, total_interest, balances

# ------------------------------
# Show results only when button is clicked
# ------------------------------
if calculate and loan_amount > 0 and annual_interest_rate > 0:
    # Monthly payments for strategies
    n_months_10yr = 10 * 12
    monthly_payment_standard = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate)**n_months_10yr) / ((1 + monthly_interest_rate)**n_months_10yr - 1)

    n_months_25yr = 25 * 12
    monthly_payment_extended = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate)**n_months_25yr) / ((1 + monthly_interest_rate)**n_months_25yr - 1)

    # Strategies
    months_standard, interest_standard, balances_standard = loan_schedule(loan_amount, monthly_payment_standard)
    months_extended, interest_extended, balances_extended = loan_schedule(loan_amount, monthly_payment_extended)
    months_aggressive, interest_aggressive, balances_aggressive = loan_schedule(loan_amount, monthly_payment_standard, extra_payment=extra_payment)

    balance_after_lump = loan_amount - lump_sum
    monthly_payment_lump = balance_after_lump * (monthly_interest_rate * (1 + monthly_interest_rate)**n_months_10yr) / ((1 + monthly_interest_rate)**n_months_10yr - 1)
    months_lump, interest_lump, balances_lump = loan_schedule(balance_after_lump, monthly_payment_lump)

    # Results table
    df = pd.DataFrame({
        "Strategy": [
            "Standard 10-Year",
            "Extended 25-Year",
            f"Aggressive +${extra_payment:.0f}",
            f"Lump Sum ${lump_sum:,.0f}"
        ],
        "Monthly Payment": [
            monthly_payment_standard,
            monthly_payment_extended,
            monthly_payment_standard + extra_payment,
            monthly_payment_lump
        ],
        "Months to Payoff": [months_standard, months_extended, months_aggressive, months_lump],
        "Years to Payoff": [months_standard/12, months_extended/12, months_aggressive/12, months_lump/12],
        "Total Interest Paid": [interest_standard, interest_extended, interest_aggressive, interest_lump],
        "Interest Saved vs Standard": [
            0,
            interest_standard - interest_extended,
            interest_standard - interest_aggressive,
            interest_standard - interest_lump
        ]
    })

    st.subheader("📊 Loan Payoff Strategy Comparison")
    st.dataframe(df.style.format({
        "Monthly Payment": "${:,.2f}".format,
        "Years to Payoff": "{:,.2f}".format,
        "Total Interest Paid": "${:,.2f}".format,
        "Interest Saved vs Standard": "${:,.2f}".format
    }))

    # Payoff chart
    st.subheader("📉 Loan Balance Over Time")
    plt.figure(figsize=(10,6))
    plt.plot(balances_standard, label="Standard 10-Year")
    plt.plot(balances_extended, label="Extended 25-Year")
    plt.plot(balances_aggressive, label=f"Aggressive +${extra_payment:.0f}")
    plt.plot(balances_lump, label=f"Lump Sum ${lump_sum:,.0f}")
    plt.xlabel("Months")
    plt.ylabel("Loan Balance ($)")
    plt.title("Loan Balance Over Time")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)
else:
    st.info("Enter your loan details and click **Calculate Loan Payoff** to see results.")
