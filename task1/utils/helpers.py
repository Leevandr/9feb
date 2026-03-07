import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_image_path(image_path):
    if image_path:
        full_path = os.path.join(BASE_DIR, image_path)
        if os.path.exists(full_path):
            return full_path
    return os.path.join(BASE_DIR, 'resources', 'picture.png')


def calculate_discounted_price(price, discount):
    if discount > 0:
        return price * (100 - discount) / 100
    return price
