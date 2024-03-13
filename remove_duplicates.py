import argparse
import os
import validators
from config import *
from download_video import download_video
from bg_modeling import capture_slides_bg_modeling
from frame_differencing import capture_slides_frame_diff
from post_process import remove_duplicates
from utils import create_output_directory, convert_slides_to_pdf


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This script is used to convert video frames into slide PDFs."
    )
    parser.add_argument(
        "-f", "--folder", help="Path to the image folder", type=str
    )
    parser.add_argument(
        "-hf",
        "--hash-func",
        help="Hash function to use for image hashing. Only effective if post-processing is enabled",
        default=HASH_FUNC,
        choices=["dhash", "phash", "ahash"],
        type=str,
    )
    parser.add_argument(
        "-hs",
        "--hash-size",
        help="Hash size to use for image hashing. Only effective if post-processing is enabled",
        default=HASH_SIZE,
        choices=[8, 12, 16],
        type=int,
    )
    parser.add_argument(
        "--threshold",
        help="Minimum similarity threshold (in percent) to consider 2 images to be similar. Only effective if post-processing is enabled",
        default=SIM_THRESHOLD,
        choices=range(80, 101),
        type=int,
    )
    parser.add_argument(
        "-q",
        "--queue-len",
        help="Number of history images used to find out duplicate image. Only effective if post-processing is enabled",
        default=HASH_BUFFER_HISTORY,
        type=int,
    )
    args = parser.parse_args()

    queue_len = args.queue_len
    hash_size = args.hash_size
    hash_func = HASH_FUNC_DICT.get(args.hash_func)
    sim_threshold = args.threshold

    diff_threshold = int(hash_size * hash_size * (100 - sim_threshold) / 100)
    remove_duplicates(
        args.folder, hash_size, hash_func, queue_len, diff_threshold
    )

