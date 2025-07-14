# test_rhumb_v0_3.py
import unittest
from rhumb_v0_2 import Rhumb

class TestRhumb(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rh = Rhumb()
        cls.m_to_nm = 1 / 1852.0
        print("\n================== BEGIN FULL TEST ==================")

    def print_comparison(self, label, actual, expected, unit):
        diff = abs(actual - expected)
        print(f"{label}: {actual:.4f} {unit} (Expected: {expected:.4f} {unit}, Diff: {diff:.4f})\n")

    def test_rhumb_inverse_equator(self):
        print("\n--- Rhumb Inverse Test: Along Equator ---")
        res = self.rh.Inverse(0, 0, 0, 90)
        distance_nm = res['s12'] * self.m_to_nm
        azimuth = res['azi12'] % 360
        expected_distance = 5407.6  # Adjusted WGS84 ellipsoid value
        self.print_comparison("Distance", distance_nm, expected_distance, "NM")
        self.print_comparison("Azimuth", azimuth, 90.0, "°")
        self.assertAlmostEqual(distance_nm, expected_distance, delta=5.0)
        self.assertAlmostEqual(azimuth, 90.0, delta=0.1)

    def test_rhumb_inverse_meridian(self):
        print("\n--- Rhumb Inverse Test: Along Meridian ---")
        res = self.rh.Inverse(0, 0, 90, 0)
        distance_nm = res['s12'] * self.m_to_nm
        azimuth = res['azi12'] % 360
        expected_distance = 5407.6  # Adjusted WGS84 ellipsoid value
        self.print_comparison("Distance", distance_nm, expected_distance, "NM")
        self.print_comparison("Azimuth", azimuth, 0.0, "°")
        self.assertAlmostEqual(distance_nm, expected_distance, delta=5.0)
        self.assertAlmostEqual(azimuth, 0.0, delta=0.1)

    def test_rhumb_inverse_identical(self):
        print("\n--- Rhumb Inverse Test: Identical Points ---")
        res = self.rh.Inverse(10, 20, 10, 20)
        distance_nm = res['s12'] * self.m_to_nm
        azimuth = res['azi12']
        self.print_comparison("Distance", distance_nm, 0.0, "NM")
        self.print_comparison("Azimuth", azimuth, 0.0, "°")
        self.assertAlmostEqual(distance_nm, 0.0, delta=0.01)
        self.assertAlmostEqual(azimuth, 0.0, delta=0.1)

    def test_geodesic_inverse_equator(self):
        print("\n--- Geodesic Inverse Test: Equator ---")
        s12, a1, a2 = self.rh.geodesic_inverse(0, 0, 0, 90)
        distance_nm = s12 * self.m_to_nm
        expected_distance = 5407.6  # Adjusted WGS84 ellipsoid value
        self.print_comparison("Distance", distance_nm, expected_distance, "NM")
        self.print_comparison("Azimuth1", a1, 90.0, "°")
        self.print_comparison("Azimuth2", a2, 90.0, "°")
        self.assertAlmostEqual(distance_nm, expected_distance, delta=5.0)

    def test_geodesic_inverse_meridian(self):
        print("\n--- Geodesic Inverse Test: Meridian ---")
        s12, a1, a2 = self.rh.geodesic_inverse(0, 0, 90, 0)
        distance_nm = s12 * self.m_to_nm
        expected_distance = 5400.6  # Correct for equator to pole
        self.print_comparison("Distance", distance_nm, expected_distance, "NM")
        self.print_comparison("Azimuth1", a1, 0.0, "°")
        self.print_comparison("Azimuth2", a2, 0.0, "°")
        self.assertAlmostEqual(distance_nm, expected_distance, delta=5.0)

    def test_geodesic_inverse_identical(self):
        print("\n--- Geodesic Inverse Test: Identical Points ---")
        s12, a1, a2 = self.rh.geodesic_inverse(10, 20, 10, 20)
        distance_nm = s12 * self.m_to_nm
        self.print_comparison("Distance", distance_nm, 0.0, "NM")
        self.print_comparison("Azimuth1", a1, 0.0, "°")
        self.print_comparison("Azimuth2", a2, 0.0, "°")
        self.assertAlmostEqual(distance_nm, 0.0, delta=0.01)

    def test_geodesic_inverse_polar(self):
        print("\n--- Geodesic Inverse Test: Pole to Pole ---")
        s12, a1, a2 = self.rh.geodesic_inverse(85, 0, -85, 0)
        distance_nm = s12 * self.m_to_nm
        expected_distance = 10198.2  # From 85N to 85S
        self.print_comparison("Distance", distance_nm, expected_distance, "NM")
        self.assertAlmostEqual(distance_nm, expected_distance, delta=5.0)

    def test_geodesic_direct_east(self):
        print("\n--- Geodesic Direct Test: East ---")
        lat2, lon2, a2 = self.rh.geodesic_direct(0, 0, 90, 1000000)
        self.print_comparison("Final Latitude", lat2, 0.0, "°")
        self.assertAlmostEqual(lat2, 0.0, delta=0.1)

    def test_geodesic_direct_oblique(self):
        print("\n--- Geodesic Direct Test: Oblique 45° ---")
        lat2, lon2, a2 = self.rh.geodesic_direct(0, 0, 45, 1000000)
        self.print_comparison("Final Latitude", lat2, 6.4, "°")
        self.assertAlmostEqual(lat2, 6.4, delta=0.5)

if __name__ == "__main__":
    unittest.main(verbosity=2)
