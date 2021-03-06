import time
import uuid
import os
import numpy as np
import tensorflow as tf
from tensorflow.python.ops.rnn import dynamic_rnn
from lstm import LSTMCell, BNLSTMCell, orthogonal_initializer
from tensorflow.examples.tutorials.mnist import input_data

batch_size = 100
hidden_size = 100

mnist = input_data.read_data_sets("/tmp3/vicky/", one_hot=True)

x = tf.placeholder(tf.float32, [None, 784])
training = tf.placeholder(tf.bool)

x_inp = tf.expand_dims(x, -1)
lstm = BNLSTMCell(hidden_size, training) #LSTMCell(hidden_size)

#c, h
initialState = (
    tf.random_normal([batch_size, hidden_size], stddev=0.1),
    tf.random_normal([batch_size, hidden_size], stddev=0.1))

outputs, state = dynamic_rnn(lstm, x_inp, initial_state=initialState, dtype=tf.float32)

_, final_hidden = state

W = tf.get_variable('W', [hidden_size, 10], initializer=orthogonal_initializer())
b = tf.get_variable('b', [10])

y = tf.nn.softmax(tf.matmul(final_hidden, W) + b)

y_ = tf.placeholder(tf.float32, [None, 10])

cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))

optimizer = tf.train.AdamOptimizer()
gvs = optimizer.compute_gradients(cross_entropy)
capped_gvs = [(None if grad is None else tf.clip_by_value(grad, -1., 1.), var) for grad, var in gvs]
train_step = optimizer.apply_gradients(capped_gvs)

correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

init = tf.initialize_all_variables()

sess = tf.Session()
sess.run(init)

current_time = time.time()
print("Using population statistics (training: False) at test time gives worse results than batch statistics")

for i in range(100000):
    batch_xs, batch_ys = mnist.train.next_batch(batch_size)
    loss, _ = sess.run([cross_entropy, train_step], feed_dict={x: batch_xs, y_: batch_ys, training: True})
    step_time = time.time() - current_time
    current_time = time.time()
    if i % 5 == 0:
        batch_xs, batch_ys = mnist.validation.next_batch(batch_size)
        sess.run(accuracy, feed_dict={x: batch_xs, y_: batch_ys, training: False})
        #for v in tf.all_variables():
        #    print v.name
        print 'mean befor bn'
        print sess.run('rnn/BNLSTMCell/c/b_mean:0')
        print 'mean after bn'
        print sess.run('rnn/BNLSTMCell/c/bn_mean:0')
    print(i,loss, step_time)
