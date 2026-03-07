"""Main entry point for agentic pipeline"""
from graph import run_pipeline
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <youtube_url>")
        print("Example: python main.py https://www.youtube.com/watch?v=...")
        sys.exit(1)
    
    run_pipeline(sys.argv[1])

if __name__ == "__main__":
    main()
