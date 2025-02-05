from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
import asyncio
import json
import random
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
        <title>State Mirror Demo</title>
    </head>
    <body>
        <h1>SSE Showcase Demo</h1>
        
        <div id="debug">Current window.state1: </div>
        <button onclick="alert(window.state1)">View State</button>
        <div id="changed">Initial content here</div>
        
        <button onclick="fetch('/update_jsstate')">Update JS State</button>
        <button onclick="fetch('/update_dom')">Update HTML Element</button>

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

@app.get("/update_jsstate")
async def update_js_state():
    random_value = random.randint(1, 100)
    update = {"js": {"state1": random_value}}
    await state_updates.put(update)
    return {"status": "success"}

@app.get("/update_dom")
async def update_dom():
    current_time = datetime.now().strftime("%H:%M:%S")
    update = {"html": {"changed": f"<p>Server updated at {current_time}</p>"}}
    await state_updates.put(update)
    return {"status": "success"}

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
        headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive'}
    )
