# ========================================
# data/loader.py
# Descarga y limpieza de datos históricos con yfinance
# ========================================

import yfinance as yf
import pandas as pd
from datetime import datetime
import streamlit as st


class DataNotFoundError(Exception):
    """Excepción personalizada cuando no se encuentran datos"""
    pass


@st.cache_data
def download_data(ticker, start, end):
    """
    Descarga datos históricos de precios usando yfinance.
    
    Args:
        ticker (str): Símbolo del activo (ej: 'AAPL', 'BTC-USD')
        start (str): Fecha de inicio en formato 'YYYY-MM-DD'
        end (str): Fecha de fin en formato 'YYYY-MM-DD'
    
    Returns:
        pd.DataFrame: DataFrame con columnas OHLCV con primera letra mayúscula
    
    Raises:
        DataNotFoundError: Si el ticker no existe o el DataFrame está vacío
    """
    try:
        # Descargar datos históricos
        df = yf.download(ticker, start=start, end=end, progress=False)
        
        # Verificar si el DataFrame está vacío
        if df.empty:
            raise DataNotFoundError(
                f"No se encontraron datos para {ticker} en el rango {start} a {end}. "
                "Verifica que el ticker sea válido."
            )
        
        # Limpiar índice (convertir a columna si es MultiIndex)
        if isinstance(df.index, pd.MultiIndex):
            df = df.reset_index()
        
        # Renombrar columnas a formato requerido por backtesting.py
        # Deben tener primera letra en mayúscula: Open, High, Low, Close, Volume
        df.columns = [col.capitalize() if col.lower() in ['open', 'high', 'low', 'close', 'volume', 'adj close'] 
                      else col for col in df.columns]
        
        # Eliminar filas con valores nulos
        df = df.dropna()
        
        # Verificar que no quede vacío después de limpiar
        if df.empty:
            raise DataNotFoundError(
                f"El DataFrame para {ticker} quedó vacío después de la limpieza. "
                "Intenta con otro rango de fechas."
            )
        
        # Asegurar que el índice sea datetime y esté ordenado
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        return df
    
    except Exception as e:
        # Si es nuestra excepción personalizada, relanzarla
        if isinstance(e, DataNotFoundError):
            raise
        
        # Si yfinance no encuentra datos, también crear excepción personalizada
        raise DataNotFoundError(
            f"Error al descargar datos para {ticker}: {str(e)}. "
            "Verifica que el ticker sea válido (ej: AAPL, BTC-USD, etc.)"
        )

