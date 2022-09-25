from dataclasses import dataclass
from typing import List

import astropy.units as u
import numpy as np
from astropy.coordinates import spherical_to_cartesian

__all__ = ["FieldLines", "FieldLine"]


@dataclass
class FieldLine:
    """
    A single field line.
    """

    r: np.ndarray
    lat: u.Quantity
    lon: u.Quantity

    def __init__(self, *, r: np.ndarray, lat: np.ndarray, lon: np.ndarray):
        """
        Parameters
        ----------
        r : numpy.ndarray
            Radial coordinates.
        lat : numpy.ndarray
            Latitude coordinates **in radians**.
        lon : numpy.ndarray
            Longitude coordinates **in radians**.
        """
        self.r = r
        self.lat = lat * u.rad
        self.lon = lon * u.rad

    @property
    def xyz(self):
        """
        Cartesian coordinates as a (n, 3) shaped array.
        """
        return np.array(spherical_to_cartesian(self.r, self.lat, self.lon)).T

    @property
    def _rlatlon(self):
        """
        Spherical coordinates as a (n, 3) shaped array.
        """
        return np.column_stack(
            [self.r, self.lat.to_value(u.rad), self.lon.to_value(u.rad)]
        )


@dataclass
class FieldLines:
    """
    A container for multiple field lines.
    """

    flines: List[FieldLine]

    def __init__(self, xs: np.ndarray, runit: u.Unit):
        """
        Parameters
        ----------
        xs : list[numpy.ndarray]
            Field lines. Each array must have lon, lat, r columns in that
            order.
        runit : u.Unit
            Unit for radial coordinate.
        """
        self.flines = [
            FieldLine(r=x[:, 2] * runit, lat=x[:, 1], lon=x[:, 0]) for x in xs
        ]

    def __getitem__(self, i):
        return self.flines[i]

    def __len__(self):
        return len(self.flines)

    def __iter__(self):
        for fline in self.flines:
            yield fline

    def save(self, filename):
        """
        Save field lines to file.

        Parameters
        ----------
        filename : pathlib.Path, str
            File to save field lines to.

        Notes
        -----
        Arrays are saved using `numpy.savez_compressed`.
        """
        np.savez_compressed(filename, *[fline._rlatlon for fline in self.flines])

    @classmethod
    def load(cls, filename):
        """
        Load field lines from a file.

        The field lines must have been saved using the ``.save()`` method.

        Parameters
        ----------
        filename : pathlib.Path, str
            File to load field lines from.

        Returns
        -------
        flines : FieldLines
        """
        arrs = np.load(str(filename))
        return cls([arrs[k][:, ::-1] for k in arrs])
