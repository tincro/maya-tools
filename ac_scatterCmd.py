import sys
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

class ACScatterCmd(ompx.MPxCommand):

    kPluginCmdName = "ac_scatter"

    def __init__(self):
        super(ACScatterCmd, self).__init__()
        self.__selection = om.MSelectionList()
        self.__copyMesh = om.MObject()
        self.__vector = om.MVector()
        self.__setsFn = om.MFnSet()
        self.__transformFn = om.MFnTransform()
        self.__dagNodeFn = om.MFnDagNode()
        self.__dagPath = om.MDagPath()
        self.__dag = None

    @classmethod
    def cmdCreator(cls):
        return ompx.asMPxPtr(cls())

    def doIt(self, *args):
        om.MGlobal.getActiveSelectionList(self.__selection)

        if not (self.__selection.length() == 2):
            om.MGlobal.displayWarning("Select only 2 objects to scatter geometry. Skipping.")
            return

        self.__selection.getDagPath(1, self.__dagPath)
        it = om.MItMeshVertex(self.__dagPath)

        self.__selection.getDagPath(0, self.__dagPath)
        self.__dagNodeFn.setObject(self.__dagPath)

        while not it.isDone():
            point = it.position(om.MSpace.kWorld)
            pos = om.MVector(point)

            copy = self.__dagNodeFn.duplicate()
            arr = om.MDagPathArray()
            om.MDagPath.getAllPathsTo(copy, arr)
            path = om.MDagPath(arr[0])

            cmds.sets(path.partialPathName(), add="initialShadingGroup")

            self.__transformFn.setObject(arr[0])
            self.__transformFn.setTranslation(pos, om.MSpace.kWorld)

            it.next()

def initializePlugin(obj):
    plugin = ompx.MFnPlugin(
        obj,
        "Austin Cronin",
        "1.0", "Any"
    )
    try:
        plugin.registerCommand(
            ACScatterCmd.kPluginCmdName,
            ACScatterCmd.cmdCreator
        )

    except:
        sys.stderr.write("Failed to register command: %s" % ACScatterCmd.kPluginCmdName)
        raise

def uninitializePlugin (obj):
    plugin = ompx.MFnPlugin(
       obj
    )
    try:
        plugin.deregisterCommand(
            ACScatterCmd.kPluginCmdName
        )
    except:
        sys.stderr.write("Failed to deregister command: %s" % ACScatterCmd.kPluginCmdName)
