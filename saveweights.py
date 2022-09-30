import bpy
import logging
import json
import bmesh


# Add-on informations
bl_info = {
    "name": "SaveWeights",
    "description": "Simple script to save and load weights in .json files.",
    "author": "MrRare",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "warning": "",
    "doc_url": "https://github.com/MrRare96/saveweights",
    "category": "User Interface",
}


# Retrieve weights of active object
def SAVEWEIGHT_StoreWeightsActiveObject():
    object = bpy.context.active_object
    name = object.name
    group_index = object.vertex_groups.active_index
    
    mesh = bmesh.new()
    mesh.from_mesh(object.data)
    dvert_lay = mesh.verts.layers.deform.active
    
    weights = {}
    for vert in mesh.verts:
        dvert = vert[dvert_lay]
        if group_index in dvert:
            weights[vert.index] = dvert[group_index]
            
    mesh.free()
            
    return {"object": name, "active_index": group_index, "weights": weights}


# Apply weights based on json to the object defined in said json.
def SAVEWEIGHT_RestoreWeights(json):
    name = json["object"]
    weights = json["weights"]
    object = bpy.context.scene.objects[name]
    
    if object is None:
        print(f"Could not find object: {name}")
        return False
    print(f"found object: {name}")
    
    group_index = json["active_index"]
    mesh = bmesh.new()
    mesh.from_mesh(object.data)
    dvert_lay = mesh.verts.layers.deform.active
    
    for vert in mesh.verts:
        dvert = vert[dvert_lay]
        if group_index in dvert:
            dvert[group_index] = weights[str(vert.index)]
        
    mesh.to_mesh(object.data)
    mesh.free()   
    
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
