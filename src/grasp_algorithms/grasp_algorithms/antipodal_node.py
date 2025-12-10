#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from grasp_interfaces.msg import GraspCandidate, GraspCandidateArray
from geometry_msgs.msg import PoseStamped
import numpy as np
import sensor_msgs_py.point_cloud2 as pc2
from scipy.spatial.transform import Rotation as R
from tf2_ros import Buffer, TransformListener

class AntipodalNode(Node):
    def __init__(self):
        super().__init__('antipodal_node')
        self.sub = self.create_subscription(PointCloud2, '/object_cloud', self.cb, 1)
        self.pub = self.create_publisher(GraspCandidateArray, '/grasp_candidates', 1)
        self.grasp_found = False 

        # --- TF SETUP (CRITICAL FOR TOP-DOWN) ---
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # --- TUNABLE OFFSETS ---
        # 1. HEIGHT (Z): Back up the wrist so fingers touch object.
        self.z_offset = -0.2
        
        # 2. LEFT/RIGHT (Y): Shift Right/Left relative to gripper
        self.y_offset = 0.02  
        
        # 3. FORWARD/BACK (X): Shift Forward/Back relative to gripper
        self.x_offset = 0.00   

        self.get_logger().info("Antipodal Node Started (Strict Top-Down Mode).")

    def get_transform(self, target_frame, source_frame):
        try:
            t = self.tf_buffer.lookup_transform(
                target_frame,
                source_frame,
                rclpy.time.Time())
            return t
        except Exception as e:
            self.get_logger().warn(f"TF Lookup failed: {e}")
            return None

    def transform_points(self, points, trans):
        """
        Manually transforms a Nx3 numpy array of points using a StampedTransform
        """
        # Extract translation
        tx = trans.transform.translation.x
        ty = trans.transform.translation.y
        tz = trans.transform.translation.z
        t = np.array([tx, ty, tz])

        # Extract rotation (quaternion) -> Matrix
        qx = trans.transform.rotation.x
        qy = trans.transform.rotation.y
        qz = trans.transform.rotation.z
        qw = trans.transform.rotation.w
        r = R.from_quat([qx, qy, qz, qw])
        rot_mat = r.as_matrix()

        # Apply: P_new = R * P_old + T
        # (points is Nx3, so we do points @ R.T + T)
        return points @ rot_mat.T + t

    def check_reachability(self, x, y, z):
        if z < 0.02: # Allow getting very close to table
            self.get_logger().error(f"REJECTED: Target Z ({z:.2f}) is too close to ground!")
            return False
        
        radius = np.sqrt(x**2 + y**2 + z**2)
        if radius > 0.80:
            self.get_logger().error(f"REJECTED: Too far ({radius:.2f}m)!")
            return False

        if radius < 0.20:
            self.get_logger().error(f"REJECTED: Too close to base!")
            return False
        return True

    def cb(self, msg):
        if self.grasp_found: return

        # 1. TRANSFORM TO BASE FRAME
        # This ensures 'Down' is actually Down, no matter the camera angle.
        target_frame = "panda_link0"
        trans = self.get_transform(target_frame, msg.header.frame_id)
        if trans is None: return

        # Unpack and Transform
        gen = pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
        raw_pts = np.array([[p[0], p[1], p[2]] for p in gen], dtype=np.float32)
        if raw_pts.shape[0] < 50: return

        pts = self.transform_points(raw_pts, trans)

        # 2. PCA CALCULATION
        centroid = pts.mean(axis=0)
        cov = np.cov((pts - centroid).T)
        eigvals, eigvecs = np.linalg.eig(cov)
        sort_indices = np.argsort(eigvals)
        
        # 3. STRICT TOP-DOWN ORIENTATION LOGIC
        
        # A. Force Approach (Z) to be straight down
        grasp_z = np.array([0.0, 0.0, -1.0])

        # B. Find Closing Direction (Y)
        # We want the gripper to close along the object's narrowest horizontal width.
        # We take the PCA minor axis and project it onto the XY plane (flatten it).
        minor_axis_3d = eigvecs[:, sort_indices[0]] 
        
        # Flatten: Remove Z component
        grasp_y = np.array([minor_axis_3d[0], minor_axis_3d[1], 0.0])

        # Handle Edge Case: If object is flat (sheet of paper), minor axis IS the Z axis.
        # In this case, 'grasp_y' becomes [0,0,0]. We switch to the secondary axis.
        if np.linalg.norm(grasp_y) < 0.1:
            middle_axis_3d = eigvecs[:, sort_indices[1]]
            grasp_y = np.array([middle_axis_3d[0], middle_axis_3d[1], 0.0])

        # Normalize Y
        grasp_y = grasp_y / np.linalg.norm(grasp_y)

        # C. Calculate X (Orthogonal)
        grasp_x = np.cross(grasp_y, grasp_z)
        grasp_x = grasp_x / np.linalg.norm(grasp_x)

        # Recalculate Y to ensure perfect orthogonality
        grasp_y = np.cross(grasp_z, grasp_x)

        # 4. BUILD POSE
        rot_matrix = np.column_stack((grasp_x, grasp_y, grasp_z))
        r = R.from_matrix(rot_matrix)
        quat = r.as_quat()

        # Apply Offsets (in the new aligned frame)
        offset_local = np.array([self.x_offset, self.y_offset, self.z_offset])
        offset_world = r.apply(offset_local)
        final_pos = centroid + offset_world

        self.get_logger().info(f"Centroid: {centroid}")
        self.get_logger().info(f"Target: {final_pos}")

        if not self.check_reachability(final_pos[0], final_pos[1], final_pos[2]):
            return

        # Publish Pose
        pose = PoseStamped()
        # IMPORTANT: Frame is now panda_link0 because we transformed the points
        pose.header.frame_id = target_frame 
        pose.header.stamp = self.get_clock().now().to_msg() # Update time
        
        pose.pose.position.x = float(final_pos[0])
        pose.pose.position.y = float(final_pos[1])
        pose.pose.position.z = float(final_pos[2])
        pose.pose.orientation.x = quat[0]
        pose.pose.orientation.y = quat[1]
        pose.pose.orientation.z = quat[2]
        pose.pose.orientation.w = quat[3]

        # Width calculation (Projected onto Y axis)
        projected = pts @ grasp_y
        width = float(projected.max() - projected.min())

        g = GraspCandidate()
        g.header = pose.header
        g.pose = pose.pose
        g.width = width
        g.score = 1.0
        
        arr = GraspCandidateArray()
        arr.candidates = [g]
        self.pub.publish(arr)
        
        self.get_logger().info(f"Top-Down Grasp Published. Locking.")
        self.grasp_found = True

def main(args=None):
    rclpy.init(args=args)
    node = AntipodalNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()