import omni.kit.commands
import omni.graph.core as og
import numpy as np
import carb
from omni.isaac.core.utils import stage, prims
from pxr import Gf
from omni.isaac.core.utils.extensions import enable_extension
import omni.replicator.core as rep
from omni.isaac.core.utils import nucleus, stage, prims
from scipy.spatial.transform import Rotation as R
import numpy as np

background_usd_path = "/home/yg-inha/Isaac/assets/warehouse_with_pallet.usd"
stage.add_reference_to_stage(background_usd_path, "/World/Background")

forklift= prims.create_prim(
usd_path =  "/home/yg-inha/Isaac/assets/forklift.usd",
prim_path="/World/forklift",
prim_type="Xform",
position=np.array([0.0, -4.0, 0.0]),
orientation=np.array([1.0, 0.0, 0.0, 0.0]),)

camera_front= prims.create_prim(
	usd_path = "/home/yg-inha/Isaac/assets/rsd455.usd",
    prim_path="/World/forklift/forklift_b/forklift_b/lift/camera_front",
    prim_type="Xform",
    )
camera_front.GetAttribute("xformOp:orient").Set(Gf.Quatd(0.70711, 0, 0, -0.70711))
camera_front.GetAttribute("xformOp:translate").Set(Gf.Vec3f(0.01786, -1.11427, 0.26118))

camera_back= prims.create_prim(
	usd_path = "/home/yg-inha/Isaac/assets/rsd455.usd",
    prim_path="/World/forklift/forklift_b/forklift_b/body/camera_back",
    prim_type="Xform",
)
camera_back.GetAttribute("xformOp:orient").Set(Gf.Quatd(0.70711, 0.0, 0, 0.70711))
camera_back.GetAttribute("xformOp:translate").Set(Gf.Vec3f(-0.02197, 0.88241, 0.17513))


