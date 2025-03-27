import test_api_streamlit as st
import pandas as pd
import numpy as np
import re
import os
import sys
import streamlit as st

# Add the project root directory to sys.path so we can import your model.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

# Load the model.
try:
    from src.component.customer import AdvancedIncomeModel

    model_path = os.path.abspath("../model/income_model.pkl")
    model = AdvancedIncomeModel.load(model_path)
except Exception as e:
    st.error(f"Error loading the model: {str(e)}")
    st.stop()

# Load training data for valid zipcodes.
try:
    training_data = pd.read_csv("../data/cleaned_income_data.csv")
    valid_zipcodes = training_data["Zipcode"].dropna().astype(int).unique()
except Exception as e:
    st.error(f"Error loading training data: {str(e)}")
    valid_zipcodes = []

def parse_user_input(user_input):
    """
    Parse user input to extract the number of profiles and zipcode.
    """
    num_profiles = 100
    zipcode = None

    # Extract number of profiles (e.g., "Generate 10 customer profile")
    num_match = re.search(r"(\d+)\s*(?:customer|profile)", user_input, re.IGNORECASE)
    if num_match:
        num_profiles = int(num_match.group(1))

    # Extract zipcode (5-digit validation)
    zip_match = re.search(r"zipcode\s*(\d{5})", user_input, re.IGNORECASE)
    zipcode = int(zip_match.group(1)) if zip_match else None

    return num_profiles, zipcode

# Streamlit UI
st.title("Synthetic Customer Profile Generator")
st.write("Enter a command to generate synthetic profiles. For example:")
st.code("Generate 10 customer profile with zipcode 12345", language="bash")

# Text input for the user command.
user_input = st.text_input("Command", value="Generate 10 customer profile")

if st.button("Generate Profiles"):
    # Validate the command format.
    if not re.search(r"(generate|create|make)\s+(\d+)?\s*(customer|profile)", user_input, re.IGNORECASE):
        st.error("Invalid command format. Please use: 'Generate [X] profiles [with zipcode YYYYY]'")
    else:
        try:
            num_profiles, zipcode = parse_user_input(user_input)
            if num_profiles < 1 or num_profiles > 1000:
                st.error("Number of profiles must be between 1 and 1000")
            else:
                # If a zipcode is provided, verify that it's in the valid list.
                if zipcode and zipcode not in valid_zipcodes:
                    st.error(f"Invalid zipcode: {zipcode}. Supported zipcodes: {', '.join(map(str, valid_zipcodes))}")
                else:
                    # Generate the synthetic data.
                    synthetic_data = model.generate(num_profiles)
                    synthetic_data.columns = synthetic_data.columns.str.lower()

                    if zipcode:
                        if "zipcode" not in synthetic_data.columns:
                            st.error("Zipcode field missing in generated data")
                        else:
                            filtered_data = synthetic_data[synthetic_data["zipcode"] == zipcode]
                            if filtered_data.empty:
                                st.warning(f"No profiles generated for zipcode {zipcode}. Showing all generated data.")
                            else:
                                synthetic_data = filtered_data

                    st.write(f"Generated {len(synthetic_data)} profiles:")
                    st.dataframe(synthetic_data)
        except Exception as e:
            st.error(f"Generation failed: {str(e)}")
