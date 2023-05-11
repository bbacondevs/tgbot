from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio


class WebhookUpdate(BaseModel):
    user_id: int
    payload: str


class WebhookServer:
    def __init__(self, webhook_host: str, api_token: str):
        self.app = FastAPI()
        self.update_queue = asyncio.Queue()
        self.webhook_host = webhook_host
        self.api_token = api_token
        self.webhook_path = f"/{self.api_token}"
        self.webhook_url = f"{self.webhook_host}{self.webhook_path}"

        @self.app.post("/submitpayload")
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
                raise HTTPException(
                    status_code=400, detail="The `user_id` must be a string!"
                )

            await self.update_queue.put(WebhookUpdate(user_id=user_id, payload=payload))
            return JSONResponse(
                content={
                    "message": "Thank you for the submission! It's being forwarded."
                }
            )

        @self.app.get("/healthcheck")
        async def health():
            return JSONResponse(content={"message": "The bot is still running fine :)"})

    def get_app(self):
        return self.app
