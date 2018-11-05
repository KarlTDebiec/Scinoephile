:github_url: https://github.com/KarlTDebiec/scinoephile

Optical Character Recognition
-----------------------------

.. automodule:: scinoephile.ocr
    :no-members:

.. autosummary::
    :nosignatures:

    scinoephile.ocr.OCRBase
    scinoephile.ocr.OCRCLToolBase
    scinoephile.ocr.OCRDataset
    scinoephile.ocr.UnlabeledOCRDataset
    scinoephile.ocr.LabeledOCRDataset
    scinoephile.ocr.GeneratedOCRDataset
    scinoephile.ocr.ImageSubtitleDataset
    scinoephile.ocr.ImageSubtitleSeries
    scinoephile.ocr.ImageSubtitleEvent

Base Classes
____________

OCR Base
````````
.. autoclass:: scinoephile.ocr.OCRBase

OCR Command Line Tool Base
``````````````````````````
.. autoclass:: scinoephile.ocr.OCRCLToolBase

Data Structures
_______________

OCR Images
``````````

Base Dataset
............
.. autoclass:: scinoephile.ocr.OCRDataset

Unlabeled Dataset
.................
.. autoclass:: scinoephile.ocr.UnlabeledOCRDataset

Labeled Dataset
...............
.. autoclass:: scinoephile.ocr.LabeledOCRDataset

Generated Dataset
.................
.. autoclass:: scinoephile.ocr.GeneratedOCRDataset


Image-Based Subtitles
`````````````````````

Dataset
.......
.. autoclass:: scinoephile.ocr.ImageSubtitleDataset

Series
......

.. autoclass:: scinoephile.ocr.ImageSubtitleSeries

Event
.....

.. autoclass:: scinoephile.ocr.ImageSubtitleEvent

Machine Learning
________________

Dataset
.......
.. autoclass:: scinoephile.ocr.AutoTrainer

Functions
_________

.. autofunction:: scinoephile.ocr.center_char_img
.. autofunction:: scinoephile.ocr.generate_char_data

