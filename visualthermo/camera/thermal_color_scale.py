from enum import Enum


class ColorScaleMode(Enum):
    AUTOMATIC = 'AUTOMÁTICA'
    FIXED = 'FIXA'


class ThermalColorScale:
    """Controla os limites de visualização sem modificar os dados Y16."""

    def __init__(self):
        self._mode = ColorScaleMode.AUTOMATIC
        self._limits = None

    @property
    def mode(self):
        return self._mode

    @property
    def limits(self):
        return self._limits

    def update(self, frame):
        """Atualiza os limites no modo automático; mantém-nos no modo fixo."""
        if self._mode is ColorScaleMode.AUTOMATIC or self._limits is None:
            minimum = int(frame.min())
            maximum = int(frame.max())
            self._limits = (minimum, max(maximum, minimum + 1))
        return self._limits

    def toggle(self):
        """Congela os últimos limites ou volta à atualização automática."""
        if self._mode is ColorScaleMode.AUTOMATIC:
            self._mode = ColorScaleMode.FIXED
        else:
            self._mode = ColorScaleMode.AUTOMATIC
        return self._mode
