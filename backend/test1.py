import asyncio
import logfire
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from agent_factory import get_text_model_instance

# Import tools
from skills.budget_projection_tool import project_budget
from skills.risk_identification_tool import risk_identification

# Load environment variables
load_dotenv()

async def main():
    BUDGET_AGENT_SYS_PROMPT = """
    <agent_role>
    1. You are the Budget Agent for the Ministry of Finance system. Your task is to generate budget projections using the BudgetProjectionTool and then evaluate the financial risk using the RiskIdentificationTool.
    2. First, call project_tool to generate projected financial data.
    3. Then, call risk_tool and pass the projections from project_tool output as the input.
    4. Your output must be a JSON object with two keys: "projections" that holds the projected financial data and "risk_ranking" that holds the risk level (e.g., "low", "medium", "high").
    </agent_role>
    """
    
    BA_model = get_text_model_instance()
    
    BA_agent = Agent(
        model=BA_model,
        name="Budget Agent",
        system_prompt=BUDGET_AGENT_SYS_PROMPT,
        retries=3,
        model_settings=ModelSettings(
            temperature=0.5,
            max_tokens=2000
        ),
    )
    
    prompt = "Create budget projections and evaluate financial risk."
    
    # Store projections between tool calls
    projection_data = None
    
    @BA_agent.tool_plain
    def project_tool() -> dict:
        nonlocal projection_data
        projection_data = project_budget(file_path="input_data.json")
        return projection_data
    
    @BA_agent.tool_plain
    def risk_tool(projections: dict = None) -> str:
        # Use either passed projections or stored projections
        nonlocal projection_data
        data_to_use = projections or projection_data
        
        if not data_to_use:
            print("Error: No projection data available")
            return "unknown"
        
        return risk_identification(projections=data_to_use)
    
    logfire.configure(send_to_logfire='if-token-present')
    result = await BA_agent.run(user_prompt=prompt)
    print(result.data)

if __name__ == "__main__":
    asyncio.run(main())