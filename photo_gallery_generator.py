import argparse
import dataclasses
import logging
import os
import shutil
import sys

from PIL import Image
from jinja2 import Template
from queue import PriorityQueue

import utils
from photo_compressor import PhotoCompressor

logger = logging.getLogger(__name__)


@dataclasses.dataclass(order=True)
class _ColumnMetadata:
    height: float
    index: int
    image_names: list


class PhotoGalleryGenerator:
    def __init__(self, src_photos_dir: str, dest_gallery_dir: str, compress_factor: float) -> None:
        self.src_photos_dir = src_photos_dir
        self.dest_gallery_dir = dest_gallery_dir
        self.raw_photos_dir = f"{dest_gallery_dir}/raw_photos"
        self.compressed_photos_dir = f"{dest_gallery_dir}/compressed_photos"
        self.photo_compressor = PhotoCompressor(
            src=self.raw_photos_dir,
            dest=self.compressed_photos_dir,
            compress_factor=compress_factor,
        )

    def generate(self):
        # self.raw_photos()
        # self.compressed_photos()
        self.html()
        self.stylesheet()
        self.javascript()

    def _order_photos_column_heights(self):
        image_names = os.listdir(self.compressed_photos_dir)
        image_names.sort()
        column1 = _ColumnMetadata(0.001, 1, [])
        column2 = _ColumnMetadata(0.002, 2, [])
        column3 = _ColumnMetadata(0.003, 3, [])
        columns = {
            1: column1,
            2: column2,
            3: column3,
        }
        columns_by_height = PriorityQueue()
        columns_by_height.put(column1)
        columns_by_height.put(column2)
        columns_by_height.put(column3)

        for image_name in image_names:
            if "column_buffer" in image_name:
                continue
            image_path = f"{self.compressed_photos_dir}/{image_name}"
            image = Image.open(image_path)
            width_ratio = image.size[0] / 100
            height_adjusted = image.size[1] / width_ratio
            column = columns_by_height.get()
            column.height += height_adjusted
            column.image_names.append(image_name)
            columns_by_height.put(column)

        smallest_column = columns_by_height.get()
        middle_column = columns_by_height.get()
        largest_column = columns_by_height.get()

        height_diff = int(largest_column.height - smallest_column.height)
        if height_diff > 1:
            smallest_column_buffer = Image.new('RGB', (100, height_diff), color='white')
            smallest_column_buffer.save(f"{self.compressed_photos_dir}/smallest_column_buffer.jpg")
            smallest_column.height += height_diff
            smallest_column.image_names.append("smallest_column_buffer.jpg")

        height_diff = int(largest_column.height - middle_column.height)
        if height_diff > 1:
            middle_column_buffer = Image.new('RGB', (100, height_diff), color='white')
            middle_column_buffer.save(f"{self.compressed_photos_dir}/middle_column_buffer.jpg")
            middle_column.height += height_diff
            middle_column.image_names.append("middle_column_buffer.jpg")

        for i in range(1, 4):
            logger.debug(columns[i].height)
            logger.debug(len(columns[i].image_names))
            logger.debug(columns[i].image_names)

        return columns[1].image_names + columns[2].image_names + columns[3].image_names


    def html(self):
        dest_html_path = f"{self.dest_gallery_dir}/index.html"
        logger.info(f"Generating HTML at {dest_html_path}")

        images = os.listdir(self.compressed_photos_dir)
        images.sort()

        photos_str = ""
        for image_name in self._order_photos_column_heights():
            photos_str += f'            <img src="compressed_photos/{image_name}">\n'

        with open(f"template/index.html", "r") as f:
            template = Template(f.read())
            final_html = template.render(
                photos=photos_str
            )

        self._make_folder_if_not_exists(self.dest_gallery_dir)
        with open(f"{self.dest_gallery_dir}/index.html", "w") as f:
            f.write(final_html)

    def stylesheet(self):
        dest_css_path = f"{self.dest_gallery_dir}/style.css"
        logger.info(f"Generating HTML at {dest_css_path}")
        self._make_folder_if_not_exists(self.dest_gallery_dir)
        shutil.copy(f"template/style.css", dest_css_path)

    def javascript(self):
        dest_js_path = f"{self.dest_gallery_dir}/gallery.js"
        logger.info(f"Generating HTML at {dest_js_path}")
        self._make_folder_if_not_exists(self.dest_gallery_dir)
        shutil.copy(f"template/gallery.js", dest_js_path)

    def raw_photos(self):
        logger.info(f"Copying raw photos to {self.raw_photos_dir}")
        files = os.listdir(self.src_photos_dir)
        files.sort()
        self._make_folder_if_not_exists(self.raw_photos_dir)

        idx = 1
        for file in files:
            shutil.copy(f"{self.src_photos_dir}/{file}", f"{self.raw_photos_dir}/{utils.zero_pad(idx)}.jpg")
            idx += 1

    def compressed_photos(self):
        logger.info(f"Creating compressed photos to {self.compressed_photos_dir}")
        self._make_folder_if_not_exists(self.compressed_photos_dir)
        self.photo_compressor.compress_photos()

    @staticmethod
    def _make_folder_if_not_exists(folder: str) -> None:
        if not os.path.exists(folder):
            os.makedirs(folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--src-photos-dir",
        required=True,
    )
    parser.add_argument(
        "--dest-gallery-dir",
        required=True,
    )
    parser.add_argument(
        "--compress-factor",
        type=float,
        required=True,
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    generator = PhotoGalleryGenerator(args.src_photos_dir, args.dest_gallery_dir, args.compress_factor)
    generator.generate()
