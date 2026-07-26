import bpy
import math
import random

PALETTE = {
    "stone": (0.42, 0.42, 0.44, 1.0),
    "dirt": (0.36, 0.25, 0.16, 1.0),
    "grass": (0.25, 0.52, 0.18, 1.0),
    "obsidian": (0.09, 0.05, 0.14, 1.0),
    "planks": (0.33, 0.22, 0.12, 1.0),
    "log": (0.40, 0.29, 0.16, 1.0),
    "leaves": (0.16, 0.42, 0.16, 1.0),
    "water": (0.16, 0.40, 0.72, 0.55),
    "sand": (0.80, 0.72, 0.46, 1.0),
    "glass": (0.75, 0.88, 0.95, 0.3),
    "brick": (0.65, 0.25, 0.15, 1.0),
    "quartz": (0.92, 0.90, 0.87, 1.0),
    "concrete": (0.25, 0.25, 0.28, 1.0),
    "cobblestone": (0.38, 0.38, 0.40, 1.0),
}

FACES = (
    ((-1, 0, 0), ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0))),
    ((1, 0, 0), ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))),
    ((0, -1, 0), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))),
    ((0, 1, 0), ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))),
    ((0, 0, -1), ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0))),
    ((0, 0, 1), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))),
)

class VoxelWorld:
    def __init__(self):
        self.voxels = {}

    def set(self, x, y, z, material):
        self.voxels[(int(x), int(y), int(z))] = material

    def get(self, x, y, z):
        return self.voxels.get((int(x), int(y), int(z)))

    def is_solid(self, x, y, z):
        return (int(x), int(y), int(z)) in self.voxels

    def fill_box(self, x0, y0, z0, x1, y1, z1, material):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    self.set(x, y, z, material)

    def fill_sphere(self, cx, cy, cz, radius, material):
        r_sq = radius * radius
        for x in range(int(cx - radius), int(cx + radius) + 1):
            for y in range(int(cy - radius), int(cy + radius) + 1):
                for z in range(int(cz - radius), int(cz + radius) + 1):
                    dx = x - cx
                    dy = y - cy
                    dz = z - cz
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

