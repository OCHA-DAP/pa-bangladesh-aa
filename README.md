# CERF Anticipatory Action framework in Bangladesh

## Background

Building on the work by individual agencies, such as the IFRC, WFP, FAO and NGOs, the pilot will methodologically combine three components, scaling-up anticipatory humanitarian action in Bangladesh:

i) A robust forecasting embedded in a clear decision-making process (the model).
The pilot will use a government run and endorsed early warning system, combining a 10-day probabilistic flood forecast for operational readiness and a 5-day deterministic flood forecast for activation of anticipatory action. This trigger has been successfully used by IFRC and WFP in the past.
  
ii) Pre-agreed, coordinated, multi-sectoral actions that can fundamentally alter the trajectory of the crisis (the action plan).
Given the short lead times of the forecasts, cash is a major component of the pilot. Bringing together the reach of WFP and IFRC (through the BDRCS), up to 70,000 households could receive $53 each about 5 days ahead of a flood.
In addition, FAO would preposition animal fodder and vaccinate livestock against waterborne diseases. UNFPA would distribute dignity and hygiene kits, and communication material preventing sexual and gender-based violence.
In the future, other actions could be integrated, including better early warning systems or prepositioning of essential medicine. Unfortunately, due to COVID-19, these options were deemed unrealistic for the upcoming monsoon season.
An inter-agency lens would be applied to determining the selection criteria for beneficiaries to ensure the most vulnerable people benefit from the anticipatory action.

iii) Pre-arranged finance (the money).
CERF set aside around $5 million [pending final plan and confirmation] for anticipatory action for floods in
Bangladesh. This funding will become available immediately once the defined trigger is reached to active the actions described above
In addition, the pilot seeks to amplify and coordinate similar anticipatory action pilots at the agency scale, including from WFP, IFRC, and others.

## Analysis

The analysis within this repository contains two components. 

1. Processing FFWC and GLOFAS forecasting data, used to trigger this pilot's anticipatory action. 
2. Calculating historical estimates of flooding extent over time in five high priority districts (Bogra, Gaibandha, Jamalpur, Kurigram, Sirajganj). This work is largely based on an analysis of Sentinel-1 SAR imagery in Google Earth Engine, accessible [here](https://code.earthengine.google.com/0fe2c1f3b2cf8ef6fe9aa81382b00191). 

## Structure of this repository 

The content within this repository is structured as follows: 

```
├── data
│   ├── processed          <- Data that has been processed or transformed in some way.  
│   └── raw                <- Original, immutable data. 
│
├── notebooks              <- Jupyter notebooks that contain a walkthrough of data analysis steps. 
│
├── results                <- Final results. 
│   └── plots              <- Output figures. 
│
├── scripts                <- Scripts to perform data processing and analysis. 
│   │
│   ├── d01_data           <- Scripts to load in datasets. 
│   ├── d02_processing     <- Scripts to perform basic cleaning and preprocessing on data.
│   ├── d03_analysis       <- Scripts to conduct more in-depth analysis of data
│   └── d04_visualization  <- Scripts to create visualizations. 
│
├── README.md              <- Description of this project.
└── environment.yml        <- Contains dependencies to set up a conda environment. 

```

Note that larger raw and processed data files are currently not included within this repository. 

## Getting started 

Set up and activate a Python environment in Anaconda using the ```environment.yml``` file provided: 

```
conda env create -f environment.yml
conda activate bang_floods
```
