# AIChemist

Beginner-friendly portfolio and broker-style **simulation** features (Streamlit + Plotly).  
**Not** connected to real brokerages or market data.

## Run locally

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

Open <http://localhost:8501>.

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. In [Streamlit Community Cloud](https://share.streamlit.io), **New app** → select the repo, main file **`app.py`**, branch (e.g. `main`).

`requirements.txt` is used automatically for dependencies.
