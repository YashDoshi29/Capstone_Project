from fastapi import FastAPI, HTTPException
import arviz as az
import numpy as np
import pandas as pd
import os

app = FastAPI()

# Load traces once at startup
TRACE_DIR = "traces"
loaded_traces = {}


@app.on_event("startup")
def load_traces():
    """Loads all saved traces from the traces directory"""
    global loaded_traces
    for file in os.listdir(TRACE_DIR):
        if file.endswith(".nc"):
            zipcode = file.replace("trace_", "").replace(".nc", "")
            loaded_traces[zipcode] = az.from_netcdf(os.path.join(TRACE_DIR, file))
    print(f"Loaded {len(loaded_traces)} traces.")


@app.get("/")
def home():
    return {"message": "Bayesian Income Prediction API is running"}


@app.get("/available_zipcodes")
def get_available_zipcodes():
    """Return the list of available zipcodes"""
    return {"zipcodes": list(loaded_traces.keys())}


@app.get("/generate_data/{zipcode}")
def generate_data(zipcode: str, num_samples: int = 100):
    """Generate synthetic income data for a given zipcode"""
    if zipcode not in loaded_traces:
        raise HTTPException(status_code=404, detail="Zipcode trace not found.")

    trace = loaded_traces[zipcode]

    # Extract the posterior samples
    posterior_ds = trace.posterior
    n_draws = posterior_ds.sizes["draw"]
    random_draw_idx = np.random.randint(0, n_draws)

    # Sample from posterior
    sampled_income = np.random.normal(
        loc=float(posterior_ds["income"].values[0, random_draw_idx]),
        scale=float(posterior_ds["sigma"].values[0, random_draw_idx]),
        size=num_samples
    )

    # Convert to DataFrame
    df = pd.DataFrame({"zipcode": zipcode, "income": sampled_income})
    return df.to_dict(orient="records")

# Run with: uvicorn server:app --reload
