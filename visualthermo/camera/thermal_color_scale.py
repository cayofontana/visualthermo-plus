from enum import Enum


class ColorScaleMode(Enum):
    AUTOMATIC = 'AUTOMÁTICA'
    FIXED = 'FIXA'
    ADAPTIVE = 'ADAPTATIVA'


class ThermalColorScale:
    """Gerencia apenas os limites de exibição; não altera os quadros Y16.

    No modo adaptativo, aplica uma média móvel exponencial (EMA) aos
    extremos dos quadros. alpha=1 equivale à atualização imediata.
    """

    def __init__(self, alpha=0.2):
        if not 0 < alpha <= 1:
            raise ValueError('alpha deve estar no intervalo (0, 1].')
        self._alpha = float(alpha)
        self._mode = ColorScaleMode.AUTOMATIC
        self._limits = None
        self._smoothed_limits = None

    @property
    def mode(self):
        return self._mode

    @property
    def limits(self):
        return self._limits

    @property
    def alpha(self):
        return self._alpha

    def update(self, frame):
        """Calcula limites para o quadro atual segundo o modo selecionado."""
        if self._mode is ColorScaleMode.FIXED and self._limits is not None:
            return self._limits

        minimum = int(frame.min())
        maximum = max(int(frame.max()), minimum + 1)
        current = (minimum, maximum)

        if self._mode is ColorScaleMode.ADAPTIVE:
            if self._smoothed_limits is None:
                self._smoothed_limits = tuple(float(v) for v in current)
            else:
                a = self._alpha
                self._smoothed_limits = tuple(
                    a * new + (1 - a) * old
                    for new, old in zip(current, self._smoothed_limits)
                )
            low, high = self._smoothed_limits
            self._limits = (low, max(high, low + 1))
        else:
            self._limits = current
        return self._limits

    def toggle(self):
        """Alterna AUTOMÁTICA → FIXA → ADAPTATIVA → AUTOMÁTICA."""
        next_mode = {
            ColorScaleMode.AUTOMATIC: ColorScaleMode.FIXED,
            ColorScaleMode.FIXED: ColorScaleMode.ADAPTIVE,
            ColorScaleMode.ADAPTIVE: ColorScaleMode.AUTOMATIC,
        }
        self._mode = next_mode[self._mode]
        if self._mode is ColorScaleMode.ADAPTIVE:
            # Parte dos limites congelados, evitando salto ao mudar de modo.
            self._smoothed_limits = (
                tuple(float(v) for v in self._limits)
                if self._limits is not None else None
            )
        else:
            self._smoothed_limits = None
        return self._mode
