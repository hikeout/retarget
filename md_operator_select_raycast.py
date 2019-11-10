import bpy
import bmesh
from mathutils import kdtree, Vector, Matrix
from bpy_extras import view3d_utils

MAX_SEARCH = 15

def get_ray_hit(context, x, y):
    current_obj = context.object
    current_obj_matrix = current_obj.matrix_world
    current_obj_matrix_inv = current_obj_matrix.inverted()
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = x, y

    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    ray_target = ray_origin + view_vector

    def visible_objects_and_duplis():
        depsgraph = context.evaluated_depsgraph_get()
        for dup in depsgraph.object_instances:
            if dup.is_instance:  # Real dupli instance
                obj = dup.instance_object
                yield (obj)
            else:  # Usual object
                obj = dup.object
                yield (obj)

    def obj_ray_cast(obj):
        matrix = obj.matrix_world
        matrix_inv = matrix.inverted()
        ray_origin_obj = matrix_inv @ ray_origin
        ray_target_obj = matrix_inv @ ray_target
        ray_direction_obj = ray_target_obj - ray_origin_obj


        success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

        #print("success: " + str(success) + " | " + str(obj.name))

        if success:
            return location, normal, face_index, matrix, matrix_inv
        else:
            return None, None, None, None, None

    best_length_squared = float("inf")
    best_obj = None
    best_normal = None
    best_face_index = -1
    best_location   = None

    for obj in visible_objects_and_duplis():
        if obj.type == 'MESH' and obj.name != current_obj.name and len(obj.data.polygons) > 0 :
            hit, normal, face_index, matrix, matrix_inv = obj_ray_cast(obj)
            if hit is not None:
                hit_world = matrix @ hit
                #context.scene.cursor.location = hit_world
                length_squared = (hit_world - ray_origin).length_squared
                if best_obj is None or length_squared < best_length_squared:
                    #print("--->")
                    best_length_squared = length_squared
                    best_obj = obj
                    best_location = hit


    if best_obj is not None: # and best_obj.matrix_world != None:
        #print("--->*")
        best_location = best_obj.matrix_world @ best_location
        best_location = current_obj_matrix_inv @ best_location

        return  best_location
    else:
        return None



class MdSelectRaycast(bpy.types.Operator):
    bl_idname = "mdutils.select_raycast"
    bl_label = "Select Raycast"

    x : bpy.props.IntProperty()
    y : bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        hit_location = get_ray_hit(context, self.x, self.y)

        #print("HIT: " + str(hit_location))
        if(hit_location != None):

            bm = bmesh.from_edit_mesh(context.object.data)

            if hasattr(bm.verts, "ensure_lookup_table"):
                bm.verts.ensure_lookup_table()

            kd = kdtree.KDTree(len(bm.verts))
            for i, v in enumerate(bm.verts):
                kd.insert(v.co, i)
            kd.balance()
            kd_closest_vertices = kd.find_n(hit_location, MAX_SEARCH)

            for v in kd_closest_vertices:
                if(bm.verts[v[1]].select == False):
                    #print("closest index: " + str(v[1]))
                    bm.verts[v[1]].select = True
                    break
            bmesh.update_edit_mesh(context.object.data)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.x = event.mouse_region_x
        self.y = event.mouse_region_y
        return self.execute(context)


def register():
    bpy.utils.register_class(MdSelectRaycast)


def unregister():
    bpy.utils.unregister_class(MdSelectRaycast)


if __name__ == "__main__":
    register()
