from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

write_queue = asyncio.Queue()
fake_db = []

async def db_worker():
    while True:
        data = await write_queue.get()
        print(f"Écriture : {data}")
        await asyncio.sleep(1)
        fake_db.append(data)
        write_queue.task_done()

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(db_worker())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.post("/add-message")
async def add_message(message: str):
    await write_queue.put(message)
    return {"status": "Ajouté à la file"}

@app.get("/messages")
async def get_messages():
    return fake_db
