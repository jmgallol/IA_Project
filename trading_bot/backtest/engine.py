# ========================================
# backtest/engine.py
# Motor de ejecución del backtesting con backtesting.py
# ========================================

from backtesting import Backtest
import pandas as pd


def run_backtest(df, strategy_class, params, cash=10000):
    """
    Ejecuta un backtesting con los parámetros especificados.
    
    Args:
        df (pd.DataFrame): DataFrame con datos OHLCV e indicadores técnicos
        strategy_class: Clase de Strategy (RSIStrategy, SMAStrategy, MACDStrategy)
        params (dict): Diccionario con los parámetros de la estrategia
                       Ejemplo: {'rsi_lower': 30, 'rsi_upper': 70}
        cash (float): Capital inicial en USD (por defecto 10,000)
    
    Returns:
        backtesting.Stats: Objeto con resultados completos del backtesting
    
    Raises:
        ValueError: Si hay error en los parámetros o datos
    """
    
    try:
        # Verificar que el DataFrame tiene las columnas requeridas
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Faltan columnas requeridas: {missing_columns}")
        
        # Verificar que el DataFrame no está vacío
        if df.empty:
            raise ValueError("El DataFrame está vacío")
        
        # Crear instancia de Backtest
        bt = Backtest(
            df,
            strategy_class,
            cash=cash,
            commission=0.001,  # 0.1% de comisión por operación
            exclusive_orders=True,
            trade_on_close=True  # Mayor realismo: ejecuta al cierre de la barra
        )
        
        # Ejecutar backtesting con los parámetros especificados
        stats = bt.run(**params)
        
        return stats
    
    except Exception as e:
        raise ValueError(f"Error ejecutando backtesting: {str(e)}")


def get_readable_stats(stats):
    """
    Extrae estadísticas legibles del objeto stats.
    
    Args:
        stats (backtesting.Stats): Objeto de resultados del backtesting
    
    Returns:
        dict: Diccionario con métricas clave formateadas
    """
    
    stats_dict = {
        'Retorno Total (%)': stats['Return [%]'],
        'Retorno Anual (%)': stats['Annual Return [%]'],
        'Sharpe Ratio': stats['Sharpe Ratio'],
        'Drawdown Máximo (%)': stats['Max. Drawdown [%]'],
        'Win Rate (%)': stats['Win Rate [%]'],
        'Operaciones': int(stats['# Trades']),
        'Duración Promedio': stats['Avg. Trade Duration'],
        'Factor de Ganancias': stats['Profit Factor'],
        'Exposición (%)': stats['Exposure Time [%]'],
    }
    
    return stats_dict
