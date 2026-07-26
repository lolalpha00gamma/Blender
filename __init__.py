bl_info = {
    "name": "Minecraft Terraforming System",
    "blender": (3, 0, 0),
    "version": (1, 0, 0),
    "location": "View3D > Sidebar > Minecraft",
    "description": "Generate Minecraft terrain and mega bases in Blender",
    "category": "Add Mesh",
}

import bpy
from bpy.types import Panel, Operator
from bpy.props import IntProperty, FloatProperty, EnumProperty
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from minecraft_terraform_megabase import (
    MinecraftTerraformingSystem, Vector3, Region,
    BlenderExporter, TerrainModifier, AdditionalFeatureGenerator,
    MegaBasePlanner
)

class MINECRAFT_OT_generate_terrain(Operator):
    bl_idname = "minecraft.generate_terrain"
    bl_label = "Generate Terrain"
    bl_options = {'REGISTER', 'UNDO'}

    chunk_range: IntProperty(name="Chunk Range", default=5, min=1, max=20)

    def execute(self, context):
        try:
            system = MinecraftTerraformingSystem(seed=42)
            system.generate_region(-self.chunk_range, -self.chunk_range,
                                  self.chunk_range, self.chunk_range)

            region = Region(Vector3(-160, 0, -160), Vector3(160, 150, 160))
            BlenderExporter.export_to_blender(system, region, batch_size=50)

            self.report({'INFO'}, f"Generated terrain with {len(system.all_blocks)} blocks")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}

class MINECRAFT_OT_generate_megabase(Operator):
    bl_idname = "minecraft.generate_megabase"
    bl_label = "Generate Mega Base"
    bl_options = {'REGISTER', 'UNDO'}

    size_x: IntProperty(name="Size X", default=200, min=50, max=500)
    size_z: IntProperty(name="Size Z", default=200, min=50, max=500)
    height: IntProperty(name="Height", default=50, min=20, max=150)

    def execute(self, context):
        try:
            system = MinecraftTerraformingSystem(seed=42)
            system.generate_region(0, 0, 10, 10)

            center = Vector3(80, 70, 80)
            system.build_mega_base_foundation(center, self.size_x, self.size_z)
            system.build_mega_base_walls(center, self.size_x, self.size_z, self.height)
            system.build_mega_base_roof(center, self.size_x, self.size_z)

            region = Region(Vector3(0, 0, 0), Vector3(160, 150, 160))
            BlenderExporter.export_to_blender(system, region, batch_size=100)

            self.report({'INFO'}, f"Generated mega base with {len(system.all_blocks)} blocks")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}

class MINECRAFT_OT_generate_forest(Operator):
    bl_idname = "minecraft.generate_forest"
    bl_label = "Generate Forest"
    bl_options = {'REGISTER', 'UNDO'}

    radius: IntProperty(name="Radius", default=50, min=10, max=200)
    density: FloatProperty(name="Tree Density", default=0.2, min=0.0, max=1.0)

    def execute(self, context):
        try:
            system = MinecraftTerraformingSystem(seed=42)
            system.generate_region(0, 0, 10, 10)

            modifier = TerrainModifier(system)
            modifier.create_forest(Vector3(50, 64, 50), self.radius, tree_density=self.density)

            region = Region(Vector3(0, 0, 0), Vector3(160, 150, 160))
            BlenderExporter.export_to_blender(system, region, batch_size=100)

            self.report({'INFO'}, f"Generated forest with {len(system.all_blocks)} blocks")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}

class MINECRAFT_PT_panel(Panel):
    bl_label = "Minecraft Terraforming"
    bl_idname = "MINECRAFT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Minecraft"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Terrain Generation", icon='WORLD')
        layout.operator("minecraft.generate_terrain")

        layout.separator()

        layout.label(text="Mega Base", icon='CUBE')
        layout.operator("minecraft.generate_megabase")

        layout.separator()

        layout.label(text="Nature", icon='LEAF_BONE')
        layout.operator("minecraft.generate_forest")

classes = (
    MINECRAFT_OT_generate_terrain,
    MINECRAFT_OT_generate_megabase,
    MINECRAFT_OT_generate_forest,
    MINECRAFT_PT_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
