import sys
from multi_agent_graph import run_pipeline

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <youtube_url>")
        sys.exit(1)

    youtube_url = sys.argv[1]
    # Generate a simple thread ID based on the URL hash for persistence
    thread_id = f"pipeline_{abs(hash(youtube_url)) % 10000}"

    print(f"Starting pipeline for URL: {youtube_url}")
    print(f"Using thread ID: {thread_id}")
    run_pipeline(youtube_url, thread_id=thread_id)