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
        analysis_mode = st.radio(
            "Modo de analisis",
            ["Evaluar una estrategia", "Comparar todas las estrategias"],
        )

        strategy = st.selectbox(
            "Elige una estrategia",
            ["RSI Strategy", "SMA Crossover", "MACD Strategy"],
            disabled=analysis_mode == "Comparar todas las estrategias",
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

        compare_all = analysis_mode == "Comparar todas las estrategias"
        optimize = st.checkbox(
            "Optimizar parametros",
            value=compare_all,
            disabled=compare_all,
        )
        if optimize:
            st.info("La optimizacion ejecuta multiples backtests y puede tardar.")
        if compare_all:
            st.info("Este modo optimiza RSI, SMA y MACD automaticamente.")

        objective = st.selectbox(
            "Funcion objetivo",
            ["Sharpe Ratio", "Score ajustado por riesgo"],
            help=(
                "Sharpe Ratio maximiza retorno ajustado por volatilidad. "
                "El score ajustado penaliza drawdowns altos."
            ),
        )

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
        "modo_analisis": "compare_all" if compare_all else "single",
        "capital": cash,
        "optimizar": optimize,
        "objetivo": "risk_adjusted" if objective == "Score ajustado por riesgo" else "sharpe",
        "modo_demo": demo_mode,
        "ejecutar": run_analysis,
    }
