import argparse
from unittest import result

import numpy as np
import matplotlib.pyplot as plt

def func1(pic1, pic2):
    v1=np.sum(pic1,axis=1).reshape(-1,1).astype(np.int64)

    v2=np.sum(pic2,axis=1).reshape(-1,1).astype(np.int64)

    return np.linalg.norm(v1-v2)

def func2(pic1, pic2):
    A = np.sum(pic1,axis=1).astype(np.int64)
    B =np.sum(pic2,axis=1).astype(np.int64)
    A_norm = A / np.linalg.norm(A)
    B_norm = B / np.linalg.norm(B)
    return np.dot(A_norm, B_norm)
def func3(pic1, pic2):
    A = np.sum(pic1,axis=1).astype(np.int64)
    B =np.sum(pic2,axis=1).astype(np.int64)
    return np.dot(A, B)


def func4(arr1, arr2):
    """
    Find the column shift of arr2 that minimizes the Frobenius norm difference with arr1.

    Returns: (best_shift, min_norm)
    """
    arr1=arr1.astype(np.int64)
    arr2=arr2.astype(np.int64)
    n_cols = arr1.shape[1]
    best_shift = 0
    min_norm = np.inf

    for shift in range(n_cols):
        shifted = np.roll(arr2, shift, axis=1)
        norm = np.linalg.norm(arr1 - shifted, 'fro')**2
        if norm < min_norm:
            min_norm = norm
            best_shift = shift

    return min_norm
def func4(arr1, arr2):
    """
    Find the column shift of arr2 that minimizes the Frobenius norm difference with arr1.

    Returns: (best_shift, min_norm)
    """
    arr1=arr1.astype(np.int64)
    arr2=arr2.astype(np.int64)
    n_cols = arr1.shape[1]
    best_shift = 0
    min_norm = np.inf

    for shift in range(n_cols):
        shifted = np.roll(arr2, shift, axis=1)
        norm = np.linalg.norm(arr1 - shifted, 'fro')**2
        if norm < min_norm:
            min_norm = norm
            best_shift = shift

    return min_norm
def func4_with_plot(arr1, arr2):
    """
    Find the column shift of arr2 that minimizes the Frobenius norm difference with arr1.

    Returns: (best_shift, min_norm)
    """
    arr1=arr1.astype(np.int64)
    arr2=arr2.astype(np.int64)
    n_cols = arr1.shape[1]
    best_shift = 0
    min_norm = np.inf

    for shift in range(n_cols):
        shifted = np.roll(arr2, shift, axis=1)
        norm = np.linalg.norm(arr1 - shifted, 'fro')
        if norm < min_norm:
            min_norm = norm
            best_shift = shift

    best_shifted = np.roll(arr2, best_shift, axis=1)
    diff_before = np.abs(arr1.astype(np.int64) - arr2.astype(np.int64))
    diff_after  = np.abs(arr1.astype(np.int64) - best_shifted.astype(np.int64))

    fig, axes = plt.subplots(1, 5, figsize=(22, 4))

    # Individual
    axes[0].imshow(arr1, aspect='auto', cmap='viridis')
    axes[0].set_title('arr1 (reference)')

    axes[1].imshow(arr2, aspect='auto', cmap='viridis')
    axes[1].set_title('arr2 (before shift)')

    # Overlay BEFORE
    overlay_before = np.zeros((*arr1.shape, 3))
    overlay_before[..., 0] = (arr1 - arr1.min()) / (arr1.max() - arr1.min())
    overlay_before[..., 1] = (arr2 - arr2.min()) / (arr2.max() - arr2.min())
    axes[2].imshow(overlay_before, aspect='auto')
    axes[2].set_title('Overlay BEFORE\narr1=red  arr2=green')

    # Overlay AFTER
    overlay_after = np.zeros((*arr1.shape, 3))
    overlay_after[..., 0] = (arr1 - arr1.min()) / (arr1.max() - arr1.min())
    overlay_after[..., 1] = (best_shifted - best_shifted.min()) / (best_shifted.max() - best_shifted.min())
    axes[3].imshow(overlay_after, aspect='auto')
    axes[3].set_title(f'Overlay AFTER shift={best_shift}\narr1=red  arr2=green  norm={min_norm:.4f}')

    # Difference
    im = axes[4].imshow(diff_after, aspect='auto', cmap='hot')
    axes[4].set_title(f'|arr1 - arr2| after shift\nmax={diff_after.max()}  mean={diff_after.mean():.2f}')
    plt.colorbar(im, ax=axes[4])

    plt.tight_layout()
    plt.show()

    return min_norm

