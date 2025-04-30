bl_info = {
    "name": "Slice 3D Mesh into 2D Curves",
    "author": "Yuan Hessed Vasig",
    "description": "Mesh Slicer add-on help to slice any 3D mesh whether it is high or low poly and give the output as SVG curves which can be used in CNC machines (Laser, Router or Plasma). The add-on is specialized to create parametric design slices from exciting object. ",
    "blender": (2, 90, 0),
    "version": (1, 0, 1),
    "location": "3D View > UI > Mesh Slicer",
    "warning": "",
    "category": "Mesh Slicer"
}
import bpy
from bpy.props import EnumProperty
class CurveExportSVGPanel(bpy.types.Panel):
    """Creates a Panel in the data context of the properties editor"""

    bl_label = "Mesh Slicer"
    bl_idname = 'DATA_PT_slicing'

    """Display example preferences"""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Mesh Slicer"

    def draw(self, context):
        """Draws the Export SVG Panel"""
        scene = context.scene
        layout = self.layout
        selected_3d_object = False

        for obj in context.selected_objects:
            if len(context.selected_objects) == 1:
                selected_3d_object = True

        if selected_3d_object:
            row = layout.row()
            row.prop(scene, 'export_number_slices')

            row = layout.row()
            row.prop(scene, 'export_space_slices')

            row = layout.row()
            row.operator('mesh.slice', text="SLICE", icon='FILE_VOLUME').action = 'SLICE'
        else:
            layout.label(icon='ERROR', text="Select one 3D object to slice")

        row = layout.row()
        row.operator('mesh.slice', text="APPLY",icon='CHECKMARK').action = 'APPLY'

        #row = layout.row()
        #row.operator('mesh.slice', text="Clear").action = 'CLEAR'

        row = layout.row()
        row.prop(scene, 'export_svg_output',text='')

        row = layout.row()
        row.operator('mesh.slice', text="Export SVG", icon='DISK_DRIVE').action = 'EXPORT'

        if len(context.selected_objects) == 0:
            layout.label(
                icon='ERROR', text="Notice: only one selected 3D Object can be sliced")


class DATA_OT_MeshToCurve(bpy.types.Operator):

    bl_label = "Slice Mesh"
    bl_idname = 'mesh.slice'

    action: EnumProperty(
        items=[
            ('SLICE', 'slice mesh', 'slice mesh'),
            ('APPLY', 'slice mesh', 'slice mesh'),
            ('EXPORT', 'slice mesh', 'slice mesh'),
            ('CLEAR', 'slice mesh', 'slice mesh')
        ]
    )

    def execute(self, context):
        """Exports selected 2D Curves to SVG file"""
        scene = context.scene
        numberSlices = scene.export_number_slices
        spaceBetweenSlices = scene.export_space_slices

        if self.action == 'SLICE':
            Slice(numberSlices, spaceBetweenSlices)
        elif self.action == 'APPLY':
            Apply()
        elif self.action == 'EXPORT':
            Export(scene.export_svg_output)
        elif self.action == 'CLEAR':
            Clear()

        return {'FINISHED'}


slicers = []