og.Controller.edit(
    {"graph_path": "/World/ROS_Camera", "evaluator_name": "execution"},
    {
        og.Controller.Keys.CREATE_NODES: [
            ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"), 
        
            
            ("IsaacCreateRenderProduct_front_center", "omni.isaac.core_nodes.IsaacCreateRenderProduct"),
            ("ROS1CameraHelper_rgb_front_center", "omni.isaac.ros_bridge.ROS1CameraHelper"),
            ("ROS1CameraHelper_info_front_center", "omni.isaac.ros_bridge.ROS1CameraHelper"),
            
            ("IsaacCreateRenderProduct_front_depth", "omni.isaac.core_nodes.IsaacCreateRenderProduct"),
            ("ROS1CameraHelper_rgb_front_depth", "omni.isaac.ros_bridge.ROS1CameraHelper"),
            ("ROS1CameraHelper_depth_front_depth", "omni.isaac.ros_bridge.ROS1CameraHelper"),
            ("ROS1CameraHelper_info_front_depth", "omni.isaac.ros_bridge.ROS1CameraHelper"),
   
            
            ("IsaacCreateRenderProduct_back_center", "omni.isaac.core_nodes.IsaacCreateRenderProduct"),
            ("ROS1CameraHelper_rgb_back_center", "omni.isaac.ros_bridge.ROS1CameraHelper"),
            ("ROS1CameraHelper_info_back_center", "omni.isaac.ros_bridge.ROS1CameraHelper"),
            
            ("IsaacCreateRenderProduct_back_depth", "omni.isaac.core_nodes.IsaacCreateRenderProduct"),
            ("ROS1CameraHelper_rgb_back_depth", "omni.isaac.ros_bridge.ROS1CameraHelper"),
            ("ROS1CameraHelper_depth_back_depth", "omni.isaac.ros_bridge.ROS1CameraHelper"),
            ("ROS1CameraHelper_info_back_depth", "omni.isaac.ros_bridge.ROS1CameraHelper"),
        ],
        og.Controller.Keys.CONNECT: [
            
            
            ("OnPlaybackTick.outputs:tick", "IsaacCreateRenderProduct_front_center.inputs:execIn"),
            ("IsaacCreateRenderProduct_front_center.outputs:execOut", "ROS1CameraHelper_rgb_front_center.inputs:execIn"),
            ("IsaacCreateRenderProduct_front_center.outputs:renderProductPath", "ROS1CameraHelper_rgb_front_center.inputs:renderProductPath"),
            
            ("OnPlaybackTick.outputs:tick", "IsaacCreateRenderProduct_front_depth.inputs:execIn"),
            ("IsaacCreateRenderProduct_front_depth.outputs:execOut", "ROS1CameraHelper_rgb_front_depth.inputs:execIn"),
            ("IsaacCreateRenderProduct_front_depth.outputs:renderProductPath", "ROS1CameraHelper_rgb_front_depth.inputs:renderProductPath"),
            ("IsaacCreateRenderProduct_front_depth.outputs:execOut", "ROS1CameraHelper_depth_front_depth.inputs:execIn"),
            ("IsaacCreateRenderProduct_front_depth.outputs:renderProductPath", "ROS1CameraHelper_depth_front_depth.inputs:renderProductPath"),
            
            
            ("OnPlaybackTick.outputs:tick", "IsaacCreateRenderProduct_back_center.inputs:execIn"),
            ("IsaacCreateRenderProduct_back_center.outputs:execOut", "ROS1CameraHelper_rgb_back_center.inputs:execIn"),
            ("IsaacCreateRenderProduct_back_center.outputs:renderProductPath", "ROS1CameraHelper_rgb_back_center.inputs:renderProductPath"),
            
            ("OnPlaybackTick.outputs:tick", "IsaacCreateRenderProduct_back_depth.inputs:execIn"),
            ("IsaacCreateRenderProduct_back_depth.outputs:execOut", "ROS1CameraHelper_rgb_back_depth.inputs:execIn"),
            ("IsaacCreateRenderProduct_back_depth.outputs:renderProductPath", "ROS1CameraHelper_rgb_back_depth.inputs:renderProductPath"),
            ("IsaacCreateRenderProduct_back_depth.outputs:execOut", "ROS1CameraHelper_depth_back_depth.inputs:execIn"),
            ("IsaacCreateRenderProduct_back_depth.outputs:renderProductPath", "ROS1CameraHelper_depth_back_depth.inputs:renderProductPath"),
        ],
        og.Controller.Keys.SET_VALUES: [
           
            
            ("IsaacCreateRenderProduct_front_center.inputs:cameraPrim", "/World/forklift/forklift_b/forklift_b/lift/camera_front/RSD455/Camera_OmniVision_OV9782_Color"),
            ("ROS1CameraHelper_rgb_front_center.inputs:topicName", "/rgb_front_center"),
            ("ROS1CameraHelper_rgb_front_center.inputs:frameId", "map"),
            
            ("IsaacCreateRenderProduct_front_depth.inputs:cameraPrim", "/World/forklift/forklift_b/forklift_b/lift/camera_front/RSD455/Camera_Pseudo_Depth"),
            ("ROS1CameraHelper_rgb_front_depth.inputs:topicName", "/rgb_front_depth"),
            ("ROS1CameraHelper_rgb_front_depth.inputs:frameId", "map"),
            ("ROS1CameraHelper_depth_front_depth.inputs:topicName", "/depth_front_depth"),
            ("ROS1CameraHelper_depth_front_depth.inputs:type", "depth"),
            ("ROS1CameraHelper_depth_front_depth.inputs:frameId", "map"),
         
            
            ("IsaacCreateRenderProduct_back_center.inputs:cameraPrim", "/World/forklift/forklift_b/forklift_b/body/camera_back/RSD455/Camera_OmniVision_OV9782_Color"
),
            ("ROS1CameraHelper_rgb_back_center.inputs:topicName", "/rgb_back_center"),
            ("ROS1CameraHelper_rgb_back_center.inputs:frameId", "map"),
            
            ("IsaacCreateRenderProduct_back_depth.inputs:cameraPrim", "/World/forklift/forklift_b/forklift_b/body/camera_back/RSD455/Camera_Pseudo_Depth"),
            ("ROS1CameraHelper_rgb_back_depth.inputs:topicName", "/rgb_back_depth"),
            ("ROS1CameraHelper_rgb_back_depth.inputs:frameId", "map"),
            ("ROS1CameraHelper_depth_back_depth.inputs:topicName", "/depth_back_depth"),
            ("ROS1CameraHelper_depth_back_depth.inputs:type", "depth"),
            ("ROS1CameraHelper_depth_back_depth.inputs:frameId", "map"),
        ],
    },
)