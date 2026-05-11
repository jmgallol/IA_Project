import pandas as pd
import yfinance as yf


class DataNotFoundError(Exception):
    """Excepcion usada cuando no se encuentran datos validos."""


REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def download_data(ticker, start, end):
    """
    Descarga y limpia precios historicos desde Yahoo Finance.

    Args:
        ticker: simbolo del activo, por ejemplo AAPL o BTC-USD.
        start: fecha inicial en formato YYYY-MM-DD.
        end: fecha final en formato YYYY-MM-DD.

    Returns:
        DataFrame con columnas Open, High, Low, Close y Volume.
    """
    try:
        data = yf.download(
            ticker,
            start=start,
            end=end,
            progress=False,
            threads=False,
            timeout=15,
        )
        data = _normalize_columns(data)
        data = _validate_data(data, ticker, start, end)
        return data
    except DataNotFoundError:
        raise
    except Exception as error:
        raise DataNotFoundError(
            f"Error al descargar datos para {ticker}: {error}. "
            "Verifica la conexion a Yahoo Finance o usa el modo demostracion."
        ) from error


def _normalize_columns(data):
    """Normaliza columnas de yfinance al formato esperado por backtesting.py."""
    if data.empty:
        return data

    normalized = data.copy()

    if isinstance(normalized.columns, pd.MultiIndex):
        normalized.columns = normalized.columns.get_level_values(0)

    rename_map = {
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "adj close": "Adj Close",
        "volume": "Volume",
    }
    normalized = normalized.rename(columns=lambda column: rename_map.get(str(column).lower(), column))

    return normalized


def _validate_data(data, ticker, start, end):
    """Valida que el DataFrame descargado tenga datos suficientes."""
    if data.empty:
        raise DataNotFoundError(
            f"No se encontraron datos para {ticker} entre {start} y {end}."
        )

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing_columns:
        raise DataNotFoundError(
            f"Los datos de {ticker} no contienen las columnas requeridas: {missing_columns}."
        )

    clean_data = data[REQUIRED_COLUMNS].apply(pd.to_numeric, errors="coerce").dropna()

    if clean_data.empty:
        raise DataNotFoundError(
            f"Los datos de {ticker} quedaron vacios despues de la limpieza."
        )

    clean_data.index = pd.to_datetime(clean_data.index)
    return clean_data.sort_index()
