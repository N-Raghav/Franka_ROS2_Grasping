#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from grasp_interfaces.msg import GraspCandidateArray
from geometry_msgs.msg import PoseStamped
import tf2_ros
# --- FIX 1: Import this to enable PoseStamped support in TF2 ---
import tf2_geometry_msgs 
# ---------------------------------------------------------------
from moveit_msgs.action import MoveGroup
try:
    from franka_msgs.action import Grasp as FrankaGrasp
except ImportError:
    from control_msgs.action import GripperCommand as FrankaGrasp

class PandaGraspExecutor(Node):
    def __init__(self):
        super().__init__('panda_grasp_executor')
        self.sub = self.create_subscription(GraspCandidateArray, '/grasp_candidates', self.cb, 1)
        self.move_action_client = ActionClient(self, MoveGroup, 'move_action')
        # Check your gripper topic name in 'ros2 action list'
        self.gripper_client = ActionClient(self, FrankaGrasp, '/panda_gripper/grasp') 

        self.tfbuf = tf2_ros.Buffer()
        self.tfl = tf2_ros.TransformListener(self.tfbuf, self)
        
        # --- FIX 2: State Flag to prevent spamming ---
        self.grasping_active = False 
        
        self.get_logger().info("Grasp Executor Ready. Waiting for candidates...")

    def cb(self, msg: GraspCandidateArray):
        # If we are already busy moving, ignore new candidates
        if self.grasping_active:
            return

        if len(msg.candidates) == 0: 
            return

        # Lock the node so we don't start a second grasp
        self.grasping_active = True
        self.get_logger().info("Candidate received! Locking executor...")

        best = max(msg.candidates, key=lambda g: g.score)
        
        target_frame = 'panda_link0' 
        try:
            # Wait for transform availability
            if not self.tfbuf.can_transform(target_frame, best.header.frame_id, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=1.0)):
                self.get_logger().warn("Waiting for TF...")
                self.grasping_active = False # Unlock if failed
                return

            p_stamped = PoseStamped()
            p_stamped.header = best.header
            p_stamped.pose = best.pose
            
            # --- FIX 1: Use the buffer to transform the pose object directly ---
            goal_stamped = self.tfbuf.transform(p_stamped, target_frame)
            
        except Exception as e:
            self.get_logger().error(f"TF Error: {e}")
            self.grasping_active = False
            return

        # EXECUTION SEQUENCE
        self.get_logger().info("1. Moving to Pre-Grasp...")
        pre_grasp = PoseStamped()
        pre_grasp.header = goal_stamped.header
        pre_grasp.pose = goal_stamped.pose
        pre_grasp.pose.position.z += 0.15 
        
        if not self.move_to_pose(pre_grasp): 
            self.grasping_active = False
            return

        self.get_logger().info("2. Moving to Grasp...")
        if not self.move_to_pose(goal_stamped): 
            self.grasping_active = False
            return

        self.get_logger().info("3. Closing Gripper...")
        self.trigger_gripper(width=best.width - 0.01)

        self.get_logger().info("4. Lifting...")
        post_grasp = PoseStamped()
        post_grasp.header = goal_stamped.header
        post_grasp.pose = goal_stamped.pose
        post_grasp.pose.position.z += 0.20
        self.move_to_pose(post_grasp)
        
        self.get_logger().info("Grasp Complete. Waiting 5 seconds before unlocking...")
        # Optional: Reset flag to allow next grasp
        # self.grasping_active = False 

    def move_to_pose(self, pose_stamped):
        if not self.move_action_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().error("MoveIt action server not available!")
            return False

        goal_msg = MoveGroup.Goal()
        goal_msg.request.group_name = "panda_arm" 
        goal_msg.request.num_planning_attempts = 10
        goal_msg.request.allowed_planning_time = 5.0
        goal_msg.request.max_velocity_scaling_factor = 0.1 
        goal_msg.request.max_acceleration_scaling_factor = 0.1
        
        # Constraints setup
        from moveit_msgs.msg import Constraints, PositionConstraint, OrientationConstraint
        from shape_msgs.msg import SolidPrimitive

        c = Constraints()
        c.name = "target_pose"
        
        pc = PositionConstraint()
        pc.header = pose_stamped.header
        pc.link_name = "panda_hand"
        pc.constraint_region.primitives.append(SolidPrimitive(type=SolidPrimitive.SPHERE, dimensions=[0.01]))
        pc.constraint_region.primitive_poses.append(pose_stamped.pose)
        pc.weight = 1.0
        
        oc = OrientationConstraint()
        oc.header = pose_stamped.header
        oc.link_name = "panda_hand"
        oc.orientation = pose_stamped.pose.orientation
        oc.absolute_x_axis_tolerance = 0.1
        oc.absolute_y_axis_tolerance = 0.1
        oc.absolute_z_axis_tolerance = 0.1
        oc.weight = 1.0

        c.position_constraints.append(pc)
        c.orientation_constraints.append(oc)
        goal_msg.request.goal_constraints.append(c)

        future = self.move_action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)
        result = future.result()
        
        if result.accepted:
            res_future = result.get_result_async()
            rclpy.spin_until_future_complete(self, res_future)
            final_res = res_future.result()
            if final_res.result.error_code.val == 1:
                return True
        
        self.get_logger().error("MoveIt planning failed")
        return False

    def trigger_gripper(self, width, force=40.0):
        if not self.gripper_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn("Gripper action not available")
            return

        goal = FrankaGrasp.Goal()
        goal.width = width
        goal.speed = 0.05
        goal.force = force
        
        future = self.gripper_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)

def main(args=None):
    rclpy.init(args=args)
    node = PandaGraspExecutor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()