def func5(pic1, pic2):

    def compute_row_fft(pic):
        fft_shifted = np.fft.fftshift(np.fft.fft(pic, axis=1), axes=1)
        amplitudes = np.abs(fft_shifted)
        cols = pic.shape[1]
        omega_col = 2 * np.pi * np.fft.fftshift(np.fft.fftfreq(cols))
        extent = [omega_col[0], omega_col[-1], pic.shape[0], 0]
        return amplitudes, extent

    amp1, ext1 = compute_row_fft(pic1)
    amp2, ext2 = compute_row_fft(pic2)

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))

    for i, (pic, amp, ext, label) in enumerate([
        (pic1, amp1, ext1, 'pic1'),
        (pic2, amp2, ext2, 'pic2')
    ]):
        im0 = axes[i, 0].imshow(pic, cmap='viridis')
        axes[i, 0].set_title(f'Original ({label})')
        axes[i, 0].set_xlabel('Column')
        axes[i, 0].set_ylabel('Row')
        plt.colorbar(im0, ax=axes[i, 0])

        im1 = axes[i, 1].imshow(amp, cmap='hot', extent=ext, aspect='auto')
        axes[i, 1].set_title(f'Row FFT Amplitude ({label})')
        axes[i, 1].set_xlabel('ω_col (rad/sample)')
        axes[i, 1].set_ylabel('Row')
        plt.colorbar(im1, ax=axes[i, 1])

        im2 = axes[i, 2].imshow(np.log1p(amp), cmap='hot', extent=ext, aspect='auto')
        axes[i, 2].set_title(f'Row FFT Amplitude log scale ({label})')
        axes[i, 2].set_xlabel('ω_col (rad/sample)')
        axes[i, 2].set_ylabel('Row')
        plt.colorbar(im2, ax=axes[i, 2])

    plt.tight_layout()
    plt.show()

def func6(arr1, arr2):
    """
    Find the column shift of arr2 that minimizes the Frobenius norm difference with arr1.

    Returns: (best_shift, min_norm)
    """
    arr1=arr1.astype(np.int64)
    arr2=arr2.astype(np.int64)
    n_cols = arr1.shape[1]
    best_shift = 0
    max_norm = -np.inf

    for shift in range(n_cols):
        shifted = np.roll(arr2, shift, axis=1)
        cross_cor = np.sum(arr1 * shifted)
        if cross_cor > max_norm:
            max_norm = cross_cor
            best_shift = shift

    return max_norm


def test_stat_pair(pic_arr1, pic_arr2,i_eq_j=True,func=func1):
    result_arr=[]
    for i in range(0,len(pic_arr1)):
        for j in range(0,len(pic_arr2)):
            if i_eq_j==False:
                if i!=j :
                    result_arr.append(func(pic_arr1[i],pic_arr2[j]))
            else:
                result_arr.append(func(pic_arr1[i],pic_arr2[j]))
    # Stats
    mean = np.mean(result_arr)
    var = np.var(result_arr)
    std = np.std(result_arr)

    print(f"Mean:     {mean:.4f}")
    print(f"Variance: {var:.4f}")
    print(f"Std Dev:  {std:.4f}")

    # Histogram
    plt.figure(figsize=(8, 5))
    plt.hist(result_arr, bins=30, edgecolor='black', color='steelblue', alpha=0.7)
    plt.axvline(mean, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean:.4f}')
    plt.axvline(mean + std, color='orange', linestyle=':', linewidth=1.5, label=f'+1 Std: {mean + std:.4f}')
    plt.axvline(mean - std, color='orange', linestyle=':', linewidth=1.5, label=f'-1 Std: {mean - std:.4f}')
    plt.title('Distribution of Results')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.legend()
    plt.tight_layout()
    plt.show()



def test_stat_solo(pic_arr,func):
    result_arr = []
    for i in range(0, len(pic_arr)):
        result_arr.append(func(pic_arr[i]))
    # Stats
    mean = np.mean(result_arr)
    var = np.var(result_arr)
    std = np.std(result_arr)

    print(f"Mean:     {mean:.4f}")
    print(f"Variance: {var:.4f}")
    print(f"Std Dev:  {std:.4f}")

    # Histogram
    plt.figure(figsize=(8, 5))
    plt.hist(result_arr, bins=30, edgecolor='black', color='steelblue', alpha=0.7)
    plt.axvline(mean, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean:.4f}')
    plt.axvline(mean + std, color='orange', linestyle=':', linewidth=1.5, label=f'+1 Std: {mean + std:.4f}')
    plt.axvline(mean - std, color='orange', linestyle=':', linewidth=1.5, label=f'-1 Std: {mean - std:.4f}')
    plt.title('Distribution of Results')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="find mean std and plot histogram of measurements from 2 pic_array in .npy form"
    )
    parser.add_argument("--file1",   help="Path to .npy file #1")
    parser.add_argument("--file2",   help="Path to .npy file #2")
    parser.add_argument('--i_eq_j', action='store_true', default=False)
    args = parser.parse_args()
    data1 = np.load(args.file1)
    data2 = np.load(args.file2)

    test_stat_solo(data1,lambda x:np.sum(x))
    #test_stat_solo(data2, lambda x: np.sum(x))
    test_stat_pair(data1,data2,args.i_eq_j,func1)