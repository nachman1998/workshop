import os
import numpy as np
import argparse


def unify_npy(dir_path,out_file):
    concat_list = []
    for filename in os.listdir(dir_path):
        path = os.path.join(dir_path, filename)

        if os.path.isfile(path) and filename.endswith(".npy"):
            print(path)
            concat_list.append(np.load(path))
    dataset = np.concatenate(concat_list,axis=0)
    np.save(out_file, dataset)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='unify npys in dir.'
    )
    parser.add_argument('--input_dir',      required=True,       help='Path to npys dir')
    parser.add_argument('--output_name', required=True, )
    args = parser.parse_args()
    unify_npy(
        args.input_dir,
        args.output_name
    )