from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.settings import ModelSettings
from typing import Dict, Any, List
from dataclasses import dataclass
from agent_factory import get_text_model_instance
from dotenv import load_dotenv
import asyncio
import logfire
from skills.budget_projection_tool import project_budget
from skills.risk_identification_tool import risk_identification
from skills.tax_slab_tool import create_tax_slabs
from skills.report_compiler_tool import compile_report

# Load environment variables
load_dotenv()

@dataclass
class RA_deps:
    projections: Dict[str, Any]
    risk_ranking: str  # This should match the parameter name in compile_report (risk_level)
    tax_slabs: List[Dict[str, Any]]  # This should match the parameter name in compile_report
    visual_plots_dir: str


async def main():
    REPORT_SYS_PROMPT = """
    <agent_role>
    You are the Report Agent for the Ministry of Finance system. Your task is to compile the data from previous agents into a final report.
    Your available tool is:
    - ReportCompilerTool (which compiles text sections from budget projections, risk analysis, tax policy recommendations, and visual plots into one PDF report)
    Your output must be a PDF report saved in the designated output folder, and return a JSON object with key "report_path" indicating where the file is saved.
    </agent_role>
    """

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
    prompt = "Create a PDF compiling all the information."

    print("Starting report generation process...")

    # Step 1: Generate budget projections
    print("Step 1: Generating budget projections...")
    projections = project_budget(file_path="input_data.json")
    print("Budget projections generated successfully.")

    # Step 2: Calculate risk level
    print("Step 2: Calculating risk level...")
    risk_level = risk_identification(projections=projections)
    print(f"Risk level determined: {risk_level}")

    # Step 3: Create tax slabs
    print("Step 3: Creating tax slabs...")
    tax_slabs = create_tax_slabs(projections=projections)
    print(f"Generated {len(tax_slabs)} tax slabs.")

    # Step 4: Set visual plots directory
    visual_plots_dir = "visual_plots"  # Directory where plots are stored

    # Step 5: Use the Report Agent to compile the final report
    print("Step 4: Compiling final report...")


    @RA_agent.tool
    def compile_report_tool(ctx: RunContext[RA_deps]) -> str:
        """Compile all data into a final PDF report"""
        output_pdf = "final_budget_report.pdf"
        compile_report(
            projections=ctx.deps.projections, 
            risk_level=ctx.deps.risk_ranking,  # Note this parameter name change
            tax_slabs=ctx.deps.tax_slabs,      # Note this parameter name change 
            visual_plots_dir=ctx.deps.visual_plots_dir,
            output_pdf=output_pdf
        )
        return output_pdf

    deps = RA_deps(
        projections=projections,
        risk_ranking=risk_level,
        tax_slabs=tax_slabs,
        visual_plots_dir=visual_plots_dir
    )

    logfire.configure(send_to_logfire='if-token-present')
    result = await RA_agent.run(user_prompt=prompt, deps=deps)
    print(result.data)

if __name__ == "__main__":
    asyncio.run(main())