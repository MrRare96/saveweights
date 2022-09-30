import bpy
import logging
import json
import bmesh


# Add-on informations
bl_info = {
    "name": "SaveWeights",
    "description": "Simple script to save and load weights in .json files.",
    "author": "MrRare",
    "version": (0, 0, 2),
    "blender": (3, 3, 0),
    "warning": "",
    "doc_url": "https://github.com/MrRare96/saveweights",
    "category": "User Interface",
}


# Retrieve weights of active object
def SAVEWEIGHT_StoreWeightsActiveObject():
    object = bpy.context.active_object
    name = object.name

    groups = {}
    mesh = bmesh.new()
    mesh.from_mesh(object.data)
    dvert_lay = mesh.verts.layers.deform.active
    for group in object.vertex_groups:
        weights = {}
        for vert in mesh.verts:
            dvert = vert[dvert_lay]
            if group.index in dvert:
                weights[vert.index] = dvert[group.index]
        groups[group.index] = {"name": group.name, "weights": weights}
    mesh.free()

    return {"object": name, "groups": groups}


# Apply weights based on json to the object defined in said json.
def SAVEWEIGHT_RestoreWeights(json):
    name = json["object"]
    object = bpy.context.scene.objects[name]

    if object is None:
        print(f"Could not find object: {name}")
        return False

    print(f"found object: {name}")

    for groupid, data in json["groups"].items():
        weights = data["weights"]
        group_name = data["name"]

        existing = object.vertex_groups.get(group_name)
        vertex_group = None
        vertexes = None
        if existing is not None:
            existing_vertexes = []
            group_index = object.vertex_groups.get(group_name).index
            for v in object.data.vertices:
                for g in v.groups:
                    if g.group == group_index:
                        if str(v.index) not in weights:
                            existing_vertexes += [v.index]
                            weights[str(v.index)] = g.weight

            object.vertex_groups.remove(existing)
            vertexes = existing_vertexes + [int(index) for index in weights.keys()]
        else:
            vertexes = [int(index) for index in weights.keys()]

        vertex_group = object.vertex_groups.new(name=group_name)
        vertex_group.add(vertexes, 0, 'ADD')

        group_index = object.vertex_groups.get(group_name).index

        object.data.update()

        for v in object.data.vertices:
            for g in v.groups:
                if g.group == group_index and str(v.index) in weights:
                    g.weight = weights[str(v.index)]

        object.data.update()

    return True


# The saveweight pannel
class SAVEWEIGHT_PT_MainPanel(bpy.types.Panel):
    bl_label =  "Save Weights"
    bl_region_type = "UI"
    bl_idname = "SAVEWEIGHT_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_category = "Save Weights"

    def draw(self, context):
        layout = self.layout
        self.layout.label(text=f"Active Object: {str(bpy.context.active_object.name)}")
        layout.operator("wm.saveweight_save_operator")
        layout.operator("wm.saveweight_load_operator")


class SAVEWEIGHT_OT_SaveOperator(bpy.types.Operator):
    bl_label = "Save Weights To File"
    bl_idname = "wm.saveweight_save_operator"

    filename: bpy.props.StringProperty(subtype="FILE_NAME")
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        weights = SAVEWEIGHT_StoreWeightsActiveObject()
        with open(self.filepath, "w") as outfile:
            outfile.write(json.dumps(weights))

        print(f"Succesfully Saved!")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filename = bpy.context.active_object.name + ".json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SAVEWEIGHT_OT_LoadOperator(bpy.types.Operator):
    bl_label = "Load Weights From File"
    bl_idname = "wm.saveweight_load_operator"

    filename: bpy.props.StringProperty(subtype="FILE_NAME")
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        with open(self.filepath, "r") as openfile:
            # Reading from json file
            json_object = json.load(openfile)
            if SAVEWEIGHT_RestoreWeights(json_object):
                print("Succesfully Applied!")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}




def register():
    bpy.utils.register_class(SAVEWEIGHT_PT_MainPanel)
    bpy.utils.register_class(SAVEWEIGHT_OT_SaveOperator)
    bpy.utils.register_class(SAVEWEIGHT_OT_LoadOperator)

def unregister():
    bpy.utils.unregister_class(SAVEWEIGHT_PT_MainPanel)
    bpy.utils.unregister_class(SAVEWEIGHT_OT_SaveOperator)
    bpy.utils.unregister_class(SAVEWEIGHT_OT_LoadOperator)

if __name__ == "__main__":
    register()
