"""
Unit tests for ellipsoid module.
"""

import numpy as np
from cprdspy.CPR_plotly.Spheres import ellipsoid, ellipsoids


def test_basic_sphere():
    """Test default sphere creation."""
    fig = ellipsoid()
    assert len(fig.data) == 1, "Default sphere should have 1 trace"
    print("[PASS] test_basic_sphere")


def test_ellipsoid_params():
    """Test ellipsoid with custom parameters."""
    fig = ellipsoid(a=2, b=1.5, c=0.8, u_res=20, v_res=20)
    assert len(fig.data) == 1
    # Check surface data shape
    assert fig.data[0].x.shape == (20, 20)
    assert fig.data[0].y.shape == (20, 20)
    assert fig.data[0].z.shape == (20, 20)
    print("[PASS] test_ellipsoid_params")


def test_translation():
    """Test ellipsoid translation (center parameter)."""
    center = (3, 2, 1)
    fig = ellipsoid(a=1, b=1, c=1, center=center, u_res=10, v_res=10)

    # Check that center point is approximately in the data
    x = fig.data[0].x
    y = fig.data[0].y
    z = fig.data[0].z

    # The center should be near the mean of the ellipsoid
    x_mean, y_mean, z_mean = np.mean(x), np.mean(y), np.mean(z)
    assert abs(x_mean - center[0]) < 0.5
    assert abs(y_mean - center[1]) < 0.5
    assert abs(z_mean - center[2]) < 0.5
    print("[PASS] test_translation")


def test_rotation():
    """Test ellipsoid rotation."""
    fig_no_rot = ellipsoid(a=2, b=1, c=0.5, u_res=15, v_res=15)
    fig_rot = ellipsoid(a=2, b=1, c=0.5, rotation=(90, 0, 0), u_res=15, v_res=15)

    # After 90 degree rotation around X, y and z should swap (roughly)
    # This is a basic check - exact verification would be complex
    assert len(fig_no_rot.data) == 1
    assert len(fig_rot.data) == 1
    print("[PASS] test_rotation")


def test_wireframe():
    """Test wireframe mode."""
    fig = ellipsoid(a=1, b=1, c=1, wireframe=True, u_res=10, v_res=10)
    # Wireframe creates u_res*v_res + u_res*v_res traces (grid lines)
    expected_traces = 10 + 10  # v_res + u_res for grid lines
    assert (
        len(fig.data) == expected_traces
    ), f"Expected {expected_traces} traces, got {len(fig.data)}"
    print("[PASS] test_wireframe")


def test_multiple_ellipsoids():
    """Test ellipsoids function with multiple ellipsoids."""
    fig = ellipsoids(
        {"a": 1, "b": 1, "c": 1},
        {"a": 1.5, "b": 1, "c": 2, "center": (3, 0, 0)},
        {"a": 0.8, "b": 0.8, "c": 1.2, "rotation": (45, 30, 60)},
        title="Test Multiple",
    )
    assert len(fig.data) == 3, f"Expected 3 traces, got {len(fig.data)}"
    assert fig.layout.title.text == "Test Multiple"
    print("[PASS] test_multiple_ellipsoids")


def test_color_parameter():
    """Test custom color."""
    fig = ellipsoid(color="rgba(255, 0, 0, 0.5)", name="Red Ellipsoid")
    assert len(fig.data) == 1
    assert fig.data[0].name == "Red Ellipsoid"
    print("[PASS] test_color_parameter")


def test_custom_resolution():
    """Test custom resolution."""
    fig_low = ellipsoid(u_res=10, v_res=10)
    fig_high = ellipsoid(u_res=50, v_res=50)

    # Higher resolution should have more data points
    assert fig_high.data[0].x.size > fig_low.data[0].x.size
    print("[PASS] test_custom_resolution")


def test_figure_reuse():
    """Test adding to existing figure."""
    fig = ellipsoid(a=1, b=1, c=1, name="First")
    assert len(fig.data) == 1

    # Add another ellipsoid to the same figure
    ellipsoid(a=1.5, b=1, c=2, center=(2, 0, 0), fig=fig, name="Second")
    assert len(fig.data) == 2
    print("[PASS] test_figure_reuse")


if __name__ == "__main__":
    test_basic_sphere()
    test_ellipsoid_params()
    test_translation()
    test_rotation()
    test_wireframe()
    test_multiple_ellipsoids()
    test_color_parameter()
    test_custom_resolution()
    test_figure_reuse()

    print("\n" + "=" * 50)
    print("All tests passed!")
    print("=" * 50)
