import sys
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx

class ACScatterCmd(ompx.MPxCommand):

    kPluginCmdName = "ac_scatter"

    def __init__(self):
        super(ACScatterCmd, self).__init__()
        self.__selection = om.MSelectionList()
        self.__copyMesh = om.MObject()
        self.__vector = om.MVector()
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
            copy_dag = om.MDagPath.getAPathTo(copy, self.__dagPath)

            self.__transformFn.setObject(copy_dag)
            self.__transformFn.setTranslation(pos, om.MSpace.kWorld)

            it.next()

        # for pos in vert_dict.values():
        #     print(pos)
        #     dag_node_fn.duplicate()
        #     new_path = om.MDagPath()
        #     dag_node_fn.getPath(new_path)
        #     transFn = om.MFnTransform(new_path)
        #     transFn.setTranslation(pos, om.MSpace.kWorld)


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
