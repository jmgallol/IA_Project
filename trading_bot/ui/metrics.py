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
        ("Capital final", ("Equity Final [$]",), "$"),
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
            if key == "# Trades":
                delta = f"{int(delta_value)}"
            elif suffix == "$":
                delta = f"${delta_value:,.2f}"
            else:
                delta = f"{delta_value:.2f}{suffix}"

        if key == "# Trades":
            formatted = f"{int(value)}"
        elif suffix == "$":
            formatted = f"${value:,.2f}"
        else:
            formatted = f"{value:.2f}{suffix}"
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

    sort_column = "score" if "score" in results_df.columns else "sharpe_ratio"
    results_df = results_df.sort_values(sort_column, ascending=False).head(10)
    display_df = results_df[
        ["score", "sharpe_ratio", "return", "max_drawdown", "win_rate", "trades", "params"]
    ].copy()
    display_df["score"] = display_df["score"].map(lambda value: f"{value:.4f}")
    display_df["sharpe_ratio"] = display_df["sharpe_ratio"].map(lambda value: f"{value:.4f}")
    display_df["return"] = display_df["return"].map(lambda value: f"{value:.2f}%")
    display_df["max_drawdown"] = display_df["max_drawdown"].map(lambda value: f"{value:.2f}%")
    display_df["win_rate"] = display_df["win_rate"].map(lambda value: f"{value:.2f}%")

    display_df.columns = [
        "Score",
        "Sharpe Ratio",
        "Retorno",
        "Drawdown maximo",
        "Win rate",
        "Trades",
        "Parametros",
    ]
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_buy_hold_comparison(strategy_stats, buy_hold_stats):
    """Muestra una comparacion directa entre estrategia y Buy & Hold."""
    strategy_return = strategy_stats["Return [%]"]
    strategy_sharpe = strategy_stats["Sharpe Ratio"]
    strategy_drawdown = strategy_stats["Max. Drawdown [%]"]
    strategy_final_equity = _get_final_equity(strategy_stats)
    buy_hold_return = buy_hold_stats["return_pct"]
    buy_hold_sharpe = buy_hold_stats["sharpe_ratio"]
    buy_hold_drawdown = buy_hold_stats["max_drawdown_pct"]
    return_diff = strategy_return - buy_hold_return

    st.subheader("Comparacion contra Buy & Hold")
    cols = st.columns(4)
    cols[0].metric("Retorno estrategia", f"{strategy_return:.2f}%")
    cols[1].metric("Retorno Buy & Hold", f"{buy_hold_return:.2f}%")
    cols[2].metric("Diferencia retorno", f"{return_diff:.2f}%")
    cols[3].metric("Capital final estrategia", f"${strategy_final_equity:,.2f}")

    comparison = pd.DataFrame(
        [
            {
                "Metrica": "Capital final",
                "Estrategia": f"${strategy_final_equity:,.2f}",
                "Buy & Hold": f"${buy_hold_stats['final_equity']:,.2f}",
            },
            {
                "Metrica": "Retorno total",
                "Estrategia": f"{strategy_return:.2f}%",
                "Buy & Hold": f"{buy_hold_return:.2f}%",
            },
            {
                "Metrica": "Sharpe Ratio",
                "Estrategia": f"{strategy_sharpe:.2f}",
                "Buy & Hold": f"{buy_hold_sharpe:.2f}",
            },
            {
                "Metrica": "Drawdown maximo",
                "Estrategia": f"{strategy_drawdown:.2f}%",
                "Buy & Hold": f"{buy_hold_drawdown:.2f}%",
            },
            {
                "Metrica": "Volatilidad anual",
                "Estrategia": "Calculada por backtesting.py",
                "Buy & Hold": f"{buy_hold_stats['volatility_pct']:.2f}%",
            },
        ]
    )
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    if return_diff > 0:
        st.success(
            "La estrategia supero a Buy & Hold en retorno total para este periodo historico."
        )
    else:
        st.warning(
            "Buy & Hold obtuvo mejor retorno total que la estrategia en este periodo historico."
        )


def _get_final_equity(stats):
    if "Equity Final [$]" in stats.index:
        return float(stats["Equity Final [$]"])

    equity_curve = stats._equity_curve
    equity = equity_curve["Equity"] if "Equity" in equity_curve.columns else equity_curve.iloc[:, 0]
    return float(equity.iloc[-1])
