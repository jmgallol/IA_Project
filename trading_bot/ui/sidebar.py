# ========================================
# ui/sidebar.py
# Componentes del panel lateral de Streamlit
# ========================================

import streamlit as st
from datetime import datetime, timedelta
from config.settings import (
    DEFAULT_TICKERS, 
    DATE_START, 
    DATE_END,
    CAPITAL_INICIAL_DEFAULT,
    CAPITAL_INICIAL_MIN,
    CAPITAL_INICIAL_MAX
)


def render_sidebar():
    """
    Renderiza el panel lateral con todos los controles de entrada.
    
    Returns:
        dict: Diccionario con la configuración del usuario:
        {
            'ticker': str,
            'fecha_inicio': str,
            'fecha_fin': str,
            'estrategia': str,
            'capital': float,
            'optimizar': bool,
            'ejecutar': bool
        }
    """
    
    with st.sidebar:
        st.title("⚙️ Configuración")
        st.divider()
        
        # Selección de ticker
        st.subheader("Activo")
        ticker = st.selectbox(
            "Selecciona un ticker:",
            DEFAULT_TICKERS,
            help="Elige el activo a analizar. Ejemplos: AAPL, BTC-USD, SPY"
        )
        
        # O permite entrada personalizada
        ticker_custom = st.text_input(
            "O ingresa un ticker personalizado:",
            value="",
            placeholder="Ej: NVDA, TSLA, ETH-USD",
            help="Deja en blanco para usar la selección anterior"
        )
        
        if ticker_custom:
            ticker = ticker_custom.upper()
        
        st.divider()
        
        # Rango de fechas
        st.subheader("Período de análisis")
        
        # Conversión de strings a datetime
        default_start = datetime.strptime(DATE_START, '%Y-%m-%d')
        default_end = datetime.strptime(DATE_END, '%Y-%m-%d')
        
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input(
                "Fecha inicio:",
                value=default_start,
                help="Primera fecha del período de análisis"
            )
        
        with col2:
            fecha_fin = st.date_input(
                "Fecha fin:",
                value=default_end,
                help="Última fecha del período de análisis"
            )
        
        st.divider()
        
        # Selección de estrategia
        st.subheader("Estrategia de trading")
        estrategia = st.selectbox(
            "Elige una estrategia:",
            ["RSI Strategy", "SMA Crossover", "MACD Strategy"],
            help="Selecciona el algoritmo de trading a usar"
        )
        
        st.divider()
        
        # Capital inicial
        st.subheader("Capital inicial")
        capital = st.slider(
            "Monto inicial (USD):",
            min_value=CAPITAL_INICIAL_MIN,
            max_value=CAPITAL_INICIAL_MAX,
            value=CAPITAL_INICIAL_DEFAULT,
            step=1000,
            help="Capital disponible para operar"
        )
        
        st.divider()
        
        # Optimización
        st.subheader("Optimización de parámetros")
        optimizar = st.checkbox(
            "Activar optimización automática",
            value=False,
            help="Busca automáticamente los mejores parámetros (puede tomar tiempo)"
        )
        
        if optimizar:
            st.info("⏳ La optimización ejecutará múltiples backtests. Esto puede tomar algunos minutos.")
        
        st.divider()
        
        # Botón de ejecución
        ejecutar = st.button(
            "🚀 Ejecutar análisis",
            use_container_width=True,
            type="primary"
        )
        
        st.divider()
        st.caption("Trading Bot v1.0 | Desarrollado con Streamlit y backtesting.py")
    
    # Convertir fechas a strings en formato YYYY-MM-DD
    config = {
        'ticker': ticker,
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
        'estrategia': estrategia,
        'capital': capital,
        'optimizar': optimizar,
        'ejecutar': ejecutar
    }
    
    return config
