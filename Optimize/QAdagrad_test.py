"""
Test for Quantized Adagrad optimizer.
A simple net is trained with QAdagrad and tf.train.AdagradOptimizer. After some iterations, the outputs of both nets are compared. If both outputs are equal, the test is successful.
"""

import tensorflow as tf
import numpy as np
from TensorQuant.Quantize import Quantizers
import QAdagrad

from tensorflow.python.ops import standard_ops

input_width = input_height =3
batch_size = 2
input_channels = 2
train_iterations = 10
fixed_size=16
fixed_prec=8

inputs_vals = np.arange(input_width*input_height*input_channels*batch_size).reshape(batch_size,input_width,input_height,input_channels)
#inputs_vals = np.ones((batch_size,input_width,input_height,input_channels))

inputs = tf.Variable(inputs_vals,dtype=tf.float32)
gold_inputs = tf.Variable(inputs_vals,dtype=tf.float32)

quantizer=Quantizers.NoQuantizer()
#quantizer=Quantizers.FixedPointQuantizer_nearest(8,4)
quantization=Quantizers.FixedPointQuantizer_nearest(fixed_size,fixed_prec)

optimizer = QAdagrad.QAdagradOptimizer(0.1,quantizer=quantizer)
output = quantization.quantize(inputs * 2)
loss = tf.nn.l2_loss(output-inputs)
grads_vars = optimizer.compute_gradients(loss)
train = optimizer.apply_gradients(grads_vars)

gold_optimizer = tf.train.AdagradOptimizer(0.1)
gold_output = quantization.quantize(gold_inputs * 2)
gold_loss = tf.nn.l2_loss(gold_output-gold_inputs)
gold_grads_vars = gold_optimizer.compute_gradients(gold_loss)
gold_train = gold_optimizer.apply_gradients(gold_grads_vars)


with tf.Session() as sess:
  sess.run(tf.global_variables_initializer())
  for i in range(train_iterations):
    sess.run(train)
    sess.run(gold_train)
  gold_result=gold_output.eval().flatten()
  result=output.eval().flatten()

#print(gold_result)
#print(result)


failed=False
for i in range(len(result)):
    if result[i] != gold_result[i]:
        failed = True
        break

print('QAdagrad test:')
if failed:
    print('---failed!---')
else:
    print('+++passed!+++')

