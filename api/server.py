from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import json
import shutil
import asyncio
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path to import from your existing code
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.append(backend_dir)

# Load environment variables
load_dotenv(os.path.join(backend_dir, '.env'))

# Verify API keys are available
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

if not openai_api_key and not anthropic_api_key:
    print("WARNING: No API keys found! Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
else:
    api_services = []
    if openai_api_key:
        api_services.append("OpenAI")
    if anthropic_api_key:
        api_services.append("Anthropic")
    print(f"Found API keys for: {', '.join(api_services)}")

# Import your existing orchestrator
from orchestrator import run as run_workflow

app = FastAPI()

# Configure CORS to allow requests from your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store job status in memory (in production, use a proper database)
job_status = {}

def cleanup_files(plot_dir, pdf_file):
    """
    Clean up the visual plots directory and PDF file
    """
    # Cleanup visual plots directory
    if os.path.exists(plot_dir):
        try:
            shutil.rmtree(plot_dir)
            print(f"Cleaned up visual plots directory: {plot_dir}")
        except Exception as e:
            print(f"Error cleaning up visual plots directory: {str(e)}")
    
    # Cleanup PDF file
    if os.path.exists(pdf_file):
        try:
            os.remove(pdf_file)
            print(f"Cleaned up PDF file: {pdf_file}")
        except Exception as e:
            print(f"Error cleaning up PDF file: {str(e)}")

@app.post("/upload")
async def upload_json(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload a JSON file and start the budget analysis process
    """
    # Check if file is a JSON
    if not file.filename.endswith('.json'):
        raise HTTPException(400, detail="Only JSON files are allowed")
    
    try:
        # Clean up any previous files before starting a new job
        plot_dir = os.path.join(backend_dir, "visual plots")
        pdf_file = os.path.join(backend_dir, "final_budget_report.pdf")
        cleanup_files(plot_dir, pdf_file)
        
        # Save the uploaded file directly to the backend directory as input_data.json
        input_path = os.path.join(backend_dir, "input_data.json")
        
        # Save the uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate the JSON structure
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
                
            # Check for required fields
            required_keys = ["revenue", "expenditure", "inflation", "gdp_growth"]
            for key in required_keys:
                if key not in data:
                    raise HTTPException(400, detail=f"Missing required key in JSON: {key}")
        except json.JSONDecodeError:
            raise HTTPException(400, detail="Invalid JSON format")
        
        # Generate a job ID
        job_id = f"job_{len(job_status) + 1}"
        job_status[job_id] = {"status": "processing"}
        
        # Start the processing in the background
        background_tasks.add_task(process_json, job_id, input_path)
        
        return {"job_id": job_id, "status": "processing"}
    
    except Exception as e:
        raise HTTPException(500, detail=str(e))

async def process_json(job_id: str, input_path: str):
    """
    Background task to process the JSON file using the existing workflow
    """
    try:
        # Make sure we're in the backend directory for any relative paths
        original_dir = os.getcwd()
        os.chdir(backend_dir)
        
        # Running your existing workflow
        result = await run_workflow()
        
        # Return to original directory
        os.chdir(original_dir)
        
        if result["status"] == "success":
            # The result might contain a long text description instead of just the path
            # So we check if the expected PDF file exists
            expected_pdf_path = os.path.join(backend_dir, "final_budget_report.pdf")
            
            if os.path.exists(expected_pdf_path):
                report_path = expected_pdf_path
            elif "report_path" in result and os.path.exists(result["report_path"]):
                report_path = result["report_path"]
            else:
                # Try to extract the filename from the text
                import re
                path_match = re.search(r"'([^']+\.pdf)'", str(result.get("report_path", "")))
                if path_match:
                    report_path = os.path.join(backend_dir, path_match.group(1))
                    if not os.path.exists(report_path):
                        report_path = None
                else:
                    report_path = None
            
            if report_path and os.path.exists(report_path):
                job_status[job_id] = {
                    "status": "completed", 
                    "report_path": report_path,
                    "summary": result.get("workflow_summary", {})
                }
            else:
                job_status[job_id] = {
                    "status": "failed", 
                    "error": "PDF report file not found"
                }
        else:
            job_status[job_id] = {
                "status": "failed", 
                "error": result.get("reason", "Unknown error")
            }
    except Exception as e:
        job_status[job_id] = {"status": "failed", "error": str(e)}

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Check the status of a processing job
    """
    if job_id not in job_status:
        raise HTTPException(404, detail="Job not found")
    
    return job_status[job_id]

@app.get("/download/{job_id}")
async def download_report(job_id: str, background_tasks: BackgroundTasks):
    """
    Download the generated PDF report
    """
    if job_id not in job_status:
        raise HTTPException(404, detail="Job not found")
    
    job = job_status[job_id]
    if job["status"] != "completed":
        raise HTTPException(400, detail=f"Report not ready. Current status: {job['status']}")
    
    report_path = job["report_path"]
    if not os.path.exists(report_path):
        raise HTTPException(404, detail="Report file not found")
    
    # Schedule cleanup for after the file is downloaded
    # We delay cleanup to ensure the download completes
    plot_dir = os.path.join(backend_dir, "visual plots")
    
    # We'll copy the PDF to a temporary file so we can delete the original
    temp_dir = tempfile.mkdtemp()
    temp_pdf = os.path.join(temp_dir, "budget_report.pdf")
    shutil.copy2(report_path, temp_pdf)
    
    # Schedule cleanup to happen after response is sent
    background_tasks.add_task(
        lambda: (
            cleanup_files(plot_dir, report_path),
            shutil.rmtree(temp_dir) if os.path.exists(temp_dir) else None
        )
    )
    
    return FileResponse(
        path=temp_pdf,
        filename="budget_report.pdf",
        media_type="application/pdf"
    )

@app.get("/api-status")
async def check_api_status():
    """
    Check the status of API keys
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    status = {
        "openai": {
            "available": bool(openai_api_key),
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-2024-08-06") if openai_api_key else None
        },
        "anthropic": {
            "available": bool(anthropic_api_key),
            "model": os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307") if anthropic_api_key else None
        },
        "preferred": "anthropic" if anthropic_api_key else "openai" if openai_api_key else None
    }
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)