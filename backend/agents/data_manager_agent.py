import asyncio
import logfire
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from agent_factory import get_text_model_instance

# Import tools
from skills.data_validation_tool import validate_data
from skills.visualization_tool import create_visual_plots_from_json

# Load environment variables
load_dotenv()

class DataManagerInput(BaseModel):
    file_path: str

DATA_MANAGER_SYS_PROMPT = """
<agent_role>
You are the Data Manager Agent for the Ministry of Finance system. Your task is to validate the input financial data using the DataValidationTool and then generate visual plots using the VisualisationTool.
</agent_role>
"""

def create_data_manager_agent():
    DMA_model = get_text_model_instance()
    
    DMA_agent = Agent(
        model=DMA_model,
        name="Data Manager Agent",
        system_prompt=DATA_MANAGER_SYS_PROMPT,
        retries=3,
        model_settings=ModelSettings(
            temperature=0.5,
            max_tokens=2000
        ),
    )
    
    @DMA_agent.tool_plain
    def validate_data_tool() -> bool:
        return validate_data(file_path="input_data.json")
    
    @DMA_agent.tool_plain
    def create_visual_plots_tool() -> None:
        return create_visual_plots_from_json(file_path="input_data.json")
    
    return DMA_agent

async def run_data_manager_agent():
    agent = create_data_manager_agent()
    prompt = "Is the input data valid? Yes or No. Also generate visual plots."
    
    # logfire.configure(send_to_logfire='if-token-present')
    result = await agent.run(user_prompt=prompt)
    return result.data

if __name__ == "__main__":
    asyncio.run(run_data_manager_agent())