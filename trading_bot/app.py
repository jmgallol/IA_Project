# ========================================
# app.py - PRUEBA SIMPLE
# ========================================

import streamlit as st

st.set_page_config(layout="wide", page_title="Trading Bot", page_icon="📈")
st.title("📈 Trading Bot")

st.write("## Estado de Carga")

# Test 1
try:
    import yfinance
    st.write("✅ yfinance cargado")
except Exception as e:
    st.error(f"❌ yfinance: {e}")

# Test 2
try:
    import pandas
    st.write("✅ pandas cargado")
except Exception as e:
    st.error(f"❌ pandas: {e}")

# Test 3
try:
    import plotly
    st.write("✅ plotly cargado")
except Exception as e:
    st.error(f"❌ plotly: {e}")

# Test 4
try:
    import backtesting
    st.write("✅ backtesting importado")
except Exception as e:
    st.error(f"❌ backtesting: {e}")

# Test 5
try:
    from backtesting import Strategy
    st.write("✅ backtesting.Strategy cargado")
except Exception as e:
    st.error(f"❌ backtesting.Strategy: {e}")

st.write("---")
st.write("Si todos los checks son verdes, haz clic en F5 para recargar.")


