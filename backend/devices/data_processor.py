import asyncio

# Create an asyncio queue
queue = asyncio.Queue()

async def process_device_data():
    """Continuously process device data from the queue."""
    while True:
        data = await queue.get()
        await save_to_db(data)  # Simulated saving
        queue.task_done()

async def save_to_db(data):
    """Simulate saving incoming data to the database asynchronously."""
    print(f"Simulating data storage for device {data['device_UUID']}")
    print(f"Device Name: {data.get('device_name', 'Unknown Device')}")
    print(f"Latitude: {data.get('device_latitude', 0.0)}, Longitude: {data.get('device_longitude', 0.0)}")
    print(f"DataLog: {data['dataLog_data']}, Metadata: {data.get('dataLog_metadata', '')}")
    print("-" * 50)

async def add_to_queue(data):
    """Add data to the queue for processing."""
    await queue.put(data)

# Start background processing loop
async def startup():
    asyncio.create_task(process_device_data())
