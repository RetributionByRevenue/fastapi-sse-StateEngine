# fastapi-sse-StateEngine
A FastAPI Server-Sent Events (SSE) engine that mirrors server-side state directly into client-side JavaScript variables and DOM elements, enabling real-time updates without WebSocket complexity.

| Update Type | JSON Format | Function | Example |
|------------|-------------|-----------|----------|
| HTML Update | `{"html": {"elementId": "content"}}` | Finds DOM element by ID, replaces its innerHTML | `{"html": {"changed": "<p>New content</p>"}}` |
| JS Update | `{"js": {"varName": value}}` | Creates/updates variables in window object space | `{"js": {"state1": 42}}` |
