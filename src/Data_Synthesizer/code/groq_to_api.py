from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json

app = FastAPI()


class TransactionRequest(BaseModel):
    customer_profile: dict
    merchant_preferences: list
    transaction_params: dict


@app.post("/api/generate-transactions")
async def generate_transactions(request: TransactionRequest):
    try:
        # Save parameters to temporary file
        with open("temp_config.json", "w") as f:
            json.dump(request.dict(), f)

        # Execute your Python script
        result = subprocess.run(
            ["python", "transaction_deepseek_synthesizer.py", "temp_config.json"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise HTTPException(500, detail=result.stderr)

        return {"transactions": json.loads(result.stdout)}

    except Exception as e:
        raise HTTPException(500, detail=str(e))