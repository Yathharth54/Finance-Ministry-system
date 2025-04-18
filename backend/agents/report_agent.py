from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.settings import ModelSettings
from typing import Dict, Any, List
from dataclasses import dataclass
from agent_factory import get_text_model_instance
from dotenv import load_dotenv
import asyncio
import logfire
import json

# Import tools
from skills.report_compiler_tool import compile_report

# Load environment variables
load_dotenv()

@dataclass
class RA_deps:
    projections: Dict[str, Any]
    risk_ranking: str
    tax_slabs: List[Dict[str, Any]]
    visual_plots_dir: str
    insights: Dict[str, Any] = None

REPORT_SYS_PROMPT = """
<agent_role>
You are the Report Agent for the Ministry of Finance system. Your task is to compile the data from previous agents into a final report.

Your first task is to analyze the data and generate insightful paragraphs for each section of the report including:
1. Revenue analysis
2. Expenditure analysis
3. Economic indicators analysis (inflation and GDP)
4. Risk assessment implications
5. Tax policy analysis
6. Analysis of each visualization

Then your second task is to use the ReportCompilerTool to compile all data and your insights into a comprehensive PDF report.

Your available tool is:
- ReportCompilerTool (which compiles text sections from budget projections, risk analysis, tax policy recommendations, and visual plots into one PDF report)

Your output must be a PDF report saved in the designated output folder, and return a JSON object with key "report_path" indicating where the file is saved.
</agent_role>
"""

def create_report_agent():
    RA_model = get_text_model_instance()

    RA_agent = Agent(
        model=RA_model, 
        name="Report Agent",
        system_prompt=REPORT_SYS_PROMPT,
        deps_type=RA_deps,
        retries=3,
        model_settings=ModelSettings(
            temperature=0.5,
        ),
    )
    
    @RA_agent.tool
    def compile_report_tool(ctx: RunContext[RA_deps]) -> str:
        """Compile all data into a final PDF report with insights"""
        output_pdf = "final_budget_report.pdf"
        compile_report(
            projections=ctx.deps.projections, 
            risk_level=ctx.deps.risk_ranking,
            tax_slabs=ctx.deps.tax_slabs,
            visual_plots_dir=ctx.deps.visual_plots_dir,
            output_pdf=output_pdf,
            insights=ctx.deps.insights
        )
        return output_pdf
    
    return RA_agent

async def run_report_agent(projections, risk_level, tax_slabs, visual_plots_dir="visual_plots", insights=None):
    agent = create_report_agent()
    
    # If insights are not provided, instruct the agent to generate them
    if insights is None:
        prompt = """
        Create a comprehensive budget report with the following steps:
        1. First, analyze the data provided and generate insightful paragraphs for each section
        2. Then, compile all data and insights into a final PDF report
        
        Be sure to include analysis for revenue streams, expenditure priorities, economic outlook, 
        risk assessment, and tax policy implications.
        """
    else:
        prompt = "Create a PDF compiling all the information with the provided insights."
    
    deps = RA_deps(
        projections=projections,
        risk_ranking=risk_level,
        tax_slabs=tax_slabs,
        visual_plots_dir=visual_plots_dir,
        insights=insights
    )
    
    # logfire.configure(send_to_logfire='if-token-present')
    result = await agent.run(user_prompt=prompt, deps=deps)
    
    # Ensure we return a consistent structure
    if isinstance(result.data, str):
        # If it's a string, try to parse it as JSON first
        try:
            parsed_data = json.loads(result.data)
            if isinstance(parsed_data, dict):
                return parsed_data
        except:
            # If not JSON, assume it's the report path
            return {"report_path": result.data}
    elif isinstance(result.data, dict):
        return result.data
    else:
        # Fall back to a default structure with the default output path
        return {"report_path": "final_budget_report.pdf"}

if __name__ == "__main__":
    # This would be for testing only - normally this agent needs data from other agents
    import json
    with open("sample_data.json", "r") as f:
        sample_data = json.load(f)
    
    result = asyncio.run(run_report_agent(
        projections=sample_data["projections"],
        risk_level="medium",
        tax_slabs=[{"slab": 1, "range": "0-10000", "rate": "10%"}, {"slab": 2, "range": "10001-50000", "rate": "20%"}]
    ))
    print("Report result:", result)