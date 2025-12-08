# GraspCandidate.msg
std_msgs/Header header
geometry_msgs/Pose pose
float32 width        # gripper width in meters
float32 score        # quality score
string grasp_type    # e.g., "antipodal", "cnn"
