import asyncio
import logfire
from dotenv import load_dotenv
import json

# Import agent runner functions
from agents.data_manager_agent import run_data_manager_agent
from agents.budget_agent import run_budget_agent
from agents.tax_policy_agent import run_tax_policy_agent
from agents.report_agent import run_report_agent

# Load environment variables
load_dotenv()

async def run_workflow():
    """
    Orchestrates the workflow by running agents in sequence and passing data between them.
    """
    print("Starting Ministry of Finance workflow...")
    
    # Step 1: Run Data Manager Agent to validate data and create visualizations
    print("Step 1: Running Data Manager Agent...")
    data_manager_result = await run_data_manager_agent()
    print(f"Data Manager Agent completed. Result: {data_manager_result}")
    
    # Verify data is valid before proceeding
    if isinstance(data_manager_result, dict) and data_manager_result.get("data_valid") is False:
        print("Error: Input data failed validation. Stopping workflow.")
        return {"status": "failed", "reason": "Data validation failed"}
    
    # Step 2: Run Budget Agent to generate projections and risk analysis
    print("Step 2: Running Budget Agent...")
    budget_result = await run_budget_agent()
    print(f"Budget Agent completed. Result type: {type(budget_result).__name__}")
    
    # Extract projections and risk level from budget agent result
    if not isinstance(budget_result, dict):
        print(f"Error: Budget Agent returned {type(budget_result).__name__} instead of dictionary")
        return {"status": "failed", "reason": f"Budget Agent returned invalid data type: {type(budget_result).__name__}"}
    
    print(f"Budget result keys: {list(budget_result.keys())}")
    
    if "projections" not in budget_result:
        print("Error: Budget Agent did not return 'projections' key")
        return {"status": "failed", "reason": "Budget data missing 'projections'"}
        
    if "risk_ranking" not in budget_result:
        print("Error: Budget Agent did not return 'risk_ranking' key")
        return {"status": "failed", "reason": "Budget data missing 'risk_ranking'"}
    
    projections = budget_result["projections"]
    risk_level = budget_result["risk_ranking"]
    
    # Step 3: Run Tax Policy Agent to create tax slabs
    print("Step 3: Running Tax Policy Agent...")
    tax_result = await run_tax_policy_agent()
    print(f"Tax Policy Agent completed. Result type: {type(tax_result).__name__}")
    
    # Extract tax slabs from tax agent result
    if not isinstance(tax_result, dict):
        print(f"Error: Tax Policy Agent returned {type(tax_result).__name__} instead of dictionary")
        return {"status": "failed", "reason": f"Tax Policy Agent returned invalid data type: {type(tax_result).__name__}"}
    
    print(f"Tax result keys: {list(tax_result.keys())}")
    
    if "recommended_slabs" not in tax_result:
        print("Error: Tax Policy Agent did not return 'recommended_slabs' key")
        return {"status": "failed", "reason": "Tax data missing 'recommended_slabs'"}
    
    tax_slabs = tax_result["recommended_slabs"]
    
    # Step 4: Run Report Agent to compile final report
    print("Step 4: Running Report Agent...")
    report_result = await run_report_agent(
        projections=projections,
        risk_level=risk_level,
        tax_slabs=tax_slabs,
        visual_plots_dir="visual plots"
    )
    print(f"Report Agent completed. Result: {report_result}")
    
    # Handle the report result, which might be a string or dictionary
    report_path = None
    if isinstance(report_result, dict) and "report_path" in report_result:
        report_path = report_result["report_path"]
    elif isinstance(report_result, str):
        # If the result is a string, it might be the path directly
        report_path = report_result
        # Check if it's a JSON string
        try:
            parsed = json.loads(report_result)
            if isinstance(parsed, dict) and "report_path" in parsed:
                report_path = parsed["report_path"]
        except:
            # Not a JSON string, use as is
            pass
    
    # Return the final result with status information
    return {
        "status": "success",
        "report_path": report_path,
        "workflow_summary": {
            "data_validation": data_manager_result,
            "budget_projections": "completed",
            "risk_level": risk_level,
            "tax_slabs_count": len(tax_slabs)
        }
    }

# Main function to run the orchestrator
async def run():
    try:
        logfire.configure(send_to_logfire='if-token-present')
        result = await run_workflow()
        print(f"Workflow complete: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        print(f"Error in workflow: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    asyncio.run(run())