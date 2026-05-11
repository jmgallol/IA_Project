# ========================================
# config/settings.py
# Configuración global: constantes, parámetros y temas visuales
# ========================================

# Tickers por defecto para el análisis
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "BTC-USD", "ETH-USD", "SPY", "QQQ"]

# Rangos de fechas por defecto (últimos 3 años)
from datetime import datetime, timedelta

DATE_START = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
DATE_END = datetime.now().strftime('%Y-%m-%d')

# Parámetros de optimización para RSI Strategy
RSI_PARAMS = {
    'rsi_lower': range(20, 41, 5),      # Umbral de compra: 20-40
    'rsi_upper': range(60, 81, 5)       # Umbral de venta: 60-80
}

# Parámetros de optimización para SMA Strategy
SMA_PARAMS = {
    'n_short': range(5, 21, 2),         # SMA corta: 5-20 periodos
    'n_long': range(30, 101, 10)        # SMA larga: 30-100 periodos
}

# Parámetros de optimización para MACD Strategy
MACD_PARAMS = {
    'fast': range(8, 16, 2),            # EMA rápida: 8-14
    'slow': range(24, 32, 2),           # EMA lenta: 24-30
    'signal': range(7, 11, 1)           # EMA señal: 7-10
}

# Colores del tema visual
COLORS = {
    'ganancia': '#00D084',              # Verde para ganancias
    'perdida': '#FF5E5B',               # Rojo para pérdidas
    'equity': '#1F77B4',                # Azul para curva de capital
    'fondo_grafico': '#111111',         # Gris oscuro para fondo de gráficas
    'sma_corta': '#FF9800',             # Naranja para SMA corta
    'sma_larga': '#2196F3',             # Azul claro para SMA larga
    'bb_superior': '#AB47BC',           # Púrpura para bandas de Bollinger
    'bb_inferior': '#AB47BC',
    'entrada': '#4CAF50',               # Verde para puntos de entrada
    'salida': '#F44336',                # Rojo para puntos de salida
    'volumen': '#607D8B'                # Gris azulado para volumen
}

# Capital inicial por defecto (en USD)
CAPITAL_INICIAL_DEFAULT = 10000
CAPITAL_INICIAL_MIN = 1000
CAPITAL_INICIAL_MAX = 100000

# Configuración de backtesting
CASH_DEFAULT = 10000
COMISION_DEFAULT = 0.001              # 0.1% de comisión por operación
