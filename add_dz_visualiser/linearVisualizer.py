import os
import bpy
#import Blender
import math


class ShapeKey(object):
    Cube = 0
    Cylinder = 1
# End class


class GridKey(object):
    Square = 0
    Circle = 1
    SpiralSquare = 2
    SpiralCircle = 3
# End class


# Multipurpouse xyz object
class Coordinate3D(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    # End fnc __init__
# End class


# Node in a grid
class Node(object):
    def __init__(self, width, height, thickness, pivot):
        self.size = Coordinate3D(width, thickness, height) # width is unit length 1
        self.pivot = pivot/-100                            # convert from % to decimal and invert
    # End fnc __init__

    def scale(self, scale):
        self.size.x *= scale
        self.size.y *= scale
        self.size.z *= scale
    # End fnc
# End class


class Frequency(object):
    def __init__(self, songPath, minF, maxF, scaleType, nodeNum):
        self.songPath = songPath
        self.minF = minF
        self.maxF = maxF
        self.scaleType = scaleType
        self.slope = self.calcSlope(nodeNum)
    # End fnc __init__

    def calcSlope(self, nodeNum):
        if(self.scaleType == '0'):                          # linear scale
            return (self.maxF-self.minF)/nodeNum            # m = (y2-y1)/(x2-x1), x1=0
        elif(self.scaleType == '1'):                        # log scale
            return math.log10(self.maxF-self.minF)/nodeNum  # m = log(y2-y1)/(x2-x1), x1=0
        elif(self.scaleType == '2'):                        # exp scale
            return (self.maxF-self.minF)/(2**nodeNum)       # m = (y2-y1)/(2^(x2-x1)), x1=0
    # End fnc

    def getNodeFrequency(self, nodePos):
        if(self.scaleType == '0'):                          # linear scale
            return self.slope*nodePos + self.minF           # F(x) = m*x + b
        elif(self.scaleType == '1'):                        # log scale
            return 10**(self.slope*nodePos) + self.minF     # F(x) = 10^(m*x) + b
        elif(self.scaleType == '2'):                        # exp scale
            return self.slope*(2**nodePos)                  # F(x) = m*(2^n)
    # End fnc
# End class



# Grid object definition
class Grid(object):
    def __init__(self, scale, rows, columns, spacingX, spacingY, node):
        self.rows = rows
        self.columns = columns
        self.spacing = Coordinate3D(spacingX*scale, spacingY*scale, 0) # not using z coordinate here
        self.node = node.scale(scale) # scale the input node appropriately
    # End fnc __init__

    def getNodeNum(self):
        return self.rows*self.columns
    # End fnc
# End class


# The visualizer class
class Visualizer(object):
    def __init__(self, node, grid, frequency, animation, addSong):
        self.node = node
        self.grid = grid
        self.animate = animation
        self.freq = frequency
        if(animation and addSong):
            # bpy.ops.sequencer.sound_strip_add(filepath = self.freq.songPath, frame_start=1) # Doesnt work, b/c of operator poll
            if not bpy.context.scene.sequence_editor:
                bpy.context.scene.sequence_editor_create()
                soundstrip = bpy.context.scene.sequence_editor.sequences.new_sound(name = self.freq.songPath, filepath = self.freq.songPath, channel=3, frame_start=1)
    # End fnc __init__

    def genGrid(self):
        # define shortcuts
        node = self.node
        grid = self.grid
        groupName = "NodeGroup"
        # animation = self.animation
        
        # Start at frame 0
        bpy.context.scene.frame_current = 0

        # Set a starting position to start the grid on 
        # (So the grid is centered about the origin)
        totXlen = grid.columns * node.size.x + (grid.columns-1) * grid.spacing.x
        totYlen = grid.rows * node.size.y + (grid.rows-1) * grid.spacing.y
        
        xStart = ((totXlen/2.0) - (node.size.x/2.0)) * (-1)
        yStart = ((totYlen/2.0) - (node.size.y/2.0)) * (-1)

        loc = Coordinate3D(xStart, yStart, 0)
        print("Starting x: %1.2f" %(loc.x))
        print("Starting y: %1.2f" %(loc.y))
        print("")
        
        # if the thinkness is < .001 make it a plane  of a cube
        if(node.size.y < 0.001):
            # Add a Plane Primitive
            bpy.ops.mesh.primitive_plane_add(
                radius = 0.5, # Make the plane 1x1x0 not 2x2x0
                location = (0,0,node.pivot * -0.5)
            )
            # Rotate the plane
            bpy.ops.transform.rotate(
                value = 90*(math.pi/180), axis = (1,0,0),
                constraint_axis = (True, False, False)
            )
            bpy.ops.object.transform_apply(rotation = True) # Apply the rotation
        else:
            # Add a Cube Primitive
            bpy.ops.mesh.primitive_cube_add(
                radius=0.5, # Make the cube 1x1x1 not 2x2x2
                location = (0,0,node.pivot * -0.5)
            )
        # Name the Cube        
        bpy.context.active_object.name = "VisNode.Base"

        ### Set the cube's origin at its base ###
        bpy.context.scene.cursor_location = bpy.context.active_object.location  # Set 3D cursor at objects location
        bpy.context.scene.cursor_location.z += (node.pivot*0.5)                 # Movie the cursor down on the z axis by 1
        bpy.ops.object.origin_set(type = "ORIGIN_CURSOR")                       # Set the cube's origin at the cursors location
        #### -------------------------------- ###
        
        ### Scale the cube base on node size ###
        bpy.context.active_object.scale=(
            node.size.x,
            node.size.y,
            node.size.z
        )
        bpy.ops.object.transform_apply(scale = True) # Apply the scale
        #### -------------------------------- ###
        
        # Create a group from the primitive cube
        if(not groupName in bpy.data.groups):
            print("Group doesnt exist!")
            bpy.ops.group.create(name=groupName)
        else:
            print("Group exists...")
            bpy.ops.object.group_link(group=groupName)
        # Move the base out of the way to last layer
        bpy.ops.object.move_to_layer(
            layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True)
        )
        
        # Build the grid of Group objects
        # bpy.context.area.type = "VIEW_3D" # make sure we are in the 3d viewport to add nodes
        for r in range (0, grid.rows):
            print("CURRENT Row: (%i)" % (r))
            for c in range (0, grid.columns):
                print("CURRENT Position: (%1.2f,%1.2f)" % (loc.x,loc.y))
                # Add a group node instance at curent pos
                bpy.ops.object.group_instance_add(
                    name = groupName,
                    location = (
                        loc.x,
                        loc.y,
                        loc.z
                    )
                )
                # Name the new node
                bpy.context.active_object.name = "VisNode.{}-{}".format(r, c)
                
                # Add animation if user clicks to
                if(self.animate):
                    if(len(self.freq.songPath) == 0):
                        raise ValueError("No song file selected!")
                        print("No song file selected!")
                    elif(not os.path.exists(self.freq.songPath)):
                        raise FileNotFoundError("Invalid song file: " + self.freq.songPath)
                        print("Invalid song file: " + self.freq.songPath)
                    else:
                        # Get the frequency range for current node
                        lowF = self.freq.getNodeFrequency(r*grid.columns + c)
                        highF = self.freq.getNodeFrequency(r*grid.columns + (c+1))
                        print("-----Node: ({0},{1}) ___ F: ({2:2.3f},{3:2.3f})-----".format(r,c,lowF,highF))
                        bpy.context.active_object.keyframe_insert('scale', index=2) # Set an initial keyframe for the z direction
                        bpy.context.area.type = 'GRAPH_EDITOR'
                        bpy.ops.graph.sound_bake(filepath=self.freq.songPath, low=lowF, high=highF) # Bake!
                        bpy.context.area.type = "VIEW_3D"
                    # End if
                # End if

                loc.x += (node.size.x + grid.spacing.x) # Move 1 up on the x axis
            # End for columns

            # Next row 
            loc.y += (node.size.y + grid.spacing.y) # Move 1 up on the y axis
            loc.x = xStart # Reset the location on the x axis
        # End for rows
    # End fnc genGrid
