import asyncio
import logfire
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from agent_factory import get_text_model_instance

# Import tools
from skills.tax_slab_tool import create_tax_slabs
from skills.budget_projection_tool import project_budget

# Load environment variables
load_dotenv()

TAX_POLICY_SYS_PROMPT = """
<agent_role>
You are the Tax Policy Agent for the Ministry of Finance system. Your task is to recommend new tax slabs based on budget projections.

Follow these steps exactly:
1. First use project_tool to generate the budget projections
2. Then immediately use the output from project_tool as input to slabs_tool by calling slabs_tool(projections=...) with the projections data

Your final output must be a JSON object with a key "recommended_slabs" containing the tax slabs returned by slabs_tool.
</agent_role>
"""

def create_tax_policy_agent():
    TA_model = get_text_model_instance()
    
    TA_agent = Agent(
        model=TA_model,
        name="Tax Agent",
        system_prompt=TAX_POLICY_SYS_PROMPT,
        retries=3,
        model_settings=ModelSettings(
            temperature=0.5,
            max_tokens=2000
        ),
    )
    
    @TA_agent.tool_plain
    def project_tool() -> dict:
        """Generate budget projections that will be used for tax slab calculation"""
        return project_budget(file_path="input_data.json")
    
    @TA_agent.tool_plain
    def slabs_tool(projections: dict) -> list:
        """Create tax slabs based on the provided projections data"""
        if not projections:
            print("Error: Empty projections data provided to slabs_tool")
            return []
            
        # Explicitly print what we received to debug
        print(f"Received projections for tax slab creation: {type(projections)}")
        
        return create_tax_slabs(projections=projections)
    
    return TA_agent

async def run_tax_policy_agent():
    agent = create_tax_policy_agent()
    prompt = "Create tax slabs based on budget projections."
    
    # logfire.configure(send_to_logfire='if-token-present')
    result = await agent.run(user_prompt=prompt)
    
    # Ensure we're returning the correct data structure
    if not isinstance(result.data, dict):
        print("Warning: Tax agent didn't return a dictionary, creating proper structure")
        # Call the tools directly to ensure we have the data
        projections = project_budget(file_path="input_data.json")
        slabs = create_tax_slabs(projections=projections)
        return {
            "recommended_slabs": slabs
        }
    
    # If the result is missing the expected key
    if "recommended_slabs" not in result.data:
        print("Warning: Tax agent response missing required keys, fixing structure")
        
        # Try to find the slabs in the result
        if isinstance(result.data, dict) and any(isinstance(result.data.get(key), list) for key in result.data):
            # Find the first list value and use it as slabs
            for key, value in result.data.items():
                if isinstance(value, list):
                    return {"recommended_slabs": value}
        
        # If no list is found, call the tools directly
        projections = project_budget(file_path="input_data.json")
        slabs = create_tax_slabs(projections=projections)
        return {
            "recommended_slabs": slabs
        }
    
    return result.data

if __name__ == "__main__":
    result = asyncio.run(run_tax_policy_agent())
    print("Tax Agent result:", result)
    print("Result contains recommended_slabs:", "recommended_slabs" in result)