from http import HTTPStatus
import base64
import json
from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4
import redis
from fastapi import Depends, FastAPI, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import UUID4, BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from config import AppSettings
from .database import get_db, run_migrations
from .models.image import ImageModel
from config import init_logger


logger = init_logger()
configs = AppSettings()

run_migrations()

r = redis.Redis(host=configs.redis.host, port=configs.redis.port, db=0)

app = FastAPI()

class ImageInfo(BaseModel):
    external_id: UUID4
    description: str
    received_at: datetime

@app.post("/api/images", response_model=ImageInfo)
async def create_image(
    file: Annotated[bytes, File()],
    description: str = Form(..., max_length=200),
    session: AsyncSession = Depends(get_db),
):
    try: 
        received_at = datetime.now(UTC).isoformat()
        encoded_data = base64.b64encode(file).decode('utf-8')

        task = {
                'image_bytes': encoded_data,
                'external_id': str(uuid4()),
                'description': description,
                'received_at': received_at
            }
        r.rpush('image_processing_queue', json.dumps(task))

        return JSONResponse(
            content={
                "external_id": str(task['external_id']),
            },
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error in service function: {e}")
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, e.message) from e

@app.get("/api/images", response_model=list[ImageInfo])
async def get_images(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ImageModel))
        return [
            ImageInfo(
                external_id=row.external_id,
                description=row.description,
                received_at=row.received_at,
            )
            for row in result.scalars().all()
        ]
    except Exception as e:
        logger.error(f"Error in service function: {e}")
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, e.message) from e


def image_generator(bytes):
    yield bytes

@app.get("/api/images/{id:uuid}", response_model=ImageInfo)
async def get_image(id: UUID4, session: AsyncSession = Depends(get_db)):
    try:
        result = await session.execute(select(ImageModel).where(ImageModel.external_id == id))
        image = result.scalar_one_or_none()
        
        if image is None:
            logger.error(f"Image with id {id} not found")
            raise HTTPException(HTTPStatus.NOT_FOUND, "Image with id {id} not found") from e
    
        return StreamingResponse(image_generator(image.data), media_type="image/jpeg")
    
        # TODO Use, when files will store in filesysem (currently, It's in bytearray of DB)
        # return FileResponse('/' + image.data.decode("utf-8"), media_type="image/jpeg")
    except Exception as e:
        logger.error(f"Error in service function: {e}")
        raise HTTPException(HTTPStatus.BAD_REQUEST, str(e)) from e
