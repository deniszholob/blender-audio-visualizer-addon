#====================== BEGIN GPL LICENSE BLOCK ======================
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
#======================= END GPL LICENSE BLOCK ========================
#

bl_info = {
    "name": "Audio Visualizer",
    "author": "Denis Zholob (DDDGamer) | www.deniszholob.com | https://github.com/DDDGamer/blender-audio-visualizer-addon",
    "version": (0, 0, 1),
    "blender": (2, 68, 0),
    "location": "View3D > Add > Mesh",
    "category": "Add Mesh",
    "description": "Generates and animates visualizer bars",
    "warning": "Early Development",  # used for warning icon and text in addons panel
    "support": 'TESTING',
    "wiki_url": "https://github.com/DDDGamer/blender-audio-visualizer-addon",
    "tracker_url": "https://github.com/DDDGamer/blender-audio-visualizer-addon/issues"
}

if "bpy" in locals():
    import imp
    imp.reload(linearVisualizer)
else:
    from . import linearVisualizer
    
import bpy
#import os
from bpy.props import *
#import LinearVisualizer
#from addVisualizer.LinearVisualizer import * 


settings = [('0', 'Geometry', 'Build Geometry'),
            ('1', 'Animation', 'Animate Geometry')]

geoType = [('0', 'Grid', 'Glid Layout'),
           ('1', 'Ring', 'Ring Layout'),
           ('2', 'Spiral', 'Spiral Layout')]

frequencyScales = [('0', 'Linear', 'Linear Scale'),
                   ('1', 'Log', 'Logarithmic Scale'),
                   ('2', 'Exp', 'Exponential Scale')]
# class AddAnimationButton(bpy.types.Operator):
    # bl_idname = "btn.add_animation"
    # bl_label = "Add Animation"
    
    # def execute(self, context):
        # print("Hello")
        # return {'FINISHED'}


