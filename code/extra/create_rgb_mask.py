from PIL import Image
import numpy as np
from scipy.ndimage import binary_dilation

def create_rgb_mask(bg_mask, epi_mask, output_path):
    # Load masks as grayscale numpy arrays
    bg = np.array(Image.open(bg_mask).convert("L"))
    epi = np.array(Image.open(epi_mask).convert("L"))

    # Binary threshold
    bg_bin = bg < 128       # True where background mask is black
    epi_bin = epi > 128     # True where epithelial mask is white

    # 30-pixel dilation of epithelial region (outside border)
    epi_border = binary_dilation(epi_bin, iterations=150) & ~epi_bin

    # Create base RGB mask (light green background)
    rgb = np.zeros((*bg.shape, 3), dtype=np.uint8)
    rgb[:] = (150, 255, 150)  # light green

    # Apply colors by priority
    # 1️⃣ Epithelial region (light blue)
    rgb[epi_bin] = (150, 150, 255)
    # 2️⃣ Border around epithelial region (dark blue)
    rgb[epi_border] = (255, 255, 150)
    # 3️⃣ Background black region (light red)
    rgb[bg_bin & ~epi_bin & ~epi_border] = (255, 150, 150)

    # Save RGB mask
    Image.fromarray(rgb).save(output_path)
    print(f"Saved RGB mask → {output_path}")

if __name__ == "__main__":

    bg_mask = "data/hari_BC/bg_mask/White_cohort/BRST_AAAAEO_2014MMDD_FW01_HE_WSI_RE--_00_3000_3000.png"
    epi_mask = "data/hari_BC/otsu/epi_mask_no_bg/White_cohort/BRST_AAAAEO_2014MMDD_FW01_HE_WSI_RE--_00_3000_3000.png"
    output_path = "rgb_mask.png"

    create_rgb_mask(bg_mask, epi_mask, output_path)