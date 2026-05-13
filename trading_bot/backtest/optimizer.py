from itertools import product
from math import isfinite

from backtest.engine import run_backtest


def run_optimization(
    df,
    strategy_class,
    param_grid,
    cash=10000,
    progress_callback=None,
    objective="sharpe",
):
    """
    Ejecuta una busqueda exhaustiva de parametros usando grid search.

    Args:
        df: DataFrame con columnas OHLCV.
        strategy_class: clase de estrategia compatible con backtesting.py.
        param_grid: diccionario con listas o rangos de valores por parametro.
        cash: capital inicial.
        progress_callback: funcion opcional con firma (current, total, params).
        objective: "sharpe" o "risk_adjusted".

    Returns:
        tuple: (best_params, best_stats, all_results).
    """
    param_names = list(param_grid.keys())
    param_values = [
        list(values) if isinstance(values, range) else list(values)
        for values in param_grid.values()
    ]
    combinations = list(product(*param_values))

    best_score = float("-inf")
    best_params = None
    best_stats = None
    all_results = []
    errors = []

    for index, values in enumerate(combinations, start=1):
        params = dict(zip(param_names, values))

        try:
            stats = run_backtest(df, strategy_class, params, cash=cash)
            sharpe_ratio = stats["Sharpe Ratio"]

            if not isfinite(sharpe_ratio):
                sharpe_ratio = float("-inf")

            score = calculate_optimization_score(stats, objective=objective)

            result = {
                "params": params.copy(),
                "score": score,
                "sharpe_ratio": sharpe_ratio,
                "return": stats["Return [%]"],
                "max_drawdown": stats["Max. Drawdown [%]"],
                "win_rate": stats["Win Rate [%]"],
                "trades": int(stats["# Trades"]),
            }
            all_results.append(result)

            if score > best_score:
                best_score = score
                best_params = params.copy()
                best_stats = stats
        except Exception as error:
            errors.append({"params": params.copy(), "error": str(error)})

        if progress_callback is not None:
            progress_callback(index, len(combinations), params)

    if best_params is None:
        details = errors[:3]
        raise ValueError(f"No se encontraron parametros validos. Errores iniciales: {details}")

    return best_params, best_stats, all_results


def calculate_optimization_score(stats, objective="sharpe"):
    """Calcula la funcion objetivo usada por el grid search."""
    sharpe_ratio = stats["Sharpe Ratio"]
    if not isfinite(sharpe_ratio):
        sharpe_ratio = float("-inf")

    if objective == "risk_adjusted":
        return sharpe_ratio - abs(stats["Max. Drawdown [%]"]) * 0.5

    if objective != "sharpe":
        raise ValueError(f"Funcion objetivo no soportada: {objective}")

    return sharpe_ratio
