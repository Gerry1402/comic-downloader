from io import BytesIO

from PIL import Image as PILImage


class Image:
    format: str = "WEBP"
    quality: int = 99
    optimize: bool = True
    subsampling: int = 0

    @classmethod
    def transform_image(cls, input: bytes) -> bytes | None:
        input_buffer = BytesIO(input)
        output_buffer = BytesIO()
        with PILImage.open(input_buffer) as img:
            img.convert("RGB").save(output_buffer, **vars(cls))
            return output_buffer.getvalue()

    @staticmethod
    def equal_widths(image1: bytes, image2: bytes) -> bool:
        with PILImage.open(BytesIO(image1)) as img1, PILImage.open(BytesIO(image2)) as img2:
            return img1.width == img2.width
