import argparse
import os
from jinja2 import Template
import logging
from photo_compressor import PhotoCompressor
import os
import shutil
import sys
logger = logging.getLogger(__name__)


class PhotoGalleryGenerator:
    def __init__(self, src_photos_dir: str, dest_gallery_dir: str, compress_factor: float) -> None:
        self.src_photos_dir = src_photos_dir
        self.dest_gallery_dir = dest_gallery_dir
        self.raw_photos_dir = f"{dest_gallery_dir}/raw_photos"
        self.compressed_photos_dir = f"{dest_gallery_dir}/compressed_photos"
        self.photo_compressor = PhotoCompressor(
            src=src_photos_dir,
            dest=self.compressed_photos_dir,
            compress_factor=compress_factor,
        )

    def generate(self):
        self.raw_photos()
        self.compressed_photos()
        self.html()
        self.stylesheet()
        self.javascript()

    def html(self):
        dest_html_path = f"{self.dest_gallery_dir}/index.html"
        logger.info(f"Generating HTML at {dest_html_path}")

        images = os.listdir(self.compressed_photos_dir)
        images.sort()

        photos_str = ""
        for image in images:
            photos_str += f'            <img src="compressed_photos/{image}">\n'

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
        self._make_folder_if_not_exists(self.raw_photos_dir)
        for file in files:
            shutil.copy(f"{self.src_photos_dir}/{file}", f"{self.raw_photos_dir}/{file}")

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
