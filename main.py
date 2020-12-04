#!/usr/bin/python
import tensorflow as tf

from config import Config
from model import CaptionGenerator
from dataset import prepare_train_data, prepare_eval_data, prepare_test_data

FLAGS = tf.app.flags.FLAGS

tf.flags.DEFINE_string('phase', 'train',
                       'The phase can be train, eval or test')

tf.flags.DEFINE_boolean('load', False,
                        'Turn on to load a pretrained model from either \
                        the latest checkpoint or a specified file')

tf.flags.DEFINE_string('model_file', None,
                       'If sepcified, load a pretrained model from this file')

tf.flags.DEFINE_boolean('load_cnn', False,
                        'Turn on to load a pretrained CNN model')

tf.flags.DEFINE_string('cnn_model_file', './vgg16_no_fc.npy',
                       'The file containing a pretrained CNN model')

tf.flags.DEFINE_boolean('train_cnn', False,
                        'Turn on to train both CNN and RNN. \
                         Otherwise, only RNN is trained')

tf.flags.DEFINE_integer('beam_size', 3,
                        'The size of beam search for caption generation')

tf.flags.DEFINE_string('namedir', '', 'The name of the directory \
                        within the phase folder containing images')


def main(argv):
    config = Config()
    config.phase = FLAGS.phase
    config.train_cnn = FLAGS.train_cnn
    config.beam_size = FLAGS.beam_size

    with tf.compat.v1.Session() as sess:
        if FLAGS.phase == 'train':
            # training phase
            config.train_image_dir = config.train_image_dir[:-1] + "_" + FLAGS.namedir + "/"

            data = prepare_train_data(config)
            model = CaptionGenerator(config)
            sess.run(tf.global_variables_initializer())
            if FLAGS.load:
                model.load(sess, FLAGS.model_file)
            if FLAGS.load_cnn:
                model.load_cnn(sess, FLAGS.cnn_model_file)
            tf.get_default_graph().finalize()
            model.train(sess, data)

        elif FLAGS.phase == 'eval':
            # evaluation phase
            config.eval_image_dir = config.eval_image_dir[:-1] + "_" + FLAGS.namedir + "/"
            config.eval_result_dir = config.eval_result_dir[:-1] + "_" + FLAGS.namedir + "/"
            config.eval_result_file = config.eval_result_file[:-5] + "_" + FLAGS.namedir + config.eval_result_file[-5:] # .json

            coco, data, vocabulary = prepare_eval_data(config)
            model = CaptionGenerator(config)
            model.load(sess, FLAGS.model_file)
            tf.get_default_graph().finalize()
            model.eval(sess, coco, data, vocabulary)

        else:
            # testing phase
            config.test_image_dir = config.test_image_dir[:-1] + "_" + FLAGS.namedir + "/"
            config.test_result_dir = config.test_result_dir[:-1] + "_" + FLAGS.namedir + "/"
            config.test_result_file = config.test_result_file[:-4] + "_" + FLAGS.namedir + config.test_result_file[-4:] # .csv

            data, vocabulary = prepare_test_data(config)
            model = CaptionGenerator(config)
            model.load(sess, FLAGS.model_file)
            tf.compat.v1.get_default_graph().finalize()
            model.test(sess, data, vocabulary)

if __name__ == '__main__':
    #tf.app.run()
    tf.compat.v1.app.run()
