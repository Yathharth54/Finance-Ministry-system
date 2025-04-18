print("0 run")  # This is the only print statement that runs

# import os
# import json
import asyncio
import logfire
# from typing import Dict, Any
from dotenv import load_dotenv
# from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from agent_factory import get_text_model_instance

# Import and register the tools used by this agent.
from skills.data_validation_tool import validate_data
from skills.visualization_tool import create_visual_plots_from_json

# Load environment variables from .env file
load_dotenv()

class DataManagerInput(BaseModel):
    file_path: str

async def main():
    print("1 run")
    DATA_MANAGER_SYS_PROMPT = """ <agent_role> You are the Data Manager Agent for the Ministry of Finance system. Your task is to validate the input financial data using the DataValidationTool and then generate visual plots using the VisualisationTool.</agent_role> """
    
    DMA_model = get_text_model_instance()
    print("2 run")
    
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
    print("3 run")
    
    prompt = "Is the input data valid? Yes or No. Also generate visual plots."
    
    @DMA_agent.tool_plain
    def validate_data_tool() -> bool:
        return validate_data(file_path="input_data.json") # Use file_path argument
    
    @DMA_agent.tool_plain
    def create_visual_plots_tool() -> None:
        return create_visual_plots_from_json(file_path="input_data.json")
    
    print("4 run")
    logfire.configure(send_to_logfire='if-token-present')
    result = await DMA_agent.run(user_prompt=prompt)
    print(result.data)

if __name__ == "__main__":  # Fixed syntax here
    asyncio.run(main())
    print("5 run")
