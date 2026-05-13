import logging

# pyrefly: ignore [missing-import]
import streamlit as st
import numpy as np
import pandas as pd

from backtest.engine import calculate_buy_hold, run_backtest
from backtest.optimizer import run_optimization
from config.settings import MACD_PARAMS, RSI_PARAMS, SMA_PARAMS
from data.loader import DataNotFoundError, download_data
from indicators.technical import add_indicators
from strategies.macd_strategy import MACDStrategy
from strategies.rsi_strategy import RSIStrategy
from strategies.sma_strategy import SMAStrategy
from ui.charts import (
    plot_candlestick,
    plot_equity_comparison,
    plot_equity_curve,
    plot_trades,
)
from ui.metrics import (
    render_best_params,
    render_buy_hold_comparison,
    render_metrics,
    render_optimization_results,
)
from ui.sidebar import render_sidebar
from ui.chatbot import render_chatbot


logger = logging.getLogger(__name__)


STRATEGIES = {
    "RSI Strategy": {
        "class": RSIStrategy,
        "base_params": {"rsi_lower": 30, "rsi_upper": 70},
        "param_grid": RSI_PARAMS,
    },
    "SMA Crossover": {
        "class": SMAStrategy,
        "base_params": {"n_short": 20, "n_long": 50},
        "param_grid": SMA_PARAMS,
    },
    "MACD Strategy": {
        "class": MACDStrategy,
        "base_params": {"fast": 12, "slow": 26, "signal": 9},
        "param_grid": MACD_PARAMS,
    },
}


@st.cache_data(show_spinner=False)
def load_market_data(ticker, start_date, end_date):
    """Descarga datos y calcula indicadores tecnicos."""
    raw_data = download_data(ticker, start_date, end_date)
    return add_indicators(raw_data)


@st.cache_data(show_spinner=False)
def load_demo_data(ticker, start_date, end_date):
    """Genera una serie OHLCV deterministica para probar la app sin internet."""
    dates = pd.date_range(start=start_date, end=end_date, freq="B")
    if len(dates) < 80:
        raise DataNotFoundError("El modo demostracion necesita al menos 80 dias habiles.")

    seed = sum(ord(character) for character in ticker)
    rng = np.random.default_rng(seed)
    returns = rng.normal(loc=0.0006, scale=0.018, size=len(dates))
    trend = np.linspace(0, 0.35, len(dates))
    close = 100 * np.exp(np.cumsum(returns) + trend)
    open_price = close * (1 + rng.normal(0, 0.004, len(dates)))
    high = np.maximum(open_price, close) * (1 + rng.uniform(0.001, 0.018, len(dates)))
    low = np.minimum(open_price, close) * (1 - rng.uniform(0.001, 0.018, len(dates)))
    volume = rng.integers(800_000, 6_000_000, size=len(dates))

    data = pd.DataFrame(
        {
            "Open": open_price,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": volume,
        },
        index=dates,
    )
    return add_indicators(data)


