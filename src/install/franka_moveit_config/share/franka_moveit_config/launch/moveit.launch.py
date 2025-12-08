#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, Shutdown
from launch.substitutions import LaunchConfiguration, Command, FindExecutable
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import yaml


def load_yaml(package_name, file_path):
    pkg_path = get_package_share_directory(package_name)
    abs_file = os.path.join(pkg_path, file_path)
    with open(abs_file, 'r') as f:
        return yaml.safe_load(f)


def generate_launch_description():

    # ---------------------------
    # Launch Arguments
    # ---------------------------
    robot_ip_arg = DeclareLaunchArgument(
        "robot_ip",
        default_value="172.16.0.2",
        description="Franka robot IP address"
    )

    use_fake_arg = DeclareLaunchArgument(
        "use_fake_hardware",
        default_value="true",
        description="Use fake hardware (simulation mode)"
    )

    robot_ip = LaunchConfiguration("robot_ip")
    use_fake = LaunchConfiguration("use_fake_hardware")

    # ---------------------------
    # Load URDF + SRDF
    # ---------------------------
    franka_desc = get_package_share_directory("franka_description")

    # STANDARD NO-PLATFORM FILE
    urdf_xacro = os.path.join(
        franka_desc, "robots", "panda.urdf.xacro"
    )

    robot_description = {
        "robot_description": Command(
            [
                FindExecutable(name="xacro"),
                " ",
                urdf_xacro,
                " use_fake_hardware:=",
                use_fake,
                " robot_ip:=",
                robot_ip,
            ]
        )
    }

    # Load STANDARD Franka SRDF
    srdf = load_yaml(
        "franka_moveit_config",
        "config/panda.srdf"
    )
    robot_description_semantic = {
        "robot_description_semantic": yaml.dump(srdf)
    }

    # ---------------------------
    # Load MoveIt config files
    # ---------------------------
    kinematics = load_yaml(
        "franka_moveit_config",
        "config/kinematics.yaml"
    )

    ompl_planning = load_yaml(
        "franka_moveit_config",
        "config/ompl_planning.yaml"
    )

    controllers_yaml = load_yaml(
        "franka_moveit_config",
        "config/panda_controllers.yaml"
    )

    joint_limits_yaml = load_yaml(
        "franka_moveit_config",
        "config/joint_limits.yaml"
    )

    planning_scene_monitor = {
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
    }

    # ---------------------------
    # Move Group Node
    # ---------------------------
    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics,
            ompl_planning,
            controllers_yaml,
            planning_scene_monitor,
            joint_limits_yaml,
        ],
    )

    # ---------------------------
    # RViz Node
    # ---------------------------
    rviz_config = os.path.join(
        get_package_share_directory("franka_moveit_config"),
        "rviz",
        "moveit.rviz",
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config],
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
        ],
    )

    # ---------------------------
    # robot_state_publisher
    # ---------------------------
    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description],
        output="screen",
    )

    # ---------------------------
    # ros2_control Node
    # ---------------------------
    controllers_file = "panda_mock_ros_controllers.yaml" if str(
        use_fake.perform({'use_fake_hardware': 'true'})) == "true" else "panda_ros_controllers.yaml"

    ros2_control_config = os.path.join(
        get_package_share_directory("franka_moveit_config"),
        "config",
        controllers_file,
    )

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, ros2_control_config],
        output="screen",
        on_exit=Shutdown(),
    )

    # ---------------------------
    # Spawn Controllers
    # ---------------------------
    spawn_arm = ExecuteProcess(
        cmd=["ros2 run controller_manager spawner panda_arm_controller"],
        shell=True,
        output="screen",
    )
    spawn_js = ExecuteProcess(
        cmd=["ros2 run controller_manager spawner joint_state_broadcaster"],
        shell=True,
        output="screen",
    )

    return LaunchDescription(
        [
            robot_ip_arg,
            use_fake_arg,
            rviz,
            move_group,
            rsp,
            ros2_control_node,
            spawn_arm,
            spawn_js,
        ]
    )
