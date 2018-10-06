from src.data_handling import AE_data
from src.encoder import AE

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-lr', '--learning-rate', default=1e-4)
parser.add_argument('-it', '--iterations', default=500)
parser.add_argument('-b', '--batch-size', default=32)
args = parser.parse_args()

lr = float(args.learning_rate)
batch_size = int(args.batch_size)
iters = int(args.iterations)

def train(*args):
    data = AE_data()
    data.load_images_list_from_directory('data/COCO_train2017/')

    autoencoder = AE(c_l1=1e8, c_tv=1e1, c_l2=0)
    autoencoder.restore_model_from_last_checkpoint()
    autoencoder.train(data, batch_size=batch_size, iters=iters, learning_rate=lr)


if __name__ == "__main__":
    train()
