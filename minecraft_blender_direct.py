import bpy
import math
import random

PALETTE = {
    "stone":        (0.42, 0.42, 0.44, 1.0),
    "dirt":         (0.36, 0.25, 0.16, 1.0),
    "grass":        (0.25, 0.52, 0.18, 1.0),
    "obsidian":     (0.09, 0.05, 0.14, 1.0),
    "planks":       (0.33, 0.22, 0.12, 1.0),
    "log":          (0.40, 0.29, 0.16, 1.0),
    "leaves":       (0.16, 0.42, 0.16, 1.0),
    "water":        (0.16, 0.40, 0.72, 0.55),
    "sand":         (0.80, 0.72, 0.46, 1.0),
    "glass":        (0.75, 0.88, 0.95, 0.30),
    "glass_pane":   (0.80, 0.92, 0.97, 0.25),
    "brick":        (0.65, 0.25, 0.15, 1.0),
    "quartz":       (0.92, 0.90, 0.87, 1.0),
    "concrete":     (0.25, 0.25, 0.28, 1.0),
    "concrete_light": (0.72, 0.72, 0.75, 1.0),
    "cobblestone":  (0.38, 0.38, 0.40, 1.0),
    "iron_block":   (0.78, 0.78, 0.80, 1.0),
    "gold_block":   (0.83, 0.70, 0.20, 1.0),
    "furnace":      (0.32, 0.32, 0.33, 1.0),
    "crafting_table": (0.40, 0.27, 0.15, 1.0),
    "bookshelf":    (0.42, 0.28, 0.14, 1.0),
    "chest":        (0.46, 0.32, 0.14, 1.0),
    "hay":          (0.75, 0.62, 0.15, 1.0),
    "torch":        (0.95, 0.75, 0.20, 1.0),
    "carpet_red":   (0.55, 0.10, 0.10, 1.0),
    "roof_dark":    (0.20, 0.14, 0.12, 1.0),
    "roof_red":     (0.45, 0.13, 0.10, 1.0),
    "fence":        (0.36, 0.25, 0.14, 1.0),
    "lantern":      (0.85, 0.70, 0.30, 1.0),
    "path":         (0.55, 0.47, 0.34, 1.0),
}

FACES = (
    ((-1, 0, 0), ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0))),
    ((1, 0, 0),  ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))),
    ((0, -1, 0), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))),
    ((0, 1, 0),  ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))),
    ((0, 0, -1), ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0))),
    ((0, 0, 1),  ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))),
)


# ---------------------------------------------------------------------------
# Core voxel engine
# ---------------------------------------------------------------------------

class VoxelWorld:
    def __init__(self):
        self.voxels = {}

    def set(self, x, y, z, material):
        if material is None:
            return
        self.voxels[(int(x), int(y), int(z))] = material

    def clear(self, x, y, z):
        self.voxels.pop((int(x), int(y), int(z)), None)

    def get(self, x, y, z):
        return self.voxels.get((int(x), int(y), int(z)))

    def is_solid(self, x, y, z):
        return (int(x), int(y), int(z)) in self.voxels

    def fill_box(self, x0, y0, z0, x1, y1, z1, material):
        if material is None:
            return
        xa, xb = sorted((int(x0), int(x1)))
        ya, yb = sorted((int(y0), int(y1)))
        za, zb = sorted((int(z0), int(z1)))
        for x in range(xa, xb + 1):
            for y in range(ya, yb + 1):
                for z in range(za, zb + 1):
                    self.voxels[(x, y, z)] = material

    def hollow_box(self, x0, y0, z0, x1, y1, z1, wall_material, floor_material=None, roof_material=None):
        xa, xb = sorted((int(x0), int(x1)))
        ya, yb = sorted((int(y0), int(y1)))
        za, zb = sorted((int(z0), int(z1)))
        for x in range(xa, xb + 1):
            for y in range(ya, yb + 1):
                for z in range(za, zb + 1):
                    on_wall = x in (xa, xb) or y in (ya, yb)
                    if on_wall:
                        self.set(x, y, z, wall_material)
                    elif z == za and floor_material:
                        self.set(x, y, z, floor_material)
                    elif z == zb and roof_material:
                        self.set(x, y, z, roof_material)

    def fill_rect_outline(self, x0, y0, z, x1, y1, material):
        xa, xb = sorted((int(x0), int(x1)))
        ya, yb = sorted((int(y0), int(y1)))
        for x in range(xa, xb + 1):
            self.set(x, ya, z, material)
            self.set(x, yb, z, material)
        for y in range(ya, yb + 1):
            self.set(xa, y, z, material)
            self.set(xb, y, z, material)

    def fill_sphere(self, cx, cy, cz, radius, material):
        r_sq = radius * radius
        for x in range(int(cx - radius), int(cx + radius) + 1):
            for y in range(int(cy - radius), int(cy + radius) + 1):
                for z in range(int(cz - radius), int(cz + radius) + 1):
                    dx, dy, dz = x - cx, y - cy, z - cz
                    if dx * dx + dy * dy + dz * dz <= r_sq:
                        self.set(x, y, z, material)

    def build_mesh_data(self):
        solid = self.voxels
        by_material = {}
        for (x, y, z), material in solid.items():
            for normal, corners in FACES:
                nx, ny, nz = x + normal[0], y + normal[1], z + normal[2]
                if (nx, ny, nz) in solid:
                    continue
                bucket = by_material.setdefault(material, ([], [], {}))
                verts, faces, index = bucket
                face = []
                for cx, cy, cz in corners:
                    key = (x + cx, y + cy, z + cz)
                    vi = index.get(key)
                    if vi is None:
                        vi = len(verts)
                        index[key] = vi
                        verts.append(key)
                    face.append(vi)
                faces.append(tuple(face))
        return {m: (v, f) for m, (v, f, _) in by_material.items()}


