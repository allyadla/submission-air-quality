# Air Quality Analysis Dashboard 

Proyek analisis data menggunakan **Beijing Multi-Site Air Quality Dataset** (12 stasiun pemantauan, periode 2013-2017), mencakup proses data wrangling, exploratory data analysis (EDA), geospatial analysis, clustering/binning, hingga dashboard interaktif menggunakan Streamlit.

## Setup Environment - Anaconda

```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App

```
streamlit run dashboard.py
```

Dashboard juga dapat diakses secara online melalui Streamlit Cloud:
🔗 [Air Quality Dashboard](https://submission-air-quality-wlpasyfiqwdcvz9b3selps.streamlit.app/)

## Struktur Proyek

```
├── dashboard/
│   ├── dashboard.py          # Script utama dashboard Streamlit
│   └── main_data.csv.gz      # Dataset hasil cleaning (terkompresi)
├── data/                     # Dataset mentah (12 file CSV per stasiun)
├── notebook.ipynb            # Notebook proses analisis data lengkap
├── requirements.txt          # Daftar library yang dibutuhkan
└── README.md
```

## Sumber Data

Beijing Multi-Site Air Quality Dataset, berisi data kualitas udara per jam (PM2.5, PM10, SO2, NO2, CO, O3) beserta data cuaca (TEMP, PRES, DEWP, RAIN, WSPM) dari 12 stasiun pemantauan di Beijing periode Maret 2013 - Februari 2017.
