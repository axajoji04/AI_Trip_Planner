from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent.agentic_workflow import GraphBuilder
from utils.save_to_document import save_document
from starlette.responses import JSONResponse
import os
import datetime
import logging
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Travel Planner API",
    description="An intelligent travel planning service with agentic workflows",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    timestamp: Optional[str] = None
    query_type: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    timestamp: str
    details: Optional[str] = None

# Global variables for caching
_graph_instance = None
_react_app = None

def get_or_create_graph():
    """Get or create graph instance with caching"""
    global _graph_instance, _react_app
    
    try:
        if _react_app is None:
            logger.info("Initializing GraphBuilder...")
            _graph_instance = GraphBuilder(model_provider="groq")
            _react_app = _graph_instance()
            
            # Save graph visualization (optional, can be disabled in production)
            try:
                png_graph = _react_app.get_graph().draw_mermaid_png()
                graph_path = "my_graph.png"
                with open(graph_path, "wb") as f:
                    f.write(png_graph)
                logger.info(f"Graph visualization saved as '{graph_path}'")
            except Exception as viz_error:
                logger.warning(f"Could not save graph visualization: {viz_error}")
            
        return _react_app
    except Exception as e:
        logger.error(f"Error creating graph: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize AI agent: {str(e)}")

def determine_query_type(question: str) -> str:
    """Determine the type of travel query"""
    question_lower = question.lower()
    
    if any(keyword in question_lower for keyword in ["hotel", "accommodation", "stay", "lodge"]):
        return "hotels"
    elif any(keyword in question_lower for keyword in ["cost", "budget", "price", "expense", "money"]):
        return "cost_breakdown"
    elif any(keyword in question_lower for keyword in ["weather", "climate", "temperature", "season"]):
        return "weather"
    elif any(keyword in question_lower for keyword in ["alternative", "option", "different", "other"]):
        return "alternatives"
    else:
        return "complete_itinerary"

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🌍 AI Travel Planner API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "POST /query": "Submit travel planning queries",
            "GET /health": "Health check endpoint",
            "GET /docs": "API documentation"
        },
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test if the graph can be created
        react_app = get_or_create_graph()
        return {
            "status": "healthy",
            "message": "AI Travel Planning service is operational",
            "ai_agent_status": "ready",
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": "AI agent initialization failed",
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

@app.post("/query", response_model=QueryResponse)
async def query_travel_agent(query: QueryRequest):
    """Main endpoint for travel planning queries"""
    start_time = datetime.datetime.now()
    
    try:
        logger.info(f"Received query: {query.question[:100]}...")  # Log first 100 chars
        
        # Get or create the AI agent
        react_app = get_or_create_graph()
        
        # Determine query type
        query_type = determine_query_type(query.question)
        logger.info(f"Query type determined: {query_type}")
        
        # Prepare messages for the agent
        messages = {"messages": [query.question]}
        
        # Invoke the AI agent
        logger.info("Invoking AI agent...")
        output = react_app.invoke(messages)
        
        # Process the output
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content
        else:
            final_output = str(output)
        
        # Validate output
        if not final_output or final_output.strip() == "":
            raise ValueError("AI agent returned empty response")
        
        # Optional: Save to document (can be enabled/disabled)
        try:
            if os.getenv("SAVE_DOCUMENTS", "false").lower() == "true":
                save_document(final_output, user_query=query.question)
        except Exception as save_error:
            logger.warning(f"Could not save document: {save_error}")
        
        # Calculate processing time
        processing_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.info(f"Query processed successfully in {processing_time:.2f} seconds")
        
        return QueryResponse(
            answer=final_output,
            timestamp=datetime.datetime.now().isoformat(),
            query_type=query_type
        )
        
    except Exception as e:
        processing_time = (datetime.datetime.now() - start_time).total_seconds()
        error_msg = str(e)
        logger.error(f"Error processing query after {processing_time:.2f} seconds: {error_msg}")
        
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Failed to process travel query",
                details=error_msg,
                timestamp=datetime.datetime.now().isoformat()
            ).dict()
        )

@app.post("/query-simple")
async def query_simple(query: QueryRequest):
    """Simplified endpoint that returns raw response (for backward compatibility)"""
    try:
        result = await query_travel_agent(query)
        if isinstance(result, JSONResponse):
            return result
        return {"answer": result.answer}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Optional: Add startup event to pre-initialize the graph
@app.on_event("startup")
async def startup_event():
    """Initialize AI agent on startup (optional)"""
    if os.getenv("PRELOAD_AI_AGENT", "false").lower() == "true":
        try:
            logger.info("Pre-loading AI agent...")
            get_or_create_graph()
            logger.info("AI agent pre-loaded successfully")
        except Exception as e:
            logger.warning(f"Could not pre-load AI agent: {e}")

# Optional: Add shutdown event for cleanup
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global _react_app, _graph_instance
    _react_app = None
    _graph_instance = None
    logger.info("AI Travel Planner API shutdown complete")

if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print("🚀 Starting AI Travel Planner Backend...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📋 API Documentation at: http://{host}:{port}/docs")
    print(f"🔄 Reload mode: {'enabled' if reload else 'disabled'}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
    