# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Contains Gradient functions for image ops."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.framework import dtypes
from tensorflow.python.framework import ops
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import gen_image_ops


@ops.RegisterGradient("ResizeNearestNeighbor")
def _ResizeNearestNeighborGrad(op, grad):
  """The derivatives for nearest neighbor resizing.

  Args:
    op: The ResizeNearestNeighbor op.
    grad: The tensor representing the gradient w.r.t. the output.

  Returns:
    The gradients w.r.t. the input and the output.
  """
  image = op.inputs[0]
  if image.get_shape()[1:3].is_fully_defined():
    image_shape = image.get_shape()[1:3]
  else:
    image_shape = array_ops.shape(image)[1:3]

  # pylint: disable=protected-access
  grads = gen_image_ops._resize_nearest_neighbor_grad(
      grad,
      image_shape,
      align_corners=op.get_attr("align_corners"))
  # pylint: enable=protected-access
  return [grads, None]


@ops.RegisterGradient("ResizeBilinear")
def _ResizeBilinearGrad(op, grad):
  """The derivatives for bilinear resizing.

  Args:
    op: The ResizeBilinear op.
    grad: The tensor representing the gradient w.r.t. the output.

  Returns:
    The gradients w.r.t. the input.
  """
  allowed_types = [dtypes.float32, dtypes.float64]
  grad0 = None
  if op.inputs[0].dtype in allowed_types:
    # pylint: disable=protected-access
    grad0 = gen_image_ops._resize_bilinear_grad(
        grad,
        op.inputs[0],
        align_corners=op.get_attr("align_corners"))
    # pylint: enable=protected-access
  return [grad0, None]


@ops.RegisterGradient("CropAndResize")
def _CropAndResizeGrad(op, grad):
  """The derivatives for crop_and_resize.

  We back-propagate to the image only when the input image tensor has floating
  point dtype but we always back-propagate to the input boxes tensor.

  Args:
    op: The CropAndResize op.
    grad: The tensor representing the gradient w.r.t. the output.

  Returns:
    The gradients w.r.t. the input image, boxes, as well as the always-None
    gradients w.r.t. box_ind and crop_size.
  """
  image = op.inputs[0]
  if image.get_shape().is_fully_defined():
    image_shape = image.get_shape().as_list()
  else:
    image_shape = array_ops.shape(image)

  allowed_types = [dtypes.float16, dtypes.float32, dtypes.float64]
  if op.inputs[0].dtype in allowed_types:
    # pylint: disable=protected-access
    grad0 = gen_image_ops.crop_and_resize_grad_image(grad,
                                                     op.inputs[1],
                                                     op.inputs[2],
                                                     image_shape,
                                                     T=op.get_attr("T"))
    # pylint: enable=protected-access
  else:
    grad0 = None

  grad1 = gen_image_ops.crop_and_resize_grad_boxes(grad, op.inputs[0],
                                                   op.inputs[1], op.inputs[2])

  return [grad0, grad1, None, None]


@ops.RegisterGradient("Resample")
def _ResampleGrad(op, grad):
  """The derivatives for OpenCV resizing.

  Args:
    op: The Resample op.
    grad: The tensor representing the gradient w.r.t. the output.

  Returns:
    The gradients w.r.t. the input.
  """
  allowed_types = [dtypes.float32, dtypes.float64]
  grad0 = None
  if op.inputs[0].dtype in allowed_types:
    # pylint: disable=protected-access
    grad0 = gen_image_ops.resample_grad(
        grad,
        op.inputs[0],
        bicubic=op.get_attr("bicubic"),
        antialias=op.get_attr("antialias"))
    # pylint: enable=protected-access
  return [grad0, None]

@ops.RegisterGradient("RoiPooling")
def _RoiPoolingGrad(op, grad, _):
  allowed_types = [dtypes.float32, dtypes.float64]
  data_grad = None
  if op.inputs[0].dtype in allowed_types:
    data = op.inputs[0]
    rois = op.inputs[1]
    argmax = op.outputs[1]
    pooled_height = op.get_attr('pooled_height')
    pooled_width = op.get_attr('pooled_width')
    spatial_scale = op.get_attr('spatial_scale')

    data_grad = gen_image_ops.roi_pooling_grad(data, rois, argmax, grad, 
                          pooled_height=pooled_height, 
                          pooled_width=pooled_width, 
                          spatial_scale=spatial_scale)
  return [data_grad, None]

@ops.RegisterGradient("RoiUnpooling")
def _RoiUnpoolingGrad(op, grad):
  allowed_types = [dtypes.float32, dtypes.float64]
  data_grad = None
  if op.inputs[0].dtype in allowed_types:
    feat = op.inputs[0]
    rois = op.inputs[1]
    data_height = op.get_attr('pooled_height')
    data_width = op.get_attr('pooled_width')
    spatial_scale = op.get_attr('spatial_scale')
    batch_size = op.get_attr('batch_size')

    data_grad = gen_image_ops.roi_pooling_grad(
                          feat, rois, grad, 
                          data_height=pooled_height, 
                          data_width=pooled_width, 
                          spatial_scale=spatial_scale,
                          batch_size=batch_size)
  return [data_grad, None]