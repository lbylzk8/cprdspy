"""fourier_copilot_3d 的单元测试。

运行方式（在 cprdspy 目录下）：

    .venv/Scripts/python.exe -m unittest discover -s tests -v

测试对应公式：
    x = Σ rᵢ·cosθᵢ·cosφᵢ
    y = Σ rᵢ·cosθᵢ·sinφᵢ
    z = Σ rᵢ·sinθᵢ
    θᵢ(t) = Aᵢ·t + deltaᵢ,  φᵢ(t) = Bᵢ·t + gammaᵢ
"""

import unittest
import warnings

import matplotlib

matplotlib.use("Agg")  # 无头后端，测试时不弹窗
import matplotlib.pyplot as plt
import numpy as np

from cprdspy.CPR_matplotlib.Cycloid.cycloid import fourier_copilot_3d

warnings.filterwarnings("ignore", message=".*non-interactive.*")


def _new_3d_axes():
    """新建一个独立的 3D axes，避免测试之间互相影响。"""
    fig = plt.figure()
    return fig, fig.add_subplot(projection="3d")


class TestFourierCopilot3D(unittest.TestCase):
    def setUp(self):
        plt.close("all")

    def tearDown(self):
        plt.close("all")

    # ---------- 数学正确性 ----------

    def test_single_term_matches_spherical_formula(self):
        """单项时应逐点等于球坐标参数方程。"""
        r, alpha, delta, beta, gamma = 2.0, 1.0, 0.3, 2.0, 0.7
        T, points = 1.0, 200
        _, ax = _new_3d_axes()

        x, y, z = fourier_copilot_3d(
            [r], [alpha], [delta], T, B=[beta], gamma=[gamma],
            points=points, ax=ax,
        )

        t = np.linspace(0, 2 * np.pi * T, points)
        theta = alpha * t + delta
        phi = beta * t + gamma
        np.testing.assert_allclose(x, r * np.cos(theta) * np.cos(phi), atol=1e-12)
        np.testing.assert_allclose(y, r * np.cos(theta) * np.sin(phi), atol=1e-12)
        np.testing.assert_allclose(z, r * np.sin(theta), atol=1e-12)

    def test_superposition_of_terms(self):
        """多项之和应等于各单项分别计算后再相加。"""
        R = [3.0, 2.0, 1.0]
        A = [1.0, 2.0, 3.0]
        delta = [0.0, np.pi / 2, np.pi]
        B = [1.0, 3.0, 5.0]
        gamma = [0.0, np.pi / 3, np.pi / 2]
        T, points = 1.0, 500

        _, ax = _new_3d_axes()
        x, y, z = fourier_copilot_3d(
            R, A, delta, T, B=B, gamma=gamma, points=points, ax=ax,
        )

        expected = np.zeros((3, points))
        for i in range(len(R)):
            _, ax_i = _new_3d_axes()
            xi, yi, zi = fourier_copilot_3d(
                [R[i]], [A[i]], [delta[i]], T,
                B=[B[i]], gamma=[gamma[i]], points=points, ax=ax_i,
            )
            expected[0] += xi
            expected[1] += yi
            expected[2] += zi

        np.testing.assert_allclose(x, expected[0], atol=1e-12)
        np.testing.assert_allclose(y, expected[1], atol=1e-12)
        np.testing.assert_allclose(z, expected[2], atol=1e-12)

    def test_defaults_equal_explicit_A_and_zero_gamma(self):
        """省略 B/gamma 时等价于 B=A、gamma=0。"""
        R = [2.0, 1.5]
        A = [1.0, 3.0]
        delta = [0.2, -0.4]
        T, points = 1.0, 300

        _, ax1 = _new_3d_axes()
        x1, y1, z1 = fourier_copilot_3d(R, A, delta, T, points=points, ax=ax1)

        _, ax2 = _new_3d_axes()
        x2, y2, z2 = fourier_copilot_3d(
            R, A, delta, T,
            B=A, gamma=[0.0, 0.0], points=points, ax=ax2,
        )

        np.testing.assert_allclose(x1, x2, atol=1e-12)
        np.testing.assert_allclose(y1, y2, atol=1e-12)
        np.testing.assert_allclose(z1, z2, atol=1e-12)

    def test_start_point_with_zero_phases(self):
        """所有相位为 0 时，t=0 处应落在 x=Σrᵢ, y=z=0。"""
        R = [1.0, 2.0, 3.0]
        _, ax = _new_3d_axes()
        x, y, z = fourier_copilot_3d(R, [1, 2, 3], [0, 0, 0], 1, points=50, ax=ax)

        self.assertAlmostEqual(x[0], sum(R), places=12)
        self.assertAlmostEqual(y[0], 0.0, places=12)
        self.assertAlmostEqual(z[0], 0.0, places=12)

    def test_closed_curve_for_integer_frequencies(self):
        """A、B 均为整数时，t=0 与 t=T·2π 应重合（闭合曲线）。"""
        _, ax = _new_3d_axes()
        x, y, z = fourier_copilot_3d(
            [1.0, 1.0, 1.0], [1, 2, 3], [0.1, 0.2, 0.3], 1,
            B=[2, 3, 5], gamma=[0.4, 0.5, 0.6], points=1000, ax=ax,
        )

        np.testing.assert_allclose([x[0], y[0], z[0]], [x[-1], y[-1], z[-1]], atol=1e-9)

    def test_radius_bounded_by_sum_of_amplitudes(self):
        """三角不等式：曲线上的点始终满足 ‖(x,y,z)‖ ≤ Σrᵢ。"""
        R = [3.0, 2.0, 1.0, 0.5]
        A = [1.0, 2.0, 3.0, 5.0]
        B = [2.0, 3.0, 5.0, 7.0]
        _, ax = _new_3d_axes()
        x, y, z = fourier_copilot_3d(
            R, A, [0.1, 0.2, 0.3, 0.4], 1,
            B=B, gamma=[0.5, 0.6, 0.7, 0.8], points=2000, ax=ax,
        )

        norms = np.sqrt(x**2 + y**2 + z**2)
        self.assertLessEqual(norms.max(), sum(R) + 1e-12)

    # ---------- 返回值与绘图行为 ----------

    def test_returns_arrays_with_requested_length(self):
        _, ax = _new_3d_axes()
        x, y, z = fourier_copilot_3d([1, 2], [1, 2], [0, 0], 1, points=321, ax=ax)

        for arr in (x, y, z):
            self.assertEqual(arr.shape, (321,))
            self.assertTrue(np.isfinite(arr).all())

    def test_draws_one_line_on_given_axes(self):
        """传入 ax 时应在该 ax 上新增一条 3D 曲线，且数据与返回值一致。"""
        _, ax = _new_3d_axes()
        x, y, z = fourier_copilot_3d(
            [1, 2], [1, 2], [0.1, 0.2], 1, B=[2, 1], gamma=[0.3, 0.4],
            color="#0ff", points=100, ax=ax,
        )

        self.assertEqual(len(ax.lines), 1)
        line = ax.lines[0]
        self.assertEqual(line.get_color(), "#0ff")
        lx, ly, lz = line.get_data_3d()
        np.testing.assert_allclose(lx, x)
        np.testing.assert_allclose(ly, y)
        np.testing.assert_allclose(lz, z)

    def test_accepts_lists_tuples_and_numpy_arrays(self):
        _, ax = _new_3d_axes()
        x, y, z = fourier_copilot_3d(
            np.array([1.0, 2.0]), (1, 2), [0, 0], 1,
            B=np.array([2.0, 1.0]), gamma=(0, 0), points=10, ax=ax,
        )
        self.assertEqual(len(x), 10)

    # ---------- 参数校验 ----------

    def test_rejects_mismatched_lengths(self):
        _, ax = _new_3d_axes()
        with self.assertRaises(ValueError):
            fourier_copilot_3d([1, 2], [1], [0], 1, ax=ax)
        with self.assertRaises(ValueError):
            fourier_copilot_3d([1, 2], [1, 2], [0, 0], 1, B=[1], ax=ax)
        with self.assertRaises(ValueError):
            fourier_copilot_3d([1, 2], [1, 2], [0, 0], 1, gamma=[0], ax=ax)

    def test_rejects_empty_input(self):
        _, ax = _new_3d_axes()
        with self.assertRaises(ValueError):
            fourier_copilot_3d([], [], [], 1, ax=ax)

    def test_rejects_too_few_points(self):
        _, ax = _new_3d_axes()
        with self.assertRaises(ValueError):
            fourier_copilot_3d([1], [1], [0], 1, points=1, ax=ax)

    def test_rejects_multi_dimensional_input(self):
        _, ax = _new_3d_axes()
        with self.assertRaises(ValueError):
            fourier_copilot_3d([[1, 2]], [[1, 2]], [[0, 0]], 1, ax=ax)


if __name__ == "__main__":
    unittest.main(verbosity=2)
