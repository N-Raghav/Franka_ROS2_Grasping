// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from camera_interfaces:srv/CameraSrv.idl
// generated code does not contain a copyright notice

#ifndef CAMERA_INTERFACES__SRV__DETAIL__CAMERA_SRV__STRUCT_H_
#define CAMERA_INTERFACES__SRV__DETAIL__CAMERA_SRV__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/CameraSrv in the package camera_interfaces.
typedef struct camera_interfaces__srv__CameraSrv_Request
{
  uint8_t structure_needs_at_least_one_member;
} camera_interfaces__srv__CameraSrv_Request;

// Struct for a sequence of camera_interfaces__srv__CameraSrv_Request.
typedef struct camera_interfaces__srv__CameraSrv_Request__Sequence
{
  camera_interfaces__srv__CameraSrv_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} camera_interfaces__srv__CameraSrv_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'rgb_image'
// Member 'depth_image'
#include "sensor_msgs/msg/detail/image__struct.h"
// Member 'timestamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in srv/CameraSrv in the package camera_interfaces.
typedef struct camera_interfaces__srv__CameraSrv_Response
{
  /// Response
  sensor_msgs__msg__Image rgb_image;
  sensor_msgs__msg__Image depth_image;
  builtin_interfaces__msg__Time timestamp;
} camera_interfaces__srv__CameraSrv_Response;

// Struct for a sequence of camera_interfaces__srv__CameraSrv_Response.
typedef struct camera_interfaces__srv__CameraSrv_Response__Sequence
{
  camera_interfaces__srv__CameraSrv_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} camera_interfaces__srv__CameraSrv_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // CAMERA_INTERFACES__SRV__DETAIL__CAMERA_SRV__STRUCT_H_
