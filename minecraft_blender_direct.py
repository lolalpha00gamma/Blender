import bpy
import math
import random

PALETTE = {
    "stone":   (0.42, 0.42, 0.44, 1.0),
    "dirt":    (0.36, 0.25, 0.16, 1.0),
    "grass":   (0.25, 0.52, 0.18, 1.0),
    "obsidian": (0.09, 0.05, 0.14, 1.0),
    "planks":  (0.33, 0.22, 0.12, 1.0),
    "log":     (0.40, 0.29, 0.16, 1.0),
    "leaves":  (0.16, 0.42, 0.16, 1.0),
    "water":   (0.16, 0.40, 0.72, 0.55),
    "sand":    (0.80, 0.72, 0.46, 1.0),
}

FACES = (
    ((-1, 0, 0), ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0))),
    ((1, 0, 0),  ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))),
    ((0, -1, 0), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))),
    ((0, 1, 0),  ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))),
    ((0, 0, -1), ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0))),
    ((0, 0, 1),  ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))),
)


class VoxelWorld:
    def __init__(self):
        self.voxels = {}

    def set(self, x, y, z, material):
        self.voxels[(int(x), int(y), int(z))] = material

    def fill_box(self, x0, y0, z0, x1, y1, z1, material):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    self.voxels[(x, y, z)] = material

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


def build_terrain(world, width, depth, thickness):
    for x in range(-width // 2, width // 2):
        for y in range(-depth // 2, depth // 2):
            for z in range(0, thickness):
                if z < thickness - 3:
                    material = "stone"
                elif z < thickness - 1:
                    material = "dirt"
                else:
                    material = "grass"
                world.set(x, y, z, material)


def build_mega_base(world, cx, cy, ground_z, radius, wall_height):
    for x in range(cx - radius, cx + radius + 1):
        for y in range(cy - radius, cy + radius + 1):
            dist = math.hypot(x - cx, y - cy)
            if dist > radius:
                continue
            world.set(x, y, ground_z, "obsidian")
            if dist > radius - 1.5:
                for z in range(ground_z + 1, ground_z + wall_height + 1):
                    world.set(x, y, z, "planks")


def build_forest(world, cx, cy, ground_z, radius, tree_count, rng):
    for _ in range(tree_count):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(0, radius)
        tx = cx + int(dist * math.cos(angle))
        ty = cy + int(dist * math.sin(angle))
        height = rng.randint(5, 9)

        for z in range(ground_z, ground_z + height):
            world.set(tx, ty, z, "log")

        crown = height // 3 + 1
        top = ground_z + height
        for dx in range(-crown, crown + 1):
            for dy in range(-crown, crown + 1):
                for dz in range(-crown, crown + 1):
                    if math.sqrt(dx * dx + dy * dy + dz * dz) > crown:
                        continue
                    if rng.random() < 0.25:
                        continue
                    pos = (tx + dx, ty + dy, top + dz)
                    if pos not in world.voxels:
                        world.set(pos[0], pos[1], pos[2], "leaves")


def build_lake(world, cx, cy, surface_z, radius, depth):
    for x in range(cx - radius, cx + radius + 1):
        for y in range(cy - radius, cy + radius + 1):
            dist = math.hypot(x - cx, y - cy)
            if dist > radius:
                continue
            basin = int(depth * (1.0 - dist / radius)) + 1
            for z in range(surface_z - basin, surface_z + 1):
                world.set(x, y, z, "water")
            for z in range(surface_z - basin - 1, surface_z - basin):
                world.set(x, y, z, "sand")


def generate(width=80, depth=80, thickness=6):
    rng = random.Random(42)
    world = VoxelWorld()

    ground_z = thickness - 1

    build_terrain(world, width, depth, thickness)
    build_mega_base(world, 0, 0, ground_z, radius=15, wall_height=8)
    build_forest(world, -28, 0, ground_z + 1, radius=12, tree_count=14, rng=rng)
    build_lake(world, 28, 0, surface_z=ground_z, radius=12, depth=3)

    faces = emit_to_blender(world)
    print("Minecraft world: {} voxels -> {} faces".format(len(world.voxels), faces))
    return world


generate()
