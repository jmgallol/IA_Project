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
    strategy_final_equity = get_final_equity(strategy_stats)
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


def render_strategy_comparison_table(strategy_results, buy_hold_stats):
    """Muestra una tabla con estrategias optimizadas y Buy & Hold."""
    rows = []
    for result in strategy_results:
        stats = result["stats"]
        rows.append(
            {
                "Estrategia": result["strategy"],
                "Mejores parametros": _format_params(result["best_params"]),
                "Retorno total": f"{safe_metric(stats, 'Return [%]'):.2f}%",
                "Sharpe Ratio": f"{safe_metric(stats, 'Sharpe Ratio'):.2f}",
                "Drawdown maximo": f"{safe_metric(stats, 'Max. Drawdown [%]'):.2f}%",
                "Win Rate": f"{safe_metric(stats, 'Win Rate [%]'):.2f}%",
                "Operaciones": int(safe_metric(stats, "# Trades")),
                "Capital final": f"${get_final_equity(stats):,.2f}",
            }
        )

    rows.append(
        {
            "Estrategia": "Buy & Hold",
            "Mejores parametros": "Compra inicial y mantener",
            "Retorno total": f"{buy_hold_stats['return_pct']:.2f}%",
            "Sharpe Ratio": f"{buy_hold_stats['sharpe_ratio']:.2f}",
            "Drawdown maximo": f"{buy_hold_stats['max_drawdown_pct']:.2f}%",
            "Win Rate": "N/A",
            "Operaciones": "1 compra",
            "Capital final": f"${buy_hold_stats['final_equity']:,.2f}",
        }
    )

    st.subheader("Tabla comparativa")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_strategy_winners(winners):
    """Resume que estrategia gano por cada criterio."""
    st.subheader("Mejores estrategias por criterio")
    cols = st.columns(4)
    cols[0].metric("Mayor retorno", winners["highest_return"]["strategy"])
    cols[1].metric("Menor drawdown", winners["lowest_drawdown"]["strategy"])
    cols[2].metric("Mejor Sharpe", winners["best_sharpe"]["strategy"])
    cols[3].metric("Mas equilibrada", winners["balanced"]["strategy"])

    st.info(
        "La estrategia mas equilibrada usa el score: "
        "Sharpe Ratio - abs(Drawdown maximo) * 0.5."
    )


def render_comparison_guide():
    """Explica como leer la comparacion sin dar recomendaciones financieras."""
    st.subheader("Como interpretar la comparacion")
    st.markdown(
        """
        - Cada estrategia responde a una logica diferente.
        - RSI busca posibles zonas de sobrecompra o sobreventa, asociadas a reversion a la media.
        - SMA Crossover y MACD siguen cruces y cambios de tendencia o momentum.
        - Buy & Hold sirve como linea base: comprar al inicio y mantener hasta el final.
        - La mejor estrategia no siempre es la de mayor retorno, porque tambien importa el riesgo.
        - Una estrategia equilibrada debe considerar retorno, Sharpe Ratio, drawdown y numero de operaciones.
        - Los resultados son historicos y no garantizan resultados futuros.
        """
    )


def build_comparison_summary(strategy_results, buy_hold_stats, winners):
    """Crea un resumen simple para que el asistente pueda responder preguntas."""
    rows = []
    for result in strategy_results:
        stats = result["stats"]
        rows.append(
            {
                "strategy": result["strategy"],
                "best_params": result["best_params"],
                "return_pct": safe_metric(stats, "Return [%]"),
                "sharpe_ratio": safe_metric(stats, "Sharpe Ratio"),
                "max_drawdown_pct": safe_metric(stats, "Max. Drawdown [%]"),
                "win_rate_pct": safe_metric(stats, "Win Rate [%]"),
                "trades": int(safe_metric(stats, "# Trades")),
                "final_equity": get_final_equity(stats),
                "balanced_score": calculate_balanced_score(stats),
                "beats_buy_hold": safe_metric(stats, "Return [%]") > buy_hold_stats["return_pct"],
            }
        )

    return {
        "rows": rows,
        "buy_hold": {
            "return_pct": buy_hold_stats["return_pct"],
            "sharpe_ratio": buy_hold_stats["sharpe_ratio"],
            "max_drawdown_pct": buy_hold_stats["max_drawdown_pct"],
            "final_equity": buy_hold_stats["final_equity"],
        },
        "winners": {
            key: value["strategy"]
            for key, value in winners.items()
        },
    }


def safe_metric(stats, key, default=0.0):
    """Obtiene una metrica evitando NaN o infinitos."""
    try:
        value = float(stats[key])
    except Exception:
        return default

    if pd.isna(value) or value in (float("inf"), float("-inf")):
        return default

    return value


def calculate_balanced_score(stats):
    return safe_metric(stats, "Sharpe Ratio") - abs(safe_metric(stats, "Max. Drawdown [%]")) * 0.5


def get_final_equity(stats):
    if "Equity Final [$]" in stats.index:
        return float(stats["Equity Final [$]"])

    equity_curve = stats._equity_curve
    equity = equity_curve["Equity"] if "Equity" in equity_curve.columns else equity_curve.iloc[:, 0]
    return float(equity.iloc[-1])


def _format_params(params):
    if not params:
        return "N/A"

    return ", ".join(f"{key}={value}" for key, value in params.items())


def render_executive_summary(stats, buy_hold_stats, strategy_name):
    """
    Muestra un resumen ejecutivo de 5 metricas clave en una fila.
    
    Perfecto para ver de un vistazo si la estrategia funciono bien.
    
    Args:
        stats: Estadísticas del backtesting de la estrategia
        buy_hold_stats: Estadísticas de Buy & Hold
        strategy_name: Nombre de la estrategia evaluada
    """
    st.subheader('Resumen Ejecutivo')
    
    return_pct = stats["Return [%]"]
    bh_return = buy_hold_stats["return_pct"]
    outperformance = return_pct - bh_return
    sharpe_ratio = stats["Sharpe Ratio"]
    max_drawdown = stats["Max. Drawdown [%]"]
    trades = int(stats["# Trades"])
    final_equity = get_final_equity(stats)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Retorno Total",
            f"{return_pct:.1f}%",
            delta=f"{outperformance:+.1f}% vs B&H" if outperformance != 0 else "Igual a B&H"
        )
    
    with col2:
        st.metric(
            "Sharpe Ratio",
            f"{sharpe_ratio:.2f}",
            delta=f"{sharpe_ratio - buy_hold_stats['sharpe_ratio']:+.2f}" if buy_hold_stats.get('sharpe_ratio') else None
        )
    
    with col3:
        st.metric(
            "Drawdown Maximo",
            f"{max_drawdown:.1f}%",
            delta=f"{max_drawdown - buy_hold_stats['max_drawdown_pct']:+.1f}%" if buy_hold_stats.get('max_drawdown_pct') else None
        )
    
    with col4:
        st.metric(
            "Capital Final",
            f"${final_equity:,.0f}"
        )
    
    with col5:
        st.metric(
            "Operaciones Ejecutadas",
            f"{trades}"
        )
