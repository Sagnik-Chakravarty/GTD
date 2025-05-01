# GTD
# Media-Aware Global Terrorism Index (GTI-ML)

This repository contains the code, data pipeline, and visualizations for an interpretable machine learning alternative to the Global Terrorism Index (GTI). Unlike the traditional GTI, which relies on fixed-weight formulas derived from incident and fatality counts, this model incorporates both event data and media framing to provide a more context-sensitive assessment of terrorism impact.

---

## 🔍 Overview

**Why this project?**

The original GTI does not consider how terrorism is portrayed in the media—leading to potential overestimation or underestimation of terrorism severity in different countries. This project addresses that limitation by combining:
- **Structured event data** from the [Global Terrorism Database (GTD)](https://www.start.umd.edu/gtd)
- **Framing classification** of news articles from international media (Al Jazeera, Reuters, The Washington Post)

---

## 🧠 Key Features

- **Framing Classifier**: Trained a decision tree using 1,000 hand-labeled news articles to identify five framing types: `Terrorism`, `State Violence`, `Insurgency`, `Freedom Fighter`, `Neutral`.
- **GTI Modeling**: Built a random forest regression model combining GTD indicators and aggregated framing ratios per country.
- **Fairness + Interpretability**: Incorporated residual analysis, confusion matrices, and local feature attribution to assess framing bias and media impact.
- **Visual Outputs**: Global GTI maps, rank comparisons, residuals, ROC curves, and feature importance plots.

---

## 📂 Project Structure

```text
.
├── data/                   # Cleaned datasets and GTI ranking CSV
├── notebooks/             # Jupyter/Rmd files for analysis and training
├── scripts/               # Core scripts for scraping, labeling, and modeling
├── figures/               # All plots and maps used in the paper
├── models/                # Trained models and prediction outputs
├── paper/                 # Final LaTeX report and PDF
└── README.md              # This file
