import sys
import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx


class ACScatterNode(ompx.MPxNode):

    kPluginNodeName = "ac_scatterNode"
    kPluginNodeClassify = "utility/general"
    kPluginNodeId = om.MTypeId(0x33333)

    kInput1Attr = "in1"
    kInput1LongAttr = "input1"
    kInput1 = om.MObject()
    kInput2Attr = "in2"
    kInput2LongAttr = "input2"
    kInput2 = om.MObject()
    kOutputAttr = "out"
    kOutputLongAttr = "output"
    kOutput = om.MObject()

    def __init__(self):
        super(ACScatterNode, self).__init__()

    @classmethod
    def nodeCreator(cls):
        return ompx.asMPxPtr(cls())

    @classmethod
    def nodeInitializer(cls):
        typedAttr = om.MFnTypedAttribute()
        cls.kInput1 = typedAttr.create(
            cls.kInput1LongAttr,
            cls.kInput1Attr,
            om.MFnData.kMesh
        )
        typedAttr.setStorable(True)
        cls.addAttribute(cls.kInput1)

        cls.kInput2 = typedAttr.create(
            cls.kInput2LongAttr,
            cls.kInput2Attr,
            om.MFnData.kMesh
        )
        typedAttr.setStorable(True)
        typedAttr.setWritable(True)
        cls.addAttribute(cls.kInput2)

        cls.kOutput = typedAttr.create( # TODO change this to output array of objects
            cls.kOutputLongAttr,
            cls.kOutputAttr,
            om.MFnData.kMesh
        )
        typedAttr.setArray(True)
        typedAttr.setWritable(False)
        typedAttr.setStorable(False)
        cls.addAttribute(cls.kOutput)

        cls.attributeAffects(
            cls.kInput1,
            cls.kOutput
        )
        cls.attributeAffects(
            cls.kInput2,
            cls.kOutput
        )

    def compute(self, pPlug, pDataBlock):
        if pPlug == kOutput:
            input1Handle = om.MDataHandle(
                pDataBlock.inputValue(
                    ACScatterNode.kInput1
                )
            )
            instance_geo = input1Handle.asMesh()

            input2Handle = om.MDataHandle(
                pDataBlock.inputValue(
                    ACScatterNode.kInput2
                )
            )
            vert_geo = input2Handle.asMesh()

            input2vertIt = om.MItMeshVertex(vert_geo)

            vert_dict = dict()

            # record the position of each vertices of input2 in world space
            while not input2vertIt.isDone():
                vert_dict[input2vertIt.currentItem()] = input2vertIt.position()
                input2vertIt.next()

            # output handle for  instanced geo1 to vertices of geo2
            outputHandle = om.MArrayDataHandle(
                pDataBlock.outputValue(
                    ACScatterNode.kOutput
                )
            )

            copy_mesh_fn = om.MFnMesh()
            copy_meshData_fn = om.MFnMeshData()
            geo_matrix = om.MTransformationMatrix()

            # Keeping track of objects
            mesh_list = om.MObjectArray()
            data_builder = om.MArrayDataBuilder(
                pDataBlock,
                ACScatterNode.kOutput,
                len(vert_dict)
            )
            # build object data
            obj = dict()
            # obj["numVerts"] =
            # obj["numPolys"] =

            for pos in vert_dict.values():
                new_geo_data = copy_meshData_fn.create()
                geo_matrix.setTranslation(pos, om.MSpace.kWorld)
                new_geo_data.setMatrix(geo_matrix.asMatrix())
                new_instance = copy_mesh_fn.copy(new_geo_data)

                # add object to array for keeping
                mesh_list.append(new_instance)
                data_builder.addLast()

            # Set the output object
            outputHandle.set(data_builder)
            outputHandle.setAllClean(pPlug)

        else:
            return om.kUnknownParameter

def initializePlugin(obj):
    plugin = ompx.MFnPlugin(
        obj,
        "Austin Cronin",
        "1.0", "Any"
    )
    try:
        plugin.registerNode(
            ACScatterNode.kPluginNodeName,
            ACScatterNode.kPluginNodeId,
            ACScatterNode.nodeCreator,
            ACScatterNode.nodeInitializer,
            ACScatterNode.kDependNode,
            ACScatterNode.kPluginNodeClassify
        )

    except:
        sys.stderr.write("Failed to register node: %s" % ACScatterNode.kPluginNodeName)
        raise

def uninitializePlugin (obj):
    plugin = ompx.MFnPlugin(
       obj
    )
    try:
        plugin.deregisterNode(
            ACScatterNode.kPluginNodeId
        )
    except:
        sys.stderr.write("Failed to deregister node: %s" % ACScatterNode.kPluginNodeName)
