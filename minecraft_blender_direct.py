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


def build_cliff_face(world, cx, cy, base_z, width, height, rng):
    for x in range(cx, cx + width):
        for z in range(base_z, base_z + height):
            if rng.random() < 0.85:
                world.set(x, cy, z, "stone")
            else:
                world.set(x, cy, z, "gravel")


def build_ravine(world, start_x, start_y, end_x, end_y, depth, width, rng):
    steps = max(abs(end_x - start_x), abs(end_y - start_y))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(start_x + (end_x - start_x) * t)
        y = int(start_y + (end_y - start_y) * t)
        for dx in range(-width // 2, width // 2 + 1):
            for dz in range(-depth, 0):
                for dy in range(-width // 2, width // 2 + 1):
                    pos_key = (x + dx, y + dy, dz)
                    if pos_key in world.voxels:
                        world.voxels.pop(pos_key, None)


def build_mansion(world, cx, cy, base_z, size, rng):
    levels = 3
    for level in range(levels):
        level_z = base_z + level * 5
        level_size = size - level * 2
        world.fill_box(cx - level_size // 2, cy - level_size // 2, level_z,
                       cx + level_size // 2, cy + level_size // 2, level_z + 4, "brick")
        for x in range(cx - level_size // 2 + 1, cx + level_size // 2):
            for y in range(cy - level_size // 2 + 1, cy + level_size // 2):
                world.set(x, y, level_z + 1, "planks")


def build_windmill(world, cx, cy, base_z, height):
    for z in range(base_z, base_z + height):
        world.set(cx, cy, z, "brick")
        world.set(cx + 1, cy, z, "brick")
        world.set(cx, cy + 1, z, "brick")
        world.set(cx + 1, cy + 1, z, "brick")
    for x in range(cx - 3, cx + 4):
        for y in range(cy - 3, cy + 4):
            if abs(x - cx) + abs(y - cy) <= 3:
                world.set(x, y, base_z + height, "wood")


def build_dock(world, cx, cy, base_z, length):
    for x in range(cx, cx + length):
        world.set(x, cy, base_z, "wood")
        world.set(x, cy + 1, base_z, "wood")
        world.set(x, cy, base_z + 1, "planks")


def build_mines(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z - 15,
                   cx + size // 2, cy + size // 2, base_z - 1, "stone")
    for x in range(cx - size // 2 + 2, cx + size // 2 - 1, 3):
        for z in range(base_z - 15, base_z - 2, 3):
            for y in range(cy - size // 2 + 2, cy + size // 2 - 1):
                if world.get(x, y, z) == "stone":
                    world.voxels.pop((x, y, z), None)


def build_lighthouse(world, cx, cy, base_z, height):
    for z in range(base_z, base_z + height):
        for x in range(cx - 2, cx + 3):
            for y in range(cy - 2, cy + 3):
                if abs(x - cx) <= 2 and abs(y - cy) <= 2:
                    dist = abs(x - cx) + abs(y - cy)
                    if dist >= 2:
                        world.set(x, y, z, "brick")
    for z in range(base_z + height - 3, base_z + height):
        for x in range(cx - 3, cx + 4):
            for y in range(cy - 3, cy + 4):
                world.set(x, y, z, "concrete_orange")


def build_harbor(world, cx, cy, base_z, size, rng):
    for x in range(cx - size, cx + size):
        for y in range(cy - size, cy + size):
            if abs(x - cx) < size and abs(y - cy) < size:
                world.set(x, y, base_z - 2, "stone")
    for i in range(4):
        dock_x = cx + (size - 2) if i % 2 == 0 else cx - (size - 2)
        dock_y = cy + (size - 2) if i // 2 == 0 else cy - (size - 2)
        build_dock(world, dock_x, dock_y, base_z - 1, size // 2)


def build_colosseum(world, cx, cy, base_z, outer_radius, inner_radius):
    for x in range(cx - outer_radius, cx + outer_radius + 1):
        for y in range(cy - outer_radius, cy + outer_radius + 1):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= outer_radius and dist >= inner_radius:
                for z in range(base_z, base_z + 8):
                    world.set(x, y, z, "brick")
    for x in range(cx - inner_radius + 1, cx + inner_radius):
        for y in range(cy - inner_radius + 1, cy + inner_radius):
            world.set(x, y, base_z, "sand")


def build_arena(world, cx, cy, base_z, size):
    for x in range(cx - size // 2, cx + size // 2 + 1):
        for y in range(cy - size // 2, cy + size // 2 + 1):
            if abs(x - cx) == size // 2 or abs(y - cy) == size // 2:
                for z in range(base_z, base_z + 5):
                    world.set(x, y, z, "brick")
            else:
                world.set(x, y, base_z, "sand")


def build_garden_maze(world, cx, cy, base_z, size, rng):
    path_width = 3
    wall_material = "oak"
    floor_material = "grass"
    for x in range(cx - size // 2, cx + size // 2):
        for y in range(cy - size // 2, cy + size // 2):
            if (x - cx) % path_width != 0 or (y - cy) % path_width != 0:
                world.set(x, y, base_z, wall_material)
            else:
                world.set(x, y, base_z, floor_material)


def build_monument(world, cx, cy, base_z, height, rng):
    for z in range(base_z, base_z + height):
        size = max(1, (height - z) // 2)
        for x in range(cx - size, cx + size + 1):
            for y in range(cy - size, cy + size + 1):
                world.set(x, y, z, "quartz_block")


def build_statue(world, cx, cy, base_z, height):
    for z in range(base_z, base_z + height):
        world.set(cx, cy, z, "quartz_block")
        world.set(cx + 1, cy, z, "quartz_block")
        world.set(cx, cy + 1, z, "quartz_block")
        world.set(cx + 1, cy + 1, z, "quartz_block")


def build_amphitheater(world, cx, cy, base_z, size):
    for layer in range(size):
        z = base_z + layer
        for x in range(cx - size + layer, cx + size - layer + 1):
            for y in range(cy - size + layer, cy + size - layer + 1):
                if abs(x - cx) == size - layer or abs(y - cy) == size - layer:
                    world.set(x, y, z, "brick")


def build_gate(world, cx, cy, base_z, width, height):
    for z in range(base_z, base_z + height):
        for x in range(cx - width // 2, cx + width // 2 + 1):
            if x == cx - width // 2 or x == cx + width // 2:
                world.set(x, cy, z, "brick")
            elif z == base_z + height - 1:
                world.set(x, cy, z, "brick")


def build_wall(world, x1, y1, x2, y2, base_z, height, rng):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        for z in range(base_z, base_z + height):
            world.set(x, y, z, "brick")
            world.set(x + 1, y, z, "brick")


def build_road(world, x1, y1, x2, y2, base_z, width):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        for dx in range(-width // 2, width // 2 + 1):
            world.set(x + dx, y, base_z, "cobblestone")


def build_marketplace(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size, cy - size, base_z, cx + size, cy + size, base_z, "cobblestone")
    for x in range(cx - size + 2, cx + size - 2, 4):
        for y in range(cy - size + 2, cy + size - 2, 4):
            for z in range(base_z + 1, base_z + 3):
                world.set(x, y, z, "wood")


def build_sky_island(world, cx, cy, height, size, rng):
    for x in range(cx - size // 2, cx + size // 2):
        for y in range(cy - size // 2, cy + size // 2):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist > size // 2:
                continue
            for z in range(height - 3, height + 1):
                if z == height:
                    world.set(x, y, z, "grass")
                else:
                    world.set(x, y, z, "dirt")


def build_floating_platforms(world, cx, cy, base_height, count, rng):
    for i in range(count):
        angle = (i / count) * 2 * math.pi
        dist = 30 + i * 5
        px = cx + int(dist * math.cos(angle))
        py = cy + int(dist * math.sin(angle))
        height = base_height + rng.randint(10, 30)
        for x in range(px - 3, px + 4):
            for y in range(py - 3, py + 4):
                world.set(x, y, height, "quartz_block")


def build_dungeon_entrance(world, cx, cy, base_z, rng):
    world.fill_box(cx - 2, cy - 2, base_z, cx + 2, cy + 2, base_z + 4, "brick")
    for x in range(cx - 1, cx + 2):
        for y in range(cy - 1, cy + 2):
            world.set(x, y, base_z + 1, "cobblestone")
    world.set(cx, cy, base_z + 1, "furnace")


def build_complete_settlement(world, cx, cy, base_z, size, rng):
    build_marketplace(world, cx, cy, base_z, size // 2, rng)
    build_village_settlement(world, cx - size, cy, base_z, size // 4, rng)
    build_farm(world, cx + size, cy, base_z, size // 3, rng)
    build_harbor(world, cx, cy + size * 2, base_z, size // 4, rng)
    for i in range(4):
        angle = (i / 4) * 2 * math.pi
        tx = cx + int(size * 1.5 * math.cos(angle))
        ty = cy + int(size * 1.5 * math.sin(angle))
        build_watchtower(world, tx, ty, base_z, 12)


def build_interconnected_structures(world, base_z, rng):
    build_castle(world, -60, 0, base_z, 20, rng)
    build_mansion(world, 0, 0, base_z, 15, rng)
    build_temple(world, 60, 0, base_z, 12, rng)
    build_wall(world, -60, 0, 0, 0, base_z, 8, rng)
    build_wall(world, 0, 0, 60, 0, base_z, 8, rng)
    build_road(world, -60, 0, 0, 0, base_z, 5)
    build_road(world, 0, 0, 60, 0, base_z, 5)


def build_sand_temple(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 3, "sand_stone")
    for layer in range(1, size // 4):
        layer_size = size - layer * 4
        for x in range(cx - layer_size // 2, cx + layer_size // 2 + 1):
            for y in range(cy - layer_size // 2, cy + layer_size // 2 + 1):
                world.set(x, y, base_z + 2 + layer, "sand_stone")


def build_jungle_temple(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 2, "stone")
    for x in range(cx - size // 2 + 2, cx + size // 2 - 1):
        for y in range(cy - size // 2 + 2, cy + size // 2 - 1):
            world.set(x, y, base_z + 1, "mossy_stone")
    for z in range(base_z + 1, base_z + size // 4):
        world.set(cx, cy, z, "log")


def build_nether_portal_frame(world, cx, cy, base_z):
    for x in range(cx - 1, cx + 2):
        for z in range(base_z, base_z + 4):
            world.set(x, cy - 1, z, "obsidian")
            world.set(x, cy + 2, z, "obsidian")
    for y in range(cy, cy + 2):
        world.set(cx - 1, y, base_z, "obsidian")
        world.set(cx - 1, y, base_z + 3, "obsidian")
        world.set(cx + 1, y, base_z, "obsidian")
        world.set(cx + 1, y, base_z + 3, "obsidian")


def build_wizard_tower(world, cx, cy, base_z, height, rng):
    for z in range(base_z, base_z + height):
        for x in range(cx - 2, cx + 3):
            for y in range(cy - 2, cy + 3):
                if abs(x - cx) == 2 and abs(y - cy) == 2:
                    world.set(x, y, z, "purple_concrete")
                elif abs(x - cx) <= 2 and abs(y - cy) <= 2:
                    world.set(x, y, z, "purple_concrete" if z % 3 == 0 else "quartz_block")
    for z in range(base_z + height - 2, base_z + height):
        for x in range(cx - 3, cx + 4):
            for y in range(cy - 3, cy + 4):
                if abs(x - cx) == 3 or abs(y - cy) == 3:
                    world.set(x, y, z, "concrete_purple")


def build_ice_palace(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + size // 3, "ice")
    for x in range(cx - size // 2 + 2, cx + size // 2 - 1):
        for y in range(cy - size // 2 + 2, cy + size // 2 - 1):
            for z in range(base_z + 1, base_z + size // 4):
                world.set(x, y, z, "snow")


def build_crystal_cave(world, cx, cy, base_z, size, rng):
    for x in range(cx - size, cx + size):
        for y in range(cy - size, cy + size):
            for z in range(base_z - 5, base_z + 1):
                if rng.random() < 0.3:
                    world.set(x, y, z, "quartz_block" if rng.random() < 0.5 else "diamond_ore")


def build_lava_chamber(world, cx, cy, base_z, size, rng):
    for x in range(cx - size, cx + size):
        for y in range(cy - size, cy + size):
            for z in range(base_z - size // 2, base_z):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2 + (z - base_z) ** 2)
                if dist < size * 0.7:
                    if world.get(x, y, z) == "stone":
                        world.voxels.pop((x, y, z), None)
    for x in range(cx - size // 2, cx + size // 2):
        for y in range(cy - size // 2, cy + size // 2):
            world.set(x, y, base_z - size // 2 - 1, "lava")


def build_advanced_caves(world, x_range, y_range, z_range, noise_gen, threshold, rng):
    for x in x_range:
        for y in y_range:
            for z in z_range:
                noise_val = noise_gen.fractal_brownian_motion(x * 0.08, y * 0.08, z * 0.15, 4, 0.75, 40)
                if noise_val > threshold:
                    if world.get(x, y, z) in ("stone", "dirt"):
                        if rng.random() < 0.9:
                            world.voxels.pop((x, y, z), None)
                        if rng.random() < 0.1:
                            world.set(x, y, z, "coal_ore")


def build_ore_veins(world, x_range, y_range, z_range, ore_data, rng):
    for ore_type, material, frequency, max_size in ore_data:
        for _ in range(int(len(x_range) * len(y_range) * len(z_range) * frequency / 10000)):
            x = rng.choice(x_range)
            y = rng.choice(y_range)
            z = rng.choice(z_range)
            vein_size = rng.randint(1, max_size)
            for _ in range(vein_size):
                vx = x + rng.randint(-2, 2)
                vy = y + rng.randint(-2, 2)
                vz = z + rng.randint(-1, 1)
                if world.get(vx, vy, vz) == "stone":
                    world.set(vx, vy, vz, material)


def build_biome_transitions(world, width, depth, base_z, noise_gen, rng):
    for x in range(-width // 2, width // 2):
        for y in range(-depth // 2, depth // 2):
            noise_val = noise_gen.fractal_brownian_motion(x * 0.15, y * 0.15, 0, 3, 0.7, 80)
            if noise_val > 0.4:
                build_advanced_tree(world, x, y, base_z + 1, "spruce", rng.randint(5, 8), rng)
            elif noise_val > 0.2:
                build_advanced_tree(world, x, y, base_z + 1, "oak", rng.randint(4, 7), rng)
            elif noise_val < -0.3:
                world.set(x, y, base_z, "sand")


def build_temple_variation_1(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z, "stone")
    for layer in range(1, size // 3):
        layer_size = size - layer * 2
        for x in range(cx - layer_size // 2, cx + layer_size // 2 + 1):
            for y in range(cy - layer_size // 2, cy + layer_size // 2 + 1):
                world.set(x, y, base_z + layer, "brick")
    for corner_idx in range(4):
        angle = corner_idx * math.pi / 2
        px = cx + int((size // 2) * math.cos(angle))
        py = cy + int((size // 2) * math.sin(angle))
        for z in range(base_z + 1, base_z + size // 2):
            world.set(px, py, z, "brick")


def build_temple_variation_2(world, cx, cy, base_z, size, rng):
    for z in range(base_z, base_z + size // 3):
        ring_size = size // 2 - z
        for x in range(cx - ring_size, cx + ring_size + 1):
            for y in range(cy - ring_size, cy + ring_size + 1):
                if abs(x - cx) == ring_size or abs(y - cy) == ring_size:
                    world.set(x, y, z, "sand_stone")


def build_fortress_section_1(world, cx, cy, base_z, size, rng):
    for x in range(cx - size // 2, cx + size // 2):
        for y in range(cy - size // 2, cy + size // 2):
            for z in range(base_z - 3, base_z + 5):
                world.set(x, y, z, "obsidian" if (x + y) % 2 == 0 else "brick")


def build_fortress_section_2(world, cx, cy, base_z, size, rng):
    for x in range(cx - size // 2, cx + size // 2):
        for z in range(base_z - 5, base_z + 2):
            world.set(x, cy, z, "obsidian")
    for y in range(cy - size // 2, cy + size // 2):
        for z in range(base_z - 5, base_z + 2):
            world.set(cx, y, z, "brick")


def build_fortified_wall_section(world, x1, y1, x2, y2, base_z, height, thickness, rng):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        for z in range(base_z, base_z + height):
            for dx in range(-thickness // 2, thickness // 2 + 1):
                world.set(x + dx, y, z, "brick")
        if step % 5 == 0:
            for z in range(base_z + height - 2, base_z + height):
                world.set(x, y - 1, z, "brick")
                world.set(x, y + 1, z, "brick")


def build_mineshaft_section(world, cx, cy, base_z, length, width, depth, rng):
    for x in range(cx, cx + length):
        for y in range(cy - width // 2, cy + width // 2):
            for z in range(base_z - depth, base_z):
                if rng.random() < 0.8:
                    world.voxels.pop((x, y, z), None)
    for x in range(cx, cx + length):
        world.set(x, cy - width // 2, base_z - 1, "wood")
        world.set(x, cy + width // 2, base_z - 1, "wood")


def build_quarry(world, cx, cy, base_z, size, depth, rng):
    for x in range(cx - size // 2, cx + size // 2):
        for y in range(cy - size // 2, cy + size // 2):
            for z in range(base_z - depth, base_z):
                if (x - cx) % 3 == 0 and (y - cy) % 3 == 0:
                    world.set(x, y, z, "stone")
                elif world.get(x, y, z) == "stone":
                    world.voxels.pop((x, y, z), None)


def build_observation_tower(world, cx, cy, base_z, height, rng):
    for z in range(base_z, base_z + height):
        world.set(cx, cy, z, "brick")
        world.set(cx + 1, cy, z, "brick")
        world.set(cx, cy + 1, z, "brick")
        world.set(cx + 1, cy + 1, z, "brick")
    for z in range(base_z + height - 4, base_z + height):
        for x in range(cx - 2, cx + 3):
            for y in range(cy - 2, cy + 3):
                if abs(x - cx) + abs(y - cy) > 1:
                    world.set(x, y, z, "planks")


def build_archery_range(world, cx, cy, base_z, size, rng):
    for x in range(cx - size, cx + size):
        for y in range(cy - 2, cy + 3):
            world.set(x, y, base_z, "clay")
    for i in range(5):
        target_x = cx - size + i * (2 * size // 5)
        world.set(target_x, cy, base_z + 2, "concrete_red")
        world.set(target_x + 1, cy, base_z + 2, "concrete_white")


def build_stable(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 3, "wood")
    for x in range(cx - size // 2 + 1, cx + size // 2):
        for y in range(cy - size // 2 + 1, cy + size // 2):
            world.set(x, y, base_z + 1, "planks")
    for i in range(4):
        stall_x = cx - size // 2 + i * (size // 4) + 1
        world.set(stall_x, cy, base_z + 2, "planks")


def build_smithy(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 3, "brick")
    world.set(cx, cy, base_z + 1, "furnace")
    world.set(cx + 1, cy, base_z + 1, "furnace")
    world.set(cx - 1, cy, base_z + 1, "crafting_table")


def build_library(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 4, "brick")
    for x in range(cx - size // 2 + 1, cx + size // 2):
        for y in range(cy - size // 2 + 1, cy + size // 2):
            if (x + y) % 2 == 0:
                world.set(x, y, base_z + 1, "bookshelf")
            world.set(x, y, base_z + 2, "planks")


def build_granary(world, cx, cy, base_z, size, rng):
    for x in range(cx - size // 2, cx + size // 2):
        for y in range(cy - size // 2, cy + size // 2):
            for z in range(base_z, base_z + size // 2):
                world.set(x, y, z, "wood")
    for x in range(cx - size // 2 + 1, cx + size // 2 - 1):
        for y in range(cy - size // 2 + 1, cy + size // 2 - 1):
            for z in range(base_z + 1, base_z + size // 2 - 1):
                world.set(x, y, z, "hay")


def build_barracks(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 3, "brick")
    rows = 4
    row_spacing = size // rows
    for row in range(rows):
        row_y = cy - size // 2 + row * row_spacing
        for col in range(3):
            col_x = cx - size // 2 + 2 + col * 4
            world.set(col_x, row_y, base_z + 1, "planks")


def build_watchtower_variant(world, cx, cy, base_z, height, size):
    for z in range(base_z, base_z + height):
        for x in range(cx - size // 2, cx + size // 2):
            for y in range(cy - size // 2, cy + size // 2):
                if abs(x - cx) == size // 2 - 1 or abs(y - cy) == size // 2 - 1:
                    world.set(x, y, z, "cobblestone")
    for z in range(base_z + height - 2, base_z + height):
        for x in range(cx - size // 2, cx + size // 2):
            for y in range(cy - size // 2, cy + size // 2):
                world.set(x, y, z, "planks")


def build_network_of_roads(world, base_z, major_points, rng):
    for i in range(len(major_points)):
        for j in range(i + 1, len(major_points)):
            x1, y1 = major_points[i]
            x2, y2 = major_points[j]
            if rng.random() < 0.6:
                build_road(world, x1, y1, x2, y2, base_z, 7)


def build_advanced_village(world, cx, cy, base_z, num_buildings, rng):
    buildings = [
        ("smithy", build_smithy),
        ("library", build_library),
        ("stable", build_stable),
        ("barracks", build_barracks),
    ]
    for i in range(num_buildings):
        angle = (i / num_buildings) * 2 * math.pi
        dist = 40 + i * 5
        bx = cx + int(dist * math.cos(angle))
        by = cy + int(dist * math.sin(angle))
        building_type, building_func = rng.choice(buildings)
        building_func(world, bx, by, base_z, rng.randint(8, 12), rng)


def build_multiple_biome_forest(world, cx, cy, base_z, radius, rng):
    sectors = 4
    tree_types_per_sector = [
        ["oak"],
        ["birch", "birch_leaves"],
        ["spruce", "spruce_leaves"],
        ["acacia", "acacia_leaves"],
    ]
    for sector in range(sectors):
        angle_start = sector * (2 * math.pi / sectors)
        angle_end = (sector + 1) * (2 * math.pi / sectors)
        for _ in range(15):
            angle = rng.uniform(angle_start, angle_end)
            dist = rng.uniform(0, radius)
            tx = cx + int(dist * math.cos(angle))
            ty = cy + int(dist * math.sin(angle))
            height = rng.randint(4, 8)
            tree_type = rng.choice(tree_types_per_sector[sector])
            build_advanced_tree(world, tx, ty, base_z + 1, tree_type, height, rng)


def build_layered_mountain(world, cx, cy, base_z, height, width, noise_gen, rng):
    for z_layer in range(height):
        current_radius = width * (1 - z_layer / height)
        current_z = base_z + z_layer
        for x in range(int(cx - current_radius), int(cx + current_radius)):
            for y in range(int(cy - current_radius), int(cy + current_radius)):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                if dist <= current_radius:
                    noise_val = noise_gen.fractal_brownian_motion(x * 0.1, y * 0.1, z_layer * 0.1, 3, 0.6, 50)
                    if rng.random() + noise_val * 0.5 > 0.3:
                        world.set(x, y, current_z, "stone")


def build_coastal_features(world, cx, cy, base_z, rng):
    build_dock(world, cx, cy, base_z, 20)
    build_lighthouse(world, cx + 30, cy, base_z, 15)
    build_harbor(world, cx + 10, cy - 20, base_z, 15, rng)


def build_trade_hub(world, cx, cy, base_z, size, rng):
    build_marketplace(world, cx, cy, base_z, size // 2, rng)
    for direction in range(4):
        angle = direction * math.pi / 2
        ox = cx + int(size * 1.5 * math.cos(angle))
        oy = cy + int(size * 1.5 * math.sin(angle))
        build_warehouse(world, ox, oy, base_z, 15, rng)


def build_warehouse(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 4, "wood")
    for x in range(cx - size // 2 + 2, cx + size // 2 - 1, 3):
        for z in range(base_z + 1, base_z + 4):
            world.set(x, cy, z, "planks")


def build_tower_cluster(world, cx, cy, base_z, count, base_radius, rng):
    for i in range(count):
        angle = (i / count) * 2 * math.pi
        dist = base_radius + rng.randint(5, 15)
        tx = cx + int(dist * math.cos(angle))
        ty = cy + int(dist * math.sin(angle))
        height = rng.randint(10, 20)
        radius = rng.randint(2, 4)
        build_tower(world, tx, ty, base_z, height, radius)


def build_structure_grid(world, cx, cy, base_z, grid_width, grid_height, spacing, structure_type, rng):
    for gx in range(grid_width):
        for gy in range(grid_height):
            struct_x = cx + gx * spacing
            struct_y = cy + gy * spacing
            if structure_type == "tower":
                build_watchtower(world, struct_x, struct_y, base_z, 10)
            elif structure_type == "house":
                build_mansion(world, struct_x, struct_y, base_z, 10, rng)


def build_multi_level_fortress(world, cx, cy, base_z, levels, size, rng):
    for level in range(levels):
        level_z = base_z - level * 8
        level_size = size - level * 4
        world.fill_box(cx - level_size // 2, cy - level_size // 2, level_z,
                       cx + level_size // 2, cy + level_size // 2, level_z + 3, "brick")


def build_canyon(world, start_x, start_y, end_x, end_y, width, depth, noise_gen, rng):
    steps = max(abs(end_x - start_x), abs(end_y - start_y))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(start_x + (end_x - start_x) * t)
        y = int(start_y + (end_y - start_y) * t)
        for dx in range(-width // 2, width // 2 + 1):
            for dz in range(-depth, 0):
                for dy in range(-1, 2):
                    pos = (x + dx, y + dy, dz)
                    if pos in world.voxels:
                        world.voxels.pop(pos, None)


def build_plateau(world, cx, cy, base_z, size, height, edge_type):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + height, "stone")
    if edge_type == "cliff":
        for x in range(cx - size // 2, cx + size // 2):
            for z in range(base_z, base_z + height):
                world.set(x, cy - size // 2, z, "stone")
                world.set(x, cy + size // 2, z, "stone")
    for x in range(cx - size // 2, cx + size // 2):
        for y in range(cy - size // 2, cy + size // 2):
            world.set(x, y, base_z + height, "grass")


def build_volcanic_crater(world, cx, cy, base_z, radius, depth, rng):
    for x in range(cx - radius, cx + radius + 1):
        for y in range(cy - radius, cy + radius + 1):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= radius:
                for z in range(base_z - depth, base_z):
                    if dist <= radius * 0.3:
                        world.set(x, y, z, "lava")
                    else:
                        world.set(x, y, z, "stone" if rng.random() < 0.7 else "gravel")


def build_geode(world, cx, cy, cz, radius, crystal_material, rng):
    for x in range(cx - radius, cx + radius + 1):
        for y in range(cy - radius, cy + radius + 1):
            for z in range(cz - radius, cz + radius + 1):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2)
                if dist <= radius:
                    if dist > radius * 0.7 and world.get(x, y, z) == "stone":
                        world.set(x, y, z, crystal_material)
                    elif dist <= radius * 0.3:
                        world.voxels.pop((x, y, z), None)


def build_lost_temple_system(world, cx, cy, base_z, complexity, rng):
    main_temple_x = cx - 50
    main_temple_y = cy
    build_temple(world, main_temple_x, main_temple_y, base_z, 20, rng)
    for i in range(complexity):
        angle = (i / complexity) * 2 * math.pi
        dist = 80 + i * 10
        satellite_x = cx + int(dist * math.cos(angle))
        satellite_y = cy + int(dist * math.sin(angle))
        build_pyramid(world, satellite_x, satellite_y, base_z, 12)
        build_road(world, main_temple_x, main_temple_y, satellite_x, satellite_y, base_z, 4)


def build_biodome(world, cx, cy, base_z, radius, tree_count, rng):
    for x in range(cx - radius, cx + radius + 1):
        for y in range(cy - radius, cy + radius + 1):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= radius:
                world.set(x, y, base_z, "grass")
    for _ in range(tree_count):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(5, radius - 5)
        tx = cx + int(dist * math.cos(angle))
        ty = cy + int(dist * math.sin(angle))
        build_advanced_tree(world, tx, ty, base_z + 1, rng.choice(["oak", "birch", "spruce"]), rng.randint(4, 7), rng)


def build_enchanted_forest(world, cx, cy, base_z, radius, tree_count, rng):
    materials = ["oak", "birch", "spruce", "dark_oak"]
    for _ in range(tree_count):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(0, radius)
        tx = cx + int(dist * math.cos(angle))
        ty = cy + int(dist * math.sin(angle))
        tree_type = rng.choice(materials)
        height = rng.randint(6, 12)
        build_advanced_tree(world, tx, ty, base_z + 1, tree_type, height, rng)


def build_mega_cavern(world, cx, cy, base_z, width, depth, height, noise_gen):
    for x in range(cx - width // 2, cx + width // 2):
        for y in range(cy - depth // 2, cy + depth // 2):
            for z in range(base_z - height, base_z):
                noise_val = noise_gen.fractal_brownian_motion(x * 0.05, y * 0.05, z * 0.1, 5, 0.7, 50)
                if noise_val > 0.4:
                    world.voxels.pop((x, y, z), None)


def build_research_facility(world, cx, cy, base_z, size, rng):
    for wing in range(3):
        wing_offset = (wing - 1) * (size // 2)
        world.fill_box(cx + wing_offset - size // 4, cy - size // 4, base_z,
                       cx + wing_offset + size // 4, cy + size // 4, base_z + 4, "quartz_block")
        for x in range(cx + wing_offset - size // 4 + 1, cx + wing_offset + size // 4):
            for y in range(cy - size // 4 + 1, cy + size // 4):
                world.set(x, y, base_z + 1, "glass")


def build_communications_tower(world, cx, cy, base_z, height, rng):
    for z in range(base_z, base_z + height):
        world.set(cx, cy, z, "quartz_block")
        world.set(cx + 1, cy, z, "quartz_block")
        world.set(cx, cy + 1, z, "quartz_block")
        world.set(cx + 1, cy + 1, z, "quartz_block")
    for z in range(base_z + height - 5, base_z + height):
        for x in range(cx - 3, cx + 4):
            world.set(x, cy, z, "concrete_orange")


def build_defense_line(world, x1, y1, x2, y2, base_z, height, spacing, rng):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(0, steps + 1, spacing):
        t = step / steps if steps > 0 else 0
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        build_watchtower(world, x, y, base_z, height)
        if step < steps:
            next_t = (step + spacing) / steps if steps > 0 else 0
            next_x = int(x1 + (x2 - x1) * next_t)
            next_y = int(y1 + (y2 - y1) * next_t)
            build_wall(world, x, y, next_x, next_y, base_z, height - 3, rng)


def build_farming_district(world, cx, cy, base_z, grid_size, rng):
    for gx in range(grid_size):
        for gy in range(grid_size):
            farm_x = cx - grid_size * 8 + gx * 16
            farm_y = cy - grid_size * 8 + gy * 16
            build_farm(world, farm_x, farm_y, base_z, 10, rng)


def build_industrial_zone(world, cx, cy, base_z, size, rng):
    build_smithy(world, cx - size, cy, base_z, 12, rng)
    build_furnace(world, cx, cy - size, base_z, 12, rng)
    build_mineshaft_section(world, cx + size, cy, base_z, 20, 8, 10, rng)


def build_furnace(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 3, "brick")
    for x in range(cx - size // 2 + 1, cx + size // 2):
        for y in range(cy - size // 2 + 1, cy + size // 2):
            world.set(x, y, base_z + 1, "furnace")


def build_central_plaza(world, cx, cy, base_z, size, rng):
    for x in range(cx - size, cx + size):
        for y in range(cy - size, cy + size):
            world.set(x, y, base_z, "cobblestone" if (x + y) % 2 == 0 else "concrete_white")
    for corner in range(4):
        angle = corner * math.pi / 2
        px = cx + int(size * 1.5 * math.cos(angle))
        py = cy + int(size * 1.5 * math.sin(angle))
        build_fountain(world, px, py, base_z)


def build_fountain(world, cx, cy, base_z):
    for x in range(cx - 2, cx + 3):
        for y in range(cy - 2, cy + 3):
            world.set(x, y, base_z, "stone")
    world.set(cx, cy, base_z + 1, "water")


def build_garden_plaza(world, cx, cy, base_z, size, rng):
    for x in range(cx - size, cx + size):
        for y in range(cy - size, cy + size):
            world.set(x, y, base_z, "grass")
    for i in range(16):
        angle = (i / 16) * 2 * math.pi
        dist = rng.randint(5, size - 5)
        tx = cx + int(dist * math.cos(angle))
        ty = cy + int(dist * math.sin(angle))
        build_advanced_tree(world, tx, ty, base_z + 1, "oak", 4, rng)


def build_meditation_garden(world, cx, cy, base_z, size, rng):
    build_central_plaza(world, cx, cy, base_z, size // 2, rng)
    build_garden_maze(world, cx, cy, base_z, size, rng)


def generate(width=200, depth=200, thickness=14):
    rng = random.Random(42)
    noise_gen = PerlinNoise(42)
    world = VoxelWorld()

    ground_z = thickness - 1

    build_terrain_features(world, width, depth, thickness, noise_gen, rng)

    build_mountain_range(world, -50, -40, ground_z, 60, 60, 30, noise_gen, rng)
    build_mountain_range(world, 50, -40, ground_z, 60, 60, 30, noise_gen, rng)
    build_mountain_range(world, 0, 60, ground_z, 50, 50, 25, noise_gen, rng)

    build_layered_mountain(world, -60, 0, ground_z, 25, 35, noise_gen, rng)
    build_plateau(world, 60, 0, ground_z, 40, 15, "cliff")

    build_forest_biome(world, -60, 10, ground_z + 1, 25, 18, ["oak", "birch"], rng)
    build_forest_biome(world, -60, -40, ground_z + 1, 22, 15, ["spruce", "oak"], rng)
    build_forest_biome(world, 60, 10, ground_z + 1, 25, 15, ["acacia", "dark_oak"], rng)
    build_enchanted_forest(world, 30, 30, ground_z + 1, 20, 20, rng)
    build_multiple_biome_forest(world, -30, -30, ground_z + 1, 25, rng)

    build_lake_system(world, 0, 0, ground_z, 16, 6, rng)
    build_lake_system(world, -70, 40, ground_z, 12, 5, rng)
    build_lake_system(world, 70, 40, ground_z, 12, 5, rng)
    build_lake_system(world, 0, -60, ground_z, 14, 5, rng)

    build_river_system(world, -90, -75, 90, 75, 6, 4, ground_z)

    build_volcano(world, 0, 0, ground_z, rng)

    build_interconnected_structures(world, ground_z, rng)

    build_colosseum(world, 0, 45, ground_z, 20, 10)
    build_arena(world, -45, 45, ground_z, 18)
    build_amphitheater(world, 45, 45, ground_z, 12)

    build_advanced_village(world, -80, 75, ground_z, 8, rng)
    build_lighthouse(world, 80, 75, ground_z, 22)

    build_lost_temple_system(world, -50, -50, ground_z, 4, rng)
    build_central_plaza(world, 40, 40, ground_z, 15, rng)

    build_sky_island(world, -30, 30, ground_z + 40, 30, rng)
    build_sky_island(world, 30, 30, ground_z + 45, 28, rng)
    build_floating_platforms(world, 0, 0, ground_z + 30, 10, rng)

    build_watchtower_network(world, ground_z, 10, rng)
    build_tower_cluster(world, 20, -20, ground_z, 5, 40, rng)

    build_multi_level_fortress(world, 0, 0, ground_z - 2, 3, 35, rng)
    build_dungeon_entrance(world, 30, 30, ground_z, rng)
    build_research_facility(world, -20, -20, ground_z, 20, rng)

    build_volcanic_crater(world, 0, 0, ground_z, 20, 8, rng)
    build_canyon(world, -80, -80, 80, 80, 15, 10, noise_gen, rng)

    build_biodome(world, 50, -50, ground_z, 25, 16, rng)
    build_meditation_garden(world, -50, 50, ground_z, 20, rng)

    build_farming_district(world, 0, -80, ground_z, 3, rng)
    build_industrial_zone(world, -70, -70, ground_z, 30, rng)

    ore_data = [
        ("coal", "coal_ore", 0.04, 6),
        ("iron", "iron_ore", 0.02, 4),
        ("gold", "gold_ore", 0.01, 3),
        ("diamond", "diamond_ore", 0.004, 2),
    ]
    ore_x_range = range(-width // 2, width // 2)
    ore_y_range = range(-depth // 2, depth // 2)
    ore_z_range = range(0, thickness - 3)
    build_ore_veins(world, ore_x_range, ore_y_range, ore_z_range, ore_data, rng)

    cave_x_range = range(-width // 2, width // 2)
    cave_y_range = range(-depth // 2, depth // 2)
    cave_z_range = range(2, thickness - 2)
    build_advanced_caves(world, cave_x_range, cave_y_range, cave_z_range, noise_gen, 0.38, rng)

    build_mega_cavern(world, -30, 60, ground_z - 3, 50, 50, 12, noise_gen)

    faces = emit_to_blender(world)
    print("Minecraft Terraforming World: {} voxels -> {} faces".format(len(world.voxels), faces))
    return world


def build_volcano(world, cx, cy, base_z, rng):
    for layer in range(20):
        radius = 30 - layer * 1.5
        z = base_z + layer
        for x in range(int(cx - radius), int(cx + radius) + 1):
            for y in range(int(cy - radius), int(cy + radius) + 1):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                if dist <= radius:
                    if layer < 10:
                        world.set(x, y, z, "stone" if rng.random() < 0.8 else "gravel")
                    elif dist <= 5:
                        world.set(x, y, z, "lava")
                    else:
                        world.set(x, y, z, "stone")


def build_castle_keep(world, cx, cy, base_z, height, rng):
    width = 20
    for z in range(base_z, base_z + height):
        for x in range(cx - width // 2, cx + width // 2):
            for y in range(cy - width // 2, cy + width // 2):
                if abs(x - cx) == width // 2 - 1 or abs(y - cy) == width // 2 - 1:
                    world.set(x, y, z, "brick")
                elif z == base_z:
                    world.set(x, y, z, "stone")


def build_defensive_palisade(world, x1, y1, x2, y2, base_z, height, rng):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        for z in range(base_z, base_z + height):
            world.set(x, y, z, "log")
        if z % 2 == 0:
            world.set(x + 1, y, z, "log")


def build_resource_depot(world, cx, cy, base_z, size, rng):
    materials = ["coal_ore", "iron_ore", "gold_ore", "diamond_ore"]
    for i, material in enumerate(materials):
        offset_x = (i % 2) * (size // 2)
        offset_y = (i // 2) * (size // 2)
        for x in range(cx + offset_x, cx + offset_x + size // 2):
            for y in range(cy + offset_y, cy + offset_y + size // 2):
                for z in range(base_z, base_z + 2):
                    if rng.random() < 0.6:
                        world.set(x, y, z, material)


def build_beacon_tower(world, cx, cy, base_z, height):
    for z in range(base_z, base_z + height - 3):
        world.set(cx, cy, z, "obsidian")
        world.set(cx + 1, cy, z, "obsidian")
        world.set(cx, cy + 1, z, "obsidian")
        world.set(cx + 1, cy + 1, z, "obsidian")
    for z in range(base_z + height - 3, base_z + height):
        for x in range(cx - 2, cx + 3):
            for y in range(cy - 2, cy + 3):
                world.set(x, y, z, "quartz_block")


def build_rope_bridge(world, x1, y1, x2, y2, z, width, rng):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        for dx in range(-width // 2, width // 2 + 1):
            world.set(x + dx, y, z, "log")
        if step % 3 == 0:
            for dx in range(-width // 2, width // 2 + 1):
                world.set(x + dx, y, z + 1, "log")


def build_spiral_tower(world, cx, cy, base_z, height, radius):
    for z in range(base_z, base_z + height):
        angle = (z - base_z) * (4 * math.pi / height)
        x = cx + int(radius * math.cos(angle))
        y = cy + int(radius * math.sin(angle))
        world.set(x, y, z, "brick")
        world.set(x + 1, y, z, "brick")


def build_underground_rail_system(world, start_x, start_y, end_x, end_y, base_z, depth, rng):
    steps = max(abs(end_x - start_x), abs(end_y - start_y))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(start_x + (end_x - start_x) * t)
        y = int(start_y + (end_y - start_y) * t)
        for z in range(base_z - depth, base_z):
            if z == base_z - 1:
                world.set(x, y, z, "cobblestone")
            elif rng.random() < 0.9:
                world.voxels.pop((x, y, z), None)


def build_underground_city_section(world, cx, cy, base_z, size, level_count, rng):
    for level in range(level_count):
        level_z = base_z - level * 10
        level_size = size - level * 2
        world.fill_box(cx - level_size // 2, cy - level_size // 2, level_z - 3,
                       cx + level_size // 2, cy + level_size // 2, level_z, "obsidian")
        for x in range(cx - level_size // 2 + 1, cx + level_size // 2):
            for y in range(cy - level_size // 2 + 1, cy + level_size // 2):
                world.set(x, y, level_z - 1, "planks")


def build_nether_fortress_section(world, cx, cy, base_z, size, rng):
    for x in range(cx - size // 2, cx + size // 2):
        for y in range(cy - size // 2, cy + size // 2):
            for z in range(base_z - 5, base_z + 5):
                if (x % 3 == 0 or y % 3 == 0) and z % 2 == 0:
                    world.set(x, y, z, "nether_brick" if "nether_brick" in PALETTE else "brick")


def build_end_platform(world, cx, cy, base_z, size, rng):
    for x in range(cx - size, cx + size):
        for y in range(cy - size, cy + size):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= size:
                world.set(x, y, base_z, "obsidian" if dist <= size * 0.3 else "purpur_block")


def build_draconic_temple(world, cx, cy, base_z, size, rng):
    for layer in range(size // 4):
        layer_z = base_z + layer * 3
        layer_size = size - layer * 4
        for x in range(cx - layer_size // 2, cx + layer_size // 2):
            for y in range(cy - layer_size // 2, cy + layer_size // 2):
                if abs(x - cx) == layer_size // 2 - 1 or abs(y - cy) == layer_size // 2 - 1:
                    world.set(x, y, layer_z, "purpur_block")


def build_crystalline_structures(world, cx, cy, base_z, count, rng):
    for i in range(count):
        angle = (i / count) * 2 * math.pi if count > 0 else 0
        dist = rng.randint(20, 60)
        struct_x = cx + int(dist * math.cos(angle))
        struct_y = cy + int(dist * math.sin(angle))
        height = rng.randint(10, 25)
        for z in range(base_z, base_z + height):
            world.set(struct_x, struct_y, z, "quartz_block")
            if rng.random() < 0.3:
                world.set(struct_x + 1, struct_y, z, "quartz_block")
                world.set(struct_x, struct_y + 1, z, "quartz_block")


def build_transport_hub(world, cx, cy, base_z, rng):
    world.fill_box(cx - 10, cy - 10, base_z, cx + 10, cy + 10, base_z + 2, "cobblestone")
    for direction in range(4):
        angle = direction * math.pi / 2
        rail_x = cx + int(20 * math.cos(angle))
        rail_y = cy + int(20 * math.sin(angle))
        build_road(world, cx, cy, rail_x, rail_y, base_z, 5)


def build_aqueduct(world, x1, y1, x2, y2, base_z, height, rng):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        for z in range(base_z - height, base_z + 1):
            world.set(x - 1, y, z, "stone")
            world.set(x + 1, y, z, "stone")
            if z == base_z:
                world.set(x, y, z, "water")


def build_town_hall(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + size // 3, "brick")
    for x in range(cx - size // 2 + 1, cx + size // 2):
        for y in range(cy - size // 2 + 1, cy + size // 2):
            world.set(x, y, base_z + 1, "planks")
    for z in range(base_z + size // 3 - 2, base_z + size // 3):
        for x in range(cx - size // 2, cx + size // 2):
            world.set(x, cy, z, "planks")


def build_market_stall(world, cx, cy, base_z):
    for x in range(cx - 2, cx + 3):
        for y in range(cy - 2, cy + 3):
            world.set(x, y, base_z, "stone")
    for z in range(base_z + 1, base_z + 3):
        world.set(cx - 2, cy - 2, z, "wood")
        world.set(cx + 2, cy - 2, z, "wood")
        world.set(cx - 2, cy + 2, z, "wood")
        world.set(cx + 2, cy + 2, z, "wood")


def build_guild_hall(world, cx, cy, base_z, size, specialty, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 4, "brick")
    specialty_material = "furnace" if specialty == "blacksmith" else "crafting_table" if specialty == "crafter" else "bookshelf"
    for x in range(cx - size // 4, cx + size // 4):
        for y in range(cy - size // 4, cy + size // 4):
            if rng.random() < 0.4:
                world.set(x, y, base_z + 1, specialty_material)


def build_defensive_outpost(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z - 2, cx + size // 2, cy + size // 2, base_z + 2, "stone")
    for direction in range(4):
        angle = direction * math.pi / 2
        tower_x = cx + int(size * math.cos(angle))
        tower_y = cy + int(size * math.sin(angle))
        build_watchtower(world, tower_x, tower_y, base_z, 10)


def build_medical_facility(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 3, "white_concrete" if "white_concrete" in PALETTE else "brick")
    for x in range(cx - size // 4, cx + size // 4):
        for y in range(cy - size // 4, cy + size // 4):
            world.set(x, y, base_z + 1, "white_concrete" if "white_concrete" in PALETTE else "quartz_block")


def build_monument_complex(world, cx, cy, base_z, complexity, rng):
    for level in range(1, complexity + 1):
        monument_z = base_z + (level - 1) * 8
        level_size = 40 - level * 5
        build_monument(world, cx, cy, monument_z, level_size, rng)


def build_botanical_garden(world, cx, cy, base_z, size, rng):
    for x in range(cx - size, cx + size):
        for y in range(cy - size, cy + size):
            world.set(x, y, base_z, "grass")
    tree_count = size // 3
    for _ in range(tree_count):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(5, size - 5)
        tx = cx + int(dist * math.cos(angle))
        ty = cy + int(dist * math.sin(angle))
        build_advanced_tree(world, tx, ty, base_z + 1, rng.choice(["oak", "birch", "spruce", "acacia"]), rng.randint(5, 8), rng)


def build_amphitheater_variant(world, cx, cy, base_z, size, stone_type, rng):
    for layer in range(size // 2):
        layer_z = base_z + layer
        layer_size = size - layer * 2
        for x in range(cx - layer_size // 2, cx + layer_size // 2 + 1):
            for y in range(cy - layer_size // 2, cy + layer_size // 2 + 1):
                if abs(x - cx) == layer_size // 2 or abs(y - cy) == layer_size // 2:
                    world.set(x, y, layer_z, stone_type)


def build_arena_complex(world, cx, cy, base_z, size, rng):
    build_arena(world, cx, cy, base_z, size)
    for direction in range(4):
        angle = direction * math.pi / 2
        spectator_x = cx + int((size + 15) * math.cos(angle))
        spectator_y = cy + int((size + 15) * math.sin(angle))
        world.fill_box(spectator_x - 5, spectator_y - 5, base_z, spectator_x + 5, spectator_y + 5, base_z + 2, "brick")


def build_custom_terrain_feature(world, cx, cy, base_z, feature_type, size, noise_gen, rng):
    if feature_type == "valley":
        for x in range(cx - size, cx + size):
            for y in range(cy - size, cy + size):
                depth = int(5 * (1 - abs(x - cx) / size))
                for z in range(base_z - depth, base_z):
                    world.set(x, y, z, "stone")
    elif feature_type == "hill":
        for x in range(cx - size, cx + size):
            for y in range(cy - size, cy + size):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                if dist <= size:
                    height = int(10 * (1 - dist / size))
                    for z in range(base_z, base_z + height):
                        world.set(x, y, z, "stone")


def build_multiple_lake_system(world, cx, cy, base_z, lake_count, base_radius, rng):
    for i in range(lake_count):
        angle = (i / lake_count) * 2 * math.pi if lake_count > 0 else 0
        dist = base_radius + rng.randint(10, 40)
        lake_x = cx + int(dist * math.cos(angle))
        lake_y = cy + int(dist * math.sin(angle))
        radius = rng.randint(8, 15)
        depth = rng.randint(2, 5)
        build_lake_system(world, lake_x, lake_y, base_z, radius, depth, rng)


def build_comprehensive_city_district(world, cx, cy, base_z, district_type, size, rng):
    if district_type == "residential":
        for i in range(6):
            angle = (i / 6) * 2 * math.pi
            house_x = cx + int(25 * math.cos(angle))
            house_y = cy + int(25 * math.sin(angle))
            build_mansion(world, house_x, house_y, base_z, 10, rng)
    elif district_type == "commercial":
        build_marketplace(world, cx, cy, base_z, size // 2, rng)
        for i in range(4):
            angle = (i / 4) * 2 * math.pi
            shop_x = cx + int(35 * math.cos(angle))
            shop_y = cy + int(35 * math.sin(angle))
            build_shop(world, shop_x, shop_y, base_z, rng)
    elif district_type == "industrial":
        build_smithy(world, cx - 20, cy, base_z, 12, rng)
        build_furnace(world, cx + 20, cy, base_z, 12, rng)
        build_mineshaft_section(world, cx, cy - 30, base_z, 25, 10, 8, rng)
    elif district_type == "military":
        build_castle(world, cx, cy, base_z, size // 2, rng)
        build_watchtower_network(world, base_z, 6, rng)


def build_shop(world, cx, cy, base_z, rng):
    world.fill_box(cx - 4, cy - 4, base_z, cx + 4, cy + 4, base_z + 3, "brick")
    for x in range(cx - 3, cx + 4):
        for y in range(cy - 3, cy + 4):
            world.set(x, y, base_z + 1, "glass")


def build_network_bridges(world, structures, base_z, rng):
    for i in range(len(structures)):
        for j in range(i + 1, len(structures)):
            x1, y1 = structures[i]
            x2, y2 = structures[j]
            build_bridge(world, x1, y1, x2, y2, base_z + 1, 4)


def build_terraced_gardens(world, cx, cy, base_z, levels, size_per_level, rng):
    for level in range(levels):
        level_z = base_z + level * 3
        level_size = size_per_level - level * 2
        for x in range(cx - level_size // 2, cx + level_size // 2):
            for y in range(cy - level_size // 2, cy + level_size // 2):
                world.set(x, y, level_z, "grass")


def build_maze_of_walls(world, cx, cy, base_z, size, cell_size, rng):
    for x in range(cx - size // 2, cx + size // 2, cell_size):
        for y in range(cy - size // 2, cy + size // 2, cell_size):
            if rng.random() < 0.5:
                for z in range(base_z, base_z + 3):
                    for dx in range(cell_size):
                        world.set(x + dx, y, z, "brick")


def build_decorative_columns(world, cx, cy, base_z, count, height, spacing, rng):
    for i in range(count):
        col_x = cx - (count // 2) * spacing + i * spacing
        for z in range(base_z, base_z + height):
            for x in range(col_x - 1, col_x + 2):
                for y in range(cy - 1, cy + 2):
                    world.set(x, y, z, "quartz_block")


def build_artistic_garden(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size, cy - size, base_z, cx + size, cy + size, base_z, "grass")
    for _ in range(size // 2):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(5, size - 5)
        tx = cx + int(dist * math.cos(angle))
        ty = cy + int(dist * math.sin(angle))
        build_fountain(world, tx, ty, base_z + 1)


def build_hedge_maze(world, cx, cy, base_z, size, passages, rng):
    for x in range(cx - size // 2, cx + size // 2):
        for y in range(cy - size // 2, cy + size // 2):
            if (x - cx) % passages == 0 or (y - cy) % passages == 0:
                world.set(x, y, base_z, "grass")
            else:
                for z in range(base_z, base_z + 3):
                    world.set(x, y, z, "leaves")


def build_pyramid_cluster(world, cx, cy, base_z, count, spacing, rng):
    for i in range(count):
        angle = (i / count) * 2 * math.pi if count > 0 else 0
        dist = spacing
        pyr_x = cx + int(dist * i * math.cos(angle))
        pyr_y = cy + int(dist * i * math.sin(angle))
        size = 10 + rng.randint(-2, 2)
        build_pyramid(world, pyr_x, pyr_y, base_z, size)


def build_terraced_towers(world, cx, cy, base_z, tiers, rng):
    for tier in range(tiers):
        tier_z = base_z + tier * 4
        tier_size = 15 - tier * 2
        for x in range(cx - tier_size // 2, cx + tier_size // 2):
            for y in range(cy - tier_size // 2, cy + tier_size // 2):
                if abs(x - cx) == tier_size // 2 - 1 or abs(y - cy) == tier_size // 2 - 1:
                    world.set(x, y, tier_z, "brick")


def build_hanging_gardens(world, cx, cy, base_z, size, levels, rng):
    for level in range(levels):
        level_z = base_z + level * 4
        level_size = size - level * 3
        for x in range(cx - level_size // 2, cx + level_size // 2):
            for y in range(cy - level_size // 2, cy + level_size // 2):
                world.set(x, y, level_z, "stone")
                if rng.random() < 0.3:
                    world.set(x, y, level_z + 1, "leaves")


def build_lattice_structure(world, cx, cy, base_z, width, depth, height, rng):
    for z in range(base_z, base_z + height):
        for x in range(cx - width // 2, cx + width // 2, 3):
            for y in range(cy - depth // 2, cy + depth // 2, 3):
                world.set(x, y, z, "quartz_block")


def build_spiral_garden_path(world, cx, cy, base_z, radius, turns, rng):
    for turn in range(turns):
        for step in range(50):
            angle = (turn * 2 * math.pi + step * (2 * math.pi / 50))
            dist = radius * (step / 50)
            x = cx + int(dist * math.cos(angle))
            y = cy + int(dist * math.sin(angle))
            for dx in range(-1, 2):
                world.set(x + dx, y, base_z, "grass")


def build_multi_building_plaza(world, cx, cy, base_z, size, building_count, rng):
    world.fill_box(cx - size, cy - size, base_z, cx + size, cy + size, base_z, "cobblestone")
    for i in range(building_count):
        angle = (i / building_count) * 2 * math.pi if building_count > 0 else 0
        dist = size // 2 + 10
        bldg_x = cx + int(dist * math.cos(angle))
        bldg_y = cy + int(dist * math.sin(angle))
        build_mansion(world, bldg_x, bldg_y, base_z, 12, rng)


def build_landmark_cluster(world, cx, cy, base_z, count, rng):
    for i in range(count):
        angle = (i / count) * 2 * math.pi if count > 0 else 0
        dist = 40 + rng.randint(5, 20)
        landmark_x = cx + int(dist * math.cos(angle))
        landmark_y = cy + int(dist * math.sin(angle))
        landmark_type = rng.choice(["pyramid", "temple", "tower"])
        if landmark_type == "pyramid":
            build_pyramid(world, landmark_x, landmark_y, base_z, 12)
        elif landmark_type == "temple":
            build_temple(world, landmark_x, landmark_y, base_z, 15, rng)
        else:
            build_watchtower(world, landmark_x, landmark_y, base_z, 15)


def build_forest_clearing(world, cx, cy, base_z, radius, rng):
    for x in range(cx - radius, cx + radius + 1):
        for y in range(cy - radius, cy + radius + 1):
            world.set(x, y, base_z, "grass")
    world.set(cx, cy, base_z + 1, "campfire" if "campfire" in PALETTE else "furnace")


def build_ruins_of_structure(world, cx, cy, base_z, original_size, damage_level, rng):
    for x in range(cx - original_size // 2, cx + original_size // 2):
        for y in range(cy - original_size // 2, cy + original_size // 2):
            for z in range(base_z, base_z + original_size // 4):
                if rng.random() > damage_level:
                    world.set(x, y, z, "brick")


def build_construction_site(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z, "dirt")
    for _ in range(size):
        pile_x = cx + rng.randint(-size // 2, size // 2)
        pile_y = cy + rng.randint(-size // 2, size // 2)
        for z in range(base_z + 1, base_z + 3):
            world.set(pile_x, pile_y, z, "brick")


def build_lookout_point(world, cx, cy, base_z, elevation, radius, rng):
    world.fill_sphere(cx, cy, base_z, radius, "stone")
    world.fill_sphere(cx, cy, base_z + elevation, radius // 2, "grass")


def build_parkway_system(world, center_x, center_y, base_z, width, length, branch_count, rng):
    build_road(world, center_x - length // 2, center_y, center_x + length // 2, center_y, base_z, width)
    build_road(world, center_x, center_y - length // 2, center_x, center_y + length // 2, base_z, width)
    for _ in range(branch_count):
        angle = rng.uniform(0, 2 * math.pi)
        dist = length // 2 - 10
        end_x = center_x + int(dist * math.cos(angle))
        end_y = center_y + int(dist * math.sin(angle))
        build_road(world, center_x, center_y, end_x, end_y, base_z, width // 2)


def build_themed_biome_cluster(world, cx, cy, base_z, theme, size, rng):
    if theme == "mushroom":
        for _ in range(size):
            mx = cx + rng.randint(-40, 40)
            my = cy + rng.randint(-40, 40)
            height = rng.randint(4, 8)
            for z in range(base_z, base_z + height):
                world.set(mx, my, z, "mushroom_stem" if "mushroom_stem" in PALETTE else "log")
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    world.set(mx + dx, my + dy, base_z + height, "mushroom_cap" if "mushroom_cap" in PALETTE else "leaves")
    elif theme == "swamp":
        for x in range(cx - 40, cx + 40):
            for y in range(cy - 40, cy + 40):
                world.set(x, y, base_z - 1, "mud" if "mud" in PALETTE else "dirt")
                if rng.random() < 0.1:
                    build_advanced_tree(world, x, y, base_z, rng.choice(["oak", "spruce"]), rng.randint(5, 8), rng)


def build_geothermal_feature(world, cx, cy, base_z, size, rng):
    for x in range(cx - size, cx + size):
        for y in range(cy - size, cy + size):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= size:
                for z in range(base_z - size // 2, base_z + 3):
                    if dist <= size * 0.3:
                        world.set(x, y, z, "lava")
                    elif z < base_z:
                        world.set(x, y, z, "stone")


def build_player_spawn_area(world, cx, cy, base_z, safe_radius, rng):
    for x in range(cx - safe_radius, cx + safe_radius + 1):
        for y in range(cy - safe_radius, cy + safe_radius + 1):
            world.set(x, y, base_z, "grass")
    world.set(cx, cy, base_z + 1, "crafting_table")
    world.set(cx + 1, cy, base_z + 1, "furnace")
    world.set(cx, cy + 1, base_z + 1, "furnace")


def build_vault_system(world, cx, cy, base_z, chamber_count, rng):
    for chamber in range(chamber_count):
        offset_x = (chamber % 3 - 1) * 30
        offset_y = (chamber // 3 - 1) * 30
        vault_x = cx + offset_x
        vault_y = cy + offset_y
        world.fill_box(vault_x - 8, vault_y - 8, base_z - 5, vault_x + 8, vault_y + 8, base_z, "obsidian")
        world.set(vault_x, vault_y, base_z - 1, "diamond_block" if "diamond_block" in PALETTE else "diamond_ore")


def build_sky_bridge_network(world, cx, cy, sky_z, count, rng):
    points = []
    for i in range(count):
        angle = (i / count) * 2 * math.pi if count > 0 else 0
        dist = 60 + rng.randint(10, 30)
        px = cx + int(dist * math.cos(angle))
        py = cy + int(dist * math.sin(angle))
        points.append((px, py))
    build_network_bridges(world, points, sky_z, rng)


def build_nether_portal_network(world, cx, cy, base_z, count, rng):
    for i in range(count):
        angle = (i / count) * 2 * math.pi if count > 0 else 0
        dist = 80 + rng.randint(20, 50)
        portal_x = cx + int(dist * math.cos(angle))
        portal_y = cy + int(dist * math.sin(angle))
        build_nether_portal_frame(world, portal_x, portal_y, base_z)


def build_beacon_network(world, cx, cy, base_z, beacon_count, rng):
    for i in range(beacon_count):
        angle = (i / beacon_count) * 2 * math.pi if beacon_count > 0 else 0
        dist = 70 + i * 10
        beacon_x = cx + int(dist * math.cos(angle))
        beacon_y = cy + int(dist * math.sin(angle))
        build_beacon_tower(world, beacon_x, beacon_y, base_z, 20)


def build_cave_entrance_system(world, cx, cy, base_z, count, rng):
    for i in range(count):
        angle = (i / count) * 2 * math.pi if count > 0 else 0
        dist = 50 + rng.randint(10, 40)
        entrance_x = cx + int(dist * math.cos(angle))
        entrance_y = cy + int(dist * math.sin(angle))
        build_dungeon_entrance(world, entrance_x, entrance_y, base_z, rng)


def build_oasis(world, cx, cy, base_z, size, rng):
    for x in range(cx - size, cx + size):
        for y in range(cy - size, cy + size):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= size:
                world.set(x, y, base_z, "sand")
    world.set(cx, cy, base_z, "water")
    world.set(cx + 1, cy, base_z, "water")
    world.set(cx, cy + 1, base_z, "water")
    for _ in range(2):
        tx = cx + rng.randint(-size + 2, size - 2)
        ty = cy + rng.randint(-size + 2, size - 2)
        build_advanced_tree(world, tx, ty, base_z + 1, "acacia", 6, rng)


def build_mega_city_center(world, cx, cy, base_z, size, rng):
    build_central_plaza(world, cx, cy, base_z, size // 2, rng)
    build_town_hall(world, cx, cy + size + 20, base_z, 20, rng)
    build_library(world, cx - size - 20, cy, base_z, 15, rng)
    build_marketplace(world, cx + size + 20, cy, base_z, size // 3, rng)
    build_colosseum(world, cx, cy - size - 20, base_z, 25, 12)


def build_interconnected_roads(world, points, base_z, width, rng):
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            x1, y1 = points[i]
            x2, y2 = points[j]
            build_road(world, x1, y1, x2, y2, base_z, width)


def build_terrain_variation(world, cx, cy, base_z, variation_type, size, noise_gen, rng):
    if variation_type == "rolling_hills":
        for x in range(cx - size, cx + size):
            for y in range(cy - size, cy + size):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                if dist <= size:
                    height = int(5 * math.sin(dist * 0.1) * (1 - dist / size))
                    for z in range(base_z, base_z + max(0, height)):
                        world.set(x, y, z, "grass")
    elif variation_type == "checkerboard_biome":
        for x in range(cx - size, cx + size):
            for y in range(cy - size, cy + size):
                biome = "grass" if (x // 10 + y // 10) % 2 == 0 else "sand"
                world.set(x, y, base_z, biome)


def generate_city_district(world, district_x, district_y, base_z, district_id, rng):
    district_types = ["residential", "commercial", "industrial", "military"]
    district_type = district_types[district_id % len(district_types)]
    build_comprehensive_city_district(world, district_x, district_y, base_z, district_type, 50, rng)


generate()


def build_advanced_pyramid_1(world, cx, cy, base_z, size):
    for layer in range(size // 2):
        layer_size = size - layer * 3
        for x in range(cx - layer_size // 2, cx + layer_size // 2):
            for y in range(cy - layer_size // 2, cy + layer_size // 2):
                world.set(x, y, base_z + layer, "sand_stone")


def build_advanced_pyramid_2(world, cx, cy, base_z, size):
    for layer in range(size // 3):
        for x in range(cx - size // 2 + layer, cx + size // 2 - layer):
            for y in range(cy - size // 2 + layer, cy + size // 2 - layer):
                world.set(x, y, base_z + layer, "brick")


def build_advanced_pyramid_3(world, cx, cy, base_z, size):
    for layer in range(size // 2):
        radius = size - layer * 2
        for x in range(cx - radius // 2, cx + radius // 2):
            for y in range(cy - radius // 2, cy + radius // 2):
                world.set(x, y, base_z + layer, "stone")


def build_fortress_variant_1(world, cx, cy, base_z, size):
    world.fill_box(cx - size // 2, cy - size // 2, base_z - 4, cx + size // 2, cy + size // 2, base_z + 6, "brick")
    for x in range(cx - size // 2 + 1, cx + size // 2 - 1, 4):
        for y in range(cy - size // 2 + 1, cy + size // 2 - 1, 4):
            world.voxels.pop((x, y, base_z + 1), None)


def build_fortress_variant_2(world, cx, cy, base_z, size):
    for layer in range(4):
        layer_size = size - layer * 3
        layer_z = base_z + layer * 2
        world.fill_box(cx - layer_size // 2, cy - layer_size // 2, layer_z,
                       cx + layer_size // 2, cy + layer_size // 2, layer_z + 1, "obsidian")


def build_fortress_variant_3(world, cx, cy, base_z, size):
    for direction in range(8):
        angle = (direction / 8) * 2 * math.pi
        ext_x = cx + int((size // 2 + 5) * math.cos(angle))
        ext_y = cy + int((size // 2 + 5) * math.sin(angle))
        world.fill_box(ext_x - 2, ext_y - 2, base_z, ext_x + 2, ext_y + 2, base_z + 3, "brick")


def build_temple_variation_3(world, cx, cy, base_z, size):
    steps = size // 4
    for step in range(steps):
        step_z = base_z + step * 2
        step_size = size - step * 4
        for x in range(cx - step_size // 2, cx + step_size // 2):
            for y in range(cy - step_size // 2, cy + step_size // 2):
                if (x + y) % 2 == 0:
                    world.set(x, y, step_z, "sand_stone")


def build_temple_variation_4(world, cx, cy, base_z, size):
    for x in range(cx - size // 2, cx + size // 2):
        for y in range(cy - size // 2, cy + size // 2):
            for z in range(base_z, base_z + size // 3):
                if abs(x - cx) % 3 == 0 or abs(y - cy) % 3 == 0:
                    world.set(x, y, z, "brick")


def build_tower_variant_1(world, cx, cy, base_z, height):
    for z in range(base_z, base_z + height):
        world.set(cx, cy, z, "stone")
        world.set(cx + 1, cy, z, "stone")
        world.set(cx, cy + 1, z, "stone")
        world.set(cx + 1, cy + 1, z, "stone")
        if z % 5 == 0:
            for x in range(cx - 2, cx + 3):
                for y in range(cy - 2, cy + 3):
                    world.set(x, y, z, "brick")


def build_tower_variant_2(world, cx, cy, base_z, height):
    for z in range(base_z, base_z + height):
        for angle_deg in range(0, 360, 45):
            angle_rad = math.radians(angle_deg)
            x = cx + int(2 * math.cos(angle_rad))
            y = cy + int(2 * math.sin(angle_rad))
            world.set(x, y, z, "stone")


def build_castle_variant_1(world, cx, cy, base_z, size):
    world.fill_box(cx - size // 2, cy - size // 2, base_z - 2, cx + size // 2, cy + size // 2, base_z, "stone")
    for x in range(cx - size // 2, cx + size // 2, size // 4):
        build_tower(world, x, cy - size // 2, base_z, 12, 3)
        build_tower(world, x, cy + size // 2, base_z, 12, 3)
    for y in range(cy - size // 2, cy + size // 2, size // 4):
        build_tower(world, cx - size // 2, y, base_z, 12, 3)
        build_tower(world, cx + size // 2, y, base_z, 12, 3)


def build_castle_variant_2(world, cx, cy, base_z, size):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 4, "brick")
    for ring in range(1, 3):
        ring_size = size - ring * 6
        for x in range(cx - ring_size // 2, cx + ring_size // 2):
            for y in range(cy - ring_size // 2, cy + ring_size // 2):
                if abs(x - cx) == ring_size // 2 - 1 or abs(y - cy) == ring_size // 2 - 1:
                    for z in range(base_z + 1, base_z + 4):
                        world.set(x, y, z, "obsidian")


def build_biome_forest_mixed(world, cx, cy, base_z, radius, tree_count):
    tree_types = ["oak", "birch", "spruce", "acacia", "dark_oak"]
    rng = random.Random(hash((cx, cy)) % (2**32))
    for i in range(tree_count):
        angle = (i / tree_count) * 2 * math.pi if tree_count > 0 else 0
        dist = rng.uniform(0, radius)
        tx = cx + int(dist * math.cos(angle))
        ty = cy + int(dist * math.sin(angle))
        tree_type = rng.choice(tree_types)
        height = rng.randint(4, 9)
        build_advanced_tree(world, tx, ty, base_z + 1, tree_type, height, rng)


def build_biome_swamp(world, cx, cy, base_z, radius, rng):
    for x in range(cx - radius, cx + radius):
        for y in range(cy - radius, cy + radius):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= radius:
                world.set(x, y, base_z - 1, "mud" if "mud" in PALETTE else "clay")
                world.set(x, y, base_z, "water" if rng.random() < 0.4 else "grass")
                if rng.random() < 0.05:
                    build_advanced_tree(world, x, y, base_z + 1, "oak", rng.randint(3, 6), rng)


def build_biome_taiga(world, cx, cy, base_z, radius, tree_count, rng):
    for x in range(cx - radius, cx + radius):
        for y in range(cy - radius, cy + radius):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= radius:
                world.set(x, y, base_z, "snow" if rng.random() < 0.7 else "grass")
    for _ in range(tree_count):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(0, radius)
        tx = cx + int(dist * math.cos(angle))
        ty = cy + int(dist * math.sin(angle))
        build_advanced_tree(world, tx, ty, base_z + 1, "spruce", rng.randint(5, 10), rng)


def build_biome_desert_extended(world, cx, cy, base_z, radius, rng):
    for x in range(cx - radius, cx + radius):
        for y in range(cy - radius, cy + radius):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= radius:
                for z in range(base_z - 2, base_z + 1):
                    world.set(x, y, z, "sand")
                if rng.random() < 0.02:
                    world.set(x, y, base_z + 1, "cactus" if "cactus" in PALETTE else "log")


def build_biome_savanna(world, cx, cy, base_z, radius, tree_count, rng):
    for x in range(cx - radius, cx + radius):
        for y in range(cy - radius, cy + radius):
            world.set(x, y, base_z, "grass")
    for _ in range(tree_count):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(0, radius)
        tx = cx + int(dist * math.cos(angle))
        ty = cy + int(dist * math.sin(angle))
        build_advanced_tree(world, tx, ty, base_z + 1, "acacia", rng.randint(4, 8), rng)


def build_terrain_cliffs(world, start_x, start_y, end_x, end_y, base_z, cliff_height, rng):
    steps = max(abs(end_x - start_x), abs(end_y - start_y))
    if steps == 0:
        return
    for step in range(steps + 1):
        t = step / steps if steps > 0 else 0
        x = int(start_x + (end_x - start_x) * t)
        y = int(start_y + (end_y - start_y) * t)
        for z in range(base_z - cliff_height, base_z):
            world.set(x, y, z, "stone")
        world.set(x, y, base_z, "grass")


def build_terrain_hills(world, cx, cy, base_z, hill_radius, max_height, noise_gen, rng):
    for x in range(cx - hill_radius, cx + hill_radius):
        for y in range(cy - hill_radius, cy + hill_radius):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist <= hill_radius:
                height = int(max_height * (1 - dist / hill_radius))
                for z in range(base_z, base_z + height):
                    world.set(x, y, z, "stone")
                if height > 0:
                    world.set(x, y, base_z + height, "grass")


def build_large_cave_chamber(world, cx, cy, base_z, chamber_width, chamber_depth, chamber_height, rng):
    for x in range(cx - chamber_width // 2, cx + chamber_width // 2):
        for y in range(cy - chamber_depth // 2, cy + chamber_depth // 2):
            for z in range(base_z - chamber_height, base_z):
                if rng.random() < 0.9:
                    world.voxels.pop((x, y, z), None)


def build_connected_caves(world, cave_count, base_z, noise_gen, rng):
    cave_positions = []
    for i in range(cave_count):
        cx = rng.randint(-80, 80)
        cy = rng.randint(-80, 80)
        cave_positions.append((cx, cy))
        build_large_cave_chamber(world, cx, cy, base_z - 5, 30, 30, 10, rng)
    for i in range(len(cave_positions) - 1):
        x1, y1 = cave_positions[i]
        x2, y2 = cave_positions[i + 1]
        build_ravine(world, x1, y1, x2, y2, 5, 6, rng)


def build_ore_distribution_advanced(world, ore_type, concentration, min_z, max_z, rng):
    materials_map = {
        "coal": "coal_ore",
        "iron": "iron_ore",
        "gold": "gold_ore",
        "diamond": "diamond_ore",
        "lapis": "lapis_ore",
        "redstone": "redstone_ore",
    }
    material = materials_map.get(ore_type, "stone")
    for x in range(-100, 100):
        for y in range(-100, 100):
            for z in range(min_z, max_z):
                if rng.random() < concentration:
                    if world.get(x, y, z) == "stone":
                        world.set(x, y, z, material)


def build_water_features_extended(world, cx, cy, base_z, count, rng):
    for i in range(count):
        angle = (i / count) * 2 * math.pi if count > 0 else 0
        dist = 50 + rng.randint(10, 40)
        feature_x = cx + int(dist * math.cos(angle))
        feature_y = cy + int(dist * math.sin(angle))
        feature_type = rng.choice(["lake", "river", "stream"])
        if feature_type == "lake":
            build_lake_system(world, feature_x, feature_y, base_z, rng.randint(8, 15), rng.randint(2, 4), rng)
        elif feature_type == "river":
            end_x = feature_x + rng.randint(-50, 50)
            end_y = feature_y + rng.randint(-50, 50)
            build_river_system(world, feature_x, feature_y, end_x, end_y, rng.randint(4, 6), rng.randint(2, 3), base_z)


def build_structure_system_1(world, cx, cy, base_z, rng):
    structure_count = 6
    for i in range(structure_count):
        angle = (i / structure_count) * 2 * math.pi
        dist = 100 + i * 15
        struct_x = cx + int(dist * math.cos(angle))
        struct_y = cy + int(dist * math.sin(angle))
        struct_type = rng.choice(["castle", "pyramid", "temple", "tower"])
        if struct_type == "castle":
            build_castle(world, struct_x, struct_y, base_z, 20, rng)
        elif struct_type == "pyramid":
            build_pyramid(world, struct_x, struct_y, base_z, 15)
        elif struct_type == "temple":
            build_temple(world, struct_x, struct_y, base_z, 15, rng)
        else:
            build_watchtower(world, struct_x, struct_y, base_z, 15)


def build_structure_system_2(world, cx, cy, base_z, rng):
    build_fortress_section_1(world, cx - 50, cy, base_z, 30, rng)
    build_fortress_section_2(world, cx + 50, cy, base_z, 30, rng)
    build_fortified_wall_section(world, cx - 50, cy, cx + 50, cy, base_z, 8, 3, rng)


def build_resource_system_1(world, cx, cy, base_z, rng):
    ore_locations = [
        (cx - 50, cy - 50, "coal_ore"),
        (cx + 50, cy - 50, "iron_ore"),
        (cx - 50, cy + 50, "gold_ore"),
        (cx + 50, cy + 50, "diamond_ore"),
    ]
    for ox, oy, ore_material in ore_locations:
        for x in range(ox - 10, ox + 10):
            for y in range(oy - 10, oy + 10):
                for z in range(base_z - 8, base_z - 2):
                    if rng.random() < 0.3:
                        world.set(x, y, z, ore_material)


def build_transportation_network_1(world, cx, cy, base_z, rng):
    major_points = [
        (cx - 80, cy - 80),
        (cx + 80, cy - 80),
        (cx - 80, cy + 80),
        (cx + 80, cy + 80),
    ]
    build_interconnected_roads(world, major_points, base_z, 7, rng)
    for point_x, point_y in major_points:
        build_marketplace(world, point_x, point_y, base_z, 12, rng)


def build_district_system_1(world, cx, cy, base_z, rng):
    for dx in [-60, 0, 60]:
        for dy in [-60, 0, 60]:
            district_x = cx + dx
            district_y = cy + dy
            generate_city_district(world, district_x, district_y, base_z, hash((dx, dy)) % 4, rng)




def build_mansion_variant_1(world, cx, cy, base_z, levels):
    for level in range(levels):
        level_z = base_z + level * 6
        level_size = 20 - level * 2
        for x in range(cx - level_size // 2, cx + level_size // 2):
            for y in range(cy - level_size // 2, cy + level_size // 2):
                if abs(x - cx) == level_size // 2 - 1 or abs(y - cy) == level_size // 2 - 1:
                    for z in range(level_z, level_z + 5):
                        world.set(x, y, z, "brick")


def build_mansion_variant_2(world, cx, cy, base_z, size):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 5, "wood")
    for x in range(cx - size // 2 + 2, cx + size // 2 - 2):
        for y in range(cy - size // 2 + 2, cy + size // 2 - 2):
            if (x + y) % 3 == 0:
                for z in range(base_z + 1, base_z + 4):
                    world.set(x, y, z, "glass")


def build_mansion_variant_3(world, cx, cy, base_z, wings):
    for wing in range(wings):
        wing_angle = (wing / wings) * 2 * math.pi
        wing_x = cx + int(25 * math.cos(wing_angle))
        wing_y = cy + int(25 * math.sin(wing_angle))
        world.fill_box(wing_x - 6, wing_y - 6, base_z, wing_x + 6, wing_y + 6, base_z + 4, "brick")


def build_house_variant_1(world, cx, cy, base_z):
    world.fill_box(cx - 4, cy - 4, base_z, cx + 4, cy + 4, base_z + 4, "wood")
    for x in range(cx - 3, cx + 4):
        for y in range(cy - 3, cy + 4):
            world.set(x, y, base_z + 1, "glass" if abs(x - cx) == 3 or abs(y - cy) == 3 else "planks")


def build_house_variant_2(world, cx, cy, base_z):
    world.fill_box(cx - 5, cy - 5, base_z, cx + 5, cy + 5, base_z + 3, "brick")
    world.set(cx - 3, cy - 5, base_z + 1, "glass")
    world.set(cx + 3, cy - 5, base_z + 1, "glass")


def build_cottage(world, cx, cy, base_z):
    world.fill_box(cx - 3, cy - 3, base_z, cx + 3, cy + 3, base_z + 3, "wood")
    for x in range(cx - 2, cx + 3):
        world.set(x, cy - 3, base_z + 1, "glass")


def build_tower_variants_cluster(world, cx, cy, base_z, tower_count, rng):
    for i in range(tower_count):
        angle = (i / tower_count) * 2 * math.pi if tower_count > 0 else 0
        dist = 30 + rng.randint(5, 20)
        tower_x = cx + int(dist * math.cos(angle))
        tower_y = cy + int(dist * math.sin(angle))
        height = rng.randint(12, 25)
        build_watchtower(world, tower_x, tower_y, base_z, height)


def build_bridge_variants(world, start_x, start_y, end_x, end_y, base_z, rng):
    bridge_type = rng.choice(["stone_arch", "wooden_simple", "suspended"])
    if bridge_type == "stone_arch":
        steps = max(abs(end_x - start_x), abs(end_y - start_y))
        if steps > 0:
            for step in range(steps + 1):
                t = step / steps
                x = int(start_x + (end_x - start_x) * t)
                y = int(start_y + (end_y - start_y) * t)
                height = int(5 * math.sin(step / steps * math.pi))
                for z in range(base_z - height, base_z + 1):
                    world.set(x, y, z, "stone")
    elif bridge_type == "wooden_simple":
        build_bridge(world, start_x, start_y, end_x, end_y, base_z, 3)
    else:
        build_rope_bridge(world, start_x, start_y, end_x, end_y, base_z, 3, rng)


def build_garden_variants_1(world, cx, cy, base_z, size):
    for x in range(cx - size, cx + size):
        for y in range(cy - size, cy + size):
            world.set(x, y, base_z, "grass" if (x + y) % 2 == 0 else "dirt")


def build_garden_variants_2(world, cx, cy, base_z, size):
    for layer in range(1, size // 3):
        for x in range(cx - size + layer, cx + size - layer):
            for y in range(cy - size + layer, cy + size - layer):
                if abs(x - cx) == size - layer - 1 or abs(y - cy) == size - layer - 1:
                    world.set(x, y, base_z, "stone")


def build_terrain_rocky_area(world, cx, cy, base_z, radius, rng):
    for x in range(cx - radius, cx + radius):
        for y in range(cy - radius, cy + radius):
            for z in range(base_z - 3, base_z + 1):
                if rng.random() < 0.4:
                    world.set(x, y, z, "gravel")


def build_terrain_sandy_area(world, cx, cy, base_z, radius):
    for x in range(cx - radius, cx + radius):
        for y in range(cy - radius, cy + radius):
            for z in range(base_z - 2, base_z + 1):
                world.set(x, y, z, "sand")


def build_terrain_snowy_area(world, cx, cy, base_z, radius):
    for x in range(cx - radius, cx + radius):
        for y in range(cy - radius, cy + radius):
            world.set(x, y, base_z, "snow")
            for z in range(base_z - 2, base_z):
                world.set(x, y, z, "ice")


def build_terrain_muddy_area(world, cx, cy, base_z, radius, rng):
    for x in range(cx - radius, cx + radius):
        for y in range(cy - radius, cy + radius):
            world.set(x, y, base_z, "dirt" if rng.random() < 0.7 else "clay")


def build_underground_network(world, cx, cy, base_z, tunnel_count, rng):
    tunnel_starts = []
    for i in range(tunnel_count):
        angle = (i / tunnel_count) * 2 * math.pi if tunnel_count > 0 else 0
        dist = 60 + rng.randint(10, 30)
        start_x = cx + int(dist * math.cos(angle))
        start_y = cy + int(dist * math.sin(angle))
        tunnel_starts.append((start_x, start_y))
    
    for i in range(len(tunnel_starts) - 1):
        x1, y1 = tunnel_starts[i]
        x2, y2 = tunnel_starts[i + 1]
        build_underground_rail_system(world, x1, y1, x2, y2, base_z, 8, rng)


def build_sky_infrastructure(world, cx, cy, sky_z, platform_count, rng):
    for i in range(platform_count):
        angle = (i / platform_count) * 2 * math.pi if platform_count > 0 else 0
        dist = 50 + i * 8
        plat_x = cx + int(dist * math.cos(angle))
        plat_y = cy + int(dist * math.sin(angle))
        for x in range(plat_x - 3, plat_x + 4):
            for y in range(plat_y - 3, plat_y + 4):
                world.set(x, y, sky_z, "quartz_block")


def build_underground_fortress_advanced(world, cx, cy, base_z, levels, rng):
    for level in range(levels):
        level_z = base_z - level * 10
        level_radius = 40 - level * 8
        for x in range(cx - level_radius, cx + level_radius):
            for y in range(cy - level_radius, cy + level_radius):
                for z in range(level_z - 5, level_z + 1):
                    if (x % 3 == 0 or y % 3 == 0) and z % 2 == 0:
                        world.set(x, y, z, "obsidian")


def build_trading_post(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z, "cobblestone")
    for direction in range(4):
        angle = direction * math.pi / 2
        stall_x = cx + int((size // 2 + 5) * math.cos(angle))
        stall_y = cy + int((size // 2 + 5) * math.sin(angle))
        build_market_stall(world, stall_x, stall_y, base_z)


def build_temple_courtyard(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size, cy - size, base_z, cx + size, cy + size, base_z, "stone")
    build_temple(world, cx, cy, base_z + 1, size // 2, rng)
    for i in range(4):
        angle = (i / 4) * 2 * math.pi
        fountain_x = cx + int((size // 2) * math.cos(angle))
        fountain_y = cy + int((size // 2) * math.sin(angle))
        build_fountain(world, fountain_x, fountain_y, base_z + 1)


def build_pyramid_complex(world, cx, cy, base_z, count, spacing, rng):
    for i in range(count):
        pyr_x = cx - (count - 1) * spacing // 2 + i * spacing
        build_pyramid(world, pyr_x, cy, base_z, 15)


def build_dungeon_system(world, cx, cy, base_z, dungeon_count, rng):
    for i in range(dungeon_count):
        angle = (i / dungeon_count) * 2 * math.pi if dungeon_count > 0 else 0
        dist = 80 + i * 15
        dung_x = cx + int(dist * math.cos(angle))
        dung_y = cy + int(dist * math.sin(angle))
        build_dungeon_entrance(world, dung_x, dung_y, base_z, rng)


def build_checkpoint_system(world, x1, y1, x2, y2, base_z, checkpoint_count, rng):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for i in range(checkpoint_count):
        t = (i + 1) / (checkpoint_count + 1)
        check_x = int(x1 + (x2 - x1) * t)
        check_y = int(y1 + (y2 - y1) * t)
        world.fill_box(check_x - 3, check_y - 3, base_z, check_x + 3, check_y + 3, base_z + 2, "brick")


def build_watchtower_line(world, x1, y1, x2, y2, base_z, spacing, height, rng):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(0, steps + 1, spacing):
        t = step / steps if steps > 0 else 0
        tower_x = int(x1 + (x2 - x1) * t)
        tower_y = int(y1 + (y2 - y1) * t)
        build_watchtower(world, tower_x, tower_y, base_z, height)


def build_monument_collection(world, cx, cy, base_z, monument_count, rng):
    for i in range(monument_count):
        angle = (i / monument_count) * 2 * math.pi if monument_count > 0 else 0
        dist = 60 + i * 10
        mon_x = cx + int(dist * math.cos(angle))
        mon_y = cy + int(dist * math.sin(angle))
        size = rng.randint(15, 25)
        build_monument(world, mon_x, mon_y, base_z, size, rng)


def build_terraced_city(world, cx, cy, base_z, terraces, rng):
    for terrace in range(terraces):
        terrace_z = base_z + terrace * 6
        terrace_size = 50 - terrace * 5
        for x in range(cx - terrace_size // 2, cx + terrace_size // 2):
            for y in range(cy - terrace_size // 2, cy + terrace_size // 2):
                if (x + y) % 4 == 0:
                    world.set(x, y, terrace_z, "stone")


def build_resource_gathering_site(world, cx, cy, base_z, rng):
    build_mineshaft_section(world, cx - 30, cy, base_z, 40, 10, 8, rng)
    build_quarry(world, cx + 30, cy, base_z, 30, 10, rng)
    build_farm(world, cx, cy + 30, base_z, 20, rng)


def build_settlement_hub(world, cx, cy, base_z, hub_size, rng):
    world.fill_box(cx - hub_size // 2, cy - hub_size // 2, base_z, cx + hub_size // 2, cy + hub_size // 2, base_z, "cobblestone")
    for i in range(6):
        angle = (i / 6) * 2 * math.pi
        building_x = cx + int((hub_size // 2 + 10) * math.cos(angle))
        building_y = cy + int((hub_size // 2 + 10) * math.sin(angle))
        build_mansion(world, building_x, building_y, base_z, 12, rng)


def build_fortress_network(world, count, base_z, rng):
    fortress_positions = []
    for i in range(count):
        angle = (i / count) * 2 * math.pi if count > 0 else 0
        dist = 120 + i * 20
        fort_x = int(dist * math.cos(angle))
        fort_y = int(dist * math.sin(angle))
        fortress_positions.append((fort_x, fort_y))
        world.fill_box(fort_x - 15, fort_y - 15, base_z, fort_x + 15, fort_y + 15, base_z + 4, "brick")
    
    for i in range(len(fortress_positions) - 1):
        x1, y1 = fortress_positions[i]
        x2, y2 = fortress_positions[i + 1]
        build_wall(world, x1, y1, x2, y2, base_z, 6, rng)


def build_massive_terrain_feature(world, cx, cy, base_z, feature_type, feature_size, noise_gen, rng):
    if feature_type == "mountain_range":
        for offset in range(-2, 3):
            build_mountain_range(world, cx + offset * 50, cy, base_z, 60, 60, 30, noise_gen, rng)
    elif feature_type == "lake_system":
        for i in range(4):
            angle = (i / 4) * 2 * math.pi
            lake_x = cx + int(80 * math.cos(angle))
            lake_y = cy + int(80 * math.sin(angle))
            build_lake_system(world, lake_x, lake_y, base_z, 15, 5, rng)
    elif feature_type == "forest_area":
        build_forest_biome(world, cx, cy, base_z, 40, 20, ["oak", "birch", "spruce"], rng)




def build_military_complex_v1(world, cx, cy, base_z, rng):
    build_castle(world, cx, cy, base_z, 25, rng)
    build_watchtower_network(world, base_z, 8, rng)
    build_armory(world, cx + 30, cy, base_z, 15, rng)


def build_armory(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 3, "brick")
    for x in range(cx - size // 4, cx + size // 4):
        for y in range(cy - size // 4, cy + size // 4):
            world.set(x, y, base_z + 1, "furnace")


def build_training_grounds(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size, cy - size, base_z, cx + size, cy + size, base_z, "sand")
    for i in range(4):
        angle = (i / 4) * 2 * math.pi
        post_x = cx + int((size - 10) * math.cos(angle))
        post_y = cy + int((size - 10) * math.sin(angle))
        for z in range(base_z + 1, base_z + 4):
            world.set(post_x, post_y, z, "wood")


def build_logistics_center(world, cx, cy, base_z, size, rng):
    for section in range(3):
        section_x = cx - size + section * (size // 1.5)
        build_warehouse(world, section_x, cy, base_z, size // 3, rng)


def build_data_repository(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z, cx + size // 2, cy + size // 2, base_z + 4, "quartz_block")
    for x in range(cx - size // 4, cx + size // 4, 2):
        for y in range(cy - size // 4, cy + size // 4, 2):
            world.set(x, y, base_z + 1, "bookshelf")


def build_power_generation_plant(world, cx, cy, base_z, rng):
    for x in range(cx - 15, cx + 16):
        for y in range(cy - 15, cy + 16):
            if (x - cx) % 5 == 0 and (y - cy) % 5 == 0:
                for z in range(base_z, base_z + 10):
                    world.set(x, y, z, "furnace")


def build_living_quarters(world, cx, cy, base_z, unit_count, rng):
    for unit in range(unit_count):
        unit_x = cx - (unit_count // 2) * 15 + unit * 15
        for z_offset in range(3):
            world.fill_box(unit_x - 3, cy - 3, base_z + z_offset * 5, unit_x + 3, cy + 3, base_z + z_offset * 5 + 4, "brick")


def build_recreational_area(world, cx, cy, base_z, area_size, rng):
    world.fill_box(cx - area_size, cy - area_size, base_z, cx + area_size, cy + area_size, base_z, "grass")
    for i in range(12):
        angle = (i / 12) * 2 * math.pi
        bench_x = cx + int((area_size - 5) * math.cos(angle))
        bench_y = cy + int((area_size - 5) * math.sin(angle))
        world.set(bench_x, bench_y, base_z + 1, "wood")


def build_observation_deck(world, cx, cy, base_z, height):
    for z in range(base_z, base_z + height):
        for x in range(cx - 5, cx + 6):
            for y in range(cy - 5, cy + 6):
                if abs(x - cx) == 5 or abs(y - cy) == 5:
                    world.set(x, y, z, "brick")
    for z in range(base_z + height - 3, base_z + height):
        for x in range(cx - 6, cx + 7):
            for y in range(cy - 6, cy + 7):
                world.set(x, y, z, "planks")


def build_archive_tower(world, cx, cy, base_z, height, rng):
    for z in range(base_z, base_z + height):
        world.set(cx, cy, z, "quartz_block")
        world.set(cx + 1, cy, z, "quartz_block")
        world.set(cx, cy + 1, z, "quartz_block")
        world.set(cx + 1, cy + 1, z, "quartz_block")
        if z % 3 == 0:
            for x in range(cx - 2, cx + 3):
                for y in range(cy - 2, cy + 3):
                    world.set(x, y, z, "bookshelf")


def build_teleport_hub(world, cx, cy, base_z, portal_count, rng):
    for i in range(portal_count):
        angle = (i / portal_count) * 2 * math.pi if portal_count > 0 else 0
        dist = 20 + i * 10
        portal_x = cx + int(dist * math.cos(angle))
        portal_y = cy + int(dist * math.sin(angle))
        build_nether_portal_frame(world, portal_x, portal_y, base_z)


def build_dimensional_gateway(world, cx, cy, base_z, rng):
    world.fill_box(cx - 5, cy - 5, base_z - 2, cx + 5, cy + 5, base_z + 8, "obsidian")
    world.set(cx, cy, base_z + 2, "beacon" if "beacon" in PALETTE else "furnace")


def build_summoning_circle(world, cx, cy, base_z, radius):
    for angle_deg in range(0, 360, 10):
        angle_rad = math.radians(angle_deg)
        x = cx + int(radius * math.cos(angle_rad))
        y = cy + int(radius * math.sin(angle_rad))
        for z in range(base_z, base_z + 2):
            world.set(x, y, z, "obsidian")
    for x in range(cx - radius + 1, cx + radius):
        for y in range(cy - radius + 1, cy + radius):
            if abs(x - cx) < radius - 2 and abs(y - cy) < radius - 2:
                world.set(x, y, base_z, "obsidian")


def build_ritual_chamber(world, cx, cy, base_z, chamber_size, rng):
    world.fill_box(cx - chamber_size // 2, cy - chamber_size // 2, base_z, cx + chamber_size // 2, cy + chamber_size // 2, base_z, "obsidian")
    for i in range(4):
        angle = (i / 4) * 2 * math.pi
        altar_x = cx + int((chamber_size // 3) * math.cos(angle))
        altar_y = cy + int((chamber_size // 3) * math.sin(angle))
        for z in range(base_z + 1, base_z + 3):
            world.set(altar_x, altar_y, z, "obsidian")


def build_arcane_tower(world, cx, cy, base_z, height):
    for z in range(base_z, base_z + height):
        world.set(cx, cy, z, "purple_concrete" if "purple_concrete" in PALETTE else "quartz_block")
        for angle_deg in range(0, 360, 90):
            angle_rad = math.radians(angle_deg)
            x = cx + int(3 * math.cos(angle_rad))
            y = cy + int(3 * math.sin(angle_rad))
            world.set(x, y, z, "purple_concrete" if "purple_concrete" in PALETTE else "quartz_block")


def build_elemental_shrine(world, cx, cy, base_z, element_type, rng):
    shrine_material = {
        "fire": "obsidian",
        "water": "ice",
        "earth": "stone",
        "air": "quartz_block",
    }.get(element_type, "obsidian")
    
    world.fill_sphere(cx, cy, base_z, 8, shrine_material)
    world.set(cx, cy, base_z + 1, element_type if element_type in PALETTE else shrine_material)


def build_sanctuary_area(world, cx, cy, base_z, size, rng):
    for x in range(cx - size, cx + size):
        for y in range(cy - size, cy + size):
            world.set(x, y, base_z, "grass")
    for i in range(8):
        angle = (i / 8) * 2 * math.pi
        tree_x = cx + int((size - 5) * math.cos(angle))
        tree_y = cy + int((size - 5) * math.sin(angle))
        build_advanced_tree(world, tree_x, tree_y, base_z + 1, "oak", 8, rng)


def build_healing_springs(world, cx, cy, base_z, count, rng):
    for i in range(count):
        spring_x = cx + rng.randint(-30, 30)
        spring_y = cy + rng.randint(-30, 30)
        for x in range(spring_x - 2, spring_x + 3):
            for y in range(spring_y - 2, spring_y + 3):
                world.set(x, y, base_z, "water")


def build_lost_ruins(world, cx, cy, base_z, complexity, rng):
    for i in range(complexity):
        ruin_x = cx + rng.randint(-60, 60)
        ruin_y = cy + rng.randint(-60, 60)
        ruin_size = rng.randint(8, 15)
        build_ruins_of_structure(world, ruin_x, ruin_y, base_z, ruin_size, 0.5, rng)


def build_ancient_temple_system(world, cx, cy, base_z, temple_count, rng):
    for i in range(temple_count):
        angle = (i / temple_count) * 2 * math.pi if temple_count > 0 else 0
        dist = 100 + i * 20
        temple_x = cx + int(dist * math.cos(angle))
        temple_y = cy + int(dist * math.sin(angle))
        build_temple(world, temple_x, temple_y, base_z, 20, rng)


def build_exploration_camp(world, cx, cy, base_z, rng):
    world.fill_box(cx - 10, cy - 10, base_z, cx + 10, cy + 10, base_z, "grass")
    build_crafting_table(world, cx - 5, cy - 5, base_z + 1)
    build_furnace(world, cx + 5, cy - 5, base_z, 8, rng)
    for i in range(3):
        tent_x = cx - 5 + i * 5
        world.fill_box(tent_x - 2, cy + 5, base_z, tent_x + 2, cy + 7, base_z + 2, "wood")


def build_crafting_table(world, cx, cy, base_z):
    world.set(cx, cy, base_z, "crafting_table")


def build_signal_tower(world, cx, cy, base_z, height, rng):
    for z in range(base_z, base_z + height):
        for x in range(cx - 1, cx + 2):
            for y in range(cy - 1, cy + 2):
                world.set(x, y, z, "stone")
    for z in range(base_z + height - 4, base_z + height):
        for x in range(cx - 3, cx + 4):
            for y in range(cy - 3, cy + 4):
                world.set(x, y, z, "concrete_orange")


def build_way_marker(world, cx, cy, base_z):
    for z in range(base_z, base_z + 3):
        world.set(cx, cy, z, "quartz_block")


def build_milestone_cluster(world, cx, cy, base_z, count, spacing):
    for i in range(count):
        marker_x = cx - (count // 2) * spacing + i * spacing
        build_way_marker(world, marker_x, cy, base_z)


def build_supply_cache(world, cx, cy, base_z, cache_type, rng):
    world.fill_box(cx - 3, cy - 3, base_z, cx + 3, cy + 3, base_z + 2, "chest" if "chest" in PALETTE else "wood")
    cache_materials = {
        "weapon": "iron_ore",
        "food": "hay",
        "tool": "diamond_ore",
        "potion": "purple_concrete" if "purple_concrete" in PALETTE else "quartz_block",
    }
    material = cache_materials.get(cache_type, "stone")
    world.set(cx, cy, base_z + 1, material)


def build_observation_post(world, cx, cy, base_z, size, rng):
    world.fill_box(cx - size // 2, cy - size // 2, base_z - 1, cx + size // 2, cy + size // 2, base_z - 1, "stone")
    for direction in range(4):
        angle = direction * math.pi / 2
        sentry_x = cx + int((size // 2 + 3) * math.cos(angle))
        sentry_y = cy + int((size // 2 + 3) * math.sin(angle))
        for z in range(base_z, base_z + 3):
            world.set(sentry_x, sentry_y, z, "brick")


def build_resource_processing_plant(world, cx, cy, base_z, resource_type, size, rng):
    if resource_type == "ore":
        for i in range(3):
            furnace_x = cx - size // 2 + i * (size // 3)
            build_furnace(world, furnace_x, cy, base_z, 8, rng)
    elif resource_type == "wood":
        for i in range(2):
            workbench_x = cx - size // 4 + i * (size // 2)
            build_crafting_table(world, workbench_x, cy, base_z)


def build_defensive_palisade_network(world, x1, y1, x2, y2, base_z, height, spacing, rng):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    if steps == 0:
        return
    for step in range(0, steps + 1, spacing):
        t = step / steps if steps > 0 else 0
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        build_defensive_palisade(world, x, y, x, y + 5, base_z, height, rng)




generate()