class AddVisualizer(bpy.types.Operator):
    def __init__(self):
        self.restoreDefaults()
    bl_idname = "mesh.vis_add"
    bl_label = "Visualizer: Add Visualizer"
    bl_options = {'REGISTER', 'UNDO'}
    
    animateString1 = "Animating..."
    animateString2 = "Animation Complete!"
    animateString = ""
    # End fnc __init__
    
    def update_vis(self, context):
        print("update_vis")
        self.do_update = True
    # End fnc
    
    def no_update_vis(self, context):
        print("no_update_vis")
        self.do_update = False
    # End fnc
        
    do_update = BoolProperty(name='Do Update',
        default=True, options={'HIDDEN'})
        
    update = BoolProperty(name='Auto Update',
        description='Enable/Disable automatic updating - useful if dealing with many nodes',
        default=False,)
    restoreDef = BoolProperty(name='Restore Defaults',
        description='Restore Default Settings',
        default=False,)
        
    # === Main Control === #
    chooseSet = EnumProperty(name='Settings',
        description='Choose the settings to modify',
        items=settings,
        default='0', update=no_update_vis)
    chooseGeoType = EnumProperty(name='Geometry Type',
        description='Choose Geometry Layout',
        items=geoType,
        default='0', update=update_vis)
        
    # === Animation Controls === #
    chooseFile = StringProperty( name="Music File",
        description = "Browse to the music file to animate to",
        default="",
        subtype = 'FILE_PATH')
    minFreq = IntProperty(name='Min Frequency',
        description='Lowest frequency to work from',
        min=0,
        max=100000,
        default=10, update=no_update_vis)
    maxFreq = IntProperty(name='Max Frequency',
        description='Highest frequency to work from',
        min=0,
        max=100000,
        default=20000, update=no_update_vis)
    freqScale = EnumProperty(name='Frequency Distribution Scale',
        description='Scale to determine frequency distribution for each node',
        items=frequencyScales,
        default='0', update=no_update_vis)
    animate = BoolProperty(name='Animate',
        description='Click to Animate the grid (bakes sound to f-curves)',
        default=False, update=update_vis)
    addSong = BoolProperty(name='Add Song',
        description='Add the song track into the sequencer',
        default=False, update=update_vis)
        
    # === Grid Controls === #
    rowNum = IntProperty(name='Rows',
        description='Number of Rows',
        min=1,
        max=500,
        default=1, update=update_vis)
    colNum = IntProperty(name='Columns',
        description='Number of Columns',
        min=1,
        max=500,
        default=9, update=update_vis)
    scalePivot = IntProperty(name='Scale Pivot',
        description='100% = scale from the node base up 0% = scale from middle -100% = scale from the top down',
        min=-100,
        max=100,
        default=100, update=update_vis)
    xSpace = FloatProperty(name='X Spacing',
        description='Horizontal Spacing between the nodes',
        min=0.0,
        max=250,
        default=0.5, update=update_vis)
    ySpace = FloatProperty(name='Y Spacing',
        description='Vertical Spacing between the nodes',
        min=0.0,
        max=250,
        default=0.5, update=update_vis)
    
    # === Node Scale Controls === #
    nodeScaleMultiplier = FloatProperty(name='Scale',
        description='Scale multiplier',
        min=0.0,
        max=10,
        default=0.5, update=update_vis)
    nodeHeight = FloatProperty(name='Height',
        description='Relative Height',
        min=0.0,
        max=500,
        default=3.0, update=update_vis)
    nodeThickness = FloatProperty(name='Thickness',
        description='Relative Thickness',
        min=0.0,
        max=500,
        default=0.5, update=update_vis)
    nodeWidth = FloatProperty(name='Width',
        description='Relative Width',
        min=0.0,
        max=500,
        default=1, update=update_vis)

    def restoreDefaults(self):
        # Main Control
        self.restoreDef = False
        self.do_update = True
        self.update = True
        self.chooseSet = '0'
        self.chooseGeoType = '0'
        # Animation Controls
        self.chooseFile = ""
        self.minFreq = 10
        self.maxFreq = 20000
        self.freqScale = '1'
        self.animate = False
        self.addSong = False
        # Grid Controls
        self.rowNum = 1
        self.colNum = 16
        self.scalePivot = 100
        self.xSpace = 0.5
        self.ySpace = self.xSpace
        # Node Scale Controls
        self.nodeScaleMultiplier = 0.5
        self.nodeHeight = 5
        self.nodeThickness = 1
        self.nodeWidth = 1
    # End fnc

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'
    # End fnc

    def draw(self, context):
        layout = self.layout

        # Branch specs
        #layout.label('Tree Definition')

        layout.prop(self, 'chooseSet')
        
        #layout.prop(self, 'do_update')
        layout.prop(self, 'update')
        print(self.chooseSet)
        
        if self.chooseSet == '0':
            #Box Layout
            box = layout.box()
            
            box.prop(self, 'chooseGeoType')
            
            #Grid Controls
            box.label("Grid Controls:")
            row = box.row()
            row.prop(self, 'rowNum')
            row.prop(self, 'ySpace')
            
            row = box.row()
            row.prop(self, 'colNum')
            row.prop(self, 'xSpace')
            
            box.prop(self, 'scalePivot')
            
            #Scale Controls
            box.label("Scale Controls:")
            box.prop(self, 'nodeScaleMultiplier')
            box.prop(self, 'nodeHeight')
            row = box.row()
            row.prop(self, 'nodeWidth')
            row.prop(self, 'nodeThickness')
            
        elif self.chooseSet == '1':
            #Box Layout
            box = layout.box()
            box.label("Add Animation:")
            box.prop(self, 'chooseFile')
            box.prop(self, 'addSong')
            box.prop(self, 'freqScale')
            box.prop(self, 'minFreq')
            box.prop(self, 'maxFreq')
            box.prop(self, 'animate')
            box.label(self.animateString)
        
        layout.prop(self, 'restoreDef')
            #box.operator(AddAnimationButton.bl_idname)
            #box.operator("btn.add_animation")
            #LinearVisualizer.animateVisualizer(self)
    # End fnc

    def execute(self, context):
        if(self.restoreDef):
            self.restoreDefaults()
        if(not self.do_update):
            print("Dont Update!")
            return {'PASS_THROUGH'}
        if(self.update):
            if(self.animate):
                self.animateString = self.animateString1
                print(self.animateString)
                #Do stuff here
                linearVisualizer.addVisualizer(self)
                self.animate = False
                print(self.animate)
                self.animateString = self.animateString2
                print(self.animateString)
                self.do_update = False
                print(self.do_update)
            else:
                linearVisualizer.addVisualizer(self)
        return {'FINISHED'}
    # End fnc
    
    def invoke(self, context, event):
        return self.execute(context)
    # End fnc
# End class


def menu_func(self, context):
    self.layout.operator(AddVisualizer.bl_idname, text="Add Visualizer", icon='PLUGIN')
# End fnc


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)
# End fnc


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
# End fnc


if __name__ == "__main__":
    register()
# End if
