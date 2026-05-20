"""
plot_random_2d_hists.py
-----------------------
Load a .npy file containing N 2D arrays, randomly pick X of them
(no repeats within the same figure), and display each as a scatter
/ dot plot. No state is saved between runs — every run picks fresh.

Usage
-----
    python plot_random_2d_hists.py --file data.npy --n 6

Optional flags
    --file      path to the .npy file              (default: data.npy)
    --n         number of arrays to show            (default: 4)
    --cols      columns in the subplot grid         (default: auto √n)
    --dot-size  base marker size                    (default: 4)
    --threshold only plot pixels whose value > threshold (default: 0)
"""

import argparse
import math
import random
import sys

import matplotlib.pyplot as plt
import numpy as np


def make_grid(n_plots, n_cols):
    cols = n_cols or math.ceil(math.sqrt(n_plots))
    rows = math.ceil(n_plots / cols)
    return rows, cols


def array_to_scatter(arr, threshold):
    row_idx, col_idx = np.where(arr > threshold)
    x = col_idx.astype(float)
    y = row_idx.astype(float)
    weights = arr[row_idx, col_idx]
    return x, y, weights


def main():
    parser = argparse.ArgumentParser(
        description="Plot random 2D arrays as scatter plots from .npy"
    )
    parser.add_argument("--file",      default="data.npy",  help="Path to .npy file")
    parser.add_argument("--n",         type=int, default=4, help="Number of arrays to plot")
    parser.add_argument("--cols",      type=int, default=None, help="Subplot columns")
    parser.add_argument("--dot-size",  type=float, default=4, help="Base marker size")
    parser.add_argument("--threshold", type=float, default=0, help="Min value to plot")
    args = parser.parse_args()

    # Load data
    data = np.load(args.file)
    if data.ndim != 3:
        sys.exit(f"Expected a 3-D array (N, H, W), got shape {data.shape}")
    n_total = data.shape[0]
    print(f"Loaded {n_total} arrays of shape {data.shape[1:]} from '{args.file}'")

    if args.n > n_total:
        sys.exit(f"--n ({args.n}) exceeds total arrays ({n_total})")

    # Pick unique random indices — no repeats within this figure only
    chosen = random.sample(range(n_total), args.n)
    print(f"Chosen indices: {chosen}")

    # Plot
    rows, cols = make_grid(args.n, args.cols)
    fig, axes = plt.subplots(rows, cols,
                             figsize=(cols * 5, rows * 5),
                             constrained_layout=True)
    axes_flat = np.array(axes).flatten()

    for ax_idx, arr_idx in enumerate(chosen):
        ax = axes_flat[ax_idx]
        arr = data[arr_idx]
        h, w = arr.shape
        bin_len=5
        xedges = np.linspace(0, 1400, w + 1)  # 301 values from 0 to 1400
        yedges = np.linspace(0, 1400, h + 1)  # 301 values from 0 to 1400
        mesh = ax.pcolormesh(
            xedges,  # X edges
            yedges,  # Y edges
            arr,
            cmap='hot_r',
            shading='auto'
        )

        ax.set_title(f"Index {arr_idx}")
        ax.set_aspect('equal')
        for ax in axes_flat[args.n:]:
            ax.set_visible(False)

    fig.suptitle(f"Random sample — {args.n} of {n_total} arrays", fontsize=13)

    out = "random_2d_scatter.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Saved → {out}")


if __name__ == "__main__":
    main()