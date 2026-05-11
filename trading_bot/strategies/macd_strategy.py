# ========================================
# strategies/macd_strategy.py
# Estrategia basada en MACD (Moving Average Convergence Divergence)
# ========================================

from backtesting import Strategy
import pandas as pd


class MACDStrategy(Strategy):
    """
    Estrategia de trading basada en el indicador MACD.
    
    Lógica:
    - Compra cuando la línea MACD cruza hacia arriba la línea de señal
    - Vende cuando la línea MACD cruza hacia abajo la línea de señal
    
    El MACD se compone de:
    - Línea MACD: diferencia entre EMA(12) y EMA(26)
    - Línea de Señal: EMA(9) del MACD
    - Histograma: diferencia entre MACD y Señal
    """
    
    def init(self):
        """Inicializar la estrategia al comenzar el backtesting"""
        pass
    
    def next(self):
        """Lógica de decisión ejecutada en cada barra"""
        
        # Verificar que los indicadores existen en los datos
        if not hasattr(self.data, 'MACD') or not hasattr(self.data, 'MACD_Signal'):
            return
        
        # Necesitamos al menos dos barras para detectar cruces
        if len(self.data) < 2:
            return
        
        # Obtener valores actuales y anteriores del MACD y su señal
        macd_actual = self.data.MACD[-1]
        signal_actual = self.data.MACD_Signal[-1]
        macd_anterior = self.data.MACD[-2]
        signal_anterior = self.data.MACD_Signal[-2]
        
        # Verificar que los valores son válidos (no NaN)
        if pd.isna(macd_actual) or pd.isna(signal_actual) or pd.isna(macd_anterior) or pd.isna(signal_anterior):
            return
        
        # Cruce alcista: MACD cruza hacia arriba la línea de señal
        if macd_anterior <= signal_anterior and macd_actual > signal_actual:
            if not self.position:  # Solo comprar si no tenemos posición
                self.buy()
        
        # Cruce bajista: MACD cruza hacia abajo la línea de señal
        elif macd_anterior >= signal_anterior and macd_actual < signal_actual:
            if self.position:  # Solo vender si tenemos posición abierta
                self.position.close()
