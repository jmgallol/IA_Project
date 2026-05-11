from backtesting import Strategy
import pandas as pd


def calculate_ema(values, period):
    """Calcula una EMA y retorna un arreglo compatible con backtesting.py."""
    return pd.Series(values).ewm(span=period, adjust=False).mean().to_numpy()


def calculate_macd(values, fast, slow):
    """Calcula la linea MACD como diferencia entre dos EMAs."""
    return calculate_ema(values, fast) - calculate_ema(values, slow)


class MACDStrategy(Strategy):
    """
    Estrategia basada en el cruce entre MACD y su linea de senal.

    Parametros optimizables:
    - fast: periodo de la EMA rapida.
    - slow: periodo de la EMA lenta.
    - signal: periodo de la EMA aplicada al MACD.
    """

    fast = 12
    slow = 26
    signal = 9

    def init(self):
        """Inicializa las series MACD con los parametros configurados."""
        self.macd = self.I(calculate_macd, self.data.Close, self.fast, self.slow)
        self.signal_line = self.I(calculate_ema, self.macd, self.signal)

    def next(self):
        """Ejecuta la logica de compra y venta en cada barra."""
        if len(self.data) < 2:
            return

        macd_current = self.macd[-1]
        signal_current = self.signal_line[-1]
        macd_previous = self.macd[-2]
        signal_previous = self.signal_line[-2]

        if (
            pd.isna(macd_current)
            or pd.isna(signal_current)
            or pd.isna(macd_previous)
            or pd.isna(signal_previous)
        ):
            return

        if macd_previous <= signal_previous and macd_current > signal_current:
            if not self.position:
                self.buy()
        elif macd_previous >= signal_previous and macd_current < signal_current:
            if self.position:
                self.position.close()
