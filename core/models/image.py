from io import BytesIO

from PIL import Image as PImage


class Image:
    format: str = "WEBP"
    quality: int = 99
    optimize: bool = True
    subsampling: int = 0

    @classmethod
    def transform_image(cls, input: bytes) -> bytes | None:
        input_buffer = BytesIO(input)
        output_buffer = BytesIO()
        with PImage.open(input_buffer) as img:
            img.convert("RGB").save(output_buffer, **vars(cls))
            return output_buffer.getvalue()

    @staticmethod
    def equal_widths(img1: bytes, img2: bytes) -> bool:
        with PImage.open(BytesIO(img1)) as i1, PImage.open(BytesIO(img2)) as i2:
            return i1.width == i2.width
