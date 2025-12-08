#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
import sensor_msgs_py.point_cloud2 as pc2
import numpy as np
import open3d as o3d
import pyrealsense2 as rs

class RealSenseObstacleNode(Node):
    def __init__(self):
        super().__init__('realsense_obstacle_node')

        # --- Parameters ---
        # Adjust these to fit your robot's size and environment
        self.declare_parameter('voxel_size', 0.01)      # 5cm grid
        self.declare_parameter('z_min', 0.20)           # Min distance (20cm)
        self.declare_parameter('z_max', 2.0)            # Max distance (2m)
        self.declare_parameter('ransac_thresh', 0.01)   # Plane tolerance (2cm)
        # Device ID taken from your camera.py file
        self.declare_parameter('device_id', '337122071438') 

        # --- RealSense Setup ---
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        
        # specific configs from your camera.py
        device_id = self.get_parameter('device_id').value
        if device_id:
            self.config.enable_device(str(device_id))

        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)

        # Start Camera
        try:
            profile = self.pipeline.start(self.config)
            depth_sensor = profile.get_device().first_depth_sensor()
            self.depth_scale = depth_sensor.get_depth_scale()
            self.get_logger().info(f"RealSense Connected. Depth Scale: {self.depth_scale}")
        except Exception as e:
            self.get_logger().fatal(f"Camera Connection Failed: {e}")
            raise e

        # Processing Blocks
        self.align = rs.align(rs.stream.color)
        self.pc_gen = rs.pointcloud() # Native SDK pointcloud generator
        
        # Publisher
        self.pub = self.create_publisher(PointCloud2, '/object_cloud', 1)
        
        # Timer (30Hz)
        self.timer = self.create_timer(1.0/30.0, self.timer_cb)

    def timer_cb(self):
        # 1. Get Frames
        # This blocks until frames are available (max 1/30th sec)
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        
        if not depth_frame: 
            return

        # 2. Generate Point Cloud (Fast C++ SDK)
        # Calculates x,y,z for every pixel based on intrinsics
        points_rs = self.pc_gen.calculate(depth_frame)
        
        # 3. Convert to NumPy (Zero-Copy)
        # The SDK returns a void* buffer of vertices. We view it as (x,y,z) floats.
        vtx = np.asanyarray(points_rs.get_vertices())
        points_np = vtx.view(np.float32).reshape(-1, 3)

        # 4. Pre-Filter: Remove Zero/Infinity points
        # RealSense returns (0,0,0) for invalid depth. We must remove these before processing.
        valid_mask = (points_np[:, 2] > 0) & (np.isfinite(points_np[:, 2]))
        points_np = points_np[valid_mask]

        if points_np.shape[0] == 0:
            return

        # 5. Open3D Processing
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points_np)

        # A. Voxel Downsample (Crucial for CPU speed)
        voxel_size = self.get_parameter('voxel_size').value
        pcd = pcd.voxel_down_sample(voxel_size)

        # B. Z-Filtering (Passthrough)
        pts = np.asarray(pcd.points)
        z_min = self.get_parameter('z_min').value
        z_max = self.get_parameter('z_max').value
        
        # Keep points within the z-range
        mask = (pts[:, 2] > z_min) & (pts[:, 2] < z_max)
        pcd = pcd.select_by_index(np.where(mask)[0])

        if len(pcd.points) < 10: return

        # C. RANSAC Plane Removal (Delete the table)
        dist_thresh = self.get_parameter('ransac_thresh').value
        _, inliers = pcd.segment_plane(distance_threshold=dist_thresh,
                                       ransac_n=3,
                                       num_iterations=50)
        
        # Invert=True keeps the objects, throws away the table
        objects = pcd.select_by_index(inliers, invert=True)

        # 6. Publish to ROS
        self.publish_cloud(objects)

    def publish_cloud(self, pcd):
        # Create header
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = "camera_link" 

        # Convert back to ROS message
        points = np.asarray(pcd.points)
        msg = pc2.create_cloud_xyz32(header, points)
        self.pub.publish(msg)

    def destroy_node(self):
        # Stop camera stream cleanly
        self.pipeline.stop()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = RealSenseObstacleNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()