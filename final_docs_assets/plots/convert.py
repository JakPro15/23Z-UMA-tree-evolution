from PIL import Image
import os

for name in os.listdir("."):
    if "confusion_" == name[:len("confusion_")]:
        im = Image.open(name)
        im = im.crop((37, 0, im.size[0] - 78, im.size[1] - 1))
        im.save(f'{name}')
