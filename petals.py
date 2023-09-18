"""
Petals Chat WebSocket Client in Python

This script demonstrates how to interact with the Petals Chat WebSocket API for text generation.
It opens an inference session and generates text based on a given prompt.

For more details and to set up your own backend, please visit: https://github.com/petals-infra/chat.petals.dev
"""

import json
import websocket

# Global variables
prompt = "Who is your daddy and what does he do?"
max_length = 150
stop_sequence = None  # You can set this to a string if you want the generation to stop at a specific sequence

def on_open(ws):
    """Handles WebSocket open event."""
    print("WebSocket opened. Opening inference session...")
    
    # Open inference session
    ws.send(json.dumps({
        "type": "open_inference_session",
        "model": "stabilityai/StableBeluga2",
        "max_length": max_length
    }))

def on_message(ws, event):
    """Handles WebSocket message event."""
    print("Received a message.")
    
    try:
        response = json.loads(event)
        
        if response.get('ok'):
            if 'outputs' not in response:
                print("Inference session opened. Generating text...")
                
                # Generate text
                ws.send(json.dumps({
                    "type": "generate",
                    "inputs": prompt,
                    "max_length": max_length,
                    "do_sample": 1,
                    "temperature": 0.6,
                    "top_p": 0.9,
                    "stop_sequence": stop_sequence  # Optional
                }))
            else:
                print(f"Generated: {prompt}{response['outputs']}")
                if response.get('stop', False):
                    print("Stopping generation.")
                    ws.close()
        else:
            print(f"Server responded with an error: {response.get('traceback', 'Unknown error')}")
            ws.close()
    except json.JSONDecodeError:
        print("Failed to decode the received message as JSON.")
        ws.close()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        ws.close()

def on_error(ws, error):
    """Handles WebSocket error event."""
    print(f"An error occurred: {error}")

def on_close(ws, close_status_code, close_msg):
    """Handles WebSocket close event."""
    print(f"WebSocket closed with code: {close_status_code}, message: {close_msg}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp("wss://chat.petals.dev/api/v2/generate",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
