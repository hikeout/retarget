
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
    "name": "Retarget topology",
    "description": "",
    "author": "Mihai Dobrin",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D ",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "http://",
    "tracker_url": "http://"
                   "func=detail&aid=<number>",
    "category": "Tools"}

import bpy
import mathutils
import math

def main(context):
    for ob in context.scene.objects:
        print(ob)

class TopologyRetarget(bpy.types.Operator):
    bl_idname = "md.retarget"
    bl_label = "RetargetTopology"
    bl_description = ""
    bl_options = {"REGISTER"}


    def unit_vector(self, vector):
        return vector / math.sqrt(sum(i**2 for i in vector))

    def angle_between(self, v1, v2):
        v1_u = self.unit_vector(v1)
        v2_u = self.unit_vector(v2)
        r = mathutils.Vector.dot(v1_u, v2_u)
        if(r > 1):
            r = 1
        if(r<-1):
            r = -1
        return math.acos(r)

    def rotate_point(self, point, angle, axis, pivot):
        R = mathutils.Matrix.Rotation(angle, 4, axis)
        T = mathutils.Matrix.Translation(pivot)
        M = T @ R @ T.inverted()
        return (M @ point)


    def retarget(self, target, retargetData,  source):

        i =  0
        while (i < len(retargetData)):

            sourceCoIni = mathutils.Vector(retargetData[i][1])
            sourceNormalIni = mathutils.Vector(retargetData[i][2])

            sourceCoFin = mathutils.Vector(source.data.vertices[retargetData[i][0]].co)
            sourceNormalFin = mathutils.Vector(source.data.vertices[retargetData[i][0]].normal)

            targetShapeKeyId = target.active_shape_key_index

            #translate
            tr = sourceCoFin - sourceCoIni
            target.data.shape_keys.key_blocks[targetShapeKeyId].data[i].co[0] = target.data.vertices[i].co[0] + sourceCoFin[0] - sourceCoIni[0]
            target.data.shape_keys.key_blocks[targetShapeKeyId].data[i].co[1] = target.data.vertices[i].co[1] + sourceCoFin[1] - sourceCoIni[1]
            target.data.shape_keys.key_blocks[targetShapeKeyId].data[i].co[2] = target.data.vertices[i].co[2] + sourceCoFin[2] - sourceCoIni[2]



            #rotate
            angle = self.angle_between(sourceNormalIni, sourceNormalFin)
            axis  = mathutils.Vector.cross(sourceNormalIni, sourceNormalFin)
            newCo = self.rotate_point(target.data.shape_keys.key_blocks[targetShapeKeyId].data[i].co, angle, axis, sourceCoFin)
            target.data.shape_keys.key_blocks[targetShapeKeyId].data[i].co[0] = newCo[0]
            target.data.shape_keys.key_blocks[targetShapeKeyId].data[i].co[1] = newCo[1]
            target.data.shape_keys.key_blocks[targetShapeKeyId].data[i].co[2] = newCo[2]

            i += 1



    def getObjects(self, ):

        if(len(bpy.context.selectable_objects) < 3):
            return None

        sourceObj = bpy.context.active_object
        targetObj = []
        lowObj    = []

        for selObj in bpy.context.selected_objects:
            print(selObj.name)
            print(sourceObj.name)
            print("  ")
            if(len(selObj.data.vertices) == len(sourceObj.data.vertices)):
                if(selObj.name != sourceObj.name):
                    targetObj.append(selObj)
            else:
                lowObj.append(selObj)

        print("Source:")
        print(sourceObj)
        print("Target:")
        print(targetObj)
        print("Low:")
        print(lowObj)

        return (sourceObj, targetObj, lowObj)


    def getRetargetData(self, source, target):

        mesh = source.data
        size = len(mesh.vertices)
        kd = mathutils.kdtree.KDTree(size)

        for i, v in enumerate(mesh.vertices):
            kd.insert(v.co, i)

        kd.balance()

        retargetData =  []

        for v in target.data.vertices:

            (c, id, dst) = kd.find(v.co)
            n = source.data.vertices[id].normal

            retargetData.append((id , c, n))

        return retargetData


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        retargetObjs = self.getObjects()

        for lowObj in retargetObjs[2]:
            retargetData =  self.getRetargetData(retargetObjs[0], lowObj)

            if(lowObj.data.shape_keys ==  None):
                lowObj.shape_key_add(from_mix=True)
                lowObj.data.shape_keys.key_blocks[0].name =  "Basis"

            for source in retargetObjs[1]:
                lowObj.shape_key_add(from_mix=False)
                lowObj.data.shape_keys.key_blocks[-1].value =  1.0
                lowObj.data.shape_keys.key_blocks[-1].name =  source.name
                lowObj.data.shape_keys.key_blocks[-1].mute =  True
                lowObj.active_shape_key_index = len(lowObj.data.shape_keys.key_blocks) - 1

                self.retarget(lowObj, retargetData,  source)

        print("END")

        return {"FINISHED"}




def register():
    bpy.utils.register_class(TopologyRetarget)


def unregister():
    bpy.utils.unregister_class(TopologyRetarget)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.object.simple_operator()
