# ========================================
# app.py
# Punto de entrada principal — Interfaz Streamlit del Trading Bot
# ========================================

import streamlit as st
from datetime import datetime
import pandas as pd

# Importar módulos del proyecto
from config.settings import (
    RSI_PARAMS, 
    SMA_PARAMS, 
    MACD_PARAMS,
    CAPITAL_INICIAL_DEFAULT,
    COLORS
)
from data.loader import download_data, DataNotFoundError
from indicators.technical import add_indicators
from strategies.rsi_strategy import RSIStrategy
from strategies.sma_strategy import SMAStrategy
from strategies.macd_strategy import MACDStrategy
from backtest.engine import run_backtest, get_readable_stats
from backtest.optimizer import run_optimization
from ui.sidebar import render_sidebar
from ui.charts import plot_candlestick, plot_equity_curve, plot_trades
from ui.metrics import render_metrics, render_best_params, render_optimization_results


# ========== CONFIGURACIÓN DE PÁGINA ==========
st.set_page_config(
    layout="wide",
    page_title="Trading Bot 📈",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00D084;
        text-align: center;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: rgba(0, 208, 132, 0.1);
        border-left: 4px solid #00D084;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-header">📈 Trading Bot - Sistema Algorítmico</h1>', unsafe_allow_html=True)

# ========== CONTROL DE SESIÓN ==========
# Guardar estados en session_state para mantener datos entre reruns
if 'df_cargado' not in st.session_state:
    st.session_state.df_cargado = None
if 'stats_base' not in st.session_state:
    st.session_state.stats_base = None
if 'stats_opt' not in st.session_state:
    st.session_state.stats_opt = None
if 'best_params' not in st.session_state:
    st.session_state.best_params = None

# ========== PANEL LATERAL ==========
config = render_sidebar()

# ========== LÓGICA PRINCIPAL ==========
if config['ejecutar']:
    
    try:
        # ===== PASO 1: Descargar datos =====
        with st.spinner(f"📥 Descargando datos para {config['ticker']}..."):
            df = download_data(
                config['ticker'],
                config['fecha_inicio'],
                config['fecha_fin']
            )
            st.session_state.df_cargado = df
            st.success(f"✅ Datos descargados: {len(df)} días de operaciones")
        
        # ===== PASO 2: Calcular indicadores =====
        with st.spinner("📊 Calculando indicadores técnicos..."):
            df = add_indicators(df)
            st.success("✅ Indicadores calculados correctamente")
        
        # ===== PASO 3: Seleccionar estrategia y parámetros =====
        # Mapeo de estrategias
        estrategias = {
            "RSI Strategy": (RSIStrategy, RSI_PARAMS),
            "SMA Crossover": (SMAStrategy, SMA_PARAMS),
            "MACD Strategy": (MACDStrategy, MACD_PARAMS)
        }
        
        strategy_class, param_grid = estrategias[config['estrategia']]
        
        # Parámetros por defecto
        if config['estrategia'] == "RSI Strategy":
            default_params = {'rsi_lower': 30, 'rsi_upper': 70}
        elif config['estrategia'] == "SMA Crossover":
            default_params = {'n_short': 20, 'n_long': 50}
        else:  # MACD Strategy
            default_params = {}
        
        # ===== PASO 4: Backtesting sin optimizar =====
        with st.spinner("⏳ Ejecutando backtesting con parámetros por defecto..."):
            stats_base = run_backtest(df, strategy_class, default_params, cash=config['capital'])
            st.session_state.stats_base = stats_base
            st.success("✅ Backtesting sin optimizar completado")
        
        # ===== PASO 5: Optimización (si está activada) =====
        if config['optimizar']:
            with st.spinner(f"🔍 Optimizando parámetros (esto puede tomar unos minutos)..."):
                best_params, stats_opt, all_results = run_optimization(
                    df, strategy_class, param_grid, cash=config['capital']
                )
                st.session_state.best_params = best_params
                st.session_state.stats_opt = stats_opt
                st.success("✅ Optimización completada")
        
        # ===== PASO 6: Mostrar resultados en tabs =====
        tab1, tab2, tab3 = st.tabs(["📊 Datos y Gráfica", "📈 Backtesting", "🏆 Optimización"])
        
        # --- TAB 1: DATOS Y GRÁFICA ---
        with tab1:
            st.subheader("Información de Datos")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Ticker", config['ticker'])
            with col2:
                st.metric("Período", f"{config['fecha_inicio']} a {config['fecha_fin']}")
            with col3:
                st.metric("Candles", len(df))
            with col4:
                st.metric("Capital Inicial", f"${config['capital']:,.0f}")
            
            st.divider()
            
            # Mostrar gráfica de velas
            st.subheader("Gráfico de Precio con Indicadores")
            fig_candlestick = plot_candlestick(df)
            st.plotly_chart(fig_candlestick, use_container_width=True)
            
            # Tabla de datos (últimas 10 filas)
            with st.expander("📋 Ver últimas 20 filas de datos"):
                display_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'SMA_20', 'SMA_50', 'MACD', 'MACD_Signal']
                available_cols = [col for col in display_cols if col in df.columns]
                st.dataframe(df[available_cols].tail(20), use_container_width=True)
        
        # --- TAB 2: BACKTESTING ---
        with tab2:
            st.subheader(f"Resultados de Backtesting - {config['estrategia']}")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write("### Parámetros Utilizados")
                params_df = pd.DataFrame(
                    [(k, v) for k, v in default_params.items()],
                    columns=["Parámetro", "Valor"]
                )
                st.dataframe(params_df, use_container_width=True, hide_index=True)
            
            with col2:
                st.write("### Estadísticas Clave")
                st.metric("Retorno Total", f"{st.session_state.stats_base['Return [%]']:.2f}%")
                st.metric("Sharpe Ratio", f"{st.session_state.stats_base['Sharpe Ratio']:.2f}")
                st.metric("Drawdown Máximo", f"{st.session_state.stats_base['Max. Drawdown [%]']:.2f}%")
            
            st.divider()
            
            # Mostrar todas las métricas
            render_metrics(st.session_state.stats_base)
            
            st.divider()
            
            # Gráficas
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Curva de Capital")
                fig_equity = plot_equity_curve(st.session_state.stats_base)
                st.plotly_chart(fig_equity, use_container_width=True)
            
            with col2:
                st.subheader("Puntos de Entrada y Salida")
                fig_trades = plot_trades(df, st.session_state.stats_base)
                st.plotly_chart(fig_trades, use_container_width=True)
        
        # --- TAB 3: OPTIMIZACIÓN ---
        with tab3:
            if config['optimizar']:
                if st.session_state.best_params is not None:
                    st.subheader("Resultados de Optimización")
                    
                    # Mostrar mejores parámetros
                    render_best_params(st.session_state.best_params)
                    
                    st.divider()
                    
                    # Comparar resultados
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.write("### Comparación de Resultados")
                    with col2:
                        col_metric1, col_metric2 = st.columns(2)
                        with col_metric1:
                            retorno_mejora = st.session_state.stats_opt['Return [%]'] - st.session_state.stats_base['Return [%]']
                            st.metric(
                                "Mejora en Retorno",
                                f"{retorno_mejora:.2f}%",
                                delta=f"{retorno_mejora:.2f}%" if retorno_mejora != 0 else None
                            )
                        with col_metric2:
                            sharpe_mejora = st.session_state.stats_opt['Sharpe Ratio'] - st.session_state.stats_base['Sharpe Ratio']
                            st.metric(
                                "Mejora en Sharpe",
                                f"{sharpe_mejora:.2f}",
                                delta=f"{sharpe_mejora:.2f}" if sharpe_mejora != 0 else None
                            )
                    
                    st.divider()
                    
                    # Mostrar métricas comparativas
                    render_metrics(st.session_state.stats_base, st.session_state.stats_opt)
                    
                    st.divider()
                    
                    # Mostrar tabla de resultados de optimización
                    if 'all_results' in locals():
                        render_optimization_results(all_results)
                else:
                    st.warning("⚠️ No se completó la optimización. Intenta nuevamente.")
            else:
                st.info("ℹ️ Activa la optimización automática en el panel lateral para ver estos resultados.")
        
        # ===== RESUMEN FINAL =====
        st.divider()
        st.markdown("""
            <div class="success-box">
            <h3>✅ Análisis completado exitosamente</h3>
            <p>Los resultados anteriores muestran el desempeño de tu estrategia en el período seleccionado.</p>
            <p><b>Importante:</b> El backtesting es solo una simulación. El desempeño pasado no garantiza resultados futuros.</p>
            </div>
            """, unsafe_allow_html=True)
    
    except DataNotFoundError as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        st.info("Por favor, verifica que los parámetros sean válidos e intenta nuevamente.")

else:
    # Mostrar pantalla de bienvenida si no se ejecuta análisis
    st.info("👈 Configura los parámetros en el panel lateral y haz clic en '🚀 Ejecutar análisis' para comenzar.")
    
    with st.expander("📚 ¿Cómo usar este Bot?"):
        st.markdown("""
        1. **Selecciona un activo** - Elige de la lista o ingresa un ticker personalizado
        2. **Define el período** - Selecciona las fechas de inicio y fin
        3. **Elige la estrategia** - RSI, SMA Crossover o MACD
        4. **Configura el capital** - Define tu capital inicial simulado
        5. **Optimiza (opcional)** - Activa para encontrar los mejores parámetros automáticamente
        6. **Ejecuta el análisis** - Haz clic en el botón para ver los resultados
        
        ### Estrategias disponibles:
        - **RSI Strategy**: Compra en sobreventa (RSI < 30), vende en sobrecompra (RSI > 70)
        - **SMA Crossover**: Compra en cruce alcista de medias móviles, vende en cruce bajista
        - **MACD Strategy**: Compra cuando MACD cruza hacia arriba la línea de señal
        """)


