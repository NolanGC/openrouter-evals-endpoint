import json
import requests
import time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from pathlib import Path
import uvicorn
import os
import yaml
import uuid
import sys
import os
from pathlib import Path
from evals import run, get_parser

# get endpoint
app = FastAPI()

@app.get("/evals")
def get_evals():
    path = "evals/evals/registry/evals"
    if not Path(path).is_dir():
        raise HTTPException(status_code=404, detail=f"The directory {path} does not exist")
    
    files = [f.split('.')[0] for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return {"evals": files} 
    
@app.post("/evals/run")
async def run_eval(request: Request):
    authorization_header = request.headers.get("Authorization")
    if not authorization_header or not authorization_header.startswith("Bearer "):
        return {"error": "Invalid authorization header"}

    api_key = authorization_header.split("Bearer ")[1].strip()
    data = await request.json()
    eval_name = data.get("eval_name")
    model = data.get("model")
    if not eval_name:
        return {"error": "Missing eval_name in request body"}
    if not model:
        return {"error": "Missing model in request body"}
    output_filename = "results/" + str(uuid.uuid4()) + ".jsonl"
    run(args=get_parser().parse_args(["openrouter/default", eval_name, "--record_path", output_filename, "--api_key", api_key, "--model", model]))
    with open(output_filename, "r") as f:
        lines = f.readlines()
    if lines:
        return lines[-1]
    else:
        raise HTTPException(status_code=500, detail="No eval response generated")
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# @app.get("/evals/{eval_id}")
# def get_eval(eval_id: str):
#     path = f"evals/evals/registry/evals/{eval_id}.yaml"
#     if not Path(path).is_file():
#         raise HTTPException(status_code=404, detail=f"The file {path} does not exist")
    
#     with open(path, 'r') as f:
#         return f.read()
    
# @app.post("/evals")
# async def create_eval(request: Request):
#     path = "evals/evals/registry/evals"
#     if not Path(path).is_dir():
#         return {"error": f"The directory {path} does not exist"}

#     try:
#         content = await request.body()
#         yaml_content = content.decode("utf-8")
#         yaml_data = yaml.safe_load(yaml_content)
        
#         # Get the first key and value in the dictionary
#         eval_name, eval_data = next(iter(yaml_data.items()), (None, {}))
#         eval_id = eval_data.get("id", "default_id") if eval_data else "default_id"
        
#         # Use eval_id as the filename
#         file_path = os.path.join(path, f"{eval_name}.yaml")

#         with open(file_path, 'w') as f:
#             f.write(yaml_content)

#         return {"message": f"Evaluation file created successfully at {file_path}"}
#     except yaml.YAMLError as e:
#         raise HTTPException(status_code=400, detail=f"YAML parsing error: {str(e)}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
# @app.post("/data/{eval_name}")
# async def create_data(eval_name: str, request: Request):
#     path = f"evals/evals/registry/data/{eval_name}"
#     os.makedirs(path, exist_ok=True)  # Create the directory if it doesn't exist

#     try:
#         # Read the request body as bytes
#         content = await request.body()

#         # Decode bytes to string
#         jsonl_content = content.decode("utf-8")

#         # Define the file name and path
#         file_path = os.path.join(path, f"samples.jsonl")

#         # Write content to file
#         with open(file_path, 'w') as f:
#             f.write(jsonl_content)

#         return {"message": f"Data file created successfully at {file_path}"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")