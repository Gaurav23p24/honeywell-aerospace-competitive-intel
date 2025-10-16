"""
LangGraph State Definition for Honeywell Analysis System
Phase 2: State management and orchestration
"""

from typing import Dict, Any, List, Optional, Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from operator import add

class AnalysisState(TypedDict):
    """State definition for the analysis workflow"""
    
    # Input parameters
    honeywell_product: str
    competitor_query: str
    
    # Workflow control
    current_step: str
    workflow_complete: bool
    error_message: Optional[str]
    
    # Results
    pdf_path: Optional[str]
    analysis_summary: Optional[str]

def create_analysis_workflow():
    """Create the LangGraph workflow for competitive analysis"""
    
    # Import agents
    from agents.scout import ScoutAgent
    from agents.validator import ValidatorAgent
    from agents.analyst import AnalystAgent
    from agents.writer import WriterAgent
    
    # Initialize agents
    scout = ScoutAgent()
    validator = ValidatorAgent()
    analyst = AnalystAgent()
    writer = WriterAgent()
    
    def scout_node(state: AnalysisState) -> AnalysisState:
        """Scout node - gather data from multiple sources"""
        print(f"LangGraph: Scout gathering data for {state['honeywell_product']}")
        
        try:
            from agents.scout import ScoutAgent
            scout = ScoutAgent()
            raw_data = scout.hunt(state['honeywell_product'], state['competitor_query'])
            
            return {
                **state,
                "current_step": "validator"
            }
        except Exception as e:
            error_msg = f"Scout failed: {str(e)}"
            print(f"LangGraph: {error_msg}")
            return {
                **state,
                "current_step": "error",
                "error_message": error_msg
            }
    
    def validator_node(state: AnalysisState) -> AnalysisState:
        """Validator node - check data quality and decide on retry"""
        print("LangGraph: Validator checking data quality")
        
        try:
            from agents.scout import ScoutAgent
            from agents.validator import ValidatorAgent
            
            scout = ScoutAgent()
            validator = ValidatorAgent()
            
            raw_data = scout.hunt(state['honeywell_product'], state['competitor_query'])
            validated_data = validator.validate(raw_data)
            
            return {
                **state,
                "current_step": "analyst"
            }
        except Exception as e:
            error_msg = f"Validator failed: {str(e)}"
            print(f"LangGraph: {error_msg}")
            return {
                **state,
                "current_step": "error",
                "error_message": error_msg
            }
    
    def analyst_node(state: AnalysisState) -> AnalysisState:
        """Analyst node - perform competitive analysis"""
        print("LangGraph: Analyst performing competitive analysis")
        
        try:
            from agents.scout import ScoutAgent
            from agents.validator import ValidatorAgent
            from agents.analyst import AnalystAgent
            
            scout = ScoutAgent()
            validator = ValidatorAgent()
            analyst = AnalystAgent()
            
            raw_data = scout.hunt(state['honeywell_product'], state['competitor_query'])
            validated_data = validator.validate(raw_data)
            analysis = analyst.analyze(validated_data)
            
            # Create summary
            gaps_count = len(analysis.get('competitive_gaps', []))
            insights_count = len(analysis.get('insights', []))
            confidence = analysis.get('confidence_score', 0)
            summary = f"Found {gaps_count} gaps, {insights_count} insights, {confidence:.1%} confidence"
            
            return {
                **state,
                "analysis_summary": summary,
                "current_step": "writer"
            }
        except Exception as e:
            error_msg = f"Analyst failed: {str(e)}"
            print(f"LangGraph: {error_msg}")
            return {
                **state,
                "current_step": "error",
                "error_message": error_msg
            }
    
    def writer_node(state: AnalysisState) -> AnalysisState:
        """Writer node - generate PDF report"""
        print("LangGraph: Writer generating PDF report")
        
        try:
            from agents.scout import ScoutAgent
            from agents.validator import ValidatorAgent
            from agents.analyst import AnalystAgent
            from agents.writer import WriterAgent
            
            scout = ScoutAgent()
            validator = ValidatorAgent()
            analyst = AnalystAgent()
            writer = WriterAgent()
            
            raw_data = scout.hunt(state['honeywell_product'], state['competitor_query'])
            validated_data = validator.validate(raw_data)
            analysis = analyst.analyze(validated_data)
            
            pdf_path = writer.write_report(
                analysis,
                state['honeywell_product'],
                state['competitor_query']
            )
            
            return {
                **state,
                "pdf_path": pdf_path,
                "current_step": "complete",
                "workflow_complete": True
            }
        except Exception as e:
            error_msg = f"Writer failed: {str(e)}"
            print(f"LangGraph: {error_msg}")
            return {
                **state,
                "current_step": "error",
                "error_message": error_msg
            }
    
    def error_node(state: AnalysisState) -> AnalysisState:
        """Error handling node"""
        print(f"LangGraph: Workflow error: {state.get('error_message', 'Unknown error')}")
        return {
            **state,
            "workflow_complete": True,
            "current_step": "error"
        }
    
    # Create the state graph
    workflow = StateGraph(AnalysisState)
    
    # Add nodes
    workflow.add_node("scout", scout_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("error", error_node)
    
    # Add edges
    workflow.set_entry_point("scout")
    
    # Simple linear flow: scout → validator → analyst → writer
    workflow.add_edge("scout", "validator")
    workflow.add_edge("validator", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", END)
    
    # Compile the workflow
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app

def run_analysis_workflow(honeywell_product: str, competitor_query: str) -> Dict[str, Any]:
    """Run the complete analysis workflow"""
    
    # Create workflow
    workflow = create_analysis_workflow()
    
    # Initial state
    initial_state = AnalysisState(
        honeywell_product=honeywell_product,
        competitor_query=competitor_query,
        current_step="scout",
        workflow_complete=False,
        error_message=None,
        pdf_path=None,
        analysis_summary=None
    )
    
    # Run workflow
    config = {"configurable": {"thread_id": "analysis_1"}}
    final_state = workflow.invoke(initial_state, config=config)
    
    return final_state

# Example usage for testing
if __name__ == "__main__":
    print("Testing LangGraph workflow...")
    
    result = run_analysis_workflow("TFE731 Engine", "compare with Pratt & Whitney PW500")
    
    print(f"\nWorkflow completed: {result['workflow_complete']}")
    print(f"Final step: {result['current_step']}")
    
    if result['pdf_path']:
        print(f"PDF generated: {result['pdf_path']}")
    else:
        print(f"Error: {result.get('error_message', 'Unknown error')}")
