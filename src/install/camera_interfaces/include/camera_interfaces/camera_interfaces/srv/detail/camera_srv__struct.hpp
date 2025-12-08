// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from camera_interfaces:srv/CameraSrv.idl
// generated code does not contain a copyright notice

#ifndef CAMERA_INTERFACES__SRV__DETAIL__CAMERA_SRV__STRUCT_HPP_
#define CAMERA_INTERFACES__SRV__DETAIL__CAMERA_SRV__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__camera_interfaces__srv__CameraSrv_Request __attribute__((deprecated))
#else
# define DEPRECATED__camera_interfaces__srv__CameraSrv_Request __declspec(deprecated)
#endif

namespace camera_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct CameraSrv_Request_
{
  using Type = CameraSrv_Request_<ContainerAllocator>;

  explicit CameraSrv_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  explicit CameraSrv_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  // field types and members
  using _structure_needs_at_least_one_member_type =
    uint8_t;
  _structure_needs_at_least_one_member_type structure_needs_at_least_one_member;


  // constant declarations

  // pointer types
  using RawPtr =
    camera_interfaces::srv::CameraSrv_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const camera_interfaces::srv::CameraSrv_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<camera_interfaces::srv::CameraSrv_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<camera_interfaces::srv::CameraSrv_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      camera_interfaces::srv::CameraSrv_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<camera_interfaces::srv::CameraSrv_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      camera_interfaces::srv::CameraSrv_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<camera_interfaces::srv::CameraSrv_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<camera_interfaces::srv::CameraSrv_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<camera_interfaces::srv::CameraSrv_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__camera_interfaces__srv__CameraSrv_Request
    std::shared_ptr<camera_interfaces::srv::CameraSrv_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__camera_interfaces__srv__CameraSrv_Request
    std::shared_ptr<camera_interfaces::srv::CameraSrv_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CameraSrv_Request_ & other) const
  {
    if (this->structure_needs_at_least_one_member != other.structure_needs_at_least_one_member) {
      return false;
    }
    return true;
  }
  bool operator!=(const CameraSrv_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CameraSrv_Request_

// alias to use template instance with default allocator
using CameraSrv_Request =
  camera_interfaces::srv::CameraSrv_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace camera_interfaces


// Include directives for member types
// Member 'rgb_image'
// Member 'depth_image'
#include "sensor_msgs/msg/detail/image__struct.hpp"
// Member 'timestamp'
#include "builtin_interfaces/msg/detail/time__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__camera_interfaces__srv__CameraSrv_Response __attribute__((deprecated))
#else
# define DEPRECATED__camera_interfaces__srv__CameraSrv_Response __declspec(deprecated)
#endif

namespace camera_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct CameraSrv_Response_
{
  using Type = CameraSrv_Response_<ContainerAllocator>;

  explicit CameraSrv_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : rgb_image(_init),
    depth_image(_init),
    timestamp(_init)
  {
    (void)_init;
  }

  explicit CameraSrv_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : rgb_image(_alloc, _init),
    depth_image(_alloc, _init),
    timestamp(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _rgb_image_type =
    sensor_msgs::msg::Image_<ContainerAllocator>;
  _rgb_image_type rgb_image;
  using _depth_image_type =
    sensor_msgs::msg::Image_<ContainerAllocator>;
  _depth_image_type depth_image;
  using _timestamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _timestamp_type timestamp;

  // setters for named parameter idiom
  Type & set__rgb_image(
    const sensor_msgs::msg::Image_<ContainerAllocator> & _arg)
  {
    this->rgb_image = _arg;
    return *this;
  }
  Type & set__depth_image(
    const sensor_msgs::msg::Image_<ContainerAllocator> & _arg)
  {
    this->depth_image = _arg;
    return *this;
  }
  Type & set__timestamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->timestamp = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    camera_interfaces::srv::CameraSrv_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const camera_interfaces::srv::CameraSrv_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<camera_interfaces::srv::CameraSrv_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<camera_interfaces::srv::CameraSrv_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      camera_interfaces::srv::CameraSrv_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<camera_interfaces::srv::CameraSrv_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      camera_interfaces::srv::CameraSrv_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<camera_interfaces::srv::CameraSrv_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<camera_interfaces::srv::CameraSrv_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<camera_interfaces::srv::CameraSrv_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__camera_interfaces__srv__CameraSrv_Response
    std::shared_ptr<camera_interfaces::srv::CameraSrv_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__camera_interfaces__srv__CameraSrv_Response
    std::shared_ptr<camera_interfaces::srv::CameraSrv_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CameraSrv_Response_ & other) const
  {
    if (this->rgb_image != other.rgb_image) {
      return false;
    }
    if (this->depth_image != other.depth_image) {
      return false;
    }
    if (this->timestamp != other.timestamp) {
      return false;
    }
    return true;
  }
  bool operator!=(const CameraSrv_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CameraSrv_Response_

// alias to use template instance with default allocator
using CameraSrv_Response =
  camera_interfaces::srv::CameraSrv_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace camera_interfaces

namespace camera_interfaces
{

namespace srv
{

struct CameraSrv
{
  using Request = camera_interfaces::srv::CameraSrv_Request;
  using Response = camera_interfaces::srv::CameraSrv_Response;
};

}  // namespace srv

}  // namespace camera_interfaces

#endif  // CAMERA_INTERFACES__SRV__DETAIL__CAMERA_SRV__STRUCT_HPP_
