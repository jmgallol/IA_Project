from datetime import datetime

import streamlit as st

from config.settings import (
    CAPITAL_INICIAL_DEFAULT,
    CAPITAL_INICIAL_MAX,
    CAPITAL_INICIAL_MIN,
    DATE_END,
    DATE_START,
    DEFAULT_TICKERS,
)


def render_sidebar():
    """
    Renderiza el panel lateral y retorna la configuracion seleccionada.

    El codigo usa nombres en ingles, pero los textos visibles quedan en espanol
    para facilitar la presentacion academica.
    """
    with st.sidebar:
        st.title("Configuracion")
        st.divider()

        st.subheader("Activo")
        ticker = st.selectbox(
            "Selecciona un ticker",
            DEFAULT_TICKERS,
            help="Ejemplos: AAPL, MSFT, BTC-USD, ETH-USD.",
        )

        custom_ticker = st.text_input(
            "Ticker personalizado",
            value="",
            placeholder="Ej: NVDA, TSLA, SOL-USD",
        ).strip()

        if custom_ticker:
            ticker = custom_ticker.upper()

        st.divider()

        st.subheader("Periodo de analisis")
        default_start = datetime.strptime(DATE_START, "%Y-%m-%d")
        default_end = datetime.strptime(DATE_END, "%Y-%m-%d")

        start_date = st.date_input("Fecha inicial", value=default_start)
        end_date = st.date_input("Fecha final", value=default_end)

        st.divider()

        st.subheader("Estrategia")
        strategy = st.selectbox(
            "Elige una estrategia",
            ["RSI Strategy", "SMA Crossover", "MACD Strategy"],
        )

        st.divider()

        st.subheader("Capital")
        cash = st.slider(
            "Capital inicial USD",
            min_value=CAPITAL_INICIAL_MIN,
            max_value=CAPITAL_INICIAL_MAX,
            value=CAPITAL_INICIAL_DEFAULT,
            step=1000,
        )

        st.divider()

        optimize = st.checkbox("Optimizar parametros", value=False)
        if optimize:
            st.info("La optimizacion ejecuta multiples backtests y puede tardar.")

        demo_mode = st.checkbox(
            "Usar datos de demostracion",
            value=False,
            help="Permite probar la app cuando Yahoo Finance no responde.",
        )

        run_analysis = st.button("Ejecutar analisis", use_container_width=True, type="primary")

    return {
        "ticker": ticker,
        "fecha_inicio": start_date.strftime("%Y-%m-%d"),
        "fecha_fin": end_date.strftime("%Y-%m-%d"),
        "estrategia": strategy,
        "capital": cash,
        "optimizar": optimize,
        "modo_demo": demo_mode,
        "ejecutar": run_analysis,
    }
