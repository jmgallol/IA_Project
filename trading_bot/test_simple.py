"""
Tests unitarios del Trading Bot.
Cubren indicadores tecnicos, estrategias, motor de backtesting y optimizador.
Ejecutar: python -m pytest test_simple.py -v
"""

import sys
import os
import numpy as np
import pandas as pd

# ── Utilidad: generar datos OHLCV sinteticos ────────────────────────────
def make_test_data(n=300, seed=42):
    """Genera un DataFrame OHLCV sintetico de n barras."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", periods=n, freq="B")
    close = 150 * np.exp(np.cumsum(rng.normal(0.0003, 0.012, n)))
    return pd.DataFrame(
        {
            "Open": close * (1 + rng.uniform(-0.005, 0.005, n)),
            "High": close * (1 + rng.uniform(0.002, 0.015, n)),
            "Low": close * (1 - rng.uniform(0.002, 0.015, n)),
            "Close": close,
            "Volume": rng.integers(1_000_000, 10_000_000, n),
        },
        index=dates,
    )


# ========================================================================
# 1. Tests de indicadores tecnicos
# ========================================================================

class TestTechnicalIndicators:
    """Verifica que los indicadores tecnicos se calculen correctamente."""

    def test_rsi_range(self):
        """RSI debe estar entre 0 y 100."""
        from indicators.technical import _calculate_rsi
        df = make_test_data()
        rsi = _calculate_rsi(df["Close"], period=14)
        valid = rsi.dropna()
        assert len(valid) > 0, "RSI no produjo valores validos"
        assert valid.min() >= 0, f"RSI minimo invalido: {valid.min()}"
        assert valid.max() <= 100, f"RSI maximo invalido: {valid.max()}"

    def test_sma_calculation(self):
        """SMA debe coincidir con la media movil de pandas."""
        from indicators.technical import add_indicators
        df = make_test_data()
        df_ind = add_indicators(df.copy())
        if "SMA_20" in df_ind.columns:
            expected = df["Close"].rolling(20).mean()
            # Alinear los indices porque add_indicators remueve NaNs
            pd.testing.assert_series_equal(
                df_ind["SMA_20"],
                expected.loc[df_ind.index],
                check_names=False,
                atol=0.01,
            )

    def test_macd_columns(self):
        """add_indicators debe agregar columnas MACD."""
        from indicators.technical import add_indicators
        df = make_test_data()
        df_ind = add_indicators(df.copy())
        for col in ["MACD", "MACD_Signal"]:
            assert col in df_ind.columns, f"Falta columna {col}"

    def test_bollinger_bands(self):
        """Bandas de Bollinger: superior > media > inferior."""
        from indicators.technical import add_indicators
        df = make_test_data()
        df_ind = add_indicators(df.copy())
        if "BB_Upper" in df_ind.columns and "BB_Lower" in df_ind.columns:
            valid = df_ind.dropna(subset=["BB_Upper", "BB_Lower", "SMA_20"])
            assert (valid["BB_Upper"] >= valid["SMA_20"]).all(), "BB_Upper < SMA_20"
            assert (valid["BB_Lower"] <= valid["SMA_20"]).all(), "BB_Lower > SMA_20"


# ========================================================================
# 2. Tests de estrategias
# ========================================================================

class TestStrategies:
    """Verifica que las clases de estrategia se instancien correctamente."""

    def test_rsi_strategy_import(self):
        """RSIStrategy se importa y tiene los parametros esperados."""
        from strategies.rsi_strategy import RSIStrategy
        assert hasattr(RSIStrategy, "rsi_lower")
        assert hasattr(RSIStrategy, "rsi_upper")

    def test_sma_strategy_import(self):
        """SMAStrategy se importa y tiene los parametros esperados."""
        from strategies.sma_strategy import SMAStrategy
        assert hasattr(SMAStrategy, "n_short")
        assert hasattr(SMAStrategy, "n_long")

    def test_macd_strategy_import(self):
        """MACDStrategy se importa y tiene los parametros esperados."""
        from strategies.macd_strategy import MACDStrategy
        assert hasattr(MACDStrategy, "fast")
        assert hasattr(MACDStrategy, "slow")
        assert hasattr(MACDStrategy, "signal")


# ========================================================================
# 3. Tests del motor de backtesting
# ========================================================================

class TestBacktestEngine:
    """Prueba la funcion run_backtest con datos sinteticos."""

    def test_run_backtest_returns_stats(self):
        """run_backtest debe retornar un objeto con metricas."""
        from backtest.engine import run_backtest
        from strategies.rsi_strategy import RSIStrategy
        df = make_test_data()
        stats = run_backtest(df, RSIStrategy, {}, cash=10_000)
        assert stats is not None, "run_backtest retorno None"
        assert "Return [%]" in stats.index, "Falta metrica 'Return [%]'"
        assert "Sharpe Ratio" in stats.index, "Falta metrica 'Sharpe Ratio'"
        assert "Max. Drawdown [%]" in stats.index, "Falta metrica 'Max. Drawdown [%]'"

    def test_run_backtest_equity_curve(self):
        """El resultado debe incluir _equity_curve."""
        from backtest.engine import run_backtest
        from strategies.rsi_strategy import RSIStrategy
        df = make_test_data()
        stats = run_backtest(df, RSIStrategy, {}, cash=10_000)
        assert hasattr(stats, "_equity_curve"), "Falta _equity_curve en stats"
        eq = stats._equity_curve
        assert "Equity" in eq.columns, "Falta columna Equity"
        assert eq["Equity"].iloc[0] > 0, "Equity inicial debe ser positiva"

    def test_buy_and_hold_baseline(self):
        """calculate_buy_hold debe retornar metricas razonables."""
        from backtest.engine import calculate_buy_hold
        df = make_test_data()
        bh = calculate_buy_hold(df, cash=10_000)
        assert "final_price" in bh, "Falta 'final_price'"
        assert "return_pct" in bh, "Falta 'return_pct'"
        assert bh["final_equity"] > 0, "Capital final B&H debe ser positivo"


# ========================================================================
# 4. Tests del optimizador
# ========================================================================

class TestOptimizer:
    """Prueba la optimizacion Grid Search."""

    def test_optimize_sma_returns_stats(self):
        """run_optimization debe retornar stats validos para SMA."""
        from backtest.optimizer import run_optimization
        from strategies.sma_strategy import SMAStrategy
        from unittest.mock import patch
        
        df = make_test_data()
        param_ranges = {
            "n_short": [2],
            "n_long": [10],
        }
        
        mock_stats = pd.Series({
            "Sharpe Ratio": 1.5,
            "Return [%]": 10.0,
            "Max. Drawdown [%]": -5.0,
            "Win Rate [%]": 50.0,
            "# Trades": 5
        })
        
        with patch('backtest.optimizer.run_backtest', return_value=mock_stats):
            best_params, best_stats, all_results = run_optimization(
                df, SMAStrategy, param_ranges, cash=10_000,
                objective="sharpe"
            )
            
        assert best_stats is not None, "run_optimization retorno None para stats"
        assert "Return [%]" in best_stats.index
        assert best_params is not None, "best_params es None"


# ========================================================================
# 5. Tests de integracion minimos
# ========================================================================

class TestIntegration:
    """Verifica que el flujo completo funcione de punta a punta."""

    def test_full_pipeline(self):
        """El pipeline completo (datos -> indicadores -> backtest) debe funcionar."""
        from indicators.technical import add_indicators
        from backtest.engine import run_backtest, calculate_buy_hold
        from strategies.sma_strategy import SMAStrategy

        df = make_test_data()
        df_ind = add_indicators(df.copy())
        assert len(df_ind) < len(df), "add_indicators debio remover los primeros NaNs"

        stats = run_backtest(df, SMAStrategy, {}, cash=10_000)
        assert stats is not None

        bh = calculate_buy_hold(df, cash=10_000)
        assert bh["final_equity"] > 0

    def test_config_imports(self):
        """settings.py debe exportar las constantes necesarias."""
        from config.settings import DEFAULT_TICKERS, CASH_DEFAULT
        assert len(DEFAULT_TICKERS) >= 1, "Debe haber al menos 1 ticker por defecto"
        assert CASH_DEFAULT > 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
