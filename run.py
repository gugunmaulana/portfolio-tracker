import uvicorn
import os
import sys

if __name__ == "__main__":
    print("=" * 60)
    print(" Starting Core-Satellite Radar & Financial Freedom Tracker ")
    print(" Local URL: http://127.0.0.1:8000")
    print("=" * 60)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
