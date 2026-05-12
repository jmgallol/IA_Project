from backtesting import Backtest


PRICE_COLUMNS = ["Open", "High", "Low", "Close"]
VOLUME_COLUMN = "Volume"
FRACTIONAL_UNIT = 1_000_000


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
