#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from grasp_interfaces.msg import GraspCandidateArray
from geometry_msgs.msg import PoseStamped
import tf2_ros
import tf2_geometry_msgs 
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
        self.gripper_client = ActionClient(self, FrankaGrasp, '/panda_gripper/grasp') 

        self.tfbuf = tf2_ros.Buffer()
        self.tfl = tf2_ros.TransformListener(self.tfbuf, self)
        
        self.grasping_active = False 
        
        # --- CONFIGURATION ---
        # Must match the z_offset in your AntipodalNode!
        self.approach_distance = 0.15  
        
        self.get_logger().info("Grasp Executor Ready. Waiting for candidates...")

    def cb(self, msg: GraspCandidateArray):
        if self.grasping_active: return
        if len(msg.candidates) == 0: return

        self.grasping_active = True
        self.get_logger().info("Candidate received! Locking executor...")

        best = max(msg.candidates, key=lambda g: g.score)
        target_frame = 'panda_link0' 

        try:
            if not self.tfbuf.can_transform(target_frame, best.header.frame_id, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=1.0)):
                self.get_logger().warn("Waiting for TF...")
                self.grasping_active = False 
                return

            p_stamped = PoseStamped()
            p_stamped.header = best.header
            p_stamped.pose = best.pose
            
            # This is the HOVER POSE (approx 15cm above object)
            hover_pose = self.tfbuf.transform(p_stamped, target_frame)
            
        except Exception as e:
            self.get_logger().error(f"TF Error: {e}")
            self.grasping_active = False
            return

        # --- 1. MOVE TO PRE-GRASP (HOVER) ---
        self.get_logger().info(f"1. Moving to Pre-Grasp (Z={hover_pose.pose.position.z:.3f})...")
        if not self.move_to_pose(hover_pose): 
            self.grasping_active = False
            return

        # --- 2. OPEN GRIPPER ---
        # Ensure gripper is open before descending
        # (Assuming you have a moveit/action for open, or just use grasp with large width)
        # self.trigger_gripper(width=0.08) 

        # --- 3. DESCEND TO GRASP ---
        self.get_logger().info("2. Descending to Grasp...")
        grasp_pose = PoseStamped()
        grasp_pose.header = hover_pose.header
        grasp_pose.pose = hover_pose.pose
        
        # CRITICAL FIX: Subtract the offset to go DOWN to the object
        # We go slightly lower (0.005) to ensure fingers surround the top surface
        grasp_pose.pose.position.z -= (self.approach_distance + 0.005)

        if not self.move_to_pose(grasp_pose): 
            self.grasping_active = False
            return

        # --- 4. CLOSE GRIPPER ---
        self.get_logger().info("3. Closing Gripper...")
        self.trigger_gripper(width=best.width - 0.005) # Close slightly tighter than object

        # --- 5. LIFT UP ---
        self.get_logger().info("4. Lifting...")
        lift_pose = PoseStamped()
        lift_pose.header = hover_pose.header
        lift_pose.pose = hover_pose.pose
        
        # Lift 10cm higher than the original hover
        lift_pose.pose.position.z += 0.10
        
        self.move_to_pose(lift_pose)
        
        self.get_logger().info("Grasp Complete. Unlocking in 5s...")
        # rclpy.sleep(5.0) # Blocking sleep is bad in callbacks, but okay for simple logic
        self.grasping_active = False 

    def move_to_pose(self, pose_stamped):
        if not self.move_action_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().error("MoveIt action server not available!")
            return False

        goal_msg = MoveGroup.Goal()
        goal_msg.request.group_name = "panda_arm" 
        goal_msg.request.num_planning_attempts = 10
        goal_msg.request.allowed_planning_time = 5.0
        # Reduce velocity for the actual grasp approach for safety
        goal_msg.request.max_velocity_scaling_factor = 0.1 
        goal_msg.request.max_acceleration_scaling_factor = 0.1
        
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
        
        goal.epsilon.inner = 0.05
        goal.epsilon.outer = 0.05
        
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