# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# exports each selected object into its own file

bl_info = {
    "name": "UnwrapAxial",
    "description": " <E> for pie menu, <Alt + A> for area coverage. Command: md.uv_unwrap_axial, md.pie_uv_unwrap | axis = 0 - vertical, 1 - horizontal, -1 - both",
    "author": "Mihai Dobrin",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "View3D ",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "http://",
    "tracker_url": "http://"
                   "func=detail&aid=<number>",
    "category": "Tools"}


import bpy
import bmesh
from bpy.types import Menu, AddonPreferences, PropertyGroup
from bpy.props import EnumProperty
import rna_keymap_ui
#import os

#verbose = True

def kmi_props_setattr(kmi_props, attr, value):
    try:
        setattr(kmi_props, attr, value)
    except AttributeError:
        print("Warning: property '%s' not found in keymap item '%s'" %
              (attr, kmi_props.__class__.__name__))
    except Exception as e:
        print("Warning: %r" % e)

def main(context, axis):
    #os.system('cls') #

    obj = context.active_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    sel_faces = (f for f in bm.faces if f.select)

    if bpy.context.scene.tool_settings.use_uv_select_sync:
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.context.scene.tool_settings.use_uv_select_sync = False

    bpy.ops.uv.seams_from_islands()

    uv_layer = bm.loops.layers.uv.verify()
    #bm.faces.layers.tex.verify()
    bpy.ops.uv.seams_from_islands()

    # gel uvs list
    uvs = []
    i = 0
    for f in bm.faces:
        for loop in f.loops:
            uvs.append(loop)
            i += 1

    # get all pinned
    pinned_uvs = []

    for uv in uvs:
        if(uv[uv_layer].pin_uv):
            pinned_uvs.append(uv)
            print(pinned_uvs[-1])

    # get all selected loops
    ini_sel_uvs = []

    for uv in uvs:
        if(uv[uv_layer].select):
            ini_sel_uvs.append(uv)
            print(ini_sel_uvs[-1])


    # select all
    bpy.ops.uv.select_all(action='SELECT')


    # unpin all
    bpy.ops.uv.pin(clear=True)


    # pin if not in initial selection
    bpy.ops.uv.select_all(action='DESELECT')
    for uv in ini_sel_uvs:
        uv[uv_layer].select = True
        uv[uv_layer].select_edge = True

    bpy.ops.uv.select_all(action='INVERT')

    for uv in pinned_uvs:
        uv[uv_layer].select = True
        uv[uv_layer].select_edge = True
    bpy.ops.uv.pin(clear=False)

    # get ini selected co
    ini_sel_co = []
    for uv in ini_sel_uvs:
        x = (uv[uv_layer].uv[0], uv[uv_layer].uv[1])
        ini_sel_co.append(x)


    # unwrap
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.unwrap(margin=0.01)


    # change to initial co
    if(axis != -1):
        for uv, co in zip(ini_sel_uvs, ini_sel_co):
            uv[uv_layer].uv[axis] = co[axis]


    # unpin all
    bpy.ops.uv.pin(clear=True)

    # pin initial
    bpy.ops.uv.select_all(action='DESELECT')
    for uv in pinned_uvs:
        uv[uv_layer].select = True
        uv[uv_layer].select_edge = True
    bpy.ops.uv.pin(clear=False)

    # Eselect initial
    bpy.ops.uv.select_all(action='DESELECT')
    for uv in ini_sel_uvs:
        uv[uv_layer].select = True
        uv[uv_layer].select_edge = True

    bmesh.update_edit_mesh(me)


class UnwrapAxial(bpy.types.Operator):
    bl_idname = "md.uv_unwrap_axial"
    bl_label = "Unwrap Axial"
    bl_options = {'REGISTER', 'UNDO'}

    axis = bpy.props.IntProperty(name="Axis", description="0 - vertical, 1 - horizontal, -1 - both", default=0)

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')


    def execute(self, context):
        main(context, self.axis)
        return {'FINISHED'}

class RotateUV_CW(bpy.types.Operator):
    bl_idname = "md.uv_rotate_cw"
    bl_label = "Rotate UV"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        layout = self.layout
        bpy.ops.transform.rotate(value=1.5708, orient_axis='Z', orient_type='VIEW', orient_matrix=((-1, -0, -0), (-0, -1, -0), (-0, -0, -1)), orient_matrix_type='VIEW', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.21, use_proportional_connected=True, use_proportional_projected=False)
        #bpy.ops.transform.rotate(value=1.5708, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.235293)

        return {'FINISHED'}

