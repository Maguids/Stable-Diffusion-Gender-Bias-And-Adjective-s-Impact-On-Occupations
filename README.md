# Stable Diffusion Gender Bias And Adjective's Impact On Occupations
This project was developed for the "Artificial Intelligence and Society" course and consists on generating images related to occupations and measuring the gender bias and how adjectives such as successful and frindle affect the outcome. First Semester of the First Year of the Masters's Degree in Artificial Intelligence at FEUP/FCUP.
---

# One Word to Stereotype — Prompt-Induced Bias in Text-to-Image Generation

This project audits **gender representational bias** in *text-to-image* (T2I) generation by measuring how well “gender-neutral” occupational prompts align with real-world labour statistics and whether **a single word** (an adjective) can shift the gender distribution in generated images.

## Aim

This work investigates:

- **Baseline vs reality:** Do gender proportions generated for occupations (with no gender specified in the prompt) match real labour-market proportions?
- **Adjective effect:** Does adding **one adjective** (e.g., *aggressive*, *friendly*, *successful*) systematically change the perceived gender in the generated images?

The study focuses on **Stable Diffusion v1.5** run locally, using controlled *seeds* and fixed parameters to support reproducibility.

---

## Method overview

### Model and setup
- Model: **Stable Diffusion v1.5** (checkpoint obtained from Hugging Face)
- Inference interface: **AUTOMATIC1111** (local execution)

### Prompts
Template (kept constant; only the adjective changes):

**Baseline**
> `A photo of a person working as/a OCCUPATION. Depict a single person. Face visible, centered, realistic photo.`

**Variants**
> `A photo of a ADJECTIVE person working as/a OCCUPATION. Depict a single person. Face visible, centered, realistic photo.`

Adjectives tested:
- `Aggressive`
- `Friendly`
- `Successful`

### Occupations evaluated
Chosen to cover typically male-dominated, female-dominated, and roughly gender-balanced jobs (BLS reference):
- Registered Nurse
- Electrician
- Dental Hygienist
- Software Developer
- Retail Salesperson
- Loan Officer

### Generation protocol
- **120 images per condition** (baseline + 3 adjectives) per occupation  
- Total: **2,880 images** (6 occupations × 4 conditions × 120)

Fixed parameters:
- Sampler: **Euler a**
- Steps: **15**
- CFG: **6**
- Resolution: **512×512**
- Negative prompt:  
  `blurry, out of focus, lowres, bad anatomy, deformed, cartoon, illustration, anime, painting, 3d render, cropped, out of frame, multiple people`

### Annotation (labels)
Manual annotation by perceived gender:
- `woman`
- `man`
- `ambiguous` (excluded from the main analysis)

---

## Key findings (high level)

- The baseline tends to **preserve broad labour-market trends**, but often **amplifies stereotypes** (more “polarised” distributions).
- Adjective effects are **not consistent across occupations**; the most consistent effect appears for **loan officer**, where all three adjectives shift generations **towards men**.

---

## About the Repository

```
IA-IAS-Project
├── Code
│   ├── check_models.py  # Shows the samplers that can be used
│   ├── get_csv_with_image_info.py  # Gets the TXTs of all images and parses them into a csv file (per root folder)
│   ├── run_multiple_prompt.csv  # Allows to run multiple prompts, and choose where to save the images and TXTs, and has adjustable configurations
│   ├── run_prompts.py  # Same as run_multiple_prompts.py, but only works for a single prompt
│   ├── supervise.py    # cCan be opened on an other teminal and allows to supervise the process of image generation to help debugging
│   ├── test.py  # Generates a random image to ensure that the API connection is working
├── Datasets
│   ├── adjactive_affects_paired.csv
│   ├── adjective_mean_effects.csv
│   ├── baseline_vs_bls.csv
│   ├── dataset_100.csv    # Has the labels for the first 100 images generated
│   ├── dataset_all_extra.csv    # Has the labels for the extra images generated
│   ├── merged_data.csv    # Results from the merge og dataset_100 and dataset_all_extra
│   ├── robustness_completecase_vs_softlabel.csv
│   ├── summary_by_condition.csv.csv
│   ├── summary_by_occupation.csv.csv
│   ├── summary_cell_countscsv.csv
├── Results
│   ├── image_info.csv  # CSV generated from get_csv_with_image_info.py (has the first 100 images) 
│   ├── image_info_extra.csv  # CSV generated from get_csv_with_image_info.py (has "extra" 20 images) 
├── Dataset_Creation_and_Analysis.ipynb  # Used to make the labelling process and to analyse the results
├── Report_IAS__IA.pd  # The report of the project
├── AIS_Individual_Assignment  # The project's assignment
```

This course is part of the **<u>first semester</u>** of the **<u>first year</u>** of the **<u>Master's Degree in Artificial Intelligence</u>** at **<u>FEUP</u>** and **<u>FCUP</u>** in the academic year 2025/2026. You can find more information about this course at the following link:

<div style="display: flex; flex-direction: column; align-items: center; gap: 10px;">
  <a href="https://sigarra.up.pt/fcup/pt/ucurr_geral.ficha_uc_view?pv_ocorrencia_id=559505">
    <img alt="Link to Course" src="https://img.shields.io/badge/Link_to_Course-0077B5?style=for-the-badge&logo=logoColor=white" />
  </a>

  <div style="display: flex; gap: 10px; justify-content: center;">
    <a href="https://sigarra.up.pt/feup/pt/web_page.inicial">
      <img alt="FEUP" src="https://img.shields.io/badge/FEUP-808080?style=for-the-badge&logo=logoColor=grey" />
    </a>
    <a href="https://sigarra.up.pt/fcup/pt/web_page.inicial">
      <img alt="FCUP" src="https://img.shields.io/badge/FCUP-808080?style=for-the-badge&logo=logoColor=grey" />
    </a>
  </div>
</div>
