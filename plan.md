# Plan

Get this working on this computer right now: make the new default character validation run end-to-end locally, then clean up correctness issues and tests. We can worry about CI/other environments later.

## Scope
- In: When validating 中文 OCR, after validating bboxes, validate the characters using this single-character OCR model: https://huggingface.co/saudadez/rec_chinese_char
- Out: changing OCR algorithms/accuracy, training new models, or adding new runtime dependencies. DO NOT WRITE ANY TESTS OR DO ANY TESTING OUTSIDE `uv run python test/data/mlamd/create_output.py`.

## Action items
[x] 1. Update `CharValidator` to handle `sub.bboxes is None` deterministically (add a warning message and skip; log messages at end).
[ ] 2. Make CharValidator download the fucking model.
  * Maybe look at what we did for Whisper under `scinoephile/audio`. I don't recall this being a fucking hour-long ordeal to code last time.
[ ] 3. Implement logic necessary for expanding bboxes.
  * Bboxes currently cover only the center of each character.
  * Bboxes should be expanded vertically to cover the full height of the subtitle.
    * We will cover multi-line subtitles later.
  * Bboxes should be expanded horizontally to the midpoint between adjacent bboxes.
    * The first and last bbox should be expanded to the edges of the subtitle.
  * The character should be extracted from the expanded bbox and centered on a 48x48 pixel white canvas.
  * This shit can all go in CharValidator in static methods and shit.
[ ] 4. Implement the loop over characters and their corresponding bboxes.
[ ] 5. Validate the first character and bbox.
[ ] 6. Figure out where to go from there.

## Development loop
* Test by running `uv run python test/data/mlamd/create_output.py`.
* Fix the shit.
* Test by running `uv run python test/data/mlamd/create_output.py`.
* Fix the shit.
* ...

## Usage sample
```python
import paddle
from paddleocr import PaddleOCR

gpu_available = paddle.device.is_compiled_with_cuda()
ocr = PaddleOCR(
    use_angle_cls=False,
    lang='ch',
    det=False,
    use_gpu=gpu_available,
    rec_model_dir='your_model_dir',  # path to this model
    rec_char_dict_path='your_model_dir/rec_custom_keys.txt',
    rec_image_shape='3,48,48',
)

result = ocr.ocr('path/to/image.jpg')
```