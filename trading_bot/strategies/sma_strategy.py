# ========================================
# strategies/sma_strategy.py
# Estrategia de cruce de medias móviles (SMA Crossover)
# ========================================

from backtesting import Strategy
import pandas as pd


class SMAStrategy(Strategy):
    """
    Estrategia de trading basada en el cruce de medias móviles simples.
    
    Lógica:
    - Compra en cruce alcista: SMA corta cruza hacia arriba la SMA larga
    - Vende en cruce bajista: SMA corta cruza hacia abajo la SMA larga
    
    Parámetros optimizables:
    - n_short: período de la media móvil corta (típicamente 5-20)
    - n_long: período de la media móvil larga (típicamente 30-100)
    """
    
    # Parámetros por defecto
    n_short = 20   # Período de SMA corta
    n_long = 50    # Período de SMA larga
    
    def init(self):
        """Inicializar la estrategia al comenzar el backtesting"""
        pass
    
    def next(self):
        """Lógica de decisión ejecutada en cada barra"""
        
        # Necesitamos al menos dos barras para detectar cruces
        if len(self.data) < self.n_long + 1:
            return
        
        # Verificar que tenemos los datos de SMA en el dataframe
        if not hasattr(self.data, 'SMA_20'):
            return
        
        # Para este cálculo, usamos los SMA del dataframe directamente
        # Obtener índice actual
        idx = len(self.data) - 1
        
        # Calcular SMAs manualmente para los períodos especificados
        close_data = self.data.Close
        ma_short_actual = close_data[-1] if len(close_data) >= self.n_short else float('nan')
        ma_long_actual = close_data[-1] if len(close_data) >= self.n_long else float('nan')
        
        # Para la media móvil corta
        if len(close_data) >= self.n_short:
            ma_short_actual = sum(close_data[-self.n_short:]) / self.n_short
        
        # Para la media móvil larga
        if len(close_data) >= self.n_long:
            ma_long_actual = sum(close_data[-self.n_long:]) / self.n_long
        
        # Para la barra anterior
        if len(close_data) >= self.n_short + 1:
            ma_short_anterior = sum(close_data[-self.n_short-1:-1]) / self.n_short
        else:
            ma_short_anterior = ma_short_actual
        
        if len(close_data) >= self.n_long + 1:
            ma_long_anterior = sum(close_data[-self.n_long-1:-1]) / self.n_long
        else:
            ma_long_anterior = ma_long_actual
        
        # Cruce alcista: SMA corta sube por encima de SMA larga
        if ma_short_anterior <= ma_long_anterior and ma_short_actual > ma_long_actual:
            if not self.position:  # Solo comprar si no tenemos posición
                self.buy()
        
        # Cruce bajista: SMA corta cae por debajo de SMA larga
        elif ma_short_anterior >= ma_long_anterior and ma_short_actual < ma_long_actual:
            if self.position:  # Solo vender si tenemos posición abierta
                self.position.close()
