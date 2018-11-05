:github_url: https://github.com/KarlTDebiec/scinoephile

Development
-----------

Implement Optical Character Recognition for Reading Blu-Ray Subtitles
_____________________________________________________________________

- [x] Fix font support on new macos and matplotlib
- [x] Update GeneratedOCRDataset's generate_training_data
- [x] Update GeneratedOCRDataset's gen_add_img
- [x] Review Subtitle and ImageSubtitle Data Structures
- [x] Review OCR Datasets
- [x] Update OCR Datasets' save
- [x] Update OCR Datasets' load
- [x] Confirm that both 8-bit and 1-bit workflows work
- [x] Review and update AutoTrainer
- [x] Save model and reload
- [x] Extend generate_training_data to check for minimal number of images
- [x] Have AutoTrainer accept OCR Datasets rather than building its own
- [x] Switch from storing each image as a 1D 6400 array to 2D 80x80 array
- [x] Convert OCRDataset to an abstract class
- [x] ImageSubtitleSeries: Collected char_data
- [x] Re-implement test data, take ImageSubtitleDataset and use to populate
- [x] Move AutoTrainer's model to a Model
- [x] Make base classes abstract
- [x] Move image mode property to a subclass of OCRBaseClass
- [ ] Check model accuracy on test data
- [ ] Calculate differences between test images and generated images
- [ ] Add log output to AutoTrainer
- [ ] Re-implement support for configuring AutoTrainer
- [ ] Add support for Western characters and punctuation
- [ ] ImageSubtitleEvent: Identify spaces in subtitle images

Migrate Compositor to New Data Structures
_________________________________________

- [ ] Print SubtitleSeries and SubtitleDataset as pandas DataFrames
- [ ] Migrate English, Chinese (may call Hanzi for clarity, and bilingual
  subtitles to SubtitleSeries

Documentation
_____________

- [x] Configure GitHub Pages documentation
- [ ] Document Base and CLToolBase
- [ ] Document Subtitle Data Structures
- [ ] Document Image Subtitle Data Structures
- [ ] Document OCRBase and OCRCLToolBase
- [ ] Document OCR Data Structures
- [ ] Document Training tool

Miscellaneous
_____________

- [ ] Make clearer whether functions are acting on Images or image data
- [ ] Visualize weights
- [ ] Extend generate_training_data to add set number of images rather than use total
- [ ] Convenience function for viewing source of method/property in IPython
- [ ] Track modifications, and if infile==outfile only save if changed

Future Projects
_______________

- Improve requirements.txt and clarify what is required for which functions
- Automated testing using pytest and TravisCI
- Sphinx checklist extension to convert "- [ ]" to "☐" and "- [X]" to "☑"
