#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificación de instalación y estructura del Trading Bot
"""

import os
import sys
from pathlib import Path

def check_file_exists(path):
    """Verificar si un archivo existe"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {path}")
    return exists

def check_directory_structure():
    """Verificar que la estructura de directorios es correcta"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE ESTRUCTURA DE DIRECTORIOS")
    print("="*60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_dirs = [
        'config',
        'data', 
        'indicators',
        'strategies',
        'backtest',
        'ui'
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        path = os.path.join(base_dir, dir_name)
        exists = os.path.isdir(path)
        status = "✅" if exists else "❌"
        print(f"{status} Directorio: {dir_name}/")
        if not exists:
            all_exist = False
    
    return all_exist

def check_required_files():
    """Verificar que todos los archivos requeridos existen"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE ARCHIVOS REQUERIDOS")
    print("="*60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        'config/settings.py',
        'data/loader.py',
        'indicators/technical.py',
        'strategies/rsi_strategy.py',
        'strategies/sma_strategy.py',
        'strategies/macd_strategy.py',
        'backtest/engine.py',
        'backtest/optimizer.py',
        'ui/sidebar.py',
        'ui/charts.py',
        'ui/metrics.py',
    ]
    
    all_exist = True
    for file_name in required_files:
        path = os.path.join(base_dir, file_name)
        check_file_exists(path)
        if not os.path.exists(path):
            all_exist = False
    
    return all_exist

def check_imports():
    """Verificar que los imports funcionan correctamente"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE IMPORTACIONES")
    print("="*60)
    
    modules_to_check = [
        ('yfinance', 'yfinance'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('plotly', 'plotly'),
        ('streamlit', 'streamlit'),
        ('backtesting', 'backtesting'),
    ]
    
    all_imported = True
    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - NO INSTALADO")
            all_imported = False
    
    return all_imported

def check_config():
    """Verificar que el archivo de configuración está correcto"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE CONFIGURACIÓN")
    print("="*60)
    
    try:
        from config.settings import (
            DEFAULT_TICKERS,
            RSI_PARAMS,
            SMA_PARAMS,
            MACD_PARAMS,
            COLORS,
            CAPITAL_INICIAL_DEFAULT
        )
        
        print(f"✅ DEFAULT_TICKERS: {len(DEFAULT_TICKERS)} tickers")
        print(f"✅ RSI_PARAMS configurado")
        print(f"✅ SMA_PARAMS configurado")
        print(f"✅ MACD_PARAMS configurado")
        print(f"✅ COLORS configurado: {len(COLORS)} colores")
        print(f"✅ CAPITAL_INICIAL_DEFAULT: ${CAPITAL_INICIAL_DEFAULT:,.0f}")
        return True
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return False

def check_strategies():
    """Verificar que las estrategias están implementadas"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE ESTRATEGIAS")
    print("="*60)
    
    strategies_ok = True
    try:
        from strategies.rsi_strategy import RSIStrategy
        print("✅ RSIStrategy")
    except Exception as e:
        print(f"❌ RSIStrategy: {e}")
        strategies_ok = False
    
    try:
        from strategies.sma_strategy import SMAStrategy
        print("✅ SMAStrategy")
    except Exception as e:
        print(f"❌ SMAStrategy: {e}")
        strategies_ok = False
    
    try:
        from strategies.macd_strategy import MACDStrategy
        print("✅ MACDStrategy")
    except Exception as e:
        print(f"❌ MACDStrategy: {e}")
        strategies_ok = False
    
    return strategies_ok

def main():
    """Ejecutar todas las verificaciones"""
    print("\n" + "🔍 VERIFICACIÓN COMPLETA DEL TRADING BOT\n")
    
    checks = [
        ("Estructura de directorios", check_directory_structure),
        ("Archivos requeridos", check_required_files),
        ("Importaciones", check_imports),
        ("Configuración", check_config),
        ("Estrategias", check_strategies),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n⚠️ Error en verificación {check_name}: {e}")
            results[check_name] = False
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    
    all_passed = all(results.values())
    
    for check_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status}: {check_name}")
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ TODA LA VERIFICACIÓN PASÓ EXITOSAMENTE")
        print("\n🚀 Puedes ejecutar la aplicación con:")
        print("   streamlit run app.py")
        return 0
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("\n⚠️ Por favor, instala las dependencias:")
        print("   pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
