from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
import asyncio
import json
import time
from datetime import datetime

app = FastAPI()

# Shared state to store the latest updates
state_updates = asyncio.Queue()

@app.get("/", response_class=HTMLResponse)
async def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Auto Unix Timestamp SSE Demo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .timestamp-display {
                margin: 20px 0;
                padding: 15px;
                background-color: #f5f5f5;
                border-radius: 5px;
                font-size: 18px;
            }
            .debug-panel {
                margin-top: 30px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            h1 {
                color: #333;
            }
        </style>
    </head>
    <body>
        <h1>Auto Unix Timestamp SSE Demo</h1>
        
        <div class="timestamp-display">
            <p>Current Unix Timestamp: <span id="timestamp">Waiting for updates...</span></p>

        </div>
        

        
        <script>
            const eventSource = new EventSource('/stream');
            eventSource.onmessage = (event) => {
                try {
                    const update = JSON.parse(event.data);
                    
                    // Handle JavaScript variable updates
                    if (update.js) {
                        Object.entries(update.js).forEach(([key, value]) => {
                            window[key] = value;
                            console.log(`Updated JS variable ${key}:`, value);
                        });
                    }
                    
                    // Handle HTML content updates
                    if (update.html) {
                        Object.entries(update.html).forEach(([elementId, htmlContent]) => {
                            const element = document.getElementById(elementId);
                            if (element) {
                                element.innerHTML = htmlContent;
                                console.log(`Updated HTML element ${elementId}`);
                            } else {
                                console.warn(`Element with id ${elementId} not found`);
                            }
                        });
                    }
                    
                } catch (error) {
                    console.error('Error processing message:', error);
                    console.error('Raw data:', event.data);
                }
            };
        </script>
    </body>
    </html>
    """
    return html_content

# Background task to send timestamp updates
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(generate_timestamps())

async def generate_timestamps():
    """Background task that runs when the application starts up."""
    while True:
        current_unix_timestamp = int(time.time())
        # Create update for both JS state and HTML content
        update = {
            "html": {"timestamp": current_unix_timestamp}
        }
        await state_updates.put(update)
        # Sleep for 1 second
        await asyncio.sleep(1)

@app.get("/stream")
async def message_stream():
    async def event_generator():
        while True:
            update = await state_updates.get()
            yield update
            
    async def event_source_wrapper():
        async for state_update in event_generator():
            message = f'data: {json.dumps(state_update)}\r\n\r\n'
            yield message.encode('utf-8')
            
    return StreamingResponse(
        event_source_wrapper(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache', 
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8345)
