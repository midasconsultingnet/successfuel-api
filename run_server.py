if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Run the FastAPI application
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)