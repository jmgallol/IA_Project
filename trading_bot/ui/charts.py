# ========================================
# ui/charts.py
# Visualizaciones interactivas con Plotly
# ========================================

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from config.settings import COLORS


def plot_candlestick(df):
    """
    Gráfico de velas con indicadores superpuestos.
    
    Muestra:
    - Velas de precio (OHLC)
    - SMA 20 y SMA 50
    - Bandas de Bollinger
    - Volumen en subplot inferior
    
    Args:
        df (pd.DataFrame): DataFrame con OHLCV e indicadores
    
    Returns:
        plotly.graph_objects.Figure: Figura interactiva
    """
    
    # Crear subplots: precio arriba, volumen abajo
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Gráfico de velas
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Precio',
            showlegend=True
        ),
        row=1, col=1
    )
    
    # SMA 20
    if 'SMA_20' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA_20'],
                name='SMA 20',
                line=dict(color=COLORS['sma_corta'], width=2),
                showlegend=True
            ),
            row=1, col=1
        )
    
    # SMA 50
    if 'SMA_50' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA_50'],
                name='SMA 50',
                line=dict(color=COLORS['sma_larga'], width=2),
                showlegend=True
            ),
            row=1, col=1
        )
    
    # Bandas de Bollinger - superior
    if 'BB_Upper' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_Upper'],
                name='BB Superior',
                line=dict(color=COLORS['bb_superior'], width=1, dash='dash'),
                showlegend=True
            ),
            row=1, col=1
        )
    
    # Bandas de Bollinger - inferior
    if 'BB_Lower' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_Lower'],
                name='BB Inferior',
                line=dict(color=COLORS['bb_inferior'], width=1, dash='dash'),
                showlegend=True
            ),
            row=1, col=1
        )
    
    # Bandas de Bollinger - relleno
    if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_Upper'],
                fill=None,
                showlegend=False,
                name='BB'
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_Lower'],
                fill='tonexty',
                fillcolor='rgba(171, 71, 188, 0.2)',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                name='BB Área'
            ),
            row=1, col=1
        )
    
    # Volumen
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volumen',
            marker=dict(color=COLORS['volumen']),
            showlegend=True
        ),
        row=2, col=1
    )
    
    # Actualizar layout
    fig.update_layout(
        title="Análisis Técnico del Precio",
        template='plotly_dark',
        plot_bgcolor=COLORS['fondo_grafico'],
        paper_bgcolor=COLORS['fondo_grafico'],
        height=600,
        hovermode='x unified',
        font=dict(size=11)
    )
    
    # Etiquetas de ejes
    fig.update_xaxes(title_text="Fecha", row=2, col=1)
    fig.update_yaxes(title_text="Precio (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volumen", row=2, col=1)
    
    return fig


def plot_equity_curve(stats):
    """
    Gráfico de curva de capital (Equity Curve).
    
    Muestra la evolución del capital durante el backtesting.
    Se rellena de verde si es ganancia, rojo si es pérdida.
    
    Args:
        stats (backtesting.Stats): Objeto de resultados del backtesting
    
    Returns:
        plotly.graph_objects.Figure: Figura interactiva
    """
    
    # Obtener la serie de capital durante el tiempo.
    equity_curve = stats._equity_curve
    equity = equity_curve["Equity"] if "Equity" in equity_curve.columns else equity_curve.iloc[:, 0]
    
    # Determinar color según el retorno final
    retorno_total = stats['Return [%]']
    color_relleno = COLORS['ganancia'] if retorno_total >= 0 else COLORS['perdida']
    
    # Crear gráfico
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=equity.index,
            y=equity,
            fill='tozeroy',
            fillcolor=color_relleno,
            line=dict(color=COLORS['equity'], width=2),
            name='Capital',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Capital: $%{y:,.2f}<extra></extra>'
        )
    )
    
    fig.update_layout(
        title="Curva de Capital (Equity Curve)",
        xaxis_title="Fecha",
        yaxis_title="Capital (USD)",
        template='plotly_dark',
        plot_bgcolor=COLORS['fondo_grafico'],
        paper_bgcolor=COLORS['fondo_grafico'],
        height=400,
        hovermode='x unified'
    )
    
    return fig


