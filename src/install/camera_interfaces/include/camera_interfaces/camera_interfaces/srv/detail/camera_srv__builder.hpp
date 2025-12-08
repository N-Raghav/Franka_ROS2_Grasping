// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from camera_interfaces:srv/CameraSrv.idl
// generated code does not contain a copyright notice

#ifndef CAMERA_INTERFACES__SRV__DETAIL__CAMERA_SRV__BUILDER_HPP_
#define CAMERA_INTERFACES__SRV__DETAIL__CAMERA_SRV__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "camera_interfaces/srv/detail/camera_srv__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace camera_interfaces
{

namespace srv
{


}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::camera_interfaces::srv::CameraSrv_Request>()
{
  return ::camera_interfaces::srv::CameraSrv_Request(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace camera_interfaces


namespace camera_interfaces
{

namespace srv
{

namespace builder
{

class Init_CameraSrv_Response_timestamp
{
public:
  explicit Init_CameraSrv_Response_timestamp(::camera_interfaces::srv::CameraSrv_Response & msg)
  : msg_(msg)
  {}
  ::camera_interfaces::srv::CameraSrv_Response timestamp(::camera_interfaces::srv::CameraSrv_Response::_timestamp_type arg)
  {
    msg_.timestamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::camera_interfaces::srv::CameraSrv_Response msg_;
};

class Init_CameraSrv_Response_depth_image
{
public:
  explicit Init_CameraSrv_Response_depth_image(::camera_interfaces::srv::CameraSrv_Response & msg)
  : msg_(msg)
  {}
  Init_CameraSrv_Response_timestamp depth_image(::camera_interfaces::srv::CameraSrv_Response::_depth_image_type arg)
  {
    msg_.depth_image = std::move(arg);
    return Init_CameraSrv_Response_timestamp(msg_);
  }

private:
  ::camera_interfaces::srv::CameraSrv_Response msg_;
};

class Init_CameraSrv_Response_rgb_image
{
public:
  Init_CameraSrv_Response_rgb_image()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CameraSrv_Response_depth_image rgb_image(::camera_interfaces::srv::CameraSrv_Response::_rgb_image_type arg)
  {
    msg_.rgb_image = std::move(arg);
    return Init_CameraSrv_Response_depth_image(msg_);
  }

private:
  ::camera_interfaces::srv::CameraSrv_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::camera_interfaces::srv::CameraSrv_Response>()
{
  return camera_interfaces::srv::builder::Init_CameraSrv_Response_rgb_image();
}

}  // namespace camera_interfaces

#endif  // CAMERA_INTERFACES__SRV__DETAIL__CAMERA_SRV__BUILDER_HPP_
