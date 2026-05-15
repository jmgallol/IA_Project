import numpy as np
import pandas as pd
from backtesting import Backtest


PRICE_COLUMNS = ["Open", "High", "Low", "Close"]
VOLUME_COLUMN = "Volume"
FRACTIONAL_UNIT = 1_000_000
TRADING_PERIODS_PER_YEAR = 252


def run_backtest(df, strategy_class, params, cash=10000):
    """
    Ejecuta un backtesting con los parametros especificados.

    backtesting.py 0.3.3 no permite operar fracciones del activo. Cuando el
    precio del activo es mayor al capital inicial, el motor escala los precios
    para simular operacion en micro-unidades, util para BTC y otros activos
    caros. Las metricas porcentuales permanecen comparables.
    """
    try:
        required_columns = PRICE_COLUMNS + [VOLUME_COLUMN]
        missing_columns = [column for column in required_columns if column not in df.columns]

        if missing_columns:
            raise ValueError(f"Faltan columnas requeridas: {missing_columns}")

        if df.empty:
            raise ValueError("El DataFrame esta vacio")

        backtest_data, price_scale = _prepare_backtest_data(df, cash)

        backtest = Backtest(
            backtest_data,
            strategy_class,
            cash=cash,
            commission=0.001,
            exclusive_orders=True,
            trade_on_close=True,
        )
        stats = backtest.run(**params)
        stats.attrs["price_scale"] = price_scale

        return stats
    except Exception as error:
        raise ValueError(f"Error ejecutando backtesting: {error}") from error


def _prepare_backtest_data(df, cash):
    """
    Escala OHLCV cuando el precio supera el capital inicial.

    Ejemplo: si BTC vale 60,000 USD y el capital es 1,000 USD, se opera sobre
    microBTC. Esto evita backtests con cero operaciones por falta de soporte
    fraccional en la version instalada de backtesting.py.
    """
    max_price = float(df["Close"].max())
    if max_price <= cash:
        return df, 1.0

    scaled_data = df.copy()
    price_scale = 1 / FRACTIONAL_UNIT
    scaled_data[PRICE_COLUMNS] = scaled_data[PRICE_COLUMNS] * price_scale

    if VOLUME_COLUMN in scaled_data.columns:
        scaled_data[VOLUME_COLUMN] = scaled_data[VOLUME_COLUMN] * FRACTIONAL_UNIT

    return scaled_data, price_scale


def calculate_buy_hold(df, cash=10000):
    """
    Calcula una linea base Buy & Hold sobre el mismo periodo del backtest.

    La estrategia compra el activo al primer cierre disponible y mantiene la
    posicion hasta el final. Las metricas se calculan desde la curva de capital
    para compararlas contra la estrategia evaluada.
    """
    if df.empty:
        raise ValueError("El DataFrame esta vacio")

    if "Close" not in df.columns:
        raise ValueError("Falta la columna requerida: Close")

    close = df["Close"].dropna()
    if close.empty:
        raise ValueError("No hay precios de cierre validos para Buy & Hold")

    initial_price = float(close.iloc[0])
    final_price = float(close.iloc[-1])
    if initial_price <= 0:
        raise ValueError("El precio inicial debe ser mayor que cero")

    quantity = cash / initial_price
    equity = close * quantity
    equity.name = "Equity"

    total_return = ((equity.iloc[-1] - cash) / cash) * 100
    max_drawdown = _calculate_max_drawdown(equity)
    returns = equity.pct_change().dropna()
    volatility = returns.std() * np.sqrt(TRADING_PERIODS_PER_YEAR) * 100
    sharpe_ratio = _calculate_sharpe_ratio(returns)

    return {
        "initial_capital": cash,
        "initial_price": initial_price,
        "final_price": final_price,
        "quantity": quantity,
        "final_equity": float(equity.iloc[-1]),
        "return_pct": float(total_return),
        "max_drawdown_pct": float(max_drawdown),
        "volatility_pct": float(volatility) if pd.notna(volatility) else 0.0,
        "sharpe_ratio": float(sharpe_ratio),
        "equity_curve": equity,
    }


def _calculate_max_drawdown(equity):
    running_max = equity.cummax()
    drawdown = (equity / running_max - 1) * 100
    return drawdown.min()


def _calculate_sharpe_ratio(returns):
    if returns.empty:
        return 0.0

    volatility = returns.std()
    if pd.isna(volatility) or volatility == 0:
        return 0.0

    return (returns.mean() / volatility) * np.sqrt(TRADING_PERIODS_PER_YEAR)


def get_readable_stats(stats):
    """Extrae metricas clave del objeto stats."""
    annual_return_key = (
        "Return (Ann.) [%]" if "Return (Ann.) [%]" in stats.index else "Annual Return [%]"
    )
    return {
        "Retorno Total (%)": stats["Return [%]"],
        "Retorno Anual (%)": stats[annual_return_key],
        "Sharpe Ratio": stats["Sharpe Ratio"],
        "Drawdown Maximo (%)": stats["Max. Drawdown [%]"],
        "Win Rate (%)": stats["Win Rate [%]"],
        "Operaciones": int(stats["# Trades"]),
        "Duracion Promedio": stats["Avg. Trade Duration"],
        "Factor de Ganancias": stats["Profit Factor"],
        "Exposicion (%)": stats["Exposure Time [%]"],
    }
