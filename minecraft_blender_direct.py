import bpy
import math
import random
from enum import Enum
from dataclasses import dataclass

class BlockType(Enum):
    STONE = 1
    DIRT = 5
    GRASS_BLOCK = 7
    WATER = 29
    OAK_LOG = 11
    OAK_LEAVES = 19
    SAND = 25
    OBSIDIAN = 48
    DARK_OAK_PLANKS = 37

@dataclass
class Vector3:
    x: float = 0
    y: float = 0
    z: float = 0

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def distance(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

class SimpleMinecraftGenerator:
    def __init__(self):
        self.blocks = {}
        self.materials = {}

    def create_material(self, name, color):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = color
        return mat

    def create_cube(self, x, y, z, material):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
        obj = bpy.context.active_object
        obj.data.materials.append(material)
        return obj

    def generate_flat_terrain(self, width=50, depth=50, height_base=5):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        print("Generating terrain...")

        grass_mat = self.create_material("grass", (0.2, 0.6, 0.2, 1.0))
        dirt_mat = self.create_material("dirt", (0.4, 0.3, 0.2, 1.0))
        stone_mat = self.create_material("stone", (0.5, 0.5, 0.5, 1.0))

        for x in range(-width//2, width//2, 2):
            for z in range(-depth//2, depth//2, 2):
                for y in range(0, height_base):
                    if y < height_base - 1:
                        mat = stone_mat if y < 2 else dirt_mat
                    else:
                        mat = grass_mat

                    self.create_cube(x, y, z, mat)

        print(f"✓ Terrain generated ({width}x{depth}x{height_base} blocks)")

    def generate_mega_base(self, center_x=0, center_z=0, size=30):
        print("Generating mega base...")

        obsidian_mat = self.create_material("obsidian", (0.1, 0.0, 0.2, 1.0))
        planks_mat = self.create_material("dark_oak_planks", (0.4, 0.3, 0.15, 1.0))

        base_y = 5

        for x in range(center_x - size, center_x + size, 1):
            for z in range(center_z - size, center_z + size, 1):
                dist = math.sqrt((x - center_x)**2 + (z - center_z)**2)

                if dist <= size:
                    self.create_cube(x, base_y, z, obsidian_mat)

                    if dist > size - 2:
                        for y in range(base_y + 1, base_y + 8):
                            self.create_cube(x, y, z, planks_mat)

        print(f"✓ Mega base generated ({size*2}x{size*2} blocks)")

    def generate_forest(self, center_x=0, center_z=0, radius=30, tree_count=20):
        print("Generating forest...")

        log_mat = self.create_material("oak_log", (0.5, 0.4, 0.2, 1.0))
        leaf_mat = self.create_material("oak_leaves", (0.2, 0.5, 0.2, 1.0))

        random.seed(42)

        for _ in range(tree_count):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, radius)
            tx = center_x + int(dist * math.cos(angle))
            tz = center_z + int(dist * math.sin(angle))

            tree_height = random.randint(6, 12)

            for y in range(5, 5 + tree_height):
                self.create_cube(tx, y, tz, log_mat)

            foliage_radius = tree_height // 3
            for fx in range(tx - foliage_radius, tx + foliage_radius + 1):
                for fz in range(tz - foliage_radius, tz + foliage_radius + 1):
                    for fy in range(5 + tree_height - foliage_radius, 5 + tree_height + 2):
                        dist_to_center = math.sqrt((fx - tx)**2 + (fz - tz)**2 + (fy - 5 - tree_height) ** 2)
                        if dist_to_center <= foliage_radius and random.random() > 0.3:
                            self.create_cube(fx, fy, fz, leaf_mat)

        print(f"✓ Forest generated ({tree_count} trees)")

    def generate_lake(self, center_x=0, center_z=0, radius=20):
        print("Generating lake...")

        water_mat = self.create_material("water", (0.2, 0.5, 0.8, 0.7))

        for x in range(int(center_x - radius), int(center_x + radius) + 1):
            for z in range(int(center_z - radius), int(center_z + radius) + 1):
                dist = math.sqrt((x - center_x)**2 + (z - center_z)**2)
                if dist <= radius:
                    for y in range(3, 6):
                        self.create_cube(x, y, z, water_mat)

        print(f"✓ Lake generated (radius {radius})")

if __name__ == "__main__":
    try:
        generator = SimpleMinecraftGenerator()

        print("=" * 60)
        print("MINECRAFT TERRAFORMING SYSTEM - BLENDER")
        print("=" * 60)

        print("\n[1/4] Generating flat terrain...")
        generator.generate_flat_terrain(width=80, depth=80, height_base=6)

        print("\n[2/4] Generating mega base...")
        generator.generate_mega_base(center_x=0, center_z=0, size=15)

        print("\n[3/4] Generating forest...")
        generator.generate_forest(center_x=-40, center_z=0, radius=20, tree_count=15)

        print("\n[4/4] Generating lake...")
        generator.generate_lake(center_x=40, center_z=0, radius=15)

        print("\n" + "=" * 60)
        print("✓ GENERATION COMPLETE!")
        print("=" * 60)
        print("\nObjects created in your scene!")
        print("You can now manipulate them in Blender.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

generator = SimpleMinecraftGenerator()
generator.generate_flat_terrain(width=80, depth=80, height_base=6)
generator.generate_mega_base(center_x=0, center_z=0, size=15)
generator.generate_forest(center_x=-40, center_z=0, radius=20, tree_count=15)
generator.generate_lake(center_x=40, center_z=0, radius=15)
