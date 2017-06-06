import bpy


# todo: create the help string
help_string = \
    '''

    '''


# todo: document everything
class DrivenShapes(bpy.types.Panel):
    bl_idname = "driven_shapes"
    bl_label = "Driven Shapes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Shapes"
    
    def draw(self, context):
        layout = self.layout
        
        bone = None
        # Check if a bone is selected
        if context.active_pose_bone:
            bone = context.active_pose_bone
        ob = None
        
        # If two objects are selected one of these may be a mesh object
        if len(context.selected_objects) == 2:
            ob = [ob for ob in context.selected_objects if ob.type == "MESH"]
            if ob:
                ob = ob[0]
        # If not just check if the active object is a mesh
        else:
            if context.active_object:
                if context.active_object.type == "MESH":
                    ob = context.active_object
        
        # If find a mesh.
        # Draw its shape key list
        if ob:
            layout.label("Shape Keys")
            shapes = ob.data.shape_keys
            row = layout.row()
            row.template_list("MESH_UL_shape_keys", "", shapes, "key_blocks", ob, "active_shape_key_index", rows = 5)
            layout.template_list("OBJECT_ul_shape_groups", "", ob, "shape_groups", ob,
                                 "active_shape_group_index", rows = 4)
            layout.template_list("OBJECT_ul_shape_G_inside", "", ob, "shape_group_inside", ob,
                                 "active_sg_inside_index", rows = 4)
            
            # If only the mesh is selected draw some special operators
            if not bone:
                col = row.column(align = True)
                col.operator("object.shape_key_add", icon = 'ZOOMIN', text = "").from_mix = False
                col.operator("object.shape_key_remove", icon = 'ZOOMOUT', text = "")
                col.menu("MESH_MT_shape_key_specials", icon = 'DOWNARROW_HLT', text = "")
                col.separator()
                col.operator("object.shape_key_move", "", icon = "TRIA_UP").type = "UP"
                col.operator("object.shape_key_move", "", icon = "TRIA_DOWN").type = "DOWN"
        
        # Finally draw the addon operators
        if bone and ob:
            col = layout.column(align = True)
            col.operator("driven.splitshapes", "Splt active shape key")
            col.label("")
            
            col.label("Drivers")
            col.operator("driven.add_driver_to_shape_key", "Add driver to active shape key")
            row = col.row(align = True)
            row.operator("driven.add_driver_to_shape_key", "To X").axis = "LOC_X"
            row.operator("driven.add_driver_to_shape_key", "To Y").axis = "LOC_Y"
            row.operator("driven.add_driver_to_shape_key", "To Z").axis = "LOC_Z"
            col.separator()
            
            col.operator("driven.remove_driver_from_shape_key")


class OBJECT_ul_shape_groups(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            split = layout.split(0.7)
            split.prop(item, "name", "", emboss = False)


# todo: make everything above work
class OBJECT_ul_shape_G_inside(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            
            ob = None
            
            if len(context.selected_objects) in [1, 2]:
                if context.active_pose_bone:
                    ob = [ob for ob in context.selected_objects if ob.type == "MESH"]
                    if ob:
                        ob = ob[0]
                else:
                    ob = context.active_object if context.active_object.type == "MESH" else None
            if ob:
                split = layout.split(0.7)
                split.prop(item, "display_name", "", emboss = False)
                i = item.get_index(ob)
                key = ob.data.shape_keys.key_blocks[i]
                split.prop(key, "value", "")


class ShapeGroupInside(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty()
    display_name = bpy.props.StringProperty()
    
    def get_index(self, ob):
        if self.name in ob.data.shape_keys.key_blocks.keys():
            return ob.data.shape_keys.key_blocks.keys().index(self.name)
        else:
            return None


class ShapeGroup(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty()
    active_index = bpy.props.IntProperty()
    shapes = bpy.props.StringProperty()
    
    def get_shape_names(self):
        tokens = self.shapes.split("\t")
        return tokens if tokens != "" else None


def sg_inside_update(self, context):
    ob = self
    if ob:
        sg = ob.shape_groups[ob.active_shape_group_index]
        shape_names = sg.get_shape_names()
        ob.shape_group_inside.clear()
        
        for name in shape_names:
            if name:
                sgi = ob.shape_group_inside.add()
                sgi.name = name
                sgi.display_name = name
