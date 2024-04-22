from flask import Flask, request
from PIL import Image
import requests
import hashlib
import random
import string
import os


def create_hash(len: int = 8) -> str:
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=len))

    hash_object = hashlib.sha256(random_string.encode())
    random_hash = hash_object.hexdigest()
    
    return random_hash

def get_img_name(img: str) -> str:
    parts = img.split("/")
    return parts[len(parts) - 1]

def resize_image(url: str, x: int, y: int) -> Image:
    try:
        r = requests.get(url)
        r.raise_for_status()

        tempImage = f"{create_hash()}.png"

        with open(tempImage, "wb") as f:    # Downloads the image
            f.write(r.content)

        with Image.open(tempImage) as img:
            width, height = img.size
            aspect_ratio = width / height
            
            if x is None:
                x = int(x * aspect_ratio)
            elif y is None:
                y = int(y / aspect_ratio)

            resized_img = img.resize((x, y), Image.Resampling.BOX)
            resized_img.save(get_img_name(url))

            #os.remove(tempImage)
            
            return resized_img

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


app = Flask(__name__)

@app.route("/resize")
def resize():
    img = request.args.get("img")
    x, y = int( request.args.get("x") ), int( request.args.get("y") )

    if img and x and y:
        newImage = resize_image(img, x, y)
        
        return newImage.tobytes() or "NULL", 200
    else:
        return "Invalid parameters.", 404

    return "OK", 200

if __name__ == "__main__":
    app.run(use_reloader = False)