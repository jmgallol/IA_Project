"""
test_trading_bot_offline.py
Script de prueba SIN conexión a internet - solo valida estructura
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("\n" + "="*70)
print("PRUEBAS OFFLINE DEL TRADING BOT (Sin conexión a Internet)")
print("="*70)

# Test 1: Verificar imports
print("\n[1/7] Verificando imports...")
try:
    from config.settings import DEFAULT_TICKERS, RSI_PARAMS, SMA_PARAMS, MACD_PARAMS, COLORS
    from indicators.technical import add_indicators
    from strategies.rsi_strategy import RSIStrategy
    from strategies.sma_strategy import SMAStrategy
    from strategies.macd_strategy import MACDStrategy
    from backtest.engine import run_backtest, get_readable_stats
    print("✅ Todos los imports funcionan correctamente")
except Exception as e:
    print(f"❌ Error en imports: {e}")
    sys.exit(1)

# Test 2: Verificar configuración
print("\n[2/7] Verificando configuración...")
try:
    assert len(DEFAULT_TICKERS) > 0, "No hay tickers por defecto"
    assert 'ganancia' in COLORS, "No hay color de ganancia"
    assert 'rsi_lower' in RSI_PARAMS, "No hay parámetros RSI"
    assert 'n_short' in SMA_PARAMS, "No hay parámetros SMA"
    assert 'fast' in MACD_PARAMS, "No hay parámetros MACD"
    print(f"✅ Configuración OK:")
    print(f"   - {len(DEFAULT_TICKERS)} tickers: {DEFAULT_TICKERS}")
    print(f"   - {len(COLORS)} colores definidos")
    print(f"   - RSI_PARAMS: {RSI_PARAMS}")
    print(f"   - SMA_PARAMS: {SMA_PARAMS}")
    print(f"   - MACD_PARAMS: {MACD_PARAMS}")
except Exception as e:
    print(f"❌ Error en configuración: {e}")
    sys.exit(1)

# Test 3: Crear datos de prueba sintéticos
print("\n[3/7] Creando datos de prueba sintéticos...")
try:
    # Generar datos OHLCV sintéticos pero realistas
    dates = pd.date_range(start='2024-01-01', periods=200, freq='D')
    prices = 100 + np.cumsum(np.random.randn(200) * 2)  # Precios con drift
    
    df = pd.DataFrame({
        'Open': prices + np.random.randn(200),
        'High': prices + abs(np.random.randn(200)),
        'Low': prices - abs(np.random.randn(200)),
        'Close': prices,
        'Volume': np.random.randint(1000000, 5000000, 200)
    }, index=dates)
    
    assert len(df) == 200, "DataFrame no tiene 200 filas"
    print(f"✅ Datos sintéticos creados: {len(df)} candles")
    print(f"   - Rango de precios: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
except Exception as e:
    print(f"❌ Error creando datos: {e}")
    sys.exit(1)

# Test 4: Calcular indicadores
print("\n[4/7] Calculando indicadores técnicos...")
try:
    df_indicators = add_indicators(df)
    
    required_indicators = ['RSI', 'MACD', 'MACD_Signal', 'SMA_20', 'SMA_50', 
                          'BB_Upper', 'BB_Lower', 'BB_Middle', 'EMA_12', 'EMA_26']
    
    missing = [ind for ind in required_indicators if ind not in df_indicators.columns]
    assert len(missing) == 0, f"Faltan indicadores: {missing}"
    assert len(df_indicators) > 0, "DataFrame vacío después de indicadores"
    
    print(f"✅ Indicadores calculados: {len(df_indicators)} filas válidas")
    print(f"   - RSI: {df_indicators['RSI'].min():.2f} - {df_indicators['RSI'].max():.2f}")
    print(f"   - MACD: {df_indicators['MACD'].min():.4f} - {df_indicators['MACD'].max():.4f}")
    print(f"   - SMA 20: ${df_indicators['SMA_20'].mean():.2f} promedio")
    print(f"   - SMA 50: ${df_indicators['SMA_50'].mean():.2f} promedio")
except Exception as e:
    print(f"❌ Error calculando indicadores: {e}")
    sys.exit(1)

# Test 5: Backtesting RSI
print("\n[5/7] Ejecutando backtesting RSI Strategy...")
try:
    params_rsi = {'rsi_lower': 30, 'rsi_upper': 70}
    stats_rsi = run_backtest(df_indicators, RSIStrategy, params_rsi, cash=10000)
    
    assert stats_rsi is not None, "Stats es None"
    assert 'Return [%]' in stats_rsi, "Falta Return"
    
    retorno = stats_rsi['Return [%]']
    sharpe = stats_rsi['Sharpe Ratio']
    trades = int(stats_rsi['# Trades'])
    
    print(f"✅ RSI Backtesting OK")
    print(f"   - Retorno Total: {retorno:.2f}%")
    print(f"   - Sharpe Ratio: {sharpe:.2f}")
    print(f"   - Trades: {trades}")
    print(f"   - Win Rate: {stats_rsi['Win Rate [%]']:.2f}%")
except Exception as e:
    print(f"❌ Error en backtesting RSI: {e}")
    sys.exit(1)

# Test 6: Backtesting SMA
print("\n[6/7] Ejecutando backtesting SMA Crossover...")
try:
    params_sma = {'n_short': 20, 'n_long': 50}
    stats_sma = run_backtest(df_indicators, SMAStrategy, params_sma, cash=10000)
    
    assert stats_sma is not None, "Stats es None"
    
    retorno = stats_sma['Return [%]']
    sharpe = stats_sma['Sharpe Ratio']
    trades = int(stats_sma['# Trades'])
    
    print(f"✅ SMA Backtesting OK")
    print(f"   - Retorno Total: {retorno:.2f}%")
    print(f"   - Sharpe Ratio: {sharpe:.2f}")
    print(f"   - Trades: {trades}")
    print(f"   - Win Rate: {stats_sma['Win Rate [%]']:.2f}%")
except Exception as e:
    print(f"❌ Error en backtesting SMA: {e}")
    sys.exit(1)

# Test 7: Backtesting MACD
print("\n[7/7] Ejecutando backtesting MACD Strategy...")
try:
    params_macd = {}  # MACD no tiene parámetros optimizables
    stats_macd = run_backtest(df_indicators, MACDStrategy, params_macd, cash=10000)
    
    assert stats_macd is not None, "Stats es None"
    
    retorno = stats_macd['Return [%]']
    sharpe = stats_macd['Sharpe Ratio']
    trades = int(stats_macd['# Trades'])
    
    print(f"✅ MACD Backtesting OK")
    print(f"   - Retorno Total: {retorno:.2f}%")
    print(f"   - Sharpe Ratio: {sharpe:.2f}")
    print(f"   - Trades: {trades}")
    print(f"   - Win Rate: {stats_macd['Win Rate [%]']:.2f}%")
except Exception as e:
    print(f"❌ Error en backtesting MACD: {e}")
    sys.exit(1)

# Resumen final
print("\n" + "="*70)
print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
print("="*70)
print("\n📊 RESUMEN DE BACKTESTS:")
print(f"   RSI Strategy:      ${10000 * (1 + stats_rsi['Return [%]']/100):,.2f}")
print(f"   SMA Crossover:     ${10000 * (1 + stats_sma['Return [%]']/100):,.2f}")
print(f"   MACD Strategy:     ${10000 * (1 + stats_macd['Return [%]']/100):,.2f}")

print("\n🚀 El Trading Bot está listo para ejecutar:")
print("   streamlit run app.py")
print("\n" + "="*70)