def build_flat_terrain(world, width, depth, ground_z):
    for x in range(-width // 2, width // 2):
        for y in range(-depth // 2, depth // 2):
            world.set(x, y, ground_z - 2, "stone")
            world.set(x, y, ground_z - 1, "dirt")
            world.set(x, y, ground_z, "grass")

def build_central_megabase(world, cx, cy, base_z):
    size = 60
    height = 15

    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + height, "concrete")

    for x in range(cx - size // 2 + 1, cx + size // 2):
        for y in range(cy - size // 2 + 1, cy + size // 2):
            for z in range(base_z + 1, base_z + height):
                if (x % 4 == 0 or y % 4 == 0):
                    world.set(x, y, z, "quartz")
                elif z % 3 == 0:
                    world.set(x, y, z, "glass")

def build_storage_area(world, cx, cy, base_z):
    width, length = 50, 40

    world.fill_box(cx - width // 2, cy - length // 2, base_z, cx + width // 2, cy + length // 2, base_z + 8, "quartz")

    for x in range(cx - width // 2 + 2, cx + width // 2 - 1, 5):
        for y in range(cy - length // 2 + 2, cy + length // 2 - 1, 5):
            world.fill_box(x, y, base_z + 1, x + 3, y + 3, base_z + 7, "air" if False else None)
            for z in range(base_z + 1, base_z + 7):
                world.set(x, y, z, "glass")
                world.set(x + 3, y, z, "glass")
                world.set(x, y + 3, z, "glass")
                world.set(x + 3, y + 3, z, "glass")

def build_farm_area(world, cx, cy, base_z, rows=6, cols=6):
    farm_width = 40
    farm_depth = 40

    world.fill_box(cx - farm_width // 2, cy - farm_depth // 2, base_z - 1, cx + farm_width // 2, cy + farm_depth // 2, base_z - 1, "dirt")

    row_spacing = farm_depth // rows
    col_spacing = farm_width // cols

    for row in range(rows):
        for col in range(cols):
            fx = cx - farm_width // 2 + col * col_spacing
            fy = cy - farm_depth // 2 + row * row_spacing
            world.fill_box(fx, fy, base_z, fx + col_spacing - 2, fy + row_spacing - 2, base_z, "grass")

            world.set(fx + col_spacing - 1, fy, base_z, "water")
            world.set(fx, fy + row_spacing - 1, base_z, "water")

def build_smelter(world, cx, cy, base_z):
    size = 15
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 6, "brick")

    for x in range(cx - size // 2 + 2, cx + size // 2 - 1, 2):
        for y in range(cy - size // 2 + 2, cy + size // 2 - 1, 2):
            world.set(x, y, base_z + 1, "furnace" if world.get(x, y, base_z + 1) is None else "glass")
            world.set(x, y, base_z + 2, "glass")

def build_road(world, x1, y1, x2, y2, base_z, width=3):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        for dx in range(-width // 2, width // 2 + 1):
            world.set(x + dx, y, base_z, "cobblestone")

def build_access_tower(world, cx, cy, base_z, height=20):
    for z in range(base_z, base_z + height):
        world.set(cx, cy, z, "obsidian")
        world.set(cx + 1, cy, z, "obsidian")
        world.set(cx, cy + 1, z, "obsidian")
        world.set(cx + 1, cy + 1, z, "obsidian")

        if z % 5 == 0:
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if abs(dx) == 2 or abs(dy) == 2:
                        world.set(cx + dx, cy + dy, z, "quartz")

def build_perimeter_wall(world, cx, cy, base_z, size, height=8):
    for x in range(cx - size // 2, cx + size // 2 + 1):
        for z in range(base_z, base_z + height):
            world.set(x, cy - size // 2, z, "brick")
            world.set(x, cy + size // 2, z, "brick")

    for y in range(cy - size // 2, cy + size // 2 + 1):
        for z in range(base_z, base_z + height):
            world.set(cx - size // 2, y, z, "brick")
            world.set(cx + size // 2, y, z, "brick")

def build_observation_deck(world, cx, cy, base_z, size=12):
    for x in range(cx - size, cx + size + 1):
        for y in range(cy - size, cy + size + 1):
            world.set(x, y, base_z, "quartz")

    for x in range(cx - size - 1, cx + size + 2):
        world.set(x, cy - size - 1, base_z + 1, "brick")
        world.set(x, cy + size + 1, base_z + 1, "brick")
    for y in range(cy - size - 1, cy + size + 2):
        world.set(cx - size - 1, y, base_z + 1, "brick")
        world.set(cx + size + 1, y, base_z + 1, "brick")

def build_utility_tunnel(world, x1, y1, x2, y2, base_z, height=3, width=3):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        for dx in range(-width // 2, width // 2 + 1):
            for dz in range(0, height + 1):
                world.set(x + dx, y, base_z + dz, "concrete")

def generate(width=200, depth=200, ground_z=0):
    world = VoxelWorld()
    base_z = ground_z

    build_flat_terrain(world, width, depth, ground_z)

    build_central_megabase(world, 0, 0, base_z + 1)

    build_storage_area(world, -80, 0, base_z + 1)
    build_storage_area(world, 80, 0, base_z + 1)

    build_farm_area(world, 0, -80, base_z + 1)
    build_farm_area(world, -60, 60, base_z + 1)
    build_farm_area(world, 60, 60, base_z + 1)

    build_smelter(world, -40, 40, base_z + 1)
    build_smelter(world, 40, 40, base_z + 1)

    build_access_tower(world, -50, -50, base_z + 1)
    build_access_tower(world, 50, -50, base_z + 1)

    build_perimeter_wall(world, 0, 0, base_z + 1, 150)

    build_observation_deck(world, 0, -70, base_z + 1)
    build_observation_deck(world, 0, 70, base_z + 1)

    build_road(world, -80, 0, 0, 0, base_z, 4)
    build_road(world, 0, 0, 80, 0, base_z, 4)
    build_road(world, 0, -80, 0, 0, base_z, 4)
    build_road(world, 0, 0, 0, 80, base_z, 4)

    build_utility_tunnel(world, -50, -50, 0, 0, base_z - 2)
    build_utility_tunnel(world, 50, -50, 0, 0, base_z - 2)
    build_utility_tunnel(world, 0, -80, 0, 0, base_z - 2)

    faces = emit_to_blender(world)
    print(f"Minecraft Megabase: {len(world.voxels)} voxels -> {faces} faces")
    return world

generate()
