#!/usr/bin/env python


import csv
import argparse
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from numpy.ma.core import append

MTU=1500
BMU=1500
TPS = 60 # TimePerSession in secs
DELTA_T = 60 # Delta T between splitted sessions
MIN_TPS = 50
bin_len = 5


def matches_filter(row,filter_csv_pd):
    """Return True if row matches all provided (non-None) filter values."""


    for _, row_filter in filter_csv_pd.iterrows():
        checks = [
            (row_filter[0],   row[1]),#src ip
            (row_filter[1], row[2]),#src port
            (row_filter[2],   row[3]),#dest ip
            (row_filter[3], row[4]),#dest port
            (row_filter[4],    row[5]),#protocol
        ]
        if all(pd.isna(fval) or fval == rval for fval, rval in checks):
            return True
    return False


def plot_sessions(csv_path,filter_csv_pd,All,bins,out_name):
    matches = []

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if len(row) < 9:
                continue
            if All==False:
                if not matches_filter(row,filter_csv_pd):
                    continue

            try:
                length = int(row[7])
            except ValueError:
                continue

            if length < 2:
                continue

            ts = np.array(row[8:8+length], dtype=float)
            sizes = np.array(row[9+length:], dtype=int)

            if len(ts) == 0 or len(sizes) == 0:
                continue

            matches.append({
                'row'      : i,
                'filename' : row[0],
                'src_ip'   : row[1],
                'src_port' : row[2],
                'dst_ip'   : row[3],
                'dst_port' : row[4],
                'proto'    : row[5],
                'start_ts' : row[6],
                'length'   : length,
                'ts'       : ts,
                'sizes'    : sizes,
            })

    if not matches:
        print("No sessions found for the given filter.")
        return

    print(f"Found {len(matches)} session(s).\n")

    tot_ts_sizes=[]

    for idx, s in enumerate(matches):
        ts = np.array(s['ts'])
        sizes = np.array(s['sizes'])
        ts=ts+float(s['start_ts'])

        tot_ts_sizes.append(np.vstack([ts, sizes]))

    concat_filterd = np.concatenate(tot_ts_sizes, axis=1)
    concat_filterd=concat_filterd[:, concat_filterd[0].argsort()]

    dataset = []
    counter = 0
    ts = concat_filterd[0]-concat_filterd[0,0]
    sizes = concat_filterd[1]

    for t in range(int(ts[-1] / DELTA_T - TPS / DELTA_T) + 1):
        mask = ((ts >= t * DELTA_T) & (ts <= (t * DELTA_T + TPS)))
        # print t * DELTA_T, t * DELTA_T + TPS, ts[-1]
        ts_mask = ts[mask]
        sizes_mask = sizes[mask]


        if len(ts_mask) > 10:

            tps = 60
            if tps is None:
                max_delta_time = ts_mask[-1] - ts_mask[0]

            else:
                max_delta_time = tps

            bin_len = bins

            ts_norm = ((np.array(ts_mask) - ts_mask[0]) / max_delta_time) * MTU
            H, xedges, yedges = np.histogram2d(
                ts_norm,
                sizes_mask,
                bins=(
                    range(0, MTU + 1, bin_len),
                    range(0, BMU + 1, bin_len)
                )
            )

            H = (H > 0).astype(np.uint16)
            if False:
                fig, ax = plt.subplots(figsize=(7, 7))

                im = ax.pcolormesh(
                    xedges,  # X edges
                    yedges,  # Y edges
                    H.T,  # transpose because histogram2d stores x first
                    cmap='hot_r',
                    shading='auto'
                )

                plt.show()

                plt.close()
            dataset.append(H.T)
            counter += 1
            if counter % 100 == 0:
                print(counter)
    dataset = np.array(dataset)

    np.save(  out_name, dataset)
    print(out_name+" is done")








if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plot 2D histogram for sessions matching a 5-tuple filter.'
    )
    parser.add_argument('--input',      required=True,       help='Path to CSV file')
    parser.add_argument('--All', action='store_true', default=False)
    parser.add_argument("--bin", required=False,type=int,default=10)
    parser.add_argument('--filter_csv', required=False, help='Path to filer CSV file data =src_ip, src_port, dst_ip, dst_port, proto')
    parser.add_argument('--out_name', required=True, help='output npy file name')


    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: file not found: {args.input}")
        sys.exit(1)

    if not (any([args.filter_csv])) and args.All==False:
        print("Error: provide filter (--src-ip, --src-port, --dst-ip, --dst-port, --proto)")
        sys.exit(1)
    filter_df = pd.read_csv(args.filter_csv, header=None)
    filter_df=filter_df.where(pd.notna(filter_df), None)
    plot_sessions(
        csv_path        = args.input,
        filter_csv_pd=filter_df,
        All = args.All,
        bins=args.bin,
        out_name = args.out_name
    )
