# ========================================
# backtest/optimizer.py
# Lógica de optimización de parámetros con grid search
# ========================================

import streamlit as st
from itertools import product
from backtest.engine import run_backtest


def run_optimization(df, strategy_class, param_grid, cash=10000):
    """
    Ejecuta optimización de parámetros usando grid search.
    Busca maximizar el Sharpe Ratio.
    
    Args:
        df (pd.DataFrame): DataFrame con datos OHLCV e indicadores
        strategy_class: Clase de Strategy (RSIStrategy, SMAStrategy, MACDStrategy)
        param_grid (dict): Diccionario con parámetros a optimizar
                           Ejemplo: {'rsi_lower': range(20, 41), 'rsi_upper': range(60, 81)}
        cash (float): Capital inicial en USD (por defecto 10,000)
    
    Returns:
        tuple: (best_params (dict), best_stats (backtesting.Stats), all_results (list))
    """
    
    # Generar todas las combinaciones de parámetros
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    
    # Convertir ranges a listas si es necesario
    param_values = [list(pv) if isinstance(pv, range) else pv for pv in param_values]
    
    # Crear todas las combinaciones
    combinations = list(product(*param_values))
    total_combinations = len(combinations)
    
    best_sharpe = float('-inf')
    best_params = None
    best_stats = None
    all_results = []
    
    # Mostrar progreso con spinner
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Iterar sobre todas las combinaciones de parámetros
    for idx, values in enumerate(combinations):
        # Crear diccionario de parámetros para esta iteración
        params = dict(zip(param_names, values))
        
        try:
            # Ejecutar backtesting con estos parámetros
            stats = run_backtest(df, strategy_class, params, cash=cash)
            
            # Obtener el Sharpe Ratio
            sharpe_ratio = stats['Sharpe Ratio']
            
            # Si no hay un valor válido para Sharpe, saltar
            if sharpe_ratio != sharpe_ratio:  # Detectar NaN
                sharpe_ratio = float('-inf')
            
            # Guardar resultado
            result = {
                'params': params.copy(),
                'sharpe_ratio': sharpe_ratio,
                'return': stats['Return [%]'],
                'max_drawdown': stats['Max. Drawdown [%]'],
                'win_rate': stats['Win Rate [%]'],
                'trades': int(stats['# Trades'])
            }
            all_results.append(result)
            
            # Actualizar mejor resultado si es necesario
            if sharpe_ratio > best_sharpe:
                best_sharpe = sharpe_ratio
                best_params = params.copy()
                best_stats = stats
        
        except Exception as e:
            # Continuar con la siguiente combinación si hay error
            pass
        
        # Actualizar barra de progreso
        progress = (idx + 1) / total_combinations
        progress_bar.progress(progress)
        status_text.text(f"Optimizando: {idx + 1}/{total_combinations} combinaciones")
    
    # Limpiar indicadores de progreso
    progress_bar.empty()
    status_text.empty()
    
    if best_params is None:
        raise ValueError("No se encontraron parámetros válidos en la optimización")
    
    return best_params, best_stats, all_results
