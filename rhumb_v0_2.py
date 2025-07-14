# rhumb_v0_2.py
# Robust Rhumb and Geodesic Calculations (WGS84)
# Developed by Ricardo Carvalho · PAM 2025

import math
from geographiclib.geodesic import Geodesic

class Rhumb:
    """
    Class for computing rhumb line (loxodrome) solutions on WGS84.
    Also includes geodesic (great circle) solutions using GeographicLib.
    """

    def __init__(self, a=6378137, f=1 / 298.257223563):
        """
        Initialize WGS84 ellipsoid parameters.
        """
        self.a = a
        self.f = f
        self.b = a * (1 - f)
        self._e2 = f * (2 - f)
        self._e = math.sqrt(self._e2)

    def atanh(self, x):
        """
        Numerically stable inverse hyperbolic tangent.
        """
        return 0.5 * math.log((1 + x) / (1 - x))

    def isometric_lat(self, phi):
        """
        Compute isometric latitude for ellipsoidal rhumb calculations.
        """
        e = self._e
        return math.log(math.tan(math.pi / 4 + phi / 2)) - e * self.atanh(e * math.sin(phi))

    def Inverse(self, lat1, lon1, lat2, lon2):
        """
        Compute rhumb line distance and azimuth from point 1 to 2.
        Returns: {'s12': distance (meters), 'azi12': azimuth (degrees)}
        """
        # Convert to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        lam1 = math.radians(lon1)
        lam2 = math.radians(lon2)

        dphi = phi2 - phi1
        dlam = lam2 - lam1

        # Normalize longitude difference to [-π, π]
        dlam = (dlam + math.pi) % (2 * math.pi) - math.pi

        psi1 = self.isometric_lat(phi1)
        psi2 = self.isometric_lat(phi2)
        dpsi = psi2 - psi1

        if abs(dpsi) > 1e-12:
            q = dphi / dpsi
        else:
            q = math.cos(phi1)  # Nearly E-W course

        azi12 = math.degrees(math.atan2(dlam, dpsi)) % 360

        # Approximate rhumb distance along ellipsoid
        s12 = math.hypot(dphi, q * dlam) * self.a

        # Handle identical points
        if abs(dphi) < 1e-12 and abs(dlam) < 1e-12:
            s12 = 0.0
            azi12 = 0.0

        return {'s12': s12, 'azi12': azi12}

    def Direct(self, lat1, lon1, azi12, s12):
        """
        Compute rhumb line destination point from start point, azimuth, and distance.
        Returns: {'lat2', 'lon2', 'azi12'}
        """
        phi1 = math.radians(lat1)
        lam1 = math.radians(lon1)
        alpha = math.radians(azi12)

        dphi = s12 * math.cos(alpha) / self.a
        phi2 = phi1 + dphi

        # Avoid pole overshoot
        phi2 = max(min(phi2, math.pi / 2), -math.pi / 2)

        psi1 = self.isometric_lat(phi1)
        psi2 = self.isometric_lat(phi2)
        dpsi = psi2 - psi1

        if abs(dpsi) > 1e-12:
            q = dphi / dpsi
            dlam = s12 * math.sin(alpha) / (self.a * q)
        else:
            dlam = s12 * math.sin(alpha) / (self.a * math.cos(phi1))

        lam2 = lam1 + dlam

        # Normalize longitude to [-180°, 180°)
        lon2 = (math.degrees(lam2) + 540) % 360 - 180
        lat2 = math.degrees(phi2)

        azi12 = azi12 % 360  # Normalize azimuth

        return {'lat2': lat2, 'lon2': lon2, 'azi12': azi12}

    # =========================
    # Geodesic (Great Circle) using GeographicLib
    # =========================
    def geodesic_inverse(self, lat1, lon1, lat2, lon2):
        """
        Compute geodesic distance and azimuths using GeographicLib.
        Returns: (distance in meters, azimuth at start [0°, 360°), azimuth at end [0°, 360°))
        """
        g = Geodesic.WGS84
        res = g.Inverse(lat1, lon1, lat2, lon2)
        azi1 = res['azi1'] % 360
        azi2 = res['azi2'] % 360
        return res['s12'], azi1, azi2

    def geodesic_direct(self, lat1, lon1, azi1, s12):
        """
        Compute geodesic destination point using GeographicLib.
        Returns: (lat2, lon2, final azimuth [0°, 360°))
        """
        g = Geodesic.WGS84
        res = g.Direct(lat1, lon1, azi1, s12)
        azi2 = res['azi2'] % 360
        return res['lat2'], res['lon2'], azi2

    # =========================
    # Examples for testing
    # =========================
    def example_tests(self):
        """
        Run example tests to verify correctness.
        """
        print("Testing Rhumb Inverse:")
        rh_res = self.Inverse(0, 0, 10, 20)
        print(f"Rhumb Distance: {rh_res['s12']:.3f} m, Azimuth: {rh_res['azi12']:.3f}°")

        print("Testing Rhumb Direct:")
        rh_dir = self.Direct(0, 0, 45, 1000000)
        print(f"Lat2: {rh_dir['lat2']:.6f}, Lon2: {rh_dir['lon2']:.6f}, Azimuth: {rh_dir['azi12']:.3f}°")

        print("Testing Geodesic Inverse:")
        s, a1, a2 = self.geodesic_inverse(0, 0, 10, 20)
        print(f"Geodesic Distance: {s:.3f} m, Azimuth1: {a1:.3f}°, Azimuth2: {a2:.3f}°")

        print("Testing Geodesic Direct:")
        lat2, lon2, a2 = self.geodesic_direct(0, 0, 45, 1000000)
        print(f"Lat2: {lat2:.6f}, Lon2: {lon2:.6f}, Azimuth2: {a2:.3f}°")

# =========================
# Example main test block
# =========================
if __name__ == "__main__":
    rh = Rhumb()
    rh.example_tests()
