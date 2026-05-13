import pandas as pd
import streamlit as st


def render_metrics(stats_base, stats_opt=None):
    """Renderiza las metricas principales del backtesting."""
    if stats_opt is None:
        st.subheader("Metricas de desempeno")
        _render_single_stats(stats_base)
        return

    st.subheader("Comparacion: parametros base vs optimizados")
    col_base, col_opt = st.columns(2)

    with col_base:
        st.write("### Parametros base")
        _render_single_stats(stats_base, compact=True)

    with col_opt:
        st.write("### Parametros optimizados")
        _render_single_stats(stats_opt, stats_base=stats_base, compact=True)


def _render_single_stats(stats, stats_base=None, compact=False):
    columns = st.columns(2 if compact else 3)
    metrics = [
        ("Retorno total", ("Return [%]",), "%"),
        ("Retorno Mercado (B&H)", ("Buy & Hold Return [%]",), "%"),
        ("Sharpe Ratio", ("Sharpe Ratio",), ""),
        ("Drawdown maximo", ("Max. Drawdown [%]",), "%"),
        ("Win rate", ("Win Rate [%]",), "%"),
        ("Operaciones", ("# Trades",), ""),
        ("Factor ganancias", ("Profit Factor",), ""),
        ("Exposicion", ("Exposure Time [%]",), "%"),
        ("Retorno anual", ("Return (Ann.) [%]", "Annual Return [%]"), "%"),
    ]

    for index, (label, keys, suffix) in enumerate(metrics):
        key = _find_metric_key(stats, keys)
        if key is None:
            continue

        value = stats[key]
        delta = None

        if stats_base is not None:
            base_key = _find_metric_key(stats_base, keys)
            if base_key is None:
                continue
            delta_value = value - stats_base[base_key]
            delta = f"{delta_value:.2f}{suffix}" if key != "# Trades" else f"{int(delta_value)}"

        formatted = f"{int(value)}" if key == "# Trades" else f"{value:.2f}{suffix}"
        columns[index % len(columns)].metric(label, formatted, delta=delta)


def _find_metric_key(stats, keys):
    """Retorna la primera clave disponible para una metrica."""
    for key in keys:
        if key in stats.index:
            return key
    return None


def render_best_params(params):
    """Muestra los mejores parametros encontrados."""
    st.success("Optimizacion completada")
    st.write("### Mejores parametros encontrados")

    params_df = pd.DataFrame(params.items(), columns=["Parametro", "Valor"])
    st.dataframe(params_df, use_container_width=True, hide_index=True)

    params_str = ", ".join(f"{key}={value}" for key, value in params.items())
    st.code(params_str, language="python")


def render_optimization_results(results):
    """Muestra los mejores resultados de la optimizacion."""
    st.subheader("Top resultados de optimizacion")

    results_df = pd.DataFrame(results)
    if results_df.empty:
        st.info("No hay resultados de optimizacion para mostrar.")
        return

    results_df = results_df.sort_values("sharpe_ratio", ascending=False).head(10)
    display_df = results_df[
        ["sharpe_ratio", "return", "max_drawdown", "win_rate", "trades", "params"]
    ].copy()
    display_df["sharpe_ratio"] = display_df["sharpe_ratio"].map(lambda value: f"{value:.4f}")
    display_df["return"] = display_df["return"].map(lambda value: f"{value:.2f}%")
    display_df["max_drawdown"] = display_df["max_drawdown"].map(lambda value: f"{value:.2f}%")
    display_df["win_rate"] = display_df["win_rate"].map(lambda value: f"{value:.2f}%")

    display_df.columns = [
        "Sharpe Ratio",
        "Retorno",
        "Drawdown maximo",
        "Win rate",
        "Trades",
        "Parametros",
    ]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
