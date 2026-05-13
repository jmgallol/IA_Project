# ========================================
# indicators/technical.py
# Cálculo de indicadores técnicos con pandas-ta
# ========================================

import pandas as pd
import numpy as np


def add_indicators(df):
    """
    Añade indicadores técnicos al DataFrame de precios.
    
    Indicadores calculados:
    - RSI (14 periodos)
    - MACD, señal y histograma
    - Bandas de Bollinger (20 periodos, 2 desv. estándar)
    - SMA de 20 y 50 periodos
    - EMA de 12 y 26 periodos (para MACD)
    
    Args:
        df (pd.DataFrame): DataFrame con columnas OHLCV (Open, High, Low, Close, Volume)
    
    Returns:
        pd.DataFrame: DataFrame original con columnas adicionales de indicadores
    """
    
    # Crear copia para no modificar el DataFrame original
    df = df.copy()
    
    # Asegurar que Close es numérico
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    
    # ===== RSI (14 periodos) =====
    df['RSI'] = _calculate_rsi(df['Close'], 14)
    
    # ===== SMA (Media Móvil Simple) =====
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # ===== EMA (Media Móvil Exponencial) para MACD =====
    df['EMA_12'] = _calculate_ema(df['Close'], 12)
    df['EMA_26'] = _calculate_ema(df['Close'], 26)
    
    # ===== MACD (12, 26, 9) =====
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = _calculate_ema(df['MACD'], 9)
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # ===== Bandas de Bollinger (20, 2) =====
    sma_20 = df['Close'].rolling(window=20).mean()
    std_20 = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = sma_20 + (std_20 * 2)
    df['BB_Middle'] = sma_20
    df['BB_Lower'] = sma_20 - (std_20 * 2)
    
    # Eliminar filas NaN que pudieron generarse al calcular indicadores
    df = df.dropna()
    
    return df


def _calculate_rsi(prices, period=14):
    """
    Calcula el RSI (Relative Strength Index).
    
    Args:
        prices (pd.Series): Serie de precios de cierre
        period (int): Período del RSI (default 14)
    
    Returns:
        pd.Series: Serie con valores RSI
    """
    # Calcular cambios
    delta = prices.diff()
    
    # Ganancias y pérdidas
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    # Evitar división por cero
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def _calculate_ema(prices, period=12):
    """
    Calcula la EMA (Media Móvil Exponencial).
    
    Args:
        prices (pd.Series): Serie de precios
        period (int): Período de la EMA
    
    Returns:
        pd.Series: Serie con valores EMA
    """
    return prices.ewm(span=period, adjust=False).mean()

