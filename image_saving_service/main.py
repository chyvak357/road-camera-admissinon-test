import base64
import json

import redis

from database import SessionLocal
from models import ImageModel
from config import AppSettings, init_logger

config = AppSettings()
logger = init_logger()


r = redis.Redis(host=config.redis.host, port=config.redis.port, db=0)

if __name__ == "__main__":
    while True:
        try: 
            task = r.blpop("image_saving_queue", timeout=0)
            with SessionLocal() as session:

                task_data = json.loads(task[1])

                image_bytes_decoded = task_data["image_bytes"]
                image_bytes = base64.b64decode(image_bytes_decoded)

                external_id = task_data["external_id"]
                description = task_data["description"]
                received_at = task_data["received_at"]

                new_image = ImageModel(
                    external_id=external_id,
                    description=description,
                    received_at=received_at,
                    data=image_bytes,
                )

                session.add(new_image)
                session.commit()
        except Exception as e: 
            logger.error(f"An error occurred: {e}", exc_info=True)
