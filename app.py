import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Sports Betting Simulator",
    layout="wide"
)

st.title("🤑 We gon' make bank julsss 🤑")

# ==========================================================
# INPUTS
# ==========================================================

col1, col2 = st.columns(2)

with col1:
    team1 = st.text_input("Team 1", "Netherlands")

with col2:
    team2 = st.text_input("Team 2", "Japan")

st.subheader("Decimal Odds")

c1, c2, c3 = st.columns(3)

with c1:
    odds_team1 = st.number_input(
        f"{team1} Win Odds",
        min_value=1.01,
        value=2.06,
        step=0.01
    )

with c2:
    odds_draw = st.number_input(
        "Draw Odds",
        min_value=1.01,
        value=3.61,
        step=0.01
    )

with c3:
    odds_team2 = st.number_input(
        f"{team2} Win Odds",
        min_value=1.01,
        value=3.75,
        step=0.01
    )

bankroll = st.number_input(
    "Total Money to Bet (₱)",
    min_value=0.0,
    value=500.0,
    step=50.0
)

# ==========================================================
# MODE
# ==========================================================

dnb_mode = st.toggle("Draw No Bet (DNB) Mode")

st.subheader("Select Outcomes to Bet On")

bet_team1 = st.checkbox(f"{team1} Win", value=True)

if not dnb_mode:
    bet_draw = st.checkbox("Draw", value=True)
else:
    bet_draw = False
    st.info("DNB mode ON → Draw becomes refund, not a losing outcome.")

bet_team2 = st.checkbox(f"{team2} Win", value=True)

if not (bet_team1 or bet_draw or bet_team2):
    st.error("Select at least one outcome.")
    st.stop()

# ==========================================================
# BUILD SELECTED BETS
# ==========================================================

selected = []

if dnb_mode:
    if bet_team1:
        selected.append(("team1", odds_team1))
    if bet_team2:
        selected.append(("team2", odds_team2))
else:
    if bet_team1:
        selected.append(("team1", odds_team1))
    if bet_draw:
        selected.append(("draw", odds_draw))
    if bet_team2:
        selected.append(("team2", odds_team2))

if len(selected) == 0:
    st.error("Select at least one valid bet.")
    st.stop()

# ==========================================================
# OPTIMAL BET ALLOCATION
# ==========================================================

inverse_sum = sum(1 / odds for _, odds in selected)

bet1 = 0.0
bet_draw_amt = 0.0
bet2 = 0.0

for outcome, odds in selected:
    amount = bankroll * (1 / odds) / inverse_sum

    if outcome == "team1":
        bet1 = amount
    elif outcome == "draw":
        bet_draw_amt = amount
    elif outcome == "team2":
        bet2 = amount

# ==========================================================
# DISPLAY BETS
# ==========================================================

st.subheader("Bet Allocation")

alloc_df = pd.DataFrame({
    "Outcome": [
        f"{team1} Win",
        "Draw",
        f"{team2} Win"
    ],
    "Bet Amount (₱)": [
        round(bet1, 2),
        round(bet_draw_amt, 2),
        round(bet2, 2)
    ]
})

st.table(alloc_df)

# ==========================================================
# PAYOUTS (SINGLE SOURCE OF TRUTH)
# ==========================================================

payout_team1 = bet1 * odds_team1
payout_draw = bet_draw_amt * odds_draw
payout_team2 = bet2 * odds_team2

# ==========================================================
# PROFIT LOGIC (FIXED)
# ==========================================================

if dnb_mode:
    profit_team1 = payout_team1 - bankroll
    profit_team2 = payout_team2 - bankroll
    profit_draw = 0
else:
    profit_team1 = payout_team1 - bankroll
    profit_draw = payout_draw - bankroll
    profit_team2 = payout_team2 - bankroll

# ==========================================================
# RESULTS TABLE
# ==========================================================

st.subheader("Results")

if dnb_mode:
    results = pd.DataFrame({
        "Actual Match Result": [
            f"{team1} Wins",
            "Draw (Refund)",
            f"{team2} Wins"
        ],
        "Payout (₱)": [
            round(payout_team1, 2),
            round(bankroll, 2),
            round(payout_team2, 2)
        ],
        "Profit / Loss (₱)": [
            round(profit_team1, 2),
            0,
            round(profit_team2, 2)
        ]
    })
else:
    results = pd.DataFrame({
        "Actual Match Result": [
            f"{team1} Wins",
            "Draw",
            f"{team2} Wins"
        ],
        "Payout (₱)": [
            round(payout_team1, 2),
            round(payout_draw, 2),
            round(payout_team2, 2)
        ],
        "Profit / Loss (₱)": [
            round(profit_team1, 2),
            round(profit_draw, 2),
            round(profit_team2, 2)
        ]
    })

st.table(results)

# ==========================================================
# IMPLIED PROBABILITIES
# ==========================================================

st.subheader("Implied Probabilities")

prob_df = pd.DataFrame({
    "Outcome": [
        f"{team1} Win",
        "Draw",
        f"{team2} Win"
    ],
    "Implied Probability (%)": [
        round((1 / odds_team1) * 100, 2),
        round((1 / odds_draw) * 100, 2),
        round((1 / odds_team2) * 100, 2)
    ]
})

st.table(prob_df)

# ==========================================================
# OVERROUND
# ==========================================================

st.subheader("Bookmaker Margin")

overround = (1 / odds_team1) + (1 / odds_draw) + (1 / odds_team2)
margin = (overround - 1) * 100

st.metric("Overround (%)", f"{margin:.2f}%")

if overround < 1:
    st.success("🔥 Arbitrage opportunity exists!")
else:
    st.warning("No full arbitrage opportunity.")

# ==========================================================
# STRATEGY ANALYSIS
# ==========================================================

st.subheader("Selected Strategy Analysis")

selected_inverse = inverse_sum

st.write(f"Inverse odds sum: **{selected_inverse:.4f}**")

if selected_inverse < 1:
    guaranteed_return = bankroll / selected_inverse
    guaranteed_profit = guaranteed_return - bankroll

    st.success(f"Guaranteed arbitrage profit: ₱{guaranteed_profit:.2f}")
else:
    st.info("Not risk-free (no arbitrage condition met).")

# ==========================================================
# RISK SUMMARY
# ==========================================================

st.subheader("Risk Summary")

profits = [profit_team1, profit_draw, profit_team2]

st.metric("Best Case Profit (₱)", f"{max(profits):.2f}")
st.metric("Worst Case Profit (₱)", f"{min(profits):.2f}")

st.write("DNB Mode:", "ON" if dnb_mode else "OFF")