def plot_equity_comparison(strategy_stats, buy_hold_stats, title="Estrategia vs Buy & Hold"):
    """Compara la curva de capital de la estrategia contra Buy & Hold."""
    strategy_equity_curve = strategy_stats._equity_curve
    strategy_equity = (
        strategy_equity_curve["Equity"]
        if "Equity" in strategy_equity_curve.columns
        else strategy_equity_curve.iloc[:, 0]
    )
    buy_hold_equity = buy_hold_stats["equity_curve"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=strategy_equity.index,
            y=strategy_equity,
            mode="lines",
            name="Estrategia",
            line=dict(color=COLORS["equity"], width=3),
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Estrategia: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=buy_hold_equity.index,
            y=buy_hold_equity,
            mode="lines",
            name="Buy & Hold",
            line=dict(color=COLORS["sma_corta"], width=3, dash="dash"),
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Buy & Hold: $%{y:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Fecha",
        yaxis_title="Capital (USD)",
        template="plotly_dark",
        plot_bgcolor=COLORS["fondo_grafico"],
        paper_bgcolor=COLORS["fondo_grafico"],
        height=430,
        hovermode="x unified",
    )
    return fig


def plot_multi_strategy_comparison(strategy_results, buy_hold_stats):
    """Compara curvas de capital de varias estrategias optimizadas y Buy & Hold."""
    line_colors = ["#1F77B4", "#00D084", "#AB47BC", "#FF9800", "#F44336"]
    fig = go.Figure()

    for index, result in enumerate(strategy_results):
        equity = _extract_equity(result["stats"])
        fig.add_trace(
            go.Scatter(
                x=equity.index,
                y=equity,
                mode="lines",
                name=result["strategy"],
                line=dict(color=line_colors[index % len(line_colors)], width=3),
                hovertemplate=(
                    f"<b>{result['strategy']}</b><br>"
                    "%{x|%Y-%m-%d}<br>Capital: $%{y:,.2f}<extra></extra>"
                ),
            )
        )

    buy_hold_equity = buy_hold_stats["equity_curve"]
    fig.add_trace(
        go.Scatter(
            x=buy_hold_equity.index,
            y=buy_hold_equity,
            mode="lines",
            name="Buy & Hold",
            line=dict(color="#FFFFFF", width=3, dash="dash"),
            hovertemplate="<b>Buy & Hold</b><br>%{x|%Y-%m-%d}<br>Capital: $%{y:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Comparacion de curvas de capital",
        xaxis_title="Fecha",
        yaxis_title="Capital (USD)",
        template="plotly_dark",
        plot_bgcolor=COLORS["fondo_grafico"],
        paper_bgcolor=COLORS["fondo_grafico"],
        height=500,
        hovermode="x unified",
    )
    return fig


def _extract_equity(stats):
    equity_curve = stats._equity_curve
    return equity_curve["Equity"] if "Equity" in equity_curve.columns else equity_curve.iloc[:, 0]


def plot_trades(df, stats):
    """
    Gráfico de precio con puntos de entrada y salida.
    
    Superpone triángulos verdes en compras y triángulos rojos en ventas
    sobre el gráfico de precio.
    
    Args:
        df (pd.DataFrame): DataFrame con OHLCV
        stats (backtesting.Stats): Objeto de resultados del backtesting
    
    Returns:
        plotly.graph_objects.Figure: Figura interactiva
    """
    
    fig = go.Figure()
    
    # Gráfico de precio
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Close'],
            name='Precio',
            line=dict(color='white', width=1),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Cierre: $%{y:,.2f}<extra></extra>'
        )
    )
    
    price_scale = stats.attrs.get("price_scale", 1.0)
    price_multiplier = 1 / price_scale if price_scale else 1.0

    # Extraer puntos de entrada y salida de las operaciones
    trades = stats._trades
    
    if trades is not None and len(trades) > 0:
        # Puntos de entrada
        entry_times = []
        entry_prices = []
        
        # Puntos de salida
        exit_times = []
        exit_prices = []
        
        for _, trade in trades.iterrows():
            entry_bar = int(trade["EntryBar"])
            exit_bar = trade["ExitBar"]

            if 0 <= entry_bar < len(df):
                entry_times.append(df.index[entry_bar])
                entry_prices.append(trade["EntryPrice"] * price_multiplier)

            if pd.notna(exit_bar):
                exit_bar = int(exit_bar)
                if 0 <= exit_bar < len(df):
                    exit_times.append(df.index[exit_bar])
                    exit_prices.append(trade["ExitPrice"] * price_multiplier)
        
        # Agregar marcadores de entrada
        if entry_times:
            fig.add_trace(
                go.Scatter(
                    x=entry_times,
                    y=entry_prices,
                    mode='markers',
                    name='Compra',
                    marker=dict(
                        size=10,
                        color=COLORS['entrada'],
                        symbol='triangle-up',
                        line=dict(width=2, color='white')
                    ),
                    hovertemplate='<b>Compra</b><br>%{x|%Y-%m-%d}<br>Precio: $%{y:,.2f}<extra></extra>'
                )
            )
        
        # Agregar marcadores de salida
        if exit_times:
            fig.add_trace(
                go.Scatter(
                    x=exit_times,
                    y=exit_prices,
                    mode='markers',
                    name='Venta',
                    marker=dict(
                        size=10,
                        color=COLORS['salida'],
                        symbol='triangle-down',
                        line=dict(width=2, color='white')
                    ),
                    hovertemplate='<b>Venta</b><br>%{x|%Y-%m-%d}<br>Precio: $%{y:,.2f}<extra></extra>'
                )
            )
    
    fig.update_layout(
        title="Puntos de Entrada y Salida",
        xaxis_title="Fecha",
        yaxis_title="Precio (USD)",
        template='plotly_dark',
        plot_bgcolor=COLORS['fondo_grafico'],
        paper_bgcolor=COLORS['fondo_grafico'],
        height=400,
        hovermode='x unified'
    )
    
    return fig