# End class Visualizer


# This is called form the __init__.py file
def addVisualizer(props):
    # if(self.grid[0] == GridKey.Square):
        # print("Generating Square Grid")
        # self.genGrid()
    # elif(self.grid[0] == GridKey.Circle):
        # print("Generating Circle Grid")
        # #Function Call
    # elif(self.grid[0] == GridKey.SpiralSquare):
        # print("Generating Spiral Square Grid")
        # #Function Call
    # elif(self.grid[0] == GridKey.SpiralCircle):
        # print("Generating Spiral Circle Grid")
        # #Function Call
    
    # Group Data
    newNode = Node(
        props.nodeWidth,
        props.nodeHeight,
        props.nodeThickness,
        props.scalePivot
    )
    newGrid = Grid(
        props.nodeScaleMultiplier,
        props.rowNum,
        props.colNum,
        props.xSpace,
        props.ySpace,
        newNode
    ) 
    myFrequency = Frequency(
        props.chooseFile,
        props.minFreq,
        props.maxFreq,
        props.freqScale,
        newGrid.getNodeNum()
    )
    animation = props.animate
    addSong = props.addSong

    # Make a Visualization object
    myVis = Visualizer(
        newNode,
        newGrid,
        myFrequency,
        animation,
        addSong
    )

    # Generate the grid!
    myVis.genGrid()
    # bpy.context.area.type = "TEXT_EDITOR"
# End fnc

#testVisClass()
#testLogScale()
