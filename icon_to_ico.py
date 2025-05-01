from PIL import Image

img = Image.open("utils/images/KGM app logo1.png")
img.save("icon.ico", format="ICO", sizes=[(256, 256)])
