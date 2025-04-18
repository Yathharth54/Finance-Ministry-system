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

async def main():
    TAX_POLICY_SYS_PROMPT = """
    <agent_role>
    You are the Tax Policy Agent for the Ministry of Finance system. Your task is to recommend new tax slabs based on budget projections.
    
    Follow these steps exactly:
    1. First use project_tool to generate the budget projections
    2. Then immediately use the output from project_tool as input to slabs_tool by calling slabs_tool(projections=...) with the projections data
    
    Your final output must be a JSON object with a key "recommended_slabs" containing the tax slabs returned by slabs_tool.
    </agent_role>
    """
    
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
    
    prompt = "Create tax slabs based on budget projections."
    
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
    
    logfire.configure(send_to_logfire='if-token-present')
    result = await TA_agent.run(user_prompt=prompt)
    print(result.data)

if __name__ == "__main__":
    asyncio.run(main())