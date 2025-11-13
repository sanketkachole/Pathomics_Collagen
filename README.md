# Collagen Biomarker

---

## Packages Required
Python was used for this study.<br>
The packages required for running this code are Numpy, Openslide, PIL, OpenCV, Pandas, Sklearn, Scipy, Skimage Matplotlib, tqdm.<br>


## Workflow for the study

<img src="example/workflow.png" width="600" height="400">


## Pipeline for Collagen biomarker
The main steps involved in the Collagen biomarker are as follows:
1. Preprocessing step: Extracting tiles from H&E-stained Whole Slide Images and Epithelium segmentation
2. Segment foreground and background from the tissue
3. Segment epithelium from the tissue
4. Extracting collagen features

## Visualization of collagen fibers
For visualizing collagen fibers in patches before feature extraction, transfer some patches and epi/stroma masks to seperate folders. Give the respective folder paths as input to the python file 'python code/visualize_collagen_fibers.py' for saving example collagen fiber masks in the results directory 'results/collagen_fiber_masks'

## Plotting heatmaps
For plotting heatmaps, please transfer some patches and epi masks to seperate folders. Give the respective folder paths as input to the python file 'python3 code/main_visualize_heatmaps.py' for saving example heatmaps in the results directory 'results/heatmaps_stroma' and 'results/heatmaps_peritumoral'

## Run Collagen Fiber pipeline on WSIs
If you wish to run the whole pipeline at once, you can simply run 'python code/main.py'. All the required arguments to the script are detailed in the argument parser documentation.

## Running the script step-wise
1. <b>Extracting tiles from H&E-stained Whole Slide Images</b><br>
This extracts patches from the whole slide image of size 3000x3000 pixels. Run the python file 'python code/extract_patches.py' (specify the 'input_path' to the location where whole slide images exist and 'output_path' where you want to store the patches (keep it <b>'data/patches'</b>)).<br>

2. <b>Foreground/Background Segemntation</b><br>
First run 'python code/create_tissue_mask.py' to generate the foreground mask. Which will be used as input into the epithelium segmentation thus subsequentyly run 'python code/epithelium_stroma_segmentation_no_model.py' to create patch-wise foreground/background masks of the tissue. Fatty regions are also considered in the background.
The white region is the foreground, and the black region is the background.

3. <b>Epithelium segmentation</b><br>
To segment the epithelium regions on the patches extracted in 1, run the 'python code/epithelium_stroma_segmentation_no_model.py'.
In the segmentation mask, the white regions correspond to the tumor/epithelium areas, and the black regions correspond to the rest of the patch. We will invert the background mask and combine it with the epithelium mask, and calculate the collagen feature on the black regions (the code handles everything).

4. <b>Extracting collagen features</b><br>
For extracting the collagen features, run the file (code/patchLevelFeatures.py) that generates the Collagen Fiber Orientation Disorder map for each patch extracted. The feature maps will be stored at the output path provided.
<br><br>
After obtaining the feature maps for each tile, run the file (code/patientLevelFeatures.py) that gives patient-level features (mean and maximum) for each patient, giving a total of 12 features. The features for each patient will be stored at the provided output path, which can be used for downstream tasks.<br><br>

<!-- ## Survival analysis
Using the extracted features, use the notebook 'survival_analysis.ipynb' for an example demo for running the survival analysis pipeline.


## License and Usage
Madabhushi Lab - This code is made available under Apache 2.0 with Commons Clause License and is available for non-commercial academic purposes. -->
