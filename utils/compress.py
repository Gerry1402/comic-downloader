from io import BytesIO
from pathlib import Path

from PIL import Image


def equal_widths(image1: bytes, image2: bytes) -> bool:
    try:
        with Image.open(BytesIO(image1)) as img1, Image.open(BytesIO(image2)) as img2:
            return img1.width == img2.width
    except Exception:
        return False

def transform_image(input: bytes | Path, output: Path | None = None) -> bytes | None:

    options = {"format": "WEBP", "quality": 99, "optimize": True, "subsampling": 0}

    def transform_path(input: Path, output: Path) -> None:
        with Image.open(input) as img:
            output = output / input.parent.parent / input.parent / input.with_suffix(".webp").name
            output.parent.mkdir(parents=True, exist_ok=True)
            img.convert("RGB").save(output, **options)

    def transform_bytes(input: bytes) -> bytes:
        input_buffer = BytesIO(input)
        output_buffer = BytesIO()
        with Image.open(input_buffer) as img:
            img.convert("RGB").save(output_buffer, **options)
            return output_buffer.getvalue()

    if isinstance(input, Path):
        if not output:
            raise ValueError("Output path must be provided when input is a Path")
        transform_path(input, output)
    elif isinstance(input, bytes):
        return transform_bytes(input)
