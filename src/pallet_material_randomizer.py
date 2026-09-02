"""
Standalone Isaac Sim Pallet Material Randomizer
================================================

Portfolio reconstruction of a pallet property-handling experiment.

What it does
------------
- Launches Isaac Sim in GUI mode.
- Creates one pallet procedurally (no external USD asset required).
- Randomizes the pallet's base color and material surface properties
  (roughness / metallic) at a fixed interval.
- Adds a floor, light, and camera so the result is immediately visible.

Run this script with Isaac Sim's bundled Python, not your system Python.

Example:
    <ISAAC_SIM_ROOT>/python.sh src/pallet_material_randomizer.py
"""

import random
import math

# Isaac Sim 4.5+/5.x first, then older 4.x fallback.
try:
    from isaacsim import SimulationApp
except ImportError:
    from omni.isaac.kit import SimulationApp

simulation_app = SimulationApp(
    {
        "headless": False,
        "width": 1280,
        "height": 720,
    }
)

from pxr import Gf, Sdf, UsdGeom, UsdLux, UsdShade

try:
    from isaacsim.core.api import World
except ImportError:
    from omni.isaac.core import World

import omni.usd


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CHANGE_EVERY_FRAMES = 90
PALLET_ROOT = "/World/Pallet"
PALLET_MATERIAL = "/World/Looks/PalletMaterial"

# (name, color-range, roughness-range, metallic-range)
MATERIAL_PRESETS = [
    ("painted_matte", ((0.10, 0.25, 0.10), (0.95, 1.00, 0.55)), (0.55, 0.90), (0.00, 0.05)),
    ("painted_smooth", ((0.05, 0.15, 0.45), (0.50, 0.85, 1.00)), (0.18, 0.40), (0.00, 0.08)),
    ("wood_like", ((0.35, 0.12, 0.03), (0.85, 0.62, 0.30)), (0.45, 0.80), (0.00, 0.03)),
    ("plastic", ((0.15, 0.15, 0.15), (1.00, 0.95, 0.80)), (0.20, 0.55), (0.00, 0.06)),
    ("metallic", ((0.12, 0.12, 0.14), (0.75, 0.80, 0.90)), (0.12, 0.38), (0.65, 1.00)),
    ("rough_industrial", ((0.10, 0.10, 0.10), (0.60, 0.60, 0.60)), (0.75, 1.00), (0.00, 0.20)),
]


def rand_vec3(lo, hi):
    return tuple(random.uniform(lo[i], hi[i]) for i in range(3))


def define_box(stage, path, center, size):
    """Create a unit cube and scale it to the requested dimensions."""
    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(1.0)

    xform = UsdGeom.Xformable(cube.GetPrim())
    xform.AddTranslateOp().Set(Gf.Vec3d(*center))
    xform.AddScaleOp().Set(Gf.Vec3d(*size))
    return cube.GetPrim()


def create_material(stage):
    material = UsdShade.Material.Define(stage, PALLET_MATERIAL)
    shader = UsdShade.Shader.Define(stage, PALLET_MATERIAL + "/PreviewSurface")
    shader.CreateIdAttr("UsdPreviewSurface")

    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
        Gf.Vec3f(0.60, 0.36, 0.16)
    )
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.60)
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.00)

    material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    return material, shader


def create_pallet(stage, material):
    """
    Create a simple Euro-pallet-like shape from boxes.

    Dimensions are intentionally approximate: this is a lightweight,
    self-contained visualization demo rather than a mechanical CAD model.
    """
    UsdGeom.Xform.Define(stage, PALLET_ROOT)

    parts = []

    # Top slats
    top_y = [-0.48, -0.32, -0.16, 0.0, 0.16, 0.32, 0.48]
    for i, y in enumerate(top_y):
        parts.append(
            define_box(
                stage,
                f"{PALLET_ROOT}/TopSlat_{i:02d}",
                center=(0.0, y, 0.20),
                size=(1.20, 0.115, 0.075),
            )
        )

    # Cross boards
    for i, x in enumerate((-0.48, 0.0, 0.48)):
        parts.append(
            define_box(
                stage,
                f"{PALLET_ROOT}/CrossBoard_{i:02d}",
                center=(x, 0.0, 0.125),
                size=(0.16, 1.00, 0.075),
            )
        )

    # Blocks
    for ix, x in enumerate((-0.48, 0.0, 0.48)):
        for iy, y in enumerate((-0.38, 0.0, 0.38)):
            parts.append(
                define_box(
                    stage,
                    f"{PALLET_ROOT}/Block_{ix}_{iy}",
                    center=(x, y, 0.055),
                    size=(0.17, 0.17, 0.11),
                )
            )

    # Bottom runners
    for i, x in enumerate((-0.48, 0.0, 0.48)):
        parts.append(
            define_box(
                stage,
                f"{PALLET_ROOT}/BottomRunner_{i:02d}",
                center=(x, 0.0, -0.02),
                size=(0.17, 1.00, 0.07),
            )
        )

    for prim in parts:
        UsdShade.MaterialBindingAPI(prim).Bind(material)


def create_floor(stage):
    floor_prim = define_box(
        stage,
        "/World/Floor",
        center=(0.0, 0.0, -0.10),
        size=(8.0, 8.0, 0.10),
    )

    material = UsdShade.Material.Define(stage, "/World/Looks/FloorMaterial")
    shader = UsdShade.Shader.Define(stage, "/World/Looks/FloorMaterial/PreviewSurface")
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
        Gf.Vec3f(0.17, 0.18, 0.20)
    )
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.80)
    material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    UsdShade.MaterialBindingAPI(floor_prim).Bind(material)


def create_lighting(stage):
    dome = UsdLux.DomeLight.Define(stage, "/World/DomeLight")
    dome.CreateIntensityAttr(700.0)

    key = UsdLux.DistantLight.Define(stage, "/World/KeyLight")
    key.CreateIntensityAttr(2200.0)
    key.CreateAngleAttr(0.8)

    xform = UsdGeom.Xformable(key.GetPrim())
    xform.AddRotateXYZOp().Set(Gf.Vec3f(45.0, -30.0, 35.0))


def create_camera(stage):
    camera = UsdGeom.Camera.Define(stage, "/World/Camera")

    # Build a camera transform that looks at the pallet center.
    eye = Gf.Vec3d(2.6, 2.4, 1.9)
    target = Gf.Vec3d(0.0, 0.0, 0.12)
    up = Gf.Vec3d(0.0, 0.0, 1.0)

    view = Gf.Matrix4d().SetLookAt(eye, target, up)
    camera_xform = view.GetInverse()

    xform = UsdGeom.Xformable(camera.GetPrim())
    xform.AddTransformOp().Set(camera_xform)

    camera.CreateFocalLengthAttr(38.0)
    camera.CreateHorizontalApertureAttr(20.955)

    try:
        import omni.kit.viewport.utility as viewport_utils
        viewport = viewport_utils.get_active_viewport()
        if viewport is not None:
            viewport.set_active_camera("/World/Camera")
    except Exception as exc:
        print(f"[INFO] Viewport camera could not be activated automatically: {exc}")


def randomize_pallet_material(shader):
    preset_name, color_bounds, roughness_bounds, metallic_bounds = random.choice(
        MATERIAL_PRESETS
    )

    color = rand_vec3(color_bounds[0], color_bounds[1])
    roughness = random.uniform(*roughness_bounds)
    metallic = random.uniform(*metallic_bounds)

    shader.GetInput("diffuseColor").Set(Gf.Vec3f(*color))
    shader.GetInput("roughness").Set(float(roughness))
    shader.GetInput("metallic").Set(float(metallic))

    print(
        "[PALLET RANDOMIZED] "
        f"preset={preset_name:>16s} | "
        f"rgb=({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f}) | "
        f"roughness={roughness:.2f} | metallic={metallic:.2f}"
    )


def main():
    world = World(stage_units_in_meters=1.0)
    world.reset()

    stage = omni.usd.get_context().get_stage()

    create_floor(stage)
    material, shader = create_material(stage)
    create_pallet(stage, material)
    create_lighting(stage)
    create_camera(stage)

    randomize_pallet_material(shader)

    print("\n" + "=" * 72)
    print("Pallet Material Randomizer is running.")
    print(f"Material changes every {CHANGE_EVERY_FRAMES} rendered frames.")
    print("Close the Isaac Sim window to stop.")
    print("=" * 72 + "\n")

    frame = 0
    while simulation_app.is_running():
        world.step(render=True)
        frame += 1

        if frame % CHANGE_EVERY_FRAMES == 0:
            randomize_pallet_material(shader)

    simulation_app.close()


if __name__ == "__main__":
    main()
