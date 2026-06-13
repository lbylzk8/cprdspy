"""
Blender petal mesh generator (NumPy-accelerated).

Usage: run inside Blender's scripting workspace. Provides `create_petal`
which builds a single petal mesh from two circular arcs (ported from
`flower_petal`) and is optimized with NumPy to support large vertex counts.

Function signature:
    create_petal(name, R, r, n, rotation=0.0, center=(0,0,0),
                      points=2048, thickness=0.0, cap=True)

`thickness` extrudes along local normal to make a thin 3D petal when >0.
"""

import math
import numpy as np

try:
    import bpy
    from mathutils import Vector, Matrix
except Exception:
    bpy = None
    try:
        from mathutils import Matrix
    except Exception:
        Matrix = None


def _compute_petal_arcs(
    R=1.0, r=1.0, n=4, rotation=0.0, center=(0.0, 0.0), points=1024, use_degree=True
):
    """Compute two mirrored arc paths (x,y) for a petal using NumPy.

    Returns concatenated points (N,2) where first half is arc1, second half is
    arc2 reversed to form a closed loop. Rotation is in radians.
    """
    angle = 2.0 * math.pi / n
    a = R * math.sin(math.pi / n)
    # guard for numerical domain
    if r <= 0:
        raise ValueError("r must be > 0")
    beta = np.arccos(np.clip(a / r, -1.0, 1.0))
    theta_arc = math.pi / 2 - math.pi / n + math.acos(np.clip(a / r, -1.0, 1.0))

    # If rotation provided in degrees, convert to radians to match math trig
    rotation_rad = math.radians(rotation) if use_degree else float(rotation)

    # rotations for two circle centers
    center1_theta = rotation_rad + angle / 2.0
    center2_theta = rotation_rad - angle / 2.0

    c1x = math.cos(center1_theta) * R + center[0]
    c1y = math.sin(center1_theta) * R + center[1]
    c2x = math.cos(center2_theta) * R + center[0]
    c2y = math.sin(center2_theta) * R + center[1]

    # compute base angles (radians) for arcs relative to each circle center
    theta1_base = math.pi + angle / 2.0
    theta2_base = theta1_base + theta_arc
    theta3_base = math.pi / 2.0 - beta
    theta4_base = theta3_base + theta_arc

    # ensure `points` is a positive integer and split between arcs
    points = int(points)

    pts_arc1 = points // 2
    pts_arc2 = points - pts_arc1

    # sample each arc in its natural (increasing-angle) direction so endpoints align
    t1 = np.linspace(theta1_base, theta2_base, pts_arc1, endpoint=True)
    t2 = np.linspace(theta3_base, theta4_base, pts_arc2, endpoint=True)

    arc1_x = c1x + r * np.cos(t1)
    arc1_y = c1y + r * np.sin(t1)

    arc2_x = c2x + r * np.cos(t2)
    arc2_y = c2y + r * np.sin(t2)

    # if one arc produced empty (defensive), fall back to mirrored arc to close loop
    if arc1_x.size == 0 and arc2_x.size == 0:
        raise ValueError("no samples generated for arcs; check parameters")
    if arc2_x.size == 0:
        arc2_x = arc1_x[::-1]
        arc2_y = arc1_y[::-1]
    if arc1_x.size == 0:
        arc1_x = arc2_x[::-1]
        arc1_y = arc2_y[::-1]

    pts1 = np.column_stack((arc1_x, arc1_y)) if arc1_x.size > 0 else np.empty((0, 2))
    pts2 = np.column_stack((arc2_x, arc2_y)) if arc2_x.size > 0 else np.empty((0, 2))

    if pts1.shape[0] == 0 and pts2.shape[0] == 0:
        raise ValueError("no samples generated for petal; check parameters")
    # return two separate arc point arrays (preserve separation to avoid connecting them)
    return pts1, pts2


