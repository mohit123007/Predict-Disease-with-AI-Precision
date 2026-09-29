# Development entrypoint
# Run with: python app.py  (or use uvicorn for reload: uvicorn backend.main:app --reload)
import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
