import sys
sys.path.append('.')
from multi_agent_graph import app
from dotenv import load_dotenv
import json

load_dotenv()

def inspect_state(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        checkpoint_tuple = next(app.checkpointer.list(config))
        data = checkpoint_tuple[1]

        if "checkpoint" in data and "channel_values" in data["checkpoint"]:
            state_snapshot = data["checkpoint"]["channel_values"]
        elif "data" in data and "channel_values" in data["data"]:
            state_snapshot = data["data"]["channel_values"]
        elif "channel_values" in data:
            state_snapshot = data["channel_values"]
        else:
            print("Unknown checkpoint format:")
            print(data)
            return

        print(f"State from thread '{thread_id}':")
        print(json.dumps({k: v for k, v in state_snapshot.items() if k != "__metadata"}, indent=2))
    except StopIteration:
        print(f"No checkpoints found for thread '{thread_id}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python persistence_test.py pipeline_7346")
        sys.exit(1)
    inspect_state(sys.argv[1])