def get_material(name):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    color = PALETTE.get(name, (0.5, 0.5, 0.5, 1.0))
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        if color[3] < 1.0:
            if "Alpha" in bsdf.inputs:
                bsdf.inputs["Alpha"].default_value = color[3]
            try:
                mat.blend_method = 'BLEND'
            except TypeError:
                pass
    mat.diffuse_color = color
    return mat


def clear_generated(collection_name="Minecraft"):
    existing = bpy.data.collections.get(collection_name)
    if existing is None:
        return
    for obj in list(existing.objects):
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    bpy.data.collections.remove(existing)


def emit_to_blender(world, collection_name="Minecraft"):
    clear_generated(collection_name)
    collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(collection)
    total_faces = 0
    for material_name, (verts, faces) in world.build_mesh_data().items():
        mesh = bpy.data.meshes.new(material_name)
        mesh.from_pydata([(float(a), float(b), float(c)) for a, b, c in verts], [], faces)
        mesh.validate()
        mesh.update()
        mesh.materials.append(get_material(material_name))
        obj = bpy.data.objects.new(material_name, mesh)
        collection.objects.link(obj)
        total_faces += len(faces)
    return total_faces


# ---------------------------------------------------------------------------
# Terrain
# ---------------------------------------------------------------------------

def build_flat_terrain(world, width, depth, ground_z):
    for x in range(-width // 2, width // 2):
        for y in range(-depth // 2, depth // 2):
            world.set(x, y, ground_z - 3, "stone")
            world.set(x, y, ground_z - 2, "stone")
            world.set(x, y, ground_z - 1, "dirt")
            world.set(x, y, ground_z, "grass")


def build_path_area(world, x0, y0, x1, y1, z, material="path"):
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    for x in range(xa, xb + 1):
        for y in range(ya, yb + 1):
            world.set(x, y, z, material)


def build_road(world, x1, y1, x2, y2, z, width=3, material="path"):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps
        x = int(round(x1 + (x2 - x1) * t))
        y = int(round(y1 + (y2 - y1) * t))
        for dx in range(-width // 2, width // 2 + 1):
            for dy in range(-width // 2, width // 2 + 1):
                if abs(dx) + abs(dy) <= width // 2 + 1:
                    world.set(x + dx, y + dy, z, material)


# ---------------------------------------------------------------------------
# Structural primitives (windows, doors, stairs, roofs, pillars, fences)
# ---------------------------------------------------------------------------

def carve_window(world, x, y, z0, z1, axis="x", material=None):
    for z in range(z0, z1 + 1):
        world.set(x, y, z, material)


def carve_windows_along_wall(world, x0, y0, x1, y1, z0, z1, spacing=3, sill=1, material="glass_pane"):
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    if xa == xb:
        for y in range(ya + 1, yb, spacing):
            for z in range(z0 + sill, z1 - sill + 1):
                world.set(xa, y, z, material)
    elif ya == yb:
        for x in range(xa + 1, xb, spacing):
            for z in range(z0 + sill, z1 - sill + 1):
                world.set(x, ya, z, material)


def build_door_gap(world, x, y, z0, height=2):
    for z in range(z0, z0 + height + 1):
        world.clear(x, y, z)


def build_pillar(world, x, y, z0, z1, material="log", cap_material=None):
    for z in range(z0, z1 + 1):
        world.set(x, y, z, material)
    if cap_material:
        world.set(x, y, z1 + 1, cap_material)


def build_fence_line(world, x0, y0, x1, y1, z, material="fence", post_every=1):
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    if ya == yb:
        for x in range(xa, xb + 1, post_every):
            world.set(x, ya, z, material)
            world.set(x, ya, z + 1, material)
    elif xa == xb:
        for y in range(ya, yb + 1, post_every):
            world.set(xa, y, z, material)
            world.set(xa, y, z + 1, material)


def build_flat_roof(world, x0, y0, x1, y1, z, material="quartz", trim_material="brick"):
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    for x in range(xa, xb + 1):
        for y in range(ya, yb + 1):
            edge = x in (xa, xb) or y in (ya, yb)
            world.set(x, y, z, trim_material if edge else material)


def build_pitched_roof(world, x0, y0, x1, y1, z0, material="roof_red", axis="x"):
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    width_x = xb - xa
    width_y = yb - ya

    if axis == "x":
        half = width_y // 2
        for x in range(xa, xb + 1):
            for offset in range(half + 1):
                z = z0 + offset
                world.set(x, ya + offset, z, material)
                world.set(x, yb - offset, z, material)
    else:
        half = width_x // 2
        for y in range(ya, yb + 1):
            for offset in range(half + 1):
                z = z0 + offset
                world.set(xa + offset, y, z, material)
                world.set(xb - offset, y, z, material)


def build_staircase(world, x, y0, y1, z0, material="stone", width=3):
    ya, yb = sorted((y0, y1))
    steps = yb - ya
    for i, y in enumerate(range(ya, yb + 1)):
        z = z0 + i
        for dx in range(width):
            world.fill_box(x + dx, y, z0, x + dx, y, z, material)


def build_ladder_shaft(world, x, y, z0, z1, material="planks"):
    for z in range(z0, z1 + 1):
        world.set(x, y, z, material)


# ---------------------------------------------------------------------------
# Interior furniture detail
# ---------------------------------------------------------------------------

def furnish_storage_room(world, x0, y0, x1, y1, z, rng):
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    for x in range(xa + 1, xb, 2):
        for y in range(ya + 1, yb, 3):
            world.set(x, y, z, "chest")


def furnish_workshop(world, x0, y0, x1, y1, z, rng):
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    cx, cy = (xa + xb) // 2, (ya + yb) // 2
    world.set(cx, cy, z, "crafting_table")
    world.set(cx + 2, cy, z, "furnace")
    world.set(cx - 2, cy, z, "furnace")


def furnish_library_shelves(world, x0, y0, x1, y1, z0, z1, rng):
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    for x in range(xa + 1, xb, 2):
        for z in range(z0, z1):
            world.set(x, ya + 1, z, "bookshelf")
            world.set(x, yb - 1, z, "bookshelf")


def place_lanterns(world, x0, y0, x1, y1, z, spacing=4, material="lantern"):
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    for x in range(xa, xb + 1, spacing):
        for y in range(ya, yb + 1, spacing):
            world.set(x, y, z, material)


def lay_carpet(world, x0, y0, x1, y1, z, material="carpet_red"):
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    for x in range(xa + 1, xb):
        for y in range(ya + 1, yb):
            world.set(x, y, z, material)


# ---------------------------------------------------------------------------
# Multi-storey building generator (the workhorse)
# ---------------------------------------------------------------------------

def build_multistorey_building(world, cx, cy, base_z, width, depth, floors,
                                floor_height=4, wall_material="brick",
                                floor_material="planks", roof_material="roof_red",
                                window_material="glass_pane", door_side="south",
                                rng=None, furnish=None, flat_roof=False,
                                corner_pillars=False, pillar_material="quartz"):
    """Builds a fully enclosed, floor-by-floor building with windows, an
    internal staircase connecting every level, and an optional furnishing
    callback per floor. Nothing floats: floor N sits directly on the
    ceiling of floor N-1."""
    if rng is None:
        rng = random.Random(hash((cx, cy, width, depth)) & 0xFFFFFFFF)

    x0, x1 = cx - width // 2, cx + width // 2
    y0, y1 = cy - depth // 2, cy + depth // 2

    stair_x = x0 + 1

    for floor in range(floors):
        z0 = base_z + floor * floor_height
        z1 = z0 + floor_height - 1

        world.hollow_box(x0, y0, z0, x1, y1, z0, wall_material, floor_material=floor_material)
        for z in range(z0, z1 + 1):
            world.fill_rect_outline(x0, y0, z, x1, y1, wall_material)

        carve_windows_along_wall(world, x0, y0, x0, y1, z0, z1, spacing=3, material=window_material)
        carve_windows_along_wall(world, x1, y0, x1, y1, z0, z1, spacing=3, material=window_material)
        carve_windows_along_wall(world, x0, y0, x1, y0, z0, z1, spacing=3, material=window_material)
        carve_windows_along_wall(world, x0, y1, x1, y1, z0, z1, spacing=3, material=window_material)

        if corner_pillars:
            for px, py in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                build_pillar(world, px, py, z0, z1, material=pillar_material)

        if floor == 0:
            door_x = cx
            if door_side == "south":
                build_door_gap(world, door_x, y0, z0, height=2)
            elif door_side == "north":
                build_door_gap(world, door_x, y1, z0, height=2)
            elif door_side == "east":
                build_door_gap(world, x1, cy, z0, height=2)
            else:
                build_door_gap(world, x0, cy, z0, height=2)

        # internal staircase shaft connecting this floor to the next
        if floor < floors - 1:
            build_ladder_shaft(world, stair_x, y0 + 1, z0 + 1, z1, material="planks")
            for z in range(z0 + 1, z1 + 1):
                world.clear(stair_x, y0 + 1, z)
            world.set(stair_x, y0 + 1, z0, "planks")

        place_lanterns(world, x0, y0, x1, y1, z0 + floor_height - 1, spacing=5)

        if furnish:
            furnish(world, x0, y0, x1, y1, z0 + 1, rng)

    roof_z = base_z + floors * floor_height
    if flat_roof:
        build_flat_roof(world, x0, y0, x1, y1, roof_z, material=roof_material, trim_material="iron_block")
    else:
        build_pitched_roof(world, x0, y0, x1, y1, roof_z, material=roof_material,
                            axis="x" if width >= depth else "y")

    return x0, y0, x1, y1, roof_z


# ---------------------------------------------------------------------------
# Named base facilities (all grounded, all detailed, all connected)
# ---------------------------------------------------------------------------

def build_keep(world, cx, cy, base_z, width=44, depth=44, floors=6, floor_height=5, rng=None):
    """The core structure of the base: a single massive fortified keep.
    Ground floor is the crafting/control hall, upper floors are armories
    and lookout levels, roof carries an observation spire. This is the
    heart everything else physically attaches to."""
    if rng is None:
        rng = random.Random(7)

    x0, x1 = cx - width // 2, cx + width // 2
    y0, y1 = cy - depth // 2, cy + depth // 2
    stair_x = x0 + 2

    for floor in range(floors):
        z0 = base_z + floor * floor_height
        z1 = z0 + floor_height - 1
        wall_mat = "obsidian" if floor == 0 else "cobblestone"

        for z in range(z0, z1 + 1):
            world.fill_rect_outline(x0, y0, z, x1, y1, wall_mat)
        world.fill_box(x0 + 1, y0 + 1, z0, x1 - 1, y1 - 1, z0, "stone")

        carve_windows_along_wall(world, x0, y0, x0, y1, z0, z1, spacing=3, material="glass_pane")
        carve_windows_along_wall(world, x1, y0, x1, y1, z0, z1, spacing=3, material="glass_pane")
        carve_windows_along_wall(world, x0, y0, x1, y0, z0, z1, spacing=3, material="glass_pane")
        carve_windows_along_wall(world, x0, y1, x1, y1, z0, z1, spacing=3, material="glass_pane")

        for px, py in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            build_pillar(world, px, py, z0, z1, material="iron_block")

        if floor == 0:
            build_door_gap(world, cx, y0, z0, height=3)
            build_door_gap(world, cx - 1, y0, z0, height=3)
            build_door_gap(world, cx + 1, y0, z0, height=3)
            lay_carpet(world, x0, y0, x1, y1, z0, "carpet_red")
            furnish_workshop(world, x0, y0, x1, y1, z0 + 1, rng)
        elif floor == 1:
            furnish_library_shelves(world, x0, y0, x1, y1, z0 + 1, z1, rng)
        else:
            furnish_storage_room(world, x0, y0, x1, y1, z0 + 1, rng)

        if floor < floors - 1:
            for z in range(z0 + 1, z1 + 1):
                world.clear(stair_x, y0 + 1, z)
                world.clear(stair_x + 1, y0 + 1, z)
            world.set(stair_x, y0 + 1, z0, "planks")
            world.set(stair_x + 1, y0 + 1, z0, "planks")

        place_lanterns(world, x0, y0, x1, y1, z1, spacing=6)

    roof_z = base_z + floors * floor_height
    build_flat_roof(world, x0, y0, x1, y1, roof_z, material="stone", trim_material="iron_block")

    spire_w = 10
    sx0, sx1 = cx - spire_w // 2, cx + spire_w // 2
    sy0, sy1 = cy - spire_w // 2, cy + spire_w // 2
    spire_height = 14
    for z in range(roof_z + 1, roof_z + 1 + spire_height):
        world.fill_rect_outline(sx0, sy0, z, sx1, sy1, "cobblestone")
        if (z - roof_z) % 3 == 0:
            for angle_deg in range(0, 360, 45):
                angle = math.radians(angle_deg)
                gx = cx + int(round((spire_w // 2 - 1) * math.cos(angle)))
                gy = cy + int(round((spire_w // 2 - 1) * math.sin(angle)))
                world.set(gx, gy, z, "glass_pane")
    spire_top = roof_z + 1 + spire_height
    build_flat_roof(world, sx0, sy0, sx1, sy1, spire_top, material="quartz", trim_material="iron_block")
    build_pillar(world, cx, cy, spire_top, spire_top + 4, material="iron_block", cap_material="lantern")

    return x0, y0, x1, y1, roof_z, spire_top + 4


def build_storage_vault_wing(world, keep_x0, keep_y0, keep_x1, keep_y1, base_z, rng,
                              rows=12, cols=16, floors=3, floor_height=4):
    """A huge storage hall fused directly onto the west face of the keep.
    Rows upon rows of chests on every floor, connected internally."""
    width = cols * 2 + 6
    depth = rows * 2 + 6
    wx1 = keep_x0
    wx0 = wx1 - width
    wy0 = (keep_y0 + keep_y1) // 2 - depth // 2
    wy1 = wy0 + depth
    stair_x = wx0 + 2

    for floor in range(floors):
        z0 = base_z + floor * floor_height
        z1 = z0 + floor_height - 1
        for z in range(z0, z1 + 1):
            world.fill_rect_outline(wx0, wy0, z, wx1, wy1, "quartz")
        world.fill_box(wx0 + 1, wy0 + 1, z0, wx1 - 1, wy1 - 1, z0, "concrete_light")

        carve_windows_along_wall(world, wx0, wy0, wx0, wy1, z0, z1, spacing=3, material="glass_pane")
        carve_windows_along_wall(world, wx0, wy0, wx1, wy0, z0, z1, spacing=3, material="glass_pane")
        carve_windows_along_wall(world, wx0, wy1, wx1, wy1, z0, z1, spacing=3, material="glass_pane")

        for row in range((wy1 - wy0 - 4) // 2):
            for col in range((wx1 - wx0 - 4) // 2):
                cxp = wx0 + 3 + col * 2
                cyp = wy0 + 3 + row * 2
                if cxp < wx1 - 1 and cyp < wy1 - 1:
                    world.set(cxp, cyp, z0 + 1, "chest")

        if floor < floors - 1:
            for z in range(z0 + 1, z1 + 1):
                world.clear(stair_x, wy0 + 2, z)
            world.set(stair_x, wy0 + 2, z0, "planks")

        place_lanterns(world, wx0, wy0, wx1, wy1, z1, spacing=5)

    # corridor fusing the vault directly onto the keep (no gap, no floating)
    corridor_y0 = (keep_y0 + keep_y1) // 2 - 2
    corridor_y1 = (keep_y0 + keep_y1) // 2 + 2
    for x in range(wx1, keep_x0 + 1):
        for y in range(corridor_y0, corridor_y1 + 1):
            world.set(x, y, base_z, "cobblestone")
            world.set(x, y, base_z + 4, "cobblestone")
    for y in range(corridor_y0, corridor_y1 + 1):
        world.clear(wx1, y, base_z + 1)
        world.clear(wx1, y, base_z + 2)
        world.clear(wx1, y, base_z + 3)

    roof_z = base_z + floors * floor_height
    build_flat_roof(world, wx0, wy0, wx1, wy1, roof_z, material="quartz", trim_material="iron_block")

    return wx0, wy0, wx1, wy1, roof_z


def build_smeltery_wing(world, keep_x0, keep_y0, keep_x1, keep_y1, base_z, rng,
                         furnace_rows=6, furnace_cols=8):
    """A dedicated smelting/processing hall fused onto the east face of
    the keep, packed with furnace rows and chimney stacks."""
    width = furnace_cols * 2 + 6
    depth = furnace_rows * 2 + 6
    fx0 = keep_x1
    fx1 = fx0 + width
    fy0 = (keep_y0 + keep_y1) // 2 - depth // 2
    fy1 = fy0 + depth
    height = 7

    for z in range(base_z, base_z + height):
        world.fill_rect_outline(fx0, fy0, z, fx1, fy1, "cobblestone")
    world.fill_box(fx0 + 1, fy0 + 1, base_z, fx1 - 1, fy1 - 1, base_z, "stone")

    carve_windows_along_wall(world, fx1, fy0, fx1, fy1, base_z, base_z + height - 1, spacing=3, material="glass_pane")
    carve_windows_along_wall(world, fx0, fy0, fx1, fy0, base_z, base_z + height - 1, spacing=3, material="glass_pane")
    carve_windows_along_wall(world, fx0, fy1, fx1, fy1, base_z, base_z + height - 1, spacing=3, material="glass_pane")

    for row in range(furnace_rows):
        for col in range(furnace_cols):
            fxp = fx0 + 3 + col * 2
            fyp = fy0 + 3 + row * 2
            if fxp < fx1 - 1 and fyp < fy1 - 1:
                world.set(fxp, fyp, base_z + 1, "furnace")
                if row % 3 == 0 and col % 4 == 0:
                    build_pillar(world, fxp, fyp, base_z + 2, base_z + height + 6, material="obsidian")

    roof_z = base_z + height
    build_flat_roof(world, fx0, fy0, fx1, fy1, roof_z, material="cobblestone", trim_material="obsidian")
    place_lanterns(world, fx0, fy0, fx1, fy1, base_z + height - 1, spacing=4)

    corridor_y0 = (keep_y0 + keep_y1) // 2 - 2
    corridor_y1 = (keep_y0 + keep_y1) // 2 + 2
    for x in range(keep_x1, fx0 + 1):
        for y in range(corridor_y0, corridor_y1 + 1):
            world.set(x, y, base_z, "cobblestone")
            world.set(x, y, base_z + 4, "cobblestone")
    for y in range(corridor_y0, corridor_y1 + 1):
        for z in range(base_z + 1, base_z + 4):
            world.clear(keep_x1, y, z)

    return fx0, fy0, fx1, fy1, roof_z


def build_farm_wing(world, keep_x0, keep_y0, keep_x1, keep_y1, base_z, rng,
                     rows=14, cols=18):
    """A large covered farming wing fused onto the north face of the
    keep, glass-roofed, fenced, with irrigation channels."""
    width = cols * 2 + 6
    depth = rows * 2 + 6
    fy1 = keep_y1
    fy0 = fy1
    fy1 = fy0 + depth
    fx0 = (keep_x0 + keep_x1) // 2 - width // 2
    fx1 = fx0 + width
    roof_height = 5

    build_fence_line(world, fx0, fy0, fx1, fy0, base_z, "fence")
    build_fence_line(world, fx0, fy1, fx1, fy1, base_z, "fence")
    build_fence_line(world, fx0, fy0, fx0, fy1, base_z, "fence")
    build_fence_line(world, fx1, fy0, fx1, fy1, base_z, "fence")

    for row in range(rows):
        for col in range(cols):
            px = fx0 + 3 + col * 2
            py = fy0 + 3 + row * 2
            if px < fx1 - 1 and py < fy1 - 1:
                world.set(px, py, base_z - 1, "dirt")
                world.set(px, py, base_z, "hay" if (row + col) % 5 == 0 else "grass")

    for row in range(0, rows + 1, 4):
        py = fy0 + 3 + row * 2
        for x in range(fx0 + 1, fx1):
            if py < fy1:
                world.set(x, py, base_z, "water")

    for x in range(fx0, fx1 + 1, 4):
        for y in range(fy0, fy1 + 1, 4):
            build_pillar(world, x, y, base_z + 1, base_z + roof_height, material="log")
    build_flat_roof(world, fx0, fy0, fx1, fy1, base_z + roof_height, material="glass", trim_material="log")

    corridor_x0 = (keep_x0 + keep_x1) // 2 - 2
    corridor_x1 = (keep_x0 + keep_x1) // 2 + 2
    for y in range(keep_y1, fy0 + 1):
        for x in range(corridor_x0, corridor_x1 + 1):
            world.set(x, y, base_z, "cobblestone")
    for x in range(corridor_x0, corridor_x1 + 1):
        for z in range(base_z + 1, base_z + 4):
            world.clear(x, keep_y1, z)

    return fx0, fy0, fx1, fy1


def build_mob_grinder_wing(world, keep_x0, keep_y0, keep_x1, keep_y1, base_z, rng,
                            shaft_height=24):
    """A dark obsidian grinding shaft fused onto the south face of the
    keep — the base's mob-farm / XP-grinding facility."""
    width, depth = 14, 14
    gx0 = (keep_x0 + keep_x1) // 2 - width // 2
    gx1 = gx0 + width
    gy1 = keep_y0
    gy0 = gy1 - depth

    for z in range(base_z, base_z + shaft_height):
        world.fill_rect_outline(gx0, gy0, z, gx1, gy1, "obsidian")
        if (z - base_z) % 4 == 0:
            for angle_deg in range(0, 360, 90):
                angle = math.radians(angle_deg)
                gx = (gx0 + gx1) // 2 + int(round((width // 2 - 1) * math.cos(angle)))
                gy = (gy0 + gy1) // 2 + int(round((depth // 2 - 1) * math.sin(angle)))
                world.set(gx, gy, z, "glass_pane")

    top = base_z + shaft_height
    build_flat_roof(world, gx0, gy0, gx1, gy1, top, material="obsidian", trim_material="iron_block")

    inner_x0, inner_x1 = gx0 + 2, gx1 - 2
    inner_y0, inner_y1 = gy0 + 2, gy1 - 2
    for x in range(inner_x0, inner_x1 + 1):
        for y in range(inner_y0, inner_y1 + 1):
            world.set(x, y, base_z + 2, "water")
    world.set((gx0 + gx1) // 2, (gy0 + gy1) // 2, base_z + 1, "chest")

    corridor_x0 = (keep_x0 + keep_x1) // 2 - 2
    corridor_x1 = (keep_x0 + keep_x1) // 2 + 2
    for y in range(gy1, keep_y0 + 1):
        for x in range(corridor_x0, corridor_x1 + 1):
            world.set(x, y, base_z, "cobblestone")
    for x in range(corridor_x0, corridor_x1 + 1):
        for z in range(base_z + 1, base_z + 4):
            world.clear(x, keep_y0, z)

    return gx0, gy0, gx1, gy1, top


def build_nether_portal_room(world, cx, cy, base_z, rng):
    width, depth, height = 10, 8, 6
    x0, x1 = cx - width // 2, cx + width // 2
    y0, y1 = cy - depth // 2, cy + depth // 2
    world.fill_box(x0, y0, base_z, x1, y1, base_z, "obsidian")
    for z in range(base_z, base_z + height):
        world.fill_rect_outline(x0, y0, z, x1, y1, "cobblestone")
    build_door_gap(world, cx, y0, base_z, height=3)

    px0, px1 = cx - 1, cx + 1
    for z in range(base_z + 1, base_z + 4):
        world.set(px0, cy, z, "obsidian")
        world.set(px1, cy, z, "obsidian")
    for x in range(px0, px1 + 1):
        world.set(x, cy, base_z, "obsidian")
        world.set(x, cy, base_z + 4, "obsidian")
    for x in range(px0 + 1, px1):
        for z in range(base_z + 1, base_z + 4):
            world.set(x, cy, z, "obsidian")

    build_flat_roof(world, x0, y0, x1, y1, base_z + height, material="obsidian", trim_material="cobblestone")
    return x0, y0, x1, y1


def build_watchtower(world, cx, cy, base_z, height=22, radius=3, rng=None):
    for z in range(base_z, base_z + height):
        for angle_deg in range(0, 360, 20):
            angle = math.radians(angle_deg)
            x = cx + int(round(radius * math.cos(angle)))
            y = cy + int(round(radius * math.sin(angle)))
            world.set(x, y, z, "cobblestone")
            angle2 = math.radians(angle_deg + 20)
            x2 = cx + int(round(radius * math.cos(angle2)))
            y2 = cy + int(round(radius * math.sin(angle2)))
            steps = max(abs(x2 - x), abs(y2 - y), 1)
            for s in range(steps + 1):
                t = s / steps
                world.set(int(round(x + (x2 - x) * t)), int(round(y + (y2 - y) * t)), z, "cobblestone")

    for z in range(base_z, base_z + height, 6):
        for angle_deg in range(0, 360, 15):
            angle = math.radians(angle_deg)
            x = cx + int(round((radius - 1) * math.cos(angle)))
            y = cy + int(round((radius - 1) * math.sin(angle)))
            world.set(x, y, z, "glass_pane")

    top = base_z + height
    for x in range(cx - radius - 1, cx + radius + 2):
        for y in range(cy - radius - 1, cy + radius + 2):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= radius + 1:
                world.set(x, y, top, "quartz")
    for x in range(cx - radius - 1, cx + radius + 2):
        for y in range(cy - radius - 1, cy + radius + 2):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= radius + 1 and (abs(x - cx) == radius + 1 or abs(y - cy) == radius + 1 or dist >= radius):
                for z in range(top + 1, top + 3):
                    world.set(x, y, z, "cobblestone")
    world.set(cx, cy, top + 4, "lantern")
    return top


def build_perimeter_wall(world, cx, cy, half_w, half_d, base_z, height=10, gate_width=8, ring="cobblestone"):
    x0, x1 = cx - half_w, cx + half_w
    y0, y1 = cy - half_d, cy + half_d

    for x in range(x0, x1 + 1):
        if abs(x - cx) > gate_width // 2:
            for z in range(base_z, base_z + height):
                world.set(x, y0, z, ring)
        for z in range(base_z, base_z + height):
            world.set(x, y1, z, ring)

    for y in range(y0, y1 + 1):
        for z in range(base_z, base_z + height):
            world.set(x0, y, z, ring)
            world.set(x1, y, z, ring)

    for x in range(x0, x1 + 1, 6):
        for z in range(base_z + height - 2, base_z + height):
            world.set(x, y0, z, "brick")
            world.set(x, y1, z, "brick")
    for y in range(y0, y1 + 1, 6):
        for z in range(base_z + height - 2, base_z + height):
            world.set(x0, y, z, "brick")
            world.set(x1, y, z, "brick")

    for gx in range(cx - gate_width // 2, cx + gate_width // 2 + 1):
        for z in range(base_z + height, base_z + height + 2):
            world.set(gx, y0, z, "iron_block")

    for corner_x in (x0, x1):
        for corner_y in (y0, y1):
            build_watchtower(world, corner_x, corner_y, base_z, height=height + 12, radius=3)

    return x0, y0, x1, y1


def build_farm_outside(world, cx, cy, base_z, rng, rows=10, cols=14):
    width = cols * 2 + 4
    depth = rows * 2 + 4
    x0, y0 = cx - width // 2, cy - depth // 2
    x1, y1 = cx + width // 2, cy + depth // 2

    build_fence_line(world, x0, y0, x1, y0, base_z, "fence")
    build_fence_line(world, x0, y1, x1, y1, base_z, "fence")
    build_fence_line(world, x0, y0, x0, y1, base_z, "fence")
    build_fence_line(world, x1, y0, x1, y1, base_z, "fence")

    for row in range(rows):
        for col in range(cols):
            fx = x0 + 2 + col * 2
            fy = y0 + 2 + row * 2
            world.set(fx, fy, base_z - 1, "dirt")
            world.set(fx, fy, base_z, "hay" if (row + col) % 5 == 0 else "grass")

    for row in range(0, rows + 1, 4):
        fy = y0 + 2 + row * 2
        for x in range(x0 + 1, x1):
            world.set(x, fy, base_z, "water")

    return x0, y0, x1, y1


def build_utility_tunnel(world, x1, y1, x2, y2, base_z, height=3, width=3, material="concrete"):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps
        x = int(round(x1 + (x2 - x1) * t))
        y = int(round(y1 + (y2 - y1) * t))
        for dx in range(-width // 2, width // 2 + 1):
            world.set(x + dx, y, base_z, material)
            world.set(x + dx, y, base_z + height, material)
        for dz in range(1, height):
            world.set(x - width // 2, y, base_z + dz, material)
            world.set(x + width // 2, y, base_z + dz, material)
        if step % 6 == 0:
            world.set(x, y, base_z + 1, "lantern")


# ---------------------------------------------------------------------------
# Master assembly — ONE fused Minecraft base, not a city
#
# A single keep at the center with four functional wings physically
# fused to its four faces via short connecting corridors (storage vault
# west, smeltery east, covered farm north, mob grinder south), a nether
# portal room tucked against the keep's southeast corner, an outside
# support farm, and one tight perimeter wall with corner watchtowers
# around the whole fused footprint. No detached houses, no roads to
# faraway districts — everything a player's base actually needs, built
# as one continuous structure.
# ---------------------------------------------------------------------------

def generate(width=220, depth=220, ground_z=0):
    world = VoxelWorld()
    rng = random.Random(1337)
    base_z = ground_z + 1

    build_flat_terrain(world, width, depth, ground_z)

    keep_x0, keep_y0, keep_x1, keep_y1, keep_roof, keep_spire = build_keep(
        world, 0, 0, base_z, width=44, depth=44, floors=6, floor_height=5, rng=rng
    )

    build_storage_vault_wing(world, keep_x0, keep_y0, keep_x1, keep_y1, base_z, rng,
                              rows=12, cols=16, floors=3)
    build_smeltery_wing(world, keep_x0, keep_y0, keep_x1, keep_y1, base_z, rng,
                         furnace_rows=6, furnace_cols=8)
    build_farm_wing(world, keep_x0, keep_y0, keep_x1, keep_y1, base_z, rng,
                     rows=14, cols=18)
    build_mob_grinder_wing(world, keep_x0, keep_y0, keep_x1, keep_y1, base_z, rng,
                            shaft_height=24)

    build_nether_portal_room(world, keep_x1 - 8, keep_y0 - 14, base_z, rng)

    build_farm_outside(world, 0, -140, base_z, rng, rows=10, cols=14)
    build_road(world, 0, keep_y0 - 60, 0, -140, ground_z + 1, width=4)

    half_w = 100
    half_d = 105
    build_perimeter_wall(world, 0, 0, half_w, half_d, ground_z + 1, height=11, gate_width=8)

    build_utility_tunnel(world, 0, 0, 0, -100, ground_z - 4, height=3, width=3)

    faces = emit_to_blender(world)
    print(f"Minecraft Basis: {len(world.voxels)} voxels -> {faces} faces")
    return world


generate()
