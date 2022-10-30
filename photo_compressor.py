import argparse
import os
from PIL import Image
import logging

import sys
logger = logging.getLogger(__name__)

class PhotoCompressor:
    def __init__(self, src: str, dest: str, compress_factor: float):
        self.src = src
        self.dest = dest
        if compress_factor <= 0 or compress_factor >= 1:
            raise ValueError(f"compress factor {compress_factor} must be between 0 and 1")
        self.compress_factor = compress_factor

    def compress_photos(self):
        paths = os.listdir(self.src)
        for path in paths:
            logger.info(f"Compressing photo {path}")
            src_path = f"{self.src}/{path}"
            dest_path = f"{self.dest}/{path}"
            image = Image.open(src_path)
            new_width = int(image.size[0] * self.compress_factor)
            new_height = int(image.size[1] * self.compress_factor)
            compressed_image = image.resize((new_width, new_height))
            compressed_image.save(dest_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--src",
        required=True,
    )
    parser.add_argument(
        "--dest",
        required=True,
    )
    parser.add_argument(
        "--compress-factor",
        type=float,
        required=True,
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    compressor = PhotoCompressor(args.src, args.dest, args.compress_factor)
    compressor.compress_photos()


