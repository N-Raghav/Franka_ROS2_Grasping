#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from grasp_interfaces.msg import GraspCandidate, GraspCandidateArray
from geometry_msgs.msg import PoseStamped
import numpy as np
import sensor_msgs_py.point_cloud2 as pc2
from scipy.spatial.transform import Rotation as R

class AntipodalNode(Node):
    def __init__(self):
        super().__init__('antipodal_node')
        self.sub = self.create_subscription(PointCloud2, '/object_cloud', self.cb, 1)
        self.pub = self.create_publisher(GraspCandidateArray, '/grasp_candidates', 1)
        
        # --- HARDCODED INTRINSICS (From your old antipodal_planner.py) ---
        self.fx = 605.622314453125
        self.fy = 605.8401489257812
        self.ppx = 321.1669921875
        self.ppy = 231.57203674316406
        
        self.get_logger().info("Antipodal Node Started (Using calibrated intrinsics).")

    def cb(self, msg):
        # 1. Unpack Cloud to Standard Numpy Array
        gen = pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
        pts = np.array([[p[0], p[1], p[2]] for p in gen], dtype=np.float32)

        if pts.shape[0] < 50:
            return

        # 2. PCA for Orientation
        centroid = pts.mean(axis=0)
        cov = np.cov((pts - centroid).T)
        eigvals, eigvecs = np.linalg.eig(cov)
        sort_indices = np.argsort(eigvals)
        minor_axis = eigvecs[:, sort_indices[0]] # Grasp closing direction
        
        # 3. Re-Calculate Centroid using Old Projective Math (Optional but verifies accuracy)
        # In this specific node, we are receiving 3D points directly, so we trust X/Y/Z.
        # However, we apply the orientation logic from your old generator.
        
        # Orientation Construction:
        # Z_hand (Approach): Points from camera forward (+Z)
        # Y_hand (Closing): Aligned with object minor axis
        z_axis = np.array([0, 0, 1]) 
        y_axis = minor_axis
        x_axis = np.cross(y_axis, z_axis)
        
        # Normalize
        x_axis = x_axis / np.linalg.norm(x_axis)
        y_axis = np.cross(z_axis, x_axis)
        
        rot_matrix = np.column_stack((x_axis, y_axis, z_axis))
        quat = R.from_matrix(rot_matrix).as_quat()

        # 4. Create Pose
        pose = PoseStamped()
        pose.header.frame_id = msg.header.frame_id
        pose.pose.position.x = float(centroid[0])
        pose.pose.position.y = float(centroid[1])
        pose.pose.position.z = float(centroid[2])
        
        pose.pose.orientation.x = quat[0]
        pose.pose.orientation.y = quat[1]
        pose.pose.orientation.z = quat[2]
        pose.pose.orientation.w = quat[3]

        # 5. Width Calculation (Project points onto minor axis)
        projected = pts @ minor_axis
        width = float(projected.max() - projected.min())

        # 6. Publish
        g = GraspCandidate()
        g.header = pose.header
        g.pose = pose.pose
        g.width = width
        g.score = 1.0
        
        arr = GraspCandidateArray()
        arr.candidates = [g]
        self.pub.publish(arr)
        
        self.get_logger().info(f"Published Grasp at {centroid} Width: {width:.3f}")

def main(args=None):
    rclpy.init(args=args)
    node = AntipodalNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()