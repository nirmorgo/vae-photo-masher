'''
This file contains all the net architecture functions
'''

import tensorflow as tf
from tensorflow.contrib.layers import conv2d, conv2d_transpose, fully_connected

def build_full_conv_autoencoder(self):
    # encoder
    with tf.variable_scope('conv1'):
        conv1 = _conv_inst_norm(self.X, num_filters=32, filter_size=9, strides=1)
    with tf.variable_scope('conv2'):
        conv2 = _conv_inst_norm(conv1, num_filters=32, filter_size=3, strides=2)
    with tf.variable_scope('conv3'):
        conv3 = _conv_inst_norm(conv2, num_filters=32, filter_size=3, strides=2)
    with tf.variable_scope('conv4'):
        conv4 = _conv_inst_norm(conv3, num_filters=32, filter_size=3, strides=2)
    with tf.variable_scope('res_block1'):
        resid1 = _residual_block(conv4, filter_size=3, filter_num=32)
    with tf.variable_scope('res_block2'):
        resid2 = _residual_block(resid1, filter_size=3, filter_num=32)
    
    # embedded space
    self.z = resid2

    # decoder
    with tf.variable_scope('res_block3'):
        resid3 = _residual_block(self.z, filter_size=3, filter_num=32)
    with tf.variable_scope('res_block4'):
        resid4 = _residual_block(resid3, filter_size=3, filter_num=32)
    with tf.variable_scope('upsample1'):
        upsample1 = _upsample(resid4, num_filters=32, filter_size=3, strides=2)
    with tf.variable_scope('upsample2'):
        upsample2 = _upsample(upsample1, num_filters=32, filter_size=3, strides=2)
    with tf.variable_scope('upsample3'):
        upsample3 = _upsample(upsample2, num_filters=32, filter_size=3, strides=2)
    with tf.variable_scope('smoothing'):
        self.net_out = _conv_inst_norm(upsample3, num_filters=3, filter_size=3, strides=1, relu=False)


def build_vae_128(self):
    '''
    build a variational autoencoder with convolutional layers instance norms.
    the input image size must be 128 X 128
    '''
    # encoder
    with tf.variable_scope('Encoder'):
        with tf.variable_scope('conv1'):
            net = _conv_inst_norm(self.X, num_filters=32, filter_size=9, strides=1)
        with tf.variable_scope('conv2'):
            net = _conv_inst_norm(net, num_filters=32, filter_size=3, strides=2)
        with tf.variable_scope('res_block1'):
            net = _residual_block(net, filter_size=3, filter_num=32)
        with tf.variable_scope('conv3'):
            net = _conv_inst_norm(net, num_filters=32, filter_size=3, strides=2)
        with tf.variable_scope('res_block2'):
            net = _residual_block(net, filter_size=3, filter_num=32)   
        with tf.variable_scope('conv4'):
            net = _conv_inst_norm(net, num_filters=32, filter_size=3, strides=2)
        with tf.variable_scope('res_block3'):
            net = _residual_block(net, filter_size=3, filter_num=32)
        with tf.variable_scope('conv5'):
            conv_out = _conv_inst_norm(net, num_filters=32, filter_size=3, strides=2)
        with tf.variable_scope('Flatten'):
            encoder_out = tf.layers.flatten(conv_out)
        
    # embedded space
    with tf.variable_scope('embedded_space'):
        self.z_mu = fully_connected(encoder_out, 128, activation_fn=None, scope='z_mean')
        self.z_log_sigma_sq = fully_connected(encoder_out, 128, activation_fn=None, scope='z_sigma')
        eps = tf.random_normal(shape=tf.shape(self.z_log_sigma_sq), mean=0, stddev=1, dtype=tf.float32)
        self.z = self.z_mu + tf.sqrt(tf.exp(self.z_log_sigma_sq)) * eps

    # decoder
    with tf.variable_scope('Decoder'):
        with tf.variable_scope('reshape'):
            net = fully_connected(self.z, 2048)
            net = tf.reshape(net, (tf.shape(net)[0], 8, 8, 32))
        with tf.variable_scope('deconv1'):
            net = _upsample(net, num_filters=32, filter_size=3, strides=2)
        with tf.variable_scope('deconv2'):
            net = _upsample(net, num_filters=32, filter_size=3, strides=2)
        with tf.variable_scope('res_block4'):
            net = _residual_block(net, filter_size=3, filter_num=32)
        with tf.variable_scope('res_block5'):
            net = _residual_block(net, filter_size=3, filter_num=32)
        with tf.variable_scope('deconv3'):
            net = _upsample(net, num_filters=32, filter_size=3, strides=2)
        with tf.variable_scope('upsample4'):
            net = _upsample(net, num_filters=32, filter_size=3, strides=2)
        with tf.variable_scope('smoothing'):
            self.net_out = _conv_inst_norm(net, num_filters=3, filter_size=3, strides=1, relu=False)


