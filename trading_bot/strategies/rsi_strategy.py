# ========================================
# strategies/rsi_strategy.py
# Estrategia basada en RSI (Relative Strength Index)
# ========================================

from backtesting import Strategy
import pandas as pd


class RSIStrategy(Strategy):
    """
    Estrategia de trading basada en el indicador RSI.
    
    Lógica:
    - Compra cuando RSI cae por debajo del umbral inferior (sobreventa)
    - Vende cuando RSI sube por encima del umbral superior (sobrecompra)
    
    Parámetros optimizables:
    - rsi_lower: umbral de compra (típicamente 20-40)
    - rsi_upper: umbral de venta (típicamente 60-80)
    """
    
    # Parámetros por defecto
    rsi_lower = 30  # Umbral de compra
    rsi_upper = 70  # Umbral de venta
    
    def init(self):
        """Inicializar la estrategia al comenzar el backtesting"""
        pass
    
    def next(self):
        """Lógica de decisión ejecutada en cada barra"""
        
        # Verificar que el indicador RSI existe en los datos
        if not hasattr(self.data, 'RSI'):
            return
        
        rsi = self.data.RSI[-1]
        
        # Señal de compra: RSI en sobreventa
        if rsi < self.rsi_lower:
            if not self.position:  # Solo comprar si no tenemos posición
                self.buy()
        
        # Señal de venta: RSI en sobrecompra
        elif rsi > self.rsi_upper:
            if self.position:  # Solo vender si tenemos posición abierta
                self.position.close()
