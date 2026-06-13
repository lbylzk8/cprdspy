import math

import bpy


def _arc_points(
    *,
    center_xy: tuple[float, float],
    radius: float,
    theta_start: float,
    theta_end: float,
    rotation_rad: float,
    points: int,
    direction: str = "ccw",
) -> list[tuple[float, float]]:
    """
    Generate points along a 2D circular arc in the XY plane (pure tuples, no Vector).
    """
    cx, cy = center_xy
    points = max(2, int(points))

    if direction not in {"ccw", "cw"}:
        direction = "ccw"

    if direction == "ccw":
        ts = [i / (points - 1) for i in range(points)]
    else:
        ts = [i / (points - 1) for i in range(points)][::-1]

    out: list[tuple[float, float]] = []
    for t in ts:
        theta = (1 - t) * theta_start + t * theta_end
        theta = theta + rotation_rad
        x = cx + radius * math.cos(theta)
        y = cy + radius * math.sin(theta)
        out.append((x, y))
    return out


def _choose_chain(
    pts1: list[tuple[float, float]], pts2: list[tuple[float, float]]
) -> list[tuple[float, float]]:
    """Order pts2 to best connect pts1 end-to-start and start-to-end (fast 2D version)."""
    if not pts1 or not pts2:
        return pts1 + pts2

    def _dist2(a: tuple[float, float], b: tuple[float, float]) -> float:
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    fwd = pts2
    rev = list(reversed(pts2))

    score_fwd = _dist2(pts1[-1], fwd[0]) + _dist2(pts1[0], fwd[-1])
    score_rev = _dist2(pts1[-1], rev[0]) + _dist2(pts1[0], rev[-1])

    chosen = fwd if score_fwd <= score_rev else rev

    if _dist2(pts1[-1], chosen[0]) < 1e-12:
        chosen = chosen[1:]
    if chosen and _dist2(pts1[0], chosen[-1]) < 1e-12:
        chosen = chosen[:-1]
    return pts1 + chosen


def flower_petal(
    R: float = 1.0,
    r: float = 1.0,
    n: int = 4,
    rotation: float = 0.0,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    use_degree: bool = True,
    direction: str = "ccw",
    boundary_points: int = 80,
    thickness: float = 0.03,
    cup: float = 0.12,
    subsurf_levels: int = 2,
    name: str = "FlowerPetal",
) -> bpy.types.Object | None:
    """
    Blender mesh version of `flower_petal` from `CPR_matplotlib/Flowers/flower.py`.

    The 2D petal outline is formed by two circular arcs (radius r) whose centers lie on a circle
    of radius R, separated by angle 2π/n, then lifted into a thin 3D surface with a gentle cup.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if r <= 0:
        raise ValueError("r must be > 0")

    angle = 2 * math.pi / n
    a = R * math.sin(math.pi / n)
    if r < a - 1e-12:
        # Same behavior as the original: cannot form a valid petal.
        print(f"r<a,不能形成花瓣。最小需要 r > {a:.3f}")
        return None

    # Match original computations.
    beta = math.acos(max(-1.0, min(1.0, a / r)))
    theta_arc = math.pi / 2 - math.pi / n + math.acos(max(-1.0, min(1.0, a / r)))

    rotation_rad = math.radians(rotation) if use_degree else rotation

    center1_theta = rotation_rad + angle / 2
    center2_theta = rotation_rad - angle / 2

    cx, cy, cz = center
    center1 = (math.cos(center1_theta) * R + cx, math.sin(center1_theta) * R + cy)
    center2 = (math.cos(center2_theta) * R + cx, math.sin(center2_theta) * R + cy)

    if abs(r - a) < 1e-12:
        theta1_base = math.pi + angle / 2
        theta2_base = math.pi + angle / 2 + theta_arc
        theta3_base = math.pi / 2
        theta4_base = math.pi / 2 + theta_arc
    else:
        theta1_base = math.pi + angle / 2
        theta2_base = math.pi + angle / 2 + theta_arc
        theta3_base = math.pi / 2 - beta
        theta4_base = math.pi / 2 - beta + theta_arc

    # Split point budget across the two arcs (lower by default for speed).
    p1 = max(8, boundary_points // 2)
    p2 = max(8, boundary_points - p1)

    arc1_2d = _arc_points(
        center_xy=center1,
        radius=r,
        theta_start=theta1_base,
        theta_end=theta2_base,
        rotation_rad=rotation_rad,
        points=p1,
        direction=direction,
    )
    arc2_2d = _arc_points(
        center_xy=center2,
        radius=r,
        theta_start=theta3_base,
        theta_end=theta4_base,
        rotation_rad=rotation_rad,
        points=p2,
        direction=direction,
    )

    outline_2d = _choose_chain(arc1_2d, arc2_2d)
    if len(outline_2d) < 3:
        return None

    # Add a soft "cup" by lifting vertices based on their local (length, width) coordinates.
    ux = math.cos(rotation_rad)
    uy = math.sin(rotation_rad)
    vx = -uy
    vy = ux

    s_vals: list[float] = []
    w_vals: list[float] = []
    for (x, y) in outline_2d:
        dx = x - cx
        dy = y - cy
        s_vals.append(dx * ux + dy * uy)
        w_vals.append(dx * vx + dy * vy)

    s_min, s_max = min(s_vals), max(s_vals)
    w_abs = max(1e-9, max(abs(w) for w in w_vals))

    def _smoothstep(x: float) -> float:
        x = max(0.0, min(1.0, x))
        return x * x * (3 - 2 * x)

    # Build full 3D outline list (x, y, z).
    outline: list[tuple[float, float, float]] = []
    for i, (x, y) in enumerate(outline_2d):
        s = 0.0 if abs(s_max - s_min) < 1e-9 else (s_vals[i] - s_min) / (s_max - s_min)
        w = w_vals[i] / w_abs
        ridge = 1.0 - w * w  # highest at centerline
        lift = cup * _smoothstep(s) * ridge
        outline.append((x, y, lift + cz))

    # Build mesh (single face) using fast from_pydata.
    mesh = bpy.data.meshes.new(f"{name}Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    verts = outline
    faces = [list(range(len(verts)))]
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    # Make it 3D with modifiers (cheap defaults).
    solid = obj.modifiers.new(name="Solidify", type="SOLIDIFY")
    solid.thickness = thickness
    solid.offset = 0.0
    solid.use_rim = True

    sub = obj.modifiers.new(name="Subsurf", type="SUBSURF")
    sub.levels = max(0, int(subsurf_levels))
    sub.render_levels = sub.levels

    # Smooth shading.
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = math.radians(45)

    return obj


def _ensure_material(
    name: str = "PetalMaterial",
    base_color=(1.0, 0.85, 0.9, 1.0),
) -> bpy.types.Material:
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Roughness"].default_value = 0.65
    return mat


def demo():
    petal = flower_petal(R=1.0, r=1.15, n=6, rotation=0, boundary_points=160)
    if petal is None:
        return
    mat = _ensure_material()
    if petal.data.materials:
        petal.data.materials[0] = mat
    else:
        petal.data.materials.append(mat)


if __name__ == "__main__":
    demo()
