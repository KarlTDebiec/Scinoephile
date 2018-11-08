:github_url: https://github.com/KarlTDebiec/scinoephile

Development
-----------

Optical Character Recognition
_____________________________

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
- [x] Apply model to chars extracted from individual subtitle
- [x] Reconstruct text from predictions
- [x] Apply model to complete subtitle series and reconstruct text
- [x] Save reconstructed subtitles to srt
- [x] Verify that subtitle series images can be saved to png files
- [x] Reconstruct including spaces
- [ ] Calculate diff between training images and test images to guide spec selection
- [ ] Prepare small amount of test data (i.e. accuracte reconstuction)
- [ ] Calculate reconstruction accuracy against test data
- [ ] Calculate model accuracy on test data
- [ ] Add log output to AutoTrainer
- [ ] Add support for Western characters and punctuation

Compositor Rewrite
__________________

- [ ] Print SubtitleSeries, SubtitleSeries and SubtitleEvent as pandas DataFrames
- [ ] Set up framework for CompositeSubtitleDataset(Dataset)
- [ ] Set up framework for Compositor(CLToolBase, CompositeSubtitleDataset)
- [ ] Migrate English, Chinese (may call Hanzi for clarity), and bilingual subtitles to separate SubtitleSeries

Documentation
_____________

- [x] Configure GitHub Pages documentation
- [ ] Document Base and CLToolBase
- [ ] Document Subtitle Data Structures
- [ ] Document Image Subtitle Data Structures
- [ ] Document OCRBase and OCRCLToolBase
- [ ] Document OCR Data Structures
- [ ] Document Training tool
- [ ] Improve examples

Miscellaneous
_____________

- [ ] Make clearer whether functions are acting on Images or image data
- [ ] Visualize weights
- [ ] Extend generate_training_data to add set number of images rather than use total
- [ ] Convenience function for viewing source of method/property in IPython
- [ ] Track modifications, and if infile==outfile only save if changed

Future
______

- Improve requirements.txt and clarify what is required for which functions
- Automated testing using pytest and TravisCI
- Sphinx checklist extension to convert "- [ ]" to "☐" and "- [X]" to "☑"
- Replace test.py with a notebook
