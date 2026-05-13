"""
test_trading_bot.py
Script de prueba para verificar que todos los módulos funcionan correctamente
"""

import sys
from datetime import datetime, timedelta
import pandas as pd

print("\n" + "="*70)
print("PRUEBAS DE MÓDULOS DEL TRADING BOT")
print("="*70)

# Test 1: Verificar imports
print("\n[1/8] Verificando imports...")
try:
    from config.settings import DEFAULT_TICKERS, RSI_PARAMS, SMA_PARAMS, MACD_PARAMS, COLORS
    from data.loader import download_data, DataNotFoundError
    from indicators.technical import add_indicators
    from strategies.rsi_strategy import RSIStrategy
    from strategies.sma_strategy import SMAStrategy
    from strategies.macd_strategy import MACDStrategy
    from backtest.engine import run_backtest, get_readable_stats
    from backtest.optimizer import run_optimization
    print("✅ Todos los imports funcionan correctamente")
except Exception as e:
    print(f"❌ Error en imports: {e}")
    sys.exit(1)

# Test 2: Verificar configuración
print("\n[2/8] Verificando configuración...")
try:
    assert len(DEFAULT_TICKERS) > 0, "No hay tickers por defecto"
    assert 'ganancia' in COLORS, "No hay color de ganancia"
    assert 'rsi_lower' in RSI_PARAMS, "No hay parámetros RSI"
    print(f"✅ Configuración OK: {len(DEFAULT_TICKERS)} tickers, {len(COLORS)} colores")
except Exception as e:
    print(f"❌ Error en configuración: {e}")
    sys.exit(1)

# Test 3: Descargar datos
print("\n[3/8] Descargando datos de prueba (AAPL últimos 100 días)...")
try:
    # Usar fechas históricas válidas (no futuras como 2026)
    end_date = '2024-05-13'  # Fecha fija para test
    start_date = '2024-02-02'  # 100 días antes
    
    df = download_data('AAPL', start_date, end_date)
    assert len(df) > 0, "DataFrame vacío"
    assert 'Close' in df.columns, "Falta columna Close"
    print(f"✅ Datos descargados: {len(df)} candles")
except Exception as e:
    print(f"❌ Error descargando datos: {e}")
    sys.exit(1)

# Test 4: Calcular indicadores
print("\n[4/8] Calculando indicadores técnicos...")
try:
    df_indicators = add_indicators(df)
    assert 'RSI' in df_indicators.columns, "Falta RSI"
    assert 'MACD' in df_indicators.columns, "Falta MACD"
    assert 'SMA_20' in df_indicators.columns, "Falta SMA_20"
    assert len(df_indicators) > 0, "DataFrame vacío después de indicadores"
    print(f"✅ Indicadores calculados: {len(df_indicators)} filas validas")
except Exception as e:
    print(f"❌ Error calculando indicadores: {e}")
    sys.exit(1)

# Test 5: Backtesting RSI
print("\n[5/8] Ejecutando backtesting RSI Strategy...")
try:
    params_rsi = {'rsi_lower': 30, 'rsi_upper': 70}
    stats_rsi = run_backtest(df_indicators, RSIStrategy, params_rsi, cash=10000)
    assert stats_rsi is not None, "Stats es None"
    assert stats_rsi['Return [%]'] is not None, "Falta Return"
    print(f"✅ RSI Backtesting OK - Retorno: {stats_rsi['Return [%]']:.2f}%")
except Exception as e:
    print(f"❌ Error en backtesting RSI: {e}")
    sys.exit(1)

# Test 6: Backtesting SMA
print("\n[6/8] Ejecutando backtesting SMA Crossover...")
try:
    params_sma = {'n_short': 20, 'n_long': 50}
    stats_sma = run_backtest(df_indicators, SMAStrategy, params_sma, cash=10000)
    assert stats_sma is not None, "Stats es None"
    assert stats_sma['Return [%]'] is not None, "Falta Return"
    print(f"✅ SMA Backtesting OK - Retorno: {stats_sma['Return [%]']:.2f}%")
except Exception as e:
    print(f"❌ Error en backtesting SMA: {e}")
    sys.exit(1)

# Test 7: Backtesting MACD
print("\n[7/8] Ejecutando backtesting MACD Strategy...")
try:
    params_macd = {}  # MACD no tiene parámetros optimizables
    stats_macd = run_backtest(df_indicators, MACDStrategy, params_macd, cash=10000)
    assert stats_macd is not None, "Stats es None"
    assert stats_macd['Return [%]'] is not None, "Falta Return"
    print(f"✅ MACD Backtesting OK - Retorno: {stats_macd['Return [%]']:.2f}%")
except Exception as e:
    print(f"❌ Error en backtesting MACD: {e}")
    sys.exit(1)

# Test 8: Verificar extracción de estadísticas
print("\n[8/8] Verificando extracción de estadísticas...")
try:
    stats_dict = get_readable_stats(stats_rsi)
    assert 'Retorno Total (%)' in stats_dict
    assert 'Sharpe Ratio' in stats_dict
    assert 'Drawdown Máximo (%)' in stats_dict
    print(f"✅ Estadísticas extraídas correctamente")
    print(f"   - Retorno Total: {stats_dict['Retorno Total (%)']:.2f}%")
    print(f"   - Sharpe Ratio: {stats_dict['Sharpe Ratio']:.2f}")
    print(f"   - Drawdown Máximo: {stats_dict['Drawdown Máximo (%)']:.2f}%")
except Exception as e:
    print(f"❌ Error extrayendo estadísticas: {e}")
    sys.exit(1)

# Resumen
print("\n" + "="*70)
print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
print("="*70)
print("\nEl Trading Bot está listo para ejecutar:")
print("  streamlit run app.py")
print("\n" + "="*70)
