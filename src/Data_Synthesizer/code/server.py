from fastapi import FastAPI, APIRouter, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
import numpy as np
import re
import os
import sys
import pandas as pd
from contextlib import asynccontextmanager
import uvicorn

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)


# --- Application Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for resource loading"""
    # Load model and data
    try:
        from src.component.customer import AdvancedIncomeModel
        app.state.model = AdvancedIncomeModel.load("../model/income_model.pkl")
        training_data = pd.read_csv("../data/cleaned_income_data.csv")
        app.state.valid_zipcodes = training_data["Zipcode"].dropna().astype(int).unique().tolist()
    except Exception as e:
        raise RuntimeError(f"Initialization failed: {str(e)}")
    yield
    # Cleanup resources
    app.state.model = None
    app.state.valid_zipcodes = []


app = FastAPI(lifespan=lifespan)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models ---
class GenerationRequest(BaseModel):
    input_text: str = Field(..., alias="input", example="Generate 50 profiles with zipcode 20001")


class ProfileResponse(BaseModel):
    profiles: List[Dict]
    generated_count: int
    warnings: Optional[List[str]] = None


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None


# --- Router Setup ---
router = APIRouter()
# --- Helper Functions ---
def parse_user_input(user_input: str) -> tuple[int, Optional[int]]:
    """Parse user input to extract generation parameters"""
    num_profiles = 100
    zipcode = None

    # Extract number of profiles
    num_match = re.search(r"(\d+)\s*(?:customer|profile)", user_input, re.IGNORECASE)
    if num_match:
        num_profiles = int(num_match.group(1))

    # Validate number range
    if not 1 <= num_profiles <= 1000:
        raise ValueError("Number of profiles must be between 1 and 1000")

    # Extract zipcode (5-digit validation)
    zip_match = re.search(r"zipcode\s*(\d{5})", user_input, re.IGNORECASE)
    if zip_match:
        zipcode = int(zip_match.group(1))
        if zipcode not in app.state.valid_zipcodes:
            raise ValueError(f"Invalid zipcode: {zipcode}. Supported: {app.state.valid_zipcodes[:5]}...")

    return num_profiles, zipcode


# --- API Endpoints ---
@router.post(
    "/generate",
    response_model=ProfileResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def generate_profiles(
        request_data: GenerationRequest = Body(...)
):
    """Generate synthetic customer profiles based on natural language input"""
    try:
        # Input validation
        if not re.search(r"(generate|create|make)\s+(\d+)?\s*(customer|profile)",
                         request_data.input_text,
                         re.IGNORECASE):
            raise HTTPException(
                status_code=400,
                detail="Invalid command format. Use: 'Generate [X] profiles [with zipcode YYYYY]'"
            )

        # Parse parameters
        num_profiles, zipcode = parse_user_input(request_data.input_text)

        # Generate data
        synthetic_data = app.state.model.generate(num_profiles)
        synthetic_data.columns = synthetic_data.columns.str.lower()

        # Apply zipcode filter
        warnings = []
        if zipcode:
            if 'zipcode' not in synthetic_data.columns:
                raise HTTPException(
                    status_code=500,
                    detail="Zipcode field missing in generated data"
                )

            filtered_data = synthetic_data[synthetic_data["zipcode"] == zipcode]
            if len(filtered_data) == 0:
                warnings.append(f"No profiles for zipcode {zipcode}")
                return ProfileResponse(
                    profiles=synthetic_data.to_dict(orient="records"),
                    generated_count=len(synthetic_data),
                    warnings=warnings
                )

            synthetic_data = filtered_data

        return ProfileResponse(
            profiles=synthetic_data.to_dict(orient="records"),
            generated_count=len(synthetic_data)
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )


# --- Application Assembly ---
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="100.25.28.66",  # Listen on all network interfaces
        port=8888,
        log_level="debug"
    )