def build_conv_vae_32(self):
    '''
    build a variational autoencoder with convolutional layers instance norms.
    '''
    # encoder
    with tf.variable_scope('conv1'):
        net = conv2d(self.X, 64, 9, 1, padding='SAME')
    with tf.variable_scope('conv2'):
        net = conv2d(net, 64, 3, 2, padding='SAME')
    with tf.variable_scope('conv3'):
        net = conv2d(net, 64, 3, 2, padding='SAME')
    with tf.variable_scope('conv4'):
        net = conv2d(net, 64, 3, 1, padding='SAME')
    with tf.variable_scope('conv5_1'):
        self.z_mu = conv2d(net, 64, 3, 1, padding='SAME')
    with tf.variable_scope('conv5_2'):
        self.z_log_sigma_sq = conv2d(net, 64, 3, 1, padding='SAME')
    
    # embedded space
    with tf.variable_scope('embedded_space'):
        eps = tf.random_normal(shape=tf.shape(self.z_log_sigma_sq), mean=0, stddev=1, dtype=tf.float32)
        self.z = self.z_mu + tf.sqrt(tf.exp(self.z_log_sigma_sq)) * eps

    # decoder
    with tf.variable_scope('conv6'):
        net = conv2d(self.z, 64, 3, 1, padding='SAME')
    with tf.variable_scope('conv7'):
        net = conv2d(net, 64, 3, 1, padding='SAME')
    with tf.variable_scope('upsample1'):
        net = _upsample(net, 64, filter_size=3, strides=2, inst_norm=False)
    with tf.variable_scope('upsample2'):
        net = _upsample(net, 64, filter_size=3, strides=2, inst_norm=False)
    with tf.variable_scope('smoothing'):
        net = conv2d(net, 3, 3, 1, padding='SAME',activation_fn=None)
        self.net_out = net


def build_cifar10_vae(self):
    # encoder
    with tf.variable_scope('conv1'):
        net = conv2d(self.X, 3, 4, 2, padding='SAME', activation_fn=tf.nn.relu)
    with tf.variable_scope('conv2'):
        net = conv2d(net, 64, 4, 2, padding='SAME', activation_fn=tf.nn.relu)
    with tf.variable_scope('conv3'):
        net = conv2d(net, 64, 4, 2, padding='SAME', activation_fn=tf.nn.relu)
    with tf.variable_scope('flatten'):
        net = tf.layers.flatten(net)
    with tf.variable_scope('dense1_1'):
        self.z_mu = tf.layers.dense(net, units=128)
    with tf.variable_scope('dense1_2'):
        self.z_log_sigma_sq = tf.layers.dense(net, units=128)
    
    # embedded space
    with tf.variable_scope('embedded_space'):
        eps = tf.random_normal(shape=tf.shape(self.z_log_sigma_sq), mean=0, stddev=1, dtype=tf.float32)
        self.z = self.z_mu + tf.exp(self.z_log_sigma_sq) * eps
    
    # decoder
    with tf.variable_scope('dense2'):
        net = tf.layers.dense(self.z, units=4*4*64)
    with tf.variable_scope('reshape'):
        net = tf.reshape(net, [-1, 4, 4, 64])
    with tf.variable_scope('deconv1'):
        net = tf.layers.conv2d_transpose(net, 64, 4, 2, padding='SAME', activation=tf.nn.relu)
    with tf.variable_scope('deconv2'):
        net = tf.layers.conv2d_transpose(net, 64, 4, 2, padding='SAME', activation=tf.nn.relu)
    with tf.variable_scope('deconv3'):
        net = tf.layers.conv2d_transpose(net, 3, 4, 2, padding='SAME', activation=tf.nn.relu)
    
    self.net_out = tf.nn.sigmoid(net)
        

def _conv_inst_norm(net, num_filters, filter_size, strides, relu=True, name='conv2d'):
    net = conv2d(net, num_filters, filter_size, 
                                         strides, padding='SAME', 
                                         activation_fn=None,
                                         scope=name)
    net = _instance_norm(net)
    if relu:
        net = tf.nn.relu(net)

    return net

def _deconv_inst_norm(net, num_filters, filter_size, strides, relu=True, name='conv2d'):
    net = conv2d_transpose(net, num_filters, filter_size, 
                                                    strides, padding='SAME', 
                                                    activation_fn=None,
                                                    scope=name)
    net = _instance_norm(net)
    if relu:
        net = tf.nn.relu(net)

    return net

def _residual_block(net, filter_size=3, filter_num=128):
    tmp = _conv_inst_norm(net, filter_num, filter_size, 1, name='conv2d_1')
    return net + _conv_inst_norm(tmp, filter_num, filter_size, 1, relu=False, name='conv2d_2')


def _instance_norm(net, train=True):
    with tf.variable_scope('instance_norm'):
        _, _, _, channels = [i.value for i in net.get_shape()]
        var_shape = [channels]
        mu, sigma_sq = tf.nn.moments(net, [1,2], keep_dims=True)
        shift = tf.Variable(tf.zeros(var_shape))
        scale = tf.Variable(tf.ones(var_shape))
        epsilon = 1e-3
        normalized = (net-mu)/(sigma_sq + epsilon)**(.5)
        out = scale * normalized + shift
    return out


def _upsample(net, num_filters, filter_size, strides, inst_norm=True):
    H = tf.shape(net)[1]
    W = tf.shape(net)[2]
    net = tf.image.resize_nearest_neighbor(net,(H*strides, W*strides),
                                               align_corners=False, name='resize')
    net = conv2d(net, num_filters, filter_size, 1, padding='SAME',
                 activation_fn=None, scope='conv2d')
    if inst_norm:
        net = _instance_norm(net)
    return tf.nn.relu(net)