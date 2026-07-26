import bpy
import math
import random

PALETTE = {
    "stone":       (0.42, 0.42, 0.44, 1.0),
    "dirt":        (0.36, 0.25, 0.16, 1.0),
    "grass":       (0.25, 0.52, 0.18, 1.0),
    "obsidian":    (0.09, 0.05, 0.14, 1.0),
    "planks":      (0.33, 0.22, 0.12, 1.0),
    "log":         (0.40, 0.29, 0.16, 1.0),
    "leaves":      (0.16, 0.42, 0.16, 1.0),
    "water":       (0.16, 0.40, 0.72, 0.55),
    "sand":        (0.80, 0.72, 0.46, 1.0),
    "gravel":      (0.55, 0.54, 0.53, 1.0),
    "clay":        (0.48, 0.55, 0.58, 1.0),
    "coal_ore":    (0.18, 0.18, 0.20, 1.0),
    "iron_ore":    (0.50, 0.35, 0.25, 1.0),
    "gold_ore":    (0.60, 0.52, 0.20, 1.0),
    "diamond_ore": (0.35, 0.75, 0.75, 1.0),
    "cobblestone": (0.38, 0.38, 0.40, 1.0),
    "brick":       (0.65, 0.25, 0.15, 1.0),
    "sand_stone":  (0.82, 0.73, 0.55, 1.0),
    "dark_oak":    (0.25, 0.15, 0.08, 1.0),
    "birch_log":   (0.70, 0.65, 0.55, 1.0),
    "birch_leaves":(0.65, 0.80, 0.35, 1.0),
    "spruce_log":  (0.30, 0.22, 0.15, 1.0),
    "spruce_leaves":(0.18, 0.35, 0.18, 1.0),
    "acacia_log":  (0.55, 0.32, 0.15, 1.0),
    "acacia_leaves":(0.70, 0.60, 0.20, 1.0),
    "snow":        (0.95, 0.96, 0.98, 1.0),
    "ice":         (0.70, 0.85, 0.95, 0.7),
    "bookshelf":   (0.40, 0.28, 0.15, 1.0),
    "furnace":     (0.35, 0.35, 0.35, 1.0),
    "crafting_table": (0.38, 0.25, 0.15, 1.0),
    "glass":       (0.75, 0.88, 0.95, 0.3),
    "quartz_block":(0.92, 0.90, 0.87, 1.0),
    "concrete_white": (0.95, 0.95, 0.95, 1.0),
    "concrete_black": (0.25, 0.25, 0.28, 1.0),
    "concrete_red":   (0.75, 0.28, 0.22, 1.0),
    "concrete_orange":(0.88, 0.45, 0.12, 1.0),
    "concrete_yellow":(0.92, 0.82, 0.18, 1.0),
    "concrete_green": (0.28, 0.60, 0.22, 1.0),
    "concrete_cyan":  (0.18, 0.70, 0.80, 1.0),
    "concrete_blue":  (0.25, 0.35, 0.88, 1.0),
    "concrete_purple":(0.65, 0.22, 0.75, 1.0),
}

FACES = (
    ((-1, 0, 0), ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0))),
    ((1, 0, 0),  ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))),
    ((0, -1, 0), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))),
    ((0, 1, 0),  ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))),
    ((0, 0, -1), ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0))),
    ((0, 0, 1),  ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))),
)


class PerlinNoise:
    def __init__(self, seed):
        self.permutation = list(range(256))
        rng = random.Random(seed)
        rng.shuffle(self.permutation)
        self.permutation = self.permutation + self.permutation
        self.p = self.permutation

    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(self, t, a, b):
        return a + t * (b - a)

    def grad(self, hash_val, x, y, z):
        h = hash_val & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else z)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def noise(self, x, y, z):
        xi = int(x) & 255
        yi = int(y) & 255
        zi = int(z) & 255
        xf = x - int(x)
        yf = y - int(y)
        zf = z - int(z)
        u = self.fade(xf)
        v = self.fade(yf)
        w = self.fade(zf)
        p = self.p
        aa = p[p[xi] + yi]
        ab = p[p[xi + 1] + yi]
        ba = p[p[xi] + yi + 1]
        bb = p[p[xi + 1] + yi + 1]
        g000 = self.grad(p[aa + zi], xf, yf, zf)
        g100 = self.grad(p[ab + zi], xf - 1, yf, zf)
        g010 = self.grad(p[ba + zi], xf, yf - 1, zf)
        g110 = self.grad(p[bb + zi], xf - 1, yf - 1, zf)
        g001 = self.grad(p[aa + zi + 1], xf, yf, zf - 1)
        g101 = self.grad(p[ab + zi + 1], xf - 1, yf, zf - 1)
        g011 = self.grad(p[ba + zi + 1], xf, yf - 1, zf - 1)
        g111 = self.grad(p[bb + zi + 1], xf - 1, yf - 1, zf - 1)
        x1 = self.lerp(u, g000, g100)
        x2 = self.lerp(u, g010, g110)
        y1 = self.lerp(v, x1, x2)
        x1 = self.lerp(u, g001, g101)
        x2 = self.lerp(u, g011, g111)
        y2 = self.lerp(v, x1, x2)
        return self.lerp(w, y1, y2)

    def fractal_brownian_motion(self, x, y, z, octaves, persistence, scale):
        value = 0.0
        amplitude = 1.0
        freq = 1.0
        max_val = 0.0
        for _ in range(octaves):
            value += self.noise(x * freq / scale, y * freq / scale, z * freq / scale) * amplitude
            max_val += amplitude
            amplitude *= persistence
            freq *= 2.0
        return value / max_val if max_val != 0 else 0


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
                    self.voxels[(x, y, z)] = material

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


def build_grass_terrain(world, width, depth, thickness, noise_gen, base_height):
    for x in range(-width // 2, width // 2):
        for y in range(-depth // 2, depth // 2):
            noise_val = noise_gen.fractal_brownian_motion(x * 0.1, y * 0.1, 0, 4, 0.6, 50)
            height = int(base_height + noise_val * 8)
            for z in range(0, height + 1):
                if z < height - 2:
                    world.set(x, y, z, "stone")
                elif z < height:
                    world.set(x, y, z, "dirt")
                else:
                    world.set(x, y, z, "grass")


def build_cave_system(world, x_range, y_range, z_range, noise_gen, cave_threshold):
    for x in x_range:
        for y in y_range:
            for z in z_range:
                noise_val = noise_gen.fractal_brownian_motion(x * 0.05, y * 0.05, z * 0.1, 3, 0.7, 30)
                if noise_val > cave_threshold and world.get(x, y, z) == "stone":
                    world.voxels.pop((x, y, z), None)


def build_ore_distribution(world, x_range, y_range, z_range, ore_type, rng, frequency, max_vein_size):
    ore_materials = {
        "coal": "coal_ore",
        "iron": "iron_ore",
        "gold": "gold_ore",
        "diamond": "diamond_ore",
    }
    material = ore_materials.get(ore_type, "stone")
    for x in x_range:
        for y in y_range:
            for z in z_range:
                if rng.random() < frequency:
                    vein_size = rng.randint(1, max_vein_size)
                    for _ in range(vein_size):
                        vx = x + rng.randint(-2, 2)
                        vy = y + rng.randint(-2, 2)
                        vz = z + rng.randint(-1, 1)
                        if world.get(vx, vy, vz) == "stone":
                            world.set(vx, vy, vz, material)


def build_mountain_range(world, cx, cy, base_z, width, depth, height, noise_gen, rng):
    for x in range(cx - width // 2, cx + width // 2):
        for y in range(cy - depth // 2, cy + depth // 2):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist > max(width, depth) // 2:
                continue
            noise_val = noise_gen.fractal_brownian_motion(x * 0.08, y * 0.08, 0, 5, 0.65, 60)
            peak_height = int(base_z + (1 - dist / (max(width, depth) // 2)) * height + noise_val * 3)
            for z in range(base_z, peak_height + 1):
                if z < peak_height - 1:
                    world.set(x, y, z, "stone")
                elif z < peak_height:
                    world.set(x, y, z, "dirt")
                else:
                    if base_z + height - z > 15:
                        world.set(x, y, z, "snow")
                    else:
                        world.set(x, y, z, "grass")


def build_desert_biome(world, cx, cy, base_z, width, depth, rng):
    for x in range(cx - width // 2, cx + width // 2):
        for y in range(cy - depth // 2, cy + depth // 2):
            for z in range(base_z, base_z + 5):
                world.set(x, y, z, "sand")
            world.set(x, y, base_z + 4, "sand")


def build_pyramid(world, cx, cy, base_z, size):
    for layer in range(size):
        layer_size = size - layer
        z = base_z + layer
        for x in range(cx - layer_size // 2, cx + layer_size // 2 + 1):
            for y in range(cy - layer_size // 2, cy + layer_size // 2 + 1):
                world.set(x, y, z, "sand_stone")


def build_temple(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z, "stone")
    for i in range(4):
        angle = i * math.pi / 2
        px = cx + int(size * math.cos(angle))
        py = cy + int(size * math.sin(angle))
        for z in range(base_z + 1, base_z + size // 3):
            world.set(px, py, z, "brick")
    for x in range(cx - size // 3, cx + size // 3):
        for y in range(cy - size // 3, cy + size // 3):
            world.set(x, y, base_z + 1, "stone")


def build_advanced_tree(world, tx, ty, base_z, tree_type, height, rng):
    log_mat, leaf_mat = {
        "oak": ("log", "leaves"),
        "birch": ("birch_log", "birch_leaves"),
        "spruce": ("spruce_log", "spruce_leaves"),
        "acacia": ("acacia_log", "acacia_leaves"),
    }.get(tree_type, ("log", "leaves"))

    for z in range(base_z, base_z + height):
        world.set(tx, ty, z, log_mat)

    crown_height = height // 2 + 1
    crown_radius = crown_height // 2
    top_z = base_z + height

    for dx in range(-crown_radius, crown_radius + 1):
        for dy in range(-crown_radius, crown_radius + 1):
            for dz in range(-crown_height, 2):
                dist = math.sqrt(dx * dx + dy * dy + (dz + crown_height // 2) ** 2)
                if dist <= crown_radius:
                    if rng.random() < 0.75:
                        world.set(tx + dx, ty + dy, top_z + dz, leaf_mat)


def build_forest_biome(world, cx, cy, base_z, radius, tree_count, tree_types, rng):
    for _ in range(tree_count):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(0, radius)
        tx = cx + int(dist * math.cos(angle))
        ty = cy + int(dist * math.sin(angle))
        height = rng.randint(4, 8)
        tree_type = rng.choice(tree_types)
        build_advanced_tree(world, tx, ty, base_z + 1, tree_type, height, rng)


def build_lake_system(world, cx, cy, surface_z, radius, depth, rng):
    for x in range(cx - radius, cx + radius + 1):
        for y in range(cy - radius, cy + radius + 1):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist > radius:
                continue
            basin = int(depth * (1.0 - dist / radius)) + 1
            for z in range(surface_z - basin, surface_z + 1):
                world.set(x, y, z, "water")
            for z in range(surface_z - basin - 2, surface_z - basin):
                if rng.random() < 0.5:
                    world.set(x, y, z, "clay")
                else:
                    world.set(x, y, z, "sand")


def build_river_system(world, start_x, start_y, end_x, end_y, width, depth, surface_z):
    steps = max(abs(end_x - start_x), abs(end_y - start_y))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(start_x + (end_x - start_x) * t)
        y = int(start_y + (end_y - start_y) * t)
        for dx in range(-width // 2, width // 2 + 1):
            for dy in range(-width // 2, width // 2 + 1):
                for dz in range(-depth, 1):
                    world.set(x + dx, y + dy, surface_z + dz, "water")


def build_bridge(world, x1, y1, x2, y2, z, width):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        for dx in range(-width // 2, width // 2 + 1):
            world.set(x + dx, y, z, "planks")
            world.set(x + dx, y, z + 1, "planks")


def build_tower(world, cx, cy, base_z, height, radius):
    for z in range(base_z, base_z + height):
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            x = cx + int(radius * math.cos(rad))
            y = cy + int(radius * math.sin(rad))
            world.set(x, y, z, "brick")
    for z in range(base_z + 1, base_z + height):
        for x in range(cx - 2, cx + 3):
            for y in range(cy - 2, cy + 3):
                if abs(x - cx) < 2 and abs(y - cy) < 2:
                    world.set(x, y, z, "planks")


def build_castle(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z, "brick")
    for corner_x in [cx - size // 2, cx + size // 2]:
        for corner_y in [cy - size // 2, cy + size // 2]:
            build_tower(world, corner_x, corner_y, base_z + 1, size // 2, 2)
    for x in range(cx - size // 2 + 2, cx + size // 2 - 1):
        for y in range(cy - size // 2 + 2, cy + size // 2 - 1):
            world.set(x, y, base_z + 1, "planks")


def build_watchtower(world, cx, cy, base_z, height):
    for x in range(cx - 1, cx + 2):
        for y in range(cy - 1, cy + 2):
            for z in range(base_z, base_z + height):
                world.set(x, y, z, "cobblestone")
    for z in range(base_z + height - 2, base_z + height):
        for x in range(cx - 2, cx + 3):
            for y in range(cy - 2, cy + 3):
                if abs(x - cx) <= 2 and abs(y - cy) <= 2:
                    world.set(x, y, z, "planks")


def build_farm(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z - 1, cx + size // 2, cy + size // 2, base_z - 1, "dirt")
    for x in range(cx - size // 2 + 1, cx + size // 2):
        for y in range(cy - size // 2 + 1, cy + size // 2):
            if (x + y) % 2 == 0:
                world.set(x, y, base_z, "water")
            else:
                world.set(x, y, base_z, "dirt")


def build_village_settlement(world, cx, cy, base_z, num_houses, rng):
    for i in range(num_houses):
        angle = (i / num_houses) * 2 * math.pi
        dist = 20 + i * 3
        hx = cx + int(dist * math.cos(angle))
        hy = cy + int(dist * math.sin(angle))
        house_size = rng.randint(5, 8)
        world.fill_box(hx - house_size // 2, hy - house_size // 2, base_z,
                      hx + house_size // 2, hy + house_size // 2, base_z + 4, "wood")
        for x in range(hx - house_size // 2 + 1, hx + house_size // 2):
            for y in range(hy - house_size // 2 + 1, hy + house_size // 2):
                world.set(x, y, base_z + 1, "planks")


def build_garden(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z, "grass")
    for i in range(size // 3):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(2, size // 2)
        fx = cx + int(dist * math.cos(angle))
        fy = cy + int(dist * math.sin(angle))
        build_advanced_tree(world, fx, fy, base_z + 1, rng.choice(["oak", "birch"]), 5, rng)


def build_underground_fortress(world, cx, cy, base_z, size, rng):
    depth = 10
    world.fill_box(cx - size // 2, cy - size // 2, base_z - depth,
                   cx + size // 2, cy + size // 2, base_z - 1, "obsidian")
    for x in range(cx - size // 2 + 2, cx + size // 2 - 1):
        for y in range(cy - size // 2 + 2, cy + size // 2 - 1):
            for z in range(base_z - depth + 2, base_z - 1):
                if rng.random() < 0.8:
                    world.voxels.pop((x, y, z), None)


def build_watchtower_network(world, base_z, num_towers, rng):
    center_x, center_y = 0, 0
    for i in range(num_towers):
        angle = (i / num_towers) * 2 * math.pi
        dist = 50
        tx = center_x + int(dist * math.cos(angle))
        ty = center_y + int(dist * math.sin(angle))
        build_watchtower(world, tx, ty, base_z, 15)
        if i < num_towers - 1:
            next_angle = ((i + 1) / num_towers) * 2 * math.pi
            next_tx = center_x + int(dist * math.cos(next_angle))
            next_ty = center_y + int(dist * math.sin(next_angle))
            build_bridge(world, tx, ty, next_tx, next_ty, base_z + 10, 3)


def build_terrain_features(world, width, depth, base_thickness, noise_gen, rng):
    build_grass_terrain(world, width, depth, base_thickness, noise_gen, base_thickness - 1)
    cave_x_range = range(-width // 2, width // 2)
    cave_y_range = range(-depth // 2, depth // 2)
    cave_z_range = range(1, base_thickness - 2)
    build_cave_system(world, cave_x_range, cave_y_range, cave_z_range, noise_gen, 0.3)
    ore_x_range = range(-width // 2, width // 2)
    ore_y_range = range(-depth // 2, depth // 2)
    ore_z_range = range(0, base_thickness - 3)
    build_ore_distribution(world, ore_x_range, ore_y_range, ore_z_range, "coal", rng, 0.02, 3)
    build_ore_distribution(world, ore_x_range, ore_y_range, ore_z_range, "iron", rng, 0.01, 2)
    build_ore_distribution(world, ore_x_range, ore_y_range, ore_z_range, "gold", rng, 0.005, 2)
    build_ore_distribution(world, ore_x_range, ore_y_range, ore_z_range, "diamond", rng, 0.002, 1)


def generate(width=120, depth=120, thickness=10):
    rng = random.Random(42)
    noise_gen = PerlinNoise(42)
    world = VoxelWorld()

    ground_z = thickness - 1

    build_terrain_features(world, width, depth, thickness, noise_gen, rng)

    build_mountain_range(world, -30, 0, ground_z, 40, 40, 20, noise_gen, rng)
    build_mountain_range(world, 30, 0, ground_z, 40, 40, 20, noise_gen, rng)

    build_forest_biome(world, -40, 20, ground_z + 1, 15, 12, ["oak", "birch"], rng)
    build_forest_biome(world, -40, -20, ground_z + 1, 15, 12, ["spruce", "oak"], rng)
    build_forest_biome(world, 40, 20, ground_z + 1, 15, 8, ["acacia"], rng)

    build_lake_system(world, 0, 0, ground_z, 12, 4, rng)
    build_lake_system(world, -50, 30, ground_z, 8, 3, rng)
    build_lake_system(world, 50, 30, ground_z, 8, 3, rng)

    build_river_system(world, -60, -50, 60, 50, 4, 2, ground_z)

    build_castle(world, 0, -40, ground_z, 20, rng)
    build_pyramid(world, -50, -30, ground_z, 15)
    build_temple(world, 50, -30, ground_z, 12, rng)

    build_watchtower_network(world, ground_z, 6, rng)

    build_village_settlement(world, -20, 40, ground_z, 6, rng)
    build_farm(world, 20, 40, ground_z, 12, rng)

    build_underground_fortress(world, 0, 0, ground_z - 2, 25, rng)

    faces = emit_to_blender(world)
    print("Minecraft Terraforming World: {} voxels -> {} faces".format(len(world.voxels), faces))
    return world


generate()
