import asyncio
from dotenv import load_dotenv
import json
import logfire
from orchestrator import run

# Load environment variables
load_dotenv()

async def main():
    """
    Main entry point for the Ministry of Finance system.
    """
    print("Initializing Ministry of Finance system...")
    logfire.configure(send_to_logfire='if-token-present')
    # Run the orchestrated workflow
    result = await run()
    
    # Output the final result
    if result["status"] == "success":
        print(f"✅ Process completed successfully!")
        print(f"📄 Generated report available at: {result['report_path']}")
        print(f"📊 Workflow summary: {json.dumps(result['workflow_summary'], indent=2)}")
    else:
        print(f"❌ Process failed: {result.get('reason', result.get('message', 'Unknown error'))}")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())