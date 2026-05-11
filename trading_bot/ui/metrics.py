# ========================================
# ui/metrics.py
# Renderizado de métricas y tablas en la interfaz
# ========================================

import streamlit as st
import pandas as pd


def render_metrics(stats_base, stats_opt=None):
    """
    Renderiza métricas de desempeño en tarjetas usando st.metric().
    
    Si se proporciona stats_opt, muestra dos columnas:
    - Izquierda: resultados sin optimización
    - Derecha: resultados con optimización
    - Con flechas de comparación usando el parámetro delta
    
    Args:
        stats_base (backtesting.Stats): Estadísticas sin optimización
        stats_opt (backtesting.Stats, optional): Estadísticas optimizadas
    """
    
    if stats_opt is None:
        # Mostrar solo una columna con resultados base
        st.subheader("📊 Métricas de Desempeño")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Retorno Total",
                f"{stats_base['Return [%]']:.2f}%",
                help="Ganancia/Pérdida total en porcentaje"
            )
            st.metric(
                "Sharpe Ratio",
                f"{stats_base['Sharpe Ratio']:.2f}",
                help="Medida de riesgo-retorno (mayor es mejor)"
            )
            st.metric(
                "Operaciones",
                f"{int(stats_base['# Trades'])}",
                help="Total de trades ejecutados"
            )
        
        with col2:
            st.metric(
                "Retorno Anual",
                f"{stats_base['Annual Return [%]']:.2f}%",
                help="Retorno anualizado"
            )
            st.metric(
                "Drawdown Máximo",
                f"{stats_base['Max. Drawdown [%]']:.2f}%",
                help="Pérdida máxima desde el pico anterior (negativo)"
            )
            st.metric(
                "Win Rate",
                f"{stats_base['Win Rate [%]']:.2f}%",
                help="Porcentaje de operaciones ganadoras"
            )
        
        with col3:
            st.metric(
                "Factor de Ganancias",
                f"{stats_base['Profit Factor']:.2f}",
                help="Ratio de ganancias brutas vs pérdidas brutas"
            )
            st.metric(
                "Duración Promedio",
                str(stats_base['Avg. Trade Duration']),
                help="Duración media de cada operación"
            )
            st.metric(
                "Exposición",
                f"{stats_base['Exposure Time [%]']:.2f}%",
                help="Porcentaje de tiempo con posición abierta"
            )
    
    else:
        # Mostrar comparación entre base y optimizado
        st.subheader("📊 Comparación: Sin Optimizar vs Optimizado")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Sin Optimizar")
            
            col1a, col1b = st.columns(2)
            with col1a:
                st.metric(
                    "Retorno Total",
                    f"{stats_base['Return [%]']:.2f}%"
                )
                st.metric(
                    "Sharpe Ratio",
                    f"{stats_base['Sharpe Ratio']:.2f}"
                )
                st.metric(
                    "Drawdown Máx.",
                    f"{stats_base['Max. Drawdown [%]']:.2f}%"
                )
            
            with col1b:
                st.metric(
                    "Win Rate",
                    f"{stats_base['Win Rate [%]']:.2f}%"
                )
                st.metric(
                    "Operaciones",
                    f"{int(stats_base['# Trades'])}"
                )
                st.metric(
                    "Factor Ganancias",
                    f"{stats_base['Profit Factor']:.2f}"
                )
        
        with col2:
            st.write("### Optimizado ✓")
            
            # Calcular deltas para comparación
            delta_retorno = stats_opt['Return [%]'] - stats_base['Return [%]']
            delta_sharpe = stats_opt['Sharpe Ratio'] - stats_base['Sharpe Ratio']
            delta_drawdown = stats_opt['Max. Drawdown [%]'] - stats_base['Max. Drawdown [%]']
            delta_winrate = stats_opt['Win Rate [%]'] - stats_base['Win Rate [%]']
            delta_trades = int(stats_opt['# Trades']) - int(stats_base['# Trades'])
            delta_profit_factor = stats_opt['Profit Factor'] - stats_base['Profit Factor']
            
            col2a, col2b = st.columns(2)
            with col2a:
                st.metric(
                    "Retorno Total",
                    f"{stats_opt['Return [%]']:.2f}%",
                    delta=f"{delta_retorno:.2f}%"
                )
                st.metric(
                    "Sharpe Ratio",
                    f"{stats_opt['Sharpe Ratio']:.2f}",
                    delta=f"{delta_sharpe:.2f}"
                )
                st.metric(
                    "Drawdown Máx.",
                    f"{stats_opt['Max. Drawdown [%]']:.2f}%",
                    delta=f"{delta_drawdown:.2f}%"
                )
            
            with col2b:
                st.metric(
                    "Win Rate",
                    f"{stats_opt['Win Rate [%]']:.2f}%",
                    delta=f"{delta_winrate:.2f}%"
                )
                st.metric(
                    "Operaciones",
                    f"{int(stats_opt['# Trades'])}",
                    delta=f"{delta_trades}"
                )
                st.metric(
                    "Factor Ganancias",
                    f"{stats_opt['Profit Factor']:.2f}",
                    delta=f"{delta_profit_factor:.2f}"
                )


def render_best_params(params):
    """
    Muestra los mejores parámetros encontrados en formato destacado.
    
    Args:
        params (dict): Diccionario con los parámetros optimizados
    """
    
    st.success("✓ Optimización completada")
    
    # Crear tabla de parámetros
    with st.container():
        st.write("### 🏆 Mejores Parámetros Encontrados")
        
        # Convertir a DataFrame para mejor visualización
        params_df = pd.DataFrame(
            [(k, v) for k, v in params.items()],
            columns=["Parámetro", "Valor"]
        )
        
        st.dataframe(params_df, use_container_width=True, hide_index=True)
        
        # Mostrar también en formato texto para copiar fácilmente
        params_str = ", ".join([f"{k}={v}" for k, v in params.items()])
        st.code(params_str, language="python")


def render_optimization_results(results):
    """
    Muestra tabla con los mejores resultados de la optimización.
    
    Args:
        results (list): Lista de resultados de las combinaciones probadas
    """
    
    st.subheader("📈 Resultados de Optimización")
    
    # Convertir a DataFrame y ordenar por Sharpe Ratio
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('sharpe_ratio', ascending=False).head(10)
    
    # Formatear columnas
    results_df_display = results_df.copy()
    results_df_display['sharpe_ratio'] = results_df_display['sharpe_ratio'].apply(lambda x: f"{x:.4f}")
    results_df_display['return'] = results_df_display['return'].apply(lambda x: f"{x:.2f}%")
    results_df_display['max_drawdown'] = results_df_display['max_drawdown'].apply(lambda x: f"{x:.2f}%")
    results_df_display['win_rate'] = results_df_display['win_rate'].apply(lambda x: f"{x:.2f}%")
    
    # Renombrar columnas
    results_df_display.columns = ['Sharpe Ratio', 'Retorno (%)', 'Drawdown Máx. (%)', 'Win Rate (%)', 'Trades', 'Parámetros']
    
    # Mostrar tabla
    st.dataframe(results_df_display, use_container_width=True, hide_index=True)