def main():
    st.set_page_config(layout="wide", page_title="Trading Bot")
    st.title("Trading Bot - Backtesting y optimizacion")
    st.caption("Sistema educativo para evaluar estrategias de trading con datos historicos.")

    config = render_sidebar()
    
    # El chatbot recibe las estadísticas guardadas en la sesión (si existen)
    stats_for_bot = st.session_state.get("last_stats")
    render_chatbot(stats=stats_for_bot, ticker=config["ticker"])

    if not config["ejecutar"]:
        last_results = st.session_state.get("last_results")
        if last_results is not None:
            st.info(
                "Mostrando el ultimo analisis ejecutado. "
                "Presiona 'Ejecutar analisis' para actualizarlo con la configuracion actual."
            )
            render_results(**last_results)
            return

        st.info("Configura el activo, periodo y estrategia en el panel lateral para iniciar.")
        return

    if config["fecha_inicio"] >= config["fecha_fin"]:
        st.error("La fecha inicial debe ser anterior a la fecha final.")
        return

    strategy_config = STRATEGIES[config["estrategia"]]
    strategy_class = strategy_config["class"]
    base_params = strategy_config["base_params"]

    try:
        with st.spinner("Descargando datos y calculando indicadores..."):
            if config["modo_demo"]:
                data = load_demo_data(
                    config["ticker"],
                    config["fecha_inicio"],
                    config["fecha_fin"],
                )
                st.warning("Estas usando datos de demostracion, no precios reales de mercado.")
            else:
                data = load_market_data(
                    config["ticker"],
                    config["fecha_inicio"],
                    config["fecha_fin"],
                )

        if data.empty:
            st.error("No quedaron datos validos despues de calcular indicadores.")
            return

        with st.spinner("Ejecutando backtesting base..."):
            base_stats = run_backtest(
                data,
                strategy_class,
                base_params,
                cash=config["capital"],
            )

        optimized_stats = None
        best_params = None
        optimization_results = []

        if config["optimizar"]:
            best_params, optimized_stats, optimization_results = optimize_strategy(
                data,
                strategy_class,
                strategy_config["param_grid"],
                cash=config["capital"],
                objective=config["objetivo"],
                label="Optimizando parametros",
            )

        buy_hold_stats = calculate_buy_hold(data, cash=config["capital"])

        results_payload = {
            "data": data,
            "ticker": config["ticker"],
            "strategy_name": config["estrategia"],
            "base_stats": base_stats,
            "optimized_stats": optimized_stats,
            "buy_hold_stats": buy_hold_stats,
            "best_params": best_params,
            "optimization_results": optimization_results,
        }
        st.session_state["last_results"] = results_payload
        render_results(**results_payload)

        # Guardamos las estadísticas para que el chatbot las analice
        st.session_state["last_stats"] = optimized_stats if optimized_stats is not None else base_stats

    except DataNotFoundError as error:
        logger.warning("No fue posible cargar datos: %s", error)
        show_user_error(str(error))
    except ValueError as error:
        logger.exception("Error de validacion durante el analisis")
        show_user_error(str(error))
    except Exception:
        logger.exception("Error inesperado durante el analisis")
        show_user_error(
            "Ocurrio un error inesperado al ejecutar el analisis. "
            "Revisa la terminal para ver el detalle tecnico."
        )


def show_user_error(message):
    """Muestra errores limpios al usuario sin exponer trazas tecnicas."""
    st.error(f"Error: {message}")


def optimize_strategy(
    data,
    strategy_class,
    param_grid,
    cash,
    objective,
    label="Optimizando parametros",
):
    """Ejecuta grid search con una barra de progreso de Streamlit."""
    progress_bar = st.progress(0)
    progress_text = st.empty()

    def update_progress(current, total, params):
        progress_bar.progress(current / total)
        progress_text.text(f"{label} {current}/{total}: {params}")

    with st.spinner(f"{label}..."):
        best_params, best_stats, optimization_results = run_optimization(
            data,
            strategy_class,
            param_grid,
            cash=cash,
            progress_callback=update_progress,
            objective=objective,
        )

    progress_bar.empty()
    progress_text.empty()
    return best_params, best_stats, optimization_results


def render_results(
    data,
    ticker,
    strategy_name,
    base_stats,
    optimized_stats=None,
    buy_hold_stats=None,
    best_params=None,
    optimization_results=None,
):
    """Renderiza las pestanas principales de resultados."""
    st.write(f"### {ticker} | {strategy_name}")
    st.write(f"Datos analizados: {len(data):,} registros")

    stats_to_plot = optimized_stats if optimized_stats is not None else base_stats
    tab_data, tab_backtest, tab_buy_hold, tab_optimization = st.tabs(
        [
            "Datos e indicadores",
            "Backtesting",
            "Buy & Hold",
            "Optimizacion",
        ]
    )

    with tab_data:
        st.plotly_chart(plot_candlestick(data), use_container_width=True)
        st.write("Ultimos registros con indicadores")
        st.dataframe(data.tail(10), use_container_width=True)

    with tab_backtest:
        render_metrics(base_stats, optimized_stats)
        st.plotly_chart(plot_equity_curve(stats_to_plot), use_container_width=True)
        st.plotly_chart(plot_trades(data, stats_to_plot), use_container_width=True)

    with tab_buy_hold:
        if buy_hold_stats is None:
            st.info("No hay datos de Buy & Hold para mostrar.")
        else:
            render_buy_hold_comparison(stats_to_plot, buy_hold_stats)
            st.plotly_chart(
                plot_equity_comparison(stats_to_plot, buy_hold_stats),
                use_container_width=True,
            )

    with tab_optimization:
        if optimized_stats is None or best_params is None:
            st.info("Activa la optimizacion para ver los mejores parametros.")
            return

        render_best_params(best_params)
        render_optimization_results(optimization_results or [])


if __name__ == "__main__":
    main()
