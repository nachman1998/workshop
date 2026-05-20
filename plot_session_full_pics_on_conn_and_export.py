#!/usr/bin/env python
"""
plot_session.py
Given a CSV file (output of generic_parser.py) and a 5-tuple filter
(src_ip, src_port, dst_ip, dst_port, protocol), plots a 2D histogram
for each matching session using sessions_plotter.py.

All filter args are optional — only the ones you provide are matched.

Examples:
    # Full 5-tuple
    python plot_session.py --input c2.csv --src-ip 10.0.0.7 --src-port 54503 --dst-ip 142.250.75.142 --dst-port 443 --proto UDP

    # Just src_ip + dst_port
    python plot_session.py --input c2.csv --src-ip 10.0.0.7 --dst-port 443

    # Just protocol — plots ALL UDP sessions
    python plot_session.py --input c2.csv --proto TCP

    # Save plots instead of showing
    python plot_session.py --input c2.csv --src-ip 10.0.0.7 --save ./plots

    # Also show spectrogram alongside histogram
    python plot_session.py --input c2.csv --dst-port 443 --spectogram
"""

import csv
import argparse
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

MTU=1500
BMU=1500
All=True
TPS = 60 # TimePerSession in secs
DELTA_T = 60 # Delta T between splitted sessions
MIN_TPS = 50
bin_len = 5


def matches_filter(row, src_ip, src_port, dst_ip, dst_port, proto):
    """Return True if row matches all provided (non-None) filter values."""
    checks = [
        (src_ip,   row[1]),
        (src_port, row[2]),
        (dst_ip,   row[3]),
        (dst_port, row[4]),
        (proto,    row[5]),
    ]
    return all(fval is None or fval == rval for fval, rval in checks)


def plot_sessions(csv_path, src_ip, src_port, dst_ip, dst_port, proto, show_spectogram=False, save_dir=None):

    matches = []

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if len(row) < 9:
                continue
            if All==False:
                if not matches_filter(row, src_ip, src_port, dst_ip, dst_port, proto):
                    continue

            try:
                length = int(row[7])
            except ValueError:
                continue

            if length < 2:
                continue

            ts    = np.array([x for x in row[8:8+length] if x], dtype=float)
            sizes = np.array([x for x in row[9+length:]  if x], dtype=int)

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

    for idx, s in enumerate(matches):
        dataset = []
        counter = 0

        ts = s['ts']
        sizes = s['sizes']
        label = (f"{s['src_ip']}:{s['src_port']} -> "
                 f"{s['dst_ip']}:{s['dst_port']} "
                 f"[{s['proto']}]  packets={s['length']}")
        print(f"  Session {idx+1}: {label}")

        for t in range(int(ts[-1] / DELTA_T - TPS / DELTA_T) + 1):
            mask = ((ts >= t * DELTA_T) & (ts <= (t * DELTA_T + TPS)))
            # print t * DELTA_T, t * DELTA_T + TPS, ts[-1]
            ts_mask = ts[mask]
            sizes_mask = sizes[mask]
            print("ts_mask[0]", ts_mask[0],"ts_mask[-1]", ts_mask[-1])

            if len(ts_mask) > 10:

                tps = 60
                if tps is None:
                    max_delta_time = ts_mask[-1] - ts_mask[0]

                else:
                    max_delta_time = tps

                bin_len = 10

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
            raw_name = (
                f"{s['src_ip']}-{s['src_port']} -> "
                f"{s['dst_ip']}-{s['dst_port']} "
                f"[{s['proto']}]  packets={s['length']}"
            )

            safe_name = (
                raw_name
                .replace(":", ".")
                .replace("->", "_to_")
                .replace("/", "_")
                .replace("\\", "_")
            )
            np.save(  safe_name, dataset)








if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plot 2D histogram for sessions matching a 5-tuple filter.'
    )
    parser.add_argument('--input',      required=True,       help='Path to CSV file')
    parser.add_argument('--src-ip',     default=None,        help='Filter by source IP')
    parser.add_argument('--src-port',   default=None,        help='Filter by source port')
    parser.add_argument('--dst-ip',     default=None,        help='Filter by destination IP')
    parser.add_argument('--dst-port',   default=None,        help='Filter by destination port')
    parser.add_argument('--proto',      default=None,        help='Filter by protocol (TCP/UDP)')
    parser.add_argument('--spectogram', action='store_true', help='Also show spectrogram for each session')
    parser.add_argument('--save',       default=None,        help='Directory to save plots (instead of showing)')

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: file not found: {args.input}")
        sys.exit(1)

    if not (any([args.src_ip, args.src_port, args.dst_ip, args.dst_port, args.proto])) and All==False:
        print("Error: provide at least one filter (--src-ip, --src-port, --dst-ip, --dst-port, --proto)")
        sys.exit(1)

    plot_sessions(
        csv_path        = args.input,
        src_ip          = args.src_ip,
        src_port        = args.src_port,
        dst_ip          = args.dst_ip,
        dst_port        = args.dst_port,
        proto           = args.proto,
        show_spectogram = args.spectogram,
        save_dir        = args.save,
    )
