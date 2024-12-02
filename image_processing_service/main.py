import base64
import json
import math
import textwrap
from io import BytesIO
import os

from PIL import Image, ImageDraw, ImageFont
from config import AppSettings, init_logger
import redis


config = AppSettings()
logger = init_logger()


r = redis.Redis(host=config.redis.host, port=config.redis.port, db=0)


def add_text_to_image(
    image_bytes: bytes, description: str, font_title: str, font_size: int = 12,  vertical_margin: int = 10
) -> bytes:
    input_img = Image.open(BytesIO(image_bytes))
    font = ImageFont.truetype(f"{font_title}.ttf", font_size, encoding="UTF-8")

    img_width, img_height = input_img.size
    avg_symbol_length = math.floor(font.getlength(description) / len(description))
    
    # TODO: 
    """  
    Разделить текст на слова по пробелам
    Получить список длинн этих слов (получится список чисел где каждое число - длинна слова)
    Проходим по этому списку с словами и длинами и заполняем новый список уже из слов,
    где каждый элемент списка - строка под тектом
    с условием, что итоговая длинна каждого элемента этого списка не более допустимой
    """
          
    # Calculating allowed amount of symbols on one row for passed image. Including distance reserve
    symbols_on_row = ((img_width - 40) // avg_symbol_length) - 4
    description_lines = textwrap.wrap(description, width=symbols_on_row)

    # Text block height
    line_height = font.size + 2
    text_height = len(description_lines) * line_height

    # Extended image
    result_img = Image.new(
        "RGB",
        (img_width, img_height + text_height + vertical_margin),
        color="black",
    )
    result_img.paste(input_img, (0, 0))
    draw = ImageDraw.Draw(result_img)

    # top margin
    y_text = img_height + vertical_margin // 2
    
    for line in description_lines:
        draw.text(
            (10, y_text),
            line,
            font=font,
            fill="white",
        )
        y_text += line_height

    buffer = BytesIO()
    result_img.save(buffer, format="JPEG")
    processed_bytes = buffer.getvalue()

    return processed_bytes


if __name__ == "__main__":
    text_size = config.text.size
    font_title = config.text.font
    
    if not os.path.exists(f"{font_title}.ttf"):
        logger.error(f"Font file '{font_title}.ttf' not found.")
        exit()
        
    

    while True:
        try: 
            task = r.blpop("image_processing_queue", timeout=0)
            task_data = json.loads(task[1])

            image_bytes_decoded = task_data["image_bytes"]
            image_bytes = base64.b64decode(image_bytes_decoded)
            external_id = task_data["external_id"]
            description = task_data["description"]
            received_at = task_data["received_at"]

            image_with_description: bytes = add_text_to_image(image_bytes, description, font_title, text_size)

            image_with_description_encoded = base64.b64encode(
                image_with_description
            ).decode("utf-8")

            
            task_on_save = {
                "image_bytes": image_with_description_encoded,
                "external_id": external_id,
                "description": description,
                "received_at": received_at,
            }

            with open(f"{external_id}.jpeg", "wb") as binary_file:
                binary_file.write(image_with_description)

            r.rpush("image_saving_queue", json.dumps(task_on_save))

        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
