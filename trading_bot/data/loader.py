import json
import shutil
import subprocess
from datetime import datetime, time, timezone
from urllib.parse import quote

import pandas as pd
import requests


class DataNotFoundError(Exception):
    """Excepcion usada cuando no se encuentran datos validos."""


REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]
CURL_TIMEOUT_SECONDS = 20


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
    errors = []

    try:
        data = _download_from_yahoo_chart(ticker, start, end)
        return _validate_data(data, ticker, start, end)
    except Exception as error:
        errors.append(f"Yahoo chart: {error}")

    details = " | ".join(errors)
    raise DataNotFoundError(
        f"No fue posible descargar datos reales para {ticker} entre {start} y {end}. "
        f"Detalle: {details}. Puedes activar el modo demostracion para probar la app."
    )


def _download_from_yahoo_chart(ticker, start, end):
    """Descarga OHLCV desde el endpoint chart de Yahoo cuando yfinance falla."""
    period1 = _date_to_timestamp(start, is_end=False)
    period2 = _date_to_timestamp(end, is_end=True)
    encoded_ticker = quote(ticker.upper(), safe="")
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded_ticker}"
        f"?period1={period1}&period2={period2}&interval=1d&events=history"
        "&includeAdjustedClose=true"
    )
    headers = {"User-Agent": "Mozilla/5.0"}

    payload = _request_json(url, headers)
    chart = payload.get("chart", {})
    error = chart.get("error")
    if error:
        raise DataNotFoundError(error.get("description", str(error)))

    results = chart.get("result") or []
    if not results:
        raise DataNotFoundError("Yahoo no retorno resultados.")

    result = results[0]
    timestamps = result.get("timestamp") or []
    quote_data = (result.get("indicators", {}).get("quote") or [{}])[0]

    if not timestamps or not quote_data:
        raise DataNotFoundError("Yahoo retorno una respuesta sin precios OHLCV.")

    data = pd.DataFrame(
        {
            "Open": quote_data.get("open"),
            "High": quote_data.get("high"),
            "Low": quote_data.get("low"),
            "Close": quote_data.get("close"),
            "Volume": quote_data.get("volume"),
        },
        index=pd.to_datetime(timestamps, unit="s").normalize(),
    )
    return data


def _request_json(url, headers):
    """Obtiene JSON de Yahoo evitando bloqueos largos del stack HTTP de Python."""
    if shutil.which("curl.exe"):
        result = subprocess.run(
            [
                "curl.exe",
                "-L",
                "--silent",
                "--show-error",
                "--max-time",
                str(CURL_TIMEOUT_SECONDS),
                "-H",
                f"User-Agent: {headers['User-Agent']}",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=CURL_TIMEOUT_SECONDS + 5,
        )

        response_text = result.stdout.strip() or result.stderr.strip()
        if result.returncode != 0:
            raise DataNotFoundError(response_text or "curl no pudo consultar Yahoo Finance.")
        return _parse_yahoo_response(response_text)

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return _parse_yahoo_response(response.text)


def _parse_yahoo_response(response_text):
    """Parsea respuesta de Yahoo y detecta bloqueos por limite de solicitudes."""
    if "Too Many Requests" in response_text:
        raise DataNotFoundError(
            "Yahoo Finance bloqueo temporalmente la consulta por limite de solicitudes."
        )
    try:
        return json.loads(response_text)
    except ValueError as error:
        raise DataNotFoundError(
            f"Yahoo retorno una respuesta no valida: {response_text[:120]}"
        ) from error


def _date_to_timestamp(date_value, is_end):
    """Convierte una fecha YYYY-MM-DD a timestamp UTC para Yahoo Finance."""
    parsed_date = datetime.strptime(str(date_value), "%Y-%m-%d").date()
    date_time = datetime.combine(parsed_date, time.max if is_end else time.min)
    return int(date_time.replace(tzinfo=timezone.utc).timestamp())


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