def CreateSlicer(iter, move):
    # create a slicer inside a loop then select the object to be sliced
    dim = bpy.context.selected_objects[0].dimensions
    scale = bpy.context.selected_objects[0].scale
    location = bpy.context.selected_objects[0].location
    name1 = bpy.context.selected_objects[0].name

    bpy.ops.mesh.primitive_plane_add(
        enter_editmode=False, align='WORLD',size=5, location=(0, 0, 0), scale=(1, 1, 1))
    bpy.ops.transform.rotate(value=1.5708, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(
        False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.21, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.transform.resize(value=(dim[0], dim[1]/2, dim[2]), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True,
                             use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.21, use_proportional_connected=False, use_proportional_projected=False)

    name2 = "Slicer"+str(iter)
    bpy.context.selected_objects[0].name = name2

    bpy.ops.object.select_all(action='DESELECT')

    for o in bpy.data.objects:
        if o.name in (name1, name2):
            o.select_set(True)

    bpy.ops.object.align(bb_quality=True, align_mode='OPT_1',
                         relative_to='OPT_4', align_axis={'X'})
    bpy.ops.object.align(bb_quality=True, align_mode='OPT_2',
                         relative_to='OPT_4', align_axis={'Y'})
    bpy.ops.object.align(bb_quality=True, align_mode='OPT_2',
                         relative_to='OPT_4', align_axis={'Z'})

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[name2].select_set(True)

    bpy.ops.transform.translate(value=(move[0], move[1], move[2]), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(
        True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.21, use_proportional_connected=False, use_proportional_projected=False, release_confirm=True)

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[name1].select_set(True)

    return name2


def Slice(number, space):
    slicers = []
    # get the current object
    if bpy.context.active_object == None:
        print("Please select an object")

    # global parameters
    numberOfSlices = number+1
    initialPosition = 0.001+1
    obj = bpy.context.selected_objects[0].name

    # Calculate space between slices based on X size of the object
    spaceBetweenSlices = bpy.context.selected_objects[0].dimensions[0] / numberOfSlices

    # ---- Slicer creation
    for i in range(0, numberOfSlices):
        if i == 0:
            slicers.append(CreateSlicer(i, (initialPosition, 0, 0)))
            continue
        slicers.append(CreateSlicer(i, (i * spaceBetweenSlices, 0, 0)))

    # ---- Add boolean modifier
    for name in slicers:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[name].select_set(True)

        ob = bpy.context.scene.objects[name]

        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_add(type='BOOLEAN')
        bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'

        oldVersion = [2, 90, 0]
        version = bpy.app.version_string.split('.')
        if(int(version[0]) > oldVersion[0] or int(version[1]) > oldVersion[1] or int(version[2]) > oldVersion[2]):
            bpy.context.object.modifiers["Boolean"].solver = 'FAST'

        bpy.context.object.modifiers["Boolean"].object = bpy.data.objects[obj]

    # move slices to collection
    for o in slicers:
        bpy.data.objects[o].select_set(True)

    bpy.ops.object.move_to_collection(
        collection_index=0, is_new=True, new_collection_name="SlicesCollection")


def Apply():
    #for obj in bpy.data.collections["SlicesCollection"].all_objects:
        #obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier="Boolean")
        bpy.ops.object.convert(target='CURVE')


def Clear():
    if(bpy.data.collections["SlicesCollection"] != None):
        slicers = []
        bpy.data.collections.remove(bpy.data.collections["SlicesCollection"])


def Export(location):
    # Scale factor based on unit settings
    scaleFactor = 1
    if bpy.context.scene.unit_settings.length_unit == "METERS":
        scaleFactor = 1000
    elif bpy.context.scene.unit_settings.length_unit == "CENTIMETERS":
        scaleFactor = 100
    elif bpy.context.scene.unit_settings.length_unit == "MILLIMETERS":
        scaleFactor = 1

    # Calculate the viewport dimension
    maxX = float('-inf')
    maxZ = float('-inf')
    minX = float('inf')
    minZ = float('inf')
    
    # First pass to calculate bounds
    for obj in bpy.context.selected_objects:
        if obj.type == "CURVE":
            for spline in obj.data.splines:
                for point in spline.points:
                    # Transform point to world space
                    world_co = obj.matrix_world @ point.co.to_3d()
                    x = world_co.x * scaleFactor
                    z = world_co.z * scaleFactor
                    maxX = max(maxX, x)
                    maxZ = max(maxZ, z)
                    minX = min(minX, x)
                    minZ = min(minZ, z)

    # Calculate dimensions
    width = (maxX - minX)
    height = (maxZ - minZ)

    temp = ""
    for obj in bpy.context.selected_objects:
        if obj.type == "CURVE":
            temp += f'<g id="{obj.name}">\n'

            for spline in obj.data.splines:
                points = []
                for point in spline.points:
                    # Transform point to world space
                    world_co = obj.matrix_world @ point.co.to_3d()
                    x = (world_co.x * scaleFactor) - minX
                    # Use Z coordinate for height and flip for SVG coordinate system
                    z = height - ((world_co.z * scaleFactor) - minZ)
                    points.append([x, z])

                if points:
                    temp += '<path style="fill:none;stroke:black;stroke-width:1;" d="'
                    temp += f"M {points[0][0]:.3f} {points[0][1]:.3f} "
                    for point in points[1:]:
                        temp += f"L {point[0]:.3f} {point[1]:.3f} "
                    temp += 'Z"/>\n'
            temp += "</g>\n"

    if bpy.context.selected_objects:
        content = '<?xml version="1.0" encoding="utf-8"?>\n'
        content += f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" '
        content += f'viewBox="0 0 {width:.3f} {height:.3f}" '
        content += f'width="{width:.3f}mm" height="{height:.3f}mm">\n'
        content += temp
        content += "</svg>"

        if not location.endswith('.svg'):
            location += '.svg'

        with open(location, 'w') as f:
            f.write(content)


class ObjectThicknessPanel(bpy.types.Panel):
    bl_label = "Thickness"
    bl_idname = "OBJECT_PT_object_thickness"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mesh Slicer"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        obj = context.object

        thickness_modifier = obj.modifiers.get("Thickness")
        thickness_enabled = thickness_modifier is not None

        row = layout.row()
        thickness_checkbox = row.operator("object.toggle_thickness_modifier", text="Enable Thickness" if not thickness_enabled else "Disable Thickness")
        thickness_checkbox.object_name = obj.name

        if thickness_enabled:
            row = layout.row()
            row.prop(thickness_modifier, "thickness")

class ToggleThicknessModifierOperator(bpy.types.Operator):
    bl_idname = "object.toggle_thickness_modifier"
    bl_label = "Toggle Thickness Modifier"
    object_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.object_name)
        if obj:
            thickness_modifier = obj.modifiers.get("Thickness")

            if thickness_modifier:
                obj.modifiers.remove(thickness_modifier)
            else:
                thickness_modifier = obj.modifiers.new("Thickness", 'SOLIDIFY')
                thickness_modifier.thickness = 0.1

        return {'FINISHED'}
classes = (ObjectThicknessPanel, ToggleThicknessModifierOperator)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()    
def register():
    """Registers curve_to_svg Add-on"""
    bpy.types.Scene.export_number_slices = bpy.props.IntProperty(
        name="Slices number",
        description="Define the number of slices will be applied on your mesh.",
        default=5,
        min=5)

    bpy.types.Scene.export_space_slices = bpy.props.FloatProperty(
        name="Gap",
        description="Define the space between the slices.",
        default=0.01, min=0.0001)

    bpy.types.Scene.export_svg_output = bpy.props.StringProperty(
        name="Output",
        description="Path to output file",
        default="output",
        subtype='FILE_PATH')

    bpy.utils.register_class(DATA_OT_MeshToCurve)
    bpy.utils.register_class(CurveExportSVGPanel)


def unregister():
    """Unregisters curve_to_svg Add-on"""

    bpy.utils.unregister_class(CurveExportSVGPanel)
    bpy.utils.unregister_class(DATA_OT_MeshToCurve)

    del bpy.types.Scene.export_number_slices
    del bpy.types.Scene.export_space_slices
    del bpy.types.Scene.export_svg_output




    
