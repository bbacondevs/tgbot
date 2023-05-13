from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from bot import handle_update  # Import the handle_update function


class WebhookUpdate(BaseModel):
    upadte_id: int
    message: dict


app = FastAPI()
update_queue = asyncio.Queue()


@app.post("/webhook")
async def webhook(update: WebhookUpdate):
    await update_queue.put(update)
    await handle_update(update)


@app.post("/submitpayload")
async def custom_updates(request: Request):
    try:
        user_id = int(request.query_params["user_id"])
        payload = request.query_params["payload"]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail="Please pass both `user_id` and `payload` as query parameters.",
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="The `user_id` must be a string!")

    await update_queue.put(WebhookUpdate(user_id=user_id, payload=payload))
    return JSONResponse(
        content={"message": "Thank you for the submission! It's being forwarded."}
    )


@app.get("/healthcheck")
async def health():
    return JSONResponse(content={"message": "The bot is still running fine :)"})
