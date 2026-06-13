import math
import math
from typing import List, Optional, Tuple

import bpy


def _arc_points_fast(
    cx: float,
    cy: float,
    radius: float,
    theta_start: float,
    theta_end: float,
    rotation_rad: float,
    points: int,
    direction: str = "ccw",
) -> List[Tuple[float, float]]:
    """Efficient arc point generator without intermediate lists.

    Uses local bindings for math functions to reduce attribute lookups.
    """
    points = max(2, int(points))
    cos = math.cos
    sin = math.sin
    delta = theta_end - theta_start
    out: List[Tuple[float, float]] = []
    if direction not in {"ccw", "cw"}:
        direction = "ccw"
    if direction == "ccw":
        rng = range(points)
        step = 1.0 / (points - 1)
    else:
        rng = range(points - 1, -1, -1)
        step = 1.0 / (points - 1)
    for i in rng:
        t = i * step
        theta = theta_start + delta * t + rotation_rad
        out.append((cx + radius * cos(theta), cy + radius * sin(theta)))
    return out


def _choose_chain_simple(
    pts1: List[Tuple[float, float]], pts2: List[Tuple[float, float]]
) -> List[Tuple[float, float]]:
    """Attach pts2 to pts1 choosing forward or reversed orientation quickly."""
    if not pts1:
        return pts2[:]
    if not pts2:
        return pts1[:]
    a0 = pts1[0]
    a1 = pts1[-1]
    b0 = pts2[0]
    b1 = pts2[-1]

    def d2(p, q):
        dx = p[0] - q[0]
        dy = p[1] - q[1]
        return dx * dx + dy * dy

    fwd_score = d2(a1, b0) + d2(a0, b1)
    rev_score = d2(a1, b1) + d2(a0, b0)
    if fwd_score <= rev_score:
        chosen = pts2
    else:
        chosen = list(reversed(pts2))
    # drop duplicates that coincide exactly
    if d2(a1, chosen[0]) < 1e-12:
        chosen = chosen[1:]
    if chosen and d2(a0, chosen[-1]) < 1e-12:
        chosen = chosen[:-1]
    return pts1 + chosen


def flower_petal(
    R: float = 1.0,
    r: float = 1.0,
    n: int = 4,
    rotation: float = 0.0,
    center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    use_degree: bool = True,
    direction: str = "ccw",
    boundary_points: int = 80,
    thickness: float = 0.03,
    cup: float = 0.12,
    subsurf_levels: int = 1,
    name: str = "FlowerPetal1",
    triangulate: bool = False,
) -> Optional[bpy.types.Object]:
    """Create a performant petal mesh in Blender from two circular arcs.

    This implementation is self-contained and avoids slow constructs.
    It does not import or rely on other local project modules.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if r <= 0:
        raise ValueError("r must be > 0")

    angle = 2.0 * math.pi / n
    a = R * math.sin(math.pi / n)
    if r < a - 1e-12:
        print(f"r<a,不能形成花瓣。最小需要 r > {a:.3f}")
        return None

    beta = math.acos(max(-1.0, min(1.0, a / r)))
    theta_arc = math.pi / 2.0 - math.pi / n + math.acos(max(-1.0, min(1.0, a / r)))

    rotation_rad = math.radians(rotation) if use_degree else rotation

    center1_theta = rotation_rad + angle / 2.0
    center2_theta = rotation_rad - angle / 2.0

    cx, cy, cz = center
    c1x = math.cos(center1_theta) * R + cx
    c1y = math.sin(center1_theta) * R + cy
    c2x = math.cos(center2_theta) * R + cx
    c2y = math.sin(center2_theta) * R + cy

    if abs(r - a) < 1e-12:
        t1 = math.pi + angle / 2.0
        t2 = math.pi + angle / 2.0 + theta_arc
        t3 = math.pi / 2.0
        t4 = math.pi / 2.0 + theta_arc
    else:
        t1 = math.pi + angle / 2.0
        t2 = math.pi + angle / 2.0 + theta_arc
        t3 = math.pi / 2.0 - beta
        t4 = math.pi / 2.0 - beta + theta_arc

    p1 = max(8, boundary_points // 2)
    p2 = max(8, boundary_points - p1)

    arc1 = _arc_points_fast(c1x, c1y, r, t1, t2, rotation_rad, p1, direction)
    arc2 = _arc_points_fast(c2x, c2y, r, t3, t4, rotation_rad, p2, direction)

    outline2d = _choose_chain_simple(arc1, arc2)
    if len(outline2d) < 3:
        return None

    # compute lift (cup) using compact loops and local bindings
    ux = math.cos(rotation_rad)
    uy = math.sin(rotation_rad)
    vx = -uy
    vy = ux

    s_vals = []
    w_vals = []
    for x, y in outline2d:
        dx = x - cx
        dy = y - cy
        s_vals.append(dx * ux + dy * uy)
        w_vals.append(dx * vx + dy * vy)

    s_min = min(s_vals)
    s_max = max(s_vals)
    w_abs = max(1e-9, max(abs(w) for w in w_vals))

    def _smoothstep(x: float) -> float:
        x = 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)
        return x * x * (3.0 - 2.0 * x)

    verts: List[Tuple[float, float, float]] = []
    span = s_max - s_min
    for i, (x, y) in enumerate(outline2d):
        s = 0.0 if abs(span) < 1e-12 else (s_vals[i] - s_min) / span
        w = w_vals[i] / w_abs
        ridge = 1.0 - w * w
        lift = cup * _smoothstep(s) * ridge
        verts.append((x, y, lift + cz))

    mesh = bpy.data.meshes.new(f"{name}Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # single n-gon face; offer optional triangulation for robustness
    faces = [list(range(len(verts)))]
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    if triangulate:
        try:
            import bmesh

            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.triangulate(
                bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY"
            )
            bm.to_mesh(mesh)
            bm.free()
        except Exception:
            pass

    # modifiers
    solid = obj.modifiers.new(name="Solidify", type="SOLIDIFY")
    solid.thickness = thickness
    solid.offset = 0.0
    solid.use_rim = True

    if subsurf_levels and subsurf_levels > 0:
        sub = obj.modifiers.new(name="Subsurf", type="SUBSURF")
        sub.levels = max(0, int(subsurf_levels))
        sub.render_levels = sub.levels

    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = math.radians(45.0)

    return obj


def demo():
    petal = flower_petal(R=1.0, r=1.15, n=6, rotation=0, boundary_points=160)
    if petal is None:
        return
    if petal.data.materials:
        petal.data.materials[0].diffuse_color = (1.0, 0.8, 0.85, 1.0)
    else:
        mat = bpy.data.materials.new("Petal1Material")
        mat.diffuse_color = (1.0, 0.8, 0.85, 1.0)
        petal.data.materials.append(mat)


if __name__ == "__main__":
    demo()