def create_petal(
    name: str,
    R=1.0,
    r=1.0,
    n=4,
    rotation=0.0,
    center=(0.0, 0.0, 0.0),
    points=2048,
    thickness=0.0,
    cap=True,
    material=None,
    color=(1.0, 1.0, 1.0, 1.0),
    line_width=1.0,
    emission_strength=1.0,
    use_degree=True,
):
    """Create a Blender mesh object representing one petal.

    - `rotation` in radians.
    - `points` total sampled points along both arcs (higher -> smoother).
    - `thickness` extrudes the 2D loop along its normal to create volume.
    Returns the created object (or vertex/face arrays if bpy not available).
    """
    # generate arcs without applying rotation, then rotate entire object in Blender
    pts1, pts2 = _compute_petal_arcs(
        R, r, n, 0.0, (center[0], center[1]), points, use_degree=use_degree
    )

    # Convert to 3D vertices centered on given z for each arc
    v1 = (
        np.hstack([pts1, np.full((pts1.shape[0], 1), center[2])])
        if pts1.size
        else np.empty((0, 3))
    )
    v2 = (
        np.hstack([pts2, np.full((pts2.shape[0], 1), center[2])])
        if pts2.size
        else np.empty((0, 3))
    )

    # If Blender not available, return arrays + style metadata for external use/testing
    if bpy is None:
        # build edges per-arc (open polyline, not closed)
        def arc_edges(nv):
            if nv < 2:
                return np.empty((0, 2), dtype=int)
            return np.column_stack([np.arange(nv - 1), np.arange(1, nv)])

        return {
            "arc1": {"verts": v1.astype(float), "edges": arc_edges(v1.shape[0])},
            "arc2": {"verts": v2.astype(float), "edges": arc_edges(v2.shape[0])},
            "thickness": float(thickness),
            "color": tuple(color),
            "line_width": float(line_width),
        }

    # Create a Curve object so we can set bevel (thickness) and resolution
    curve_data = bpy.data.curves.new(name + "_curve", type="CURVE")
    curve_data.dimensions = "3D"

    # create spline for arc1
    if v1.shape[0] > 0:
        spline1 = curve_data.splines.new(type="POLY")
        spline1.points.add(v1.shape[0] - 1)
        for i, vv in enumerate(v1.tolist()):
            x, y, z = vv
            spline1.points[i].co = (x, y, z, 1.0)
        spline1.use_cyclic_u = False

    # create spline for arc2
    if v2.shape[0] > 0:
        spline2 = curve_data.splines.new(type="POLY")
        spline2.points.add(v2.shape[0] - 1)
        for i, vv in enumerate(v2.tolist()):
            x, y, z = vv
            spline2.points[i].co = (x, y, z, 1.0)
        spline2.use_cyclic_u = False

    # set bevel (thickness) and resolution
    curve_data.bevel_depth = float(thickness)
    curve_data.bevel_resolution = max(0, int(line_width))

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)

    # apply rotation to the whole object around world origin using Blender's matrix
    if rotation is not None and rotation != 0:
        rot_rad = math.radians(rotation) if use_degree else float(rotation)
        if Matrix is not None:
            rotm = Matrix.Rotation(rot_rad, 4, "Z")
            # apply rotation about world origin
            obj.matrix_world = rotm @ obj.matrix_world
        else:
            # fallback: set Euler rotation (may rotate around object origin)
            try:
                obj.rotation_euler[2] = rot_rad
            except Exception:
                pass

    # create or assign an Emission material so color is visible regardless of lighting
    if color is not None:
        try:
            r, g, b, a = color
        except Exception:
            r, g, b, a = (1.0, 1.0, 1.0, 1.0)
        mat_name = f"mat_{name}_emission"
        if mat_name in bpy.data.materials:
            mat = bpy.data.materials[mat_name]
        else:
            mat = bpy.data.materials.new(mat_name)
            mat.use_nodes = True
            # clear existing nodes
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            for n in list(nodes):
                nodes.remove(n)
            # create emission -> output
            em = nodes.new(type="ShaderNodeEmission")
            em.inputs[0].default_value = (r, g, b, a)
            em.inputs[1].default_value = float(emission_strength)
            out = nodes.new(type="ShaderNodeOutputMaterial")
            links.new(em.outputs[0], out.inputs[0])
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat
        # also set object viewport/display color for Solid view
        try:
            obj.color = (r, g, b, a)
            obj.active_material.diffuse_color = (r, g, b, a)
        except Exception:
            pass

    return obj


def clear_scene(remove_mesh_data=True):
    objs = list(bpy.context.scene.objects)
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)
    if remove_mesh_data:
        for m in list(bpy.data.meshes):
            bpy.data.meshes.remove(m, do_unlink=True)


if __name__ == "__main__":
    # example quick usage when run inside Blender's text editor
    if bpy is None:
        print("Blender not available. Import inside Blender to create objects.")
    else:
        clear_scene()
        # create_petal(
        #     "petal_example",
        #     R=1.0,
        #     r=1.05,
        #     n=5,
        #     rotation=0.0,
        #     points=4096,
        #     thickness=0.01,
        # )
        # create_petal(
        #     "petal_line",
        #     R=1.0,
        #     r=1.0,
        #     n=6,
        #     rotation=np.pi / 3,
        #     points=2048,
        #     thickness=0.02,
        #     color=(1, 0, 0, 1),
        #     line_width=2,
        # )
        for i in range(6):
            create_petal(
                f"petal_{i}",
                R=1.0,
                r=1.0,
                n=6,
                rotation=i * np.pi / 3,
                points=4096,
                thickness=0.01,
                color=(1, 0.5, 0.5, 1),
                line_width=2,
            )