class RotateUV_CCW(bpy.types.Operator):
    bl_idname = "md.uv_rotate_ccw"
    bl_label = "Rotate UV"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        layout = self.layout
        bpy.ops.transform.rotate(value=-1.5708, orient_axis='Z', orient_type='VIEW', orient_matrix=((-1, -0, -0), (-0, -1, -0), (-0, -0, -1)), orient_matrix_type='VIEW', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.21, use_proportional_connected=True, use_proportional_projected=False)

        #bpy.ops.transform.rotate(value=-1.5708, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.235293)

        return {'FINISHED'}

class RotateUV_CW45(bpy.types.Operator):
    bl_idname = "md.uv_rotate_cw45"
    bl_label = "Rotate CW 45"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        layout = self.layout

        bpy.ops.transform.rotate(value=0.785398, orient_axis='Z', orient_type='VIEW', orient_matrix=((-1, -0, -0), (-0, -1, -0), (-0, -0, -1)), orient_matrix_type='VIEW', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.21, use_proportional_connected=True, use_proportional_projected=False)

        #bpy.ops.transform.rotate(value=0.785398, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.0749715)

        return {'FINISHED'}

class RotateUV_CCW45(bpy.types.Operator):
    bl_idname = "md.uv_rotate_ccw45"
    bl_label = "Rotate CCW 45"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        layout = self.layout
        bpy.ops.transform.rotate(value=-0.785398, orient_axis='Z', orient_type='VIEW', orient_matrix=((-1, -0, -0), (-0, -1, -0), (-0, -0, -1)), orient_matrix_type='VIEW', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.21, use_proportional_connected=True, use_proportional_projected=False)

        #bpy.ops.transform.rotate(value=-0.785398, axis=(-0, -0, -1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.0749715)

        return {'FINISHED'}


class FlipUvHorizontal(bpy.types.Operator):
    bl_idname = "md.uv_flip_horizontal"
    bl_label = "Flip Horizontal"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        layout = self.layout

        bpy.ops.transform.resize(value=(-1, 1, 1))

        return {'FINISHED'}


class PIE_UV_UnwrapType(Menu):
    bl_idname = "md.pie_uv_unwrap"
    bl_label = "Unwrap type"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator("md.uv_rotate_ccw", text="Rotate 90 CCW")
        pie.operator("md.uv_rotate_cw", text="Rotate 90 CW")
        pie.operator("md.uv_unwrap_axial", text="Both").axis = -1
        pie.operator("md.uv_unwrap_axial", text="Vertical").axis = 0
        pie.operator("md.uv_flip_horizontal", text="Flip Horizontal")
        pie.operator("md.uv_unwrap_axial", text="Horizontal").axis = 1
        pie.operator("md.uv_rotate_ccw45", text="Rotate 45 CCW")
        pie.operator("md.uv_rotate_cw45", text="Rotate 45 CW")



class UvCoverage(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "md.get_uv_area"
    bl_label = "Get uv coverage"


    def poly_area2D(self, poly):
        total = 0.0
        N = len(poly)
        for i in range(N):
            v1 = poly[i]
            v2 = poly[(i+1) % N]
            total += v1[0]*v2[1] - v1[1]*v2[0]
        return abs(total/2)


    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        #os.system('cls') #

        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        uv_layer = bm.loops.layers.uv.verify()
        #bm.faces.layers.tex.verify()

        area = 0.
        for f in bm.faces:
            face = []
            for loop in f.loops:
                face.append(loop[uv_layer].uv)

            area_face = self.poly_area2D(face)
            area += area_face

        self.report({'INFO'}, 'UV Area Coverave:  %.2f' % (area))
        return {'FINISHED'}




addon_keymaps = []


def register():
    bpy.utils.register_class(RotateUV_CW45)
    bpy.utils.register_class(RotateUV_CCW45)
    bpy.utils.register_class(RotateUV_CW)
    bpy.utils.register_class(RotateUV_CCW)
    bpy.utils.register_class(UnwrapAxial)
    bpy.utils.register_class(UvCoverage)
    bpy.utils.register_class(FlipUvHorizontal)
    bpy.utils.register_class(PIE_UV_UnwrapType)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)

    kmi = km.keymap_items.new('md.get_uv_area', 'A', 'PRESS', alt=True)
    kmi = km.keymap_items.new('wm.call_menu_pie', 'E', 'PRESS')
    kmi_props_setattr(kmi.properties, 'name', 'md.pie_uv_unwrap')
    #kmi.properties.total = 4

    addon_keymaps.append(km)


def unregister():
    bpy.utils.unregister_class(RotateUV_CeeW45)
    bpy.utils.unregister_class(RotateUV_CCW45)
    bpy.utils.unregister_class(RotateUV_CW)
    bpy.utils.unregister_class(RotateUV_CCW)
    bpy.utils.unregister_class(UnwrapAxial)
    bpy.utils.unregister_class(UvCoverage)
    bpy.utils.unregister_class(FlipUvHorizontal)
    bpy.utils.unregister_class(PIE_UV_UnwrapType)


    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    # clear the list
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
