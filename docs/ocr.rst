:github_url: https://github.com/KarlTDebiec/scinoephile

Optical Character Recognition
-----------------------------

.. automodule:: scinoephile.ocr
    :no-members:

.. autosummary::
    :nosignatures:

    scinoephile.ocr.OCRBase
    scinoephile.ocr.OCRDataset
    scinoephile.ocr.LabeledOCRDataset
    scinoephile.ocr.TrainOCRDataset
    scinoephile.ocr.TestOCRDataset
    scinoephile.ocr.ImageSubtitleDataset
    scinoephile.ocr.ImageSubtitleSeries
    scinoephile.ocr.ImageSubtitleEvent
    scinoephile.ocr.Model
    scinoephile.ocr.AutoTrainer

Base Classes
____________

OCR Base
````````
.. autoclass:: scinoephile.ocr.OCRBase

Data Structures
_______________

OCR Images
``````````

Base Dataset
............
.. autoclass:: scinoephile.ocr.OCRDataset

Labeled Dataset
...............
.. autoclass:: scinoephile.ocr.LabeledOCRDataset

Train Dataset
.............
.. autoclass:: scinoephile.ocr.TrainOCRDataset


Test Dataset
............
.. autoclass:: scinoephile.ocr.TestOCRDataset

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

Model
.....
.. autoclass:: scinoephile.ocr.Model

AutoTrainer
...........
.. autoclass:: scinoephile.ocr.AutoTrainer

Functions
_________

.. autofunction:: scinoephile.ocr.center_char_img
.. autofunction:: scinoephile.ocr.generate_char_data

