# Scinoephile Data

## Cantonese

`hanzi_to_jyutping.cha` contains Jyutping Cantonese romanization of selected characters
not included in the
[Hong Kong Cantonese Corpus](http://compling.hss.ntu.edu.sg/hkcancor/) used by 
`pycantonese`.

## OCR

`Blocks-12.1.0.txt` lists the block ranges for Unicode.

`characters.txt` contains frequency data for 9933 Chinese characters originating from
(Da, Jun. 2004. A corpus-based study of character and bigram frequencies in  Chinese
e-texts and its implications for Chinese language instruction. The studies on the theory
and methodology of the digitized Chinese teaching to foreigners. Proceedings of the 4th
International Conference on New Technologies in Teaching and Learning Chinese, ed. by
Zhang, Pu, Tianwei Xie and Juan Xu, 501-511. Beijing: The Tsinghua University Press)
[http://lingua.mtsu.edu/academic/dajun-4thtech.pdf]

### ML-Based Character Validation

The OCR validation system supports ML-based character validation using the Hugging Face
model `saudadez/rec_chinese_char`. This feature can be enabled by passing 
`use_ml_validation=True` to the validation functions:

```python
from scinoephile.lang.zho import validate_zho_ocr
from scinoephile.image.subtitles import ImageSeries

# Load your image series
series = ImageSeries.load("path/to/subtitles")

# Validate with ML-based character validation
validated_series = validate_zho_ocr(
    series,
    interactive=False,
    use_ml_validation=True
)
```

When enabled, after bounding boxes are determined and matched to characters, the ML
model validates each character to ensure the OCR text matches what the model predicts
from the image. Mismatches are logged for review.

Note: Using ML validation requires downloading the model on first use, which may take
some time and requires an internet connection.

