
import os
from PIL import ImageFont

os.path.realpath

picdir = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'pic'))

def space_mono(style: str, size: int):
  return ImageFont.truetype(os.path.join(picdir, 'Space_Mono', 'SpaceMono-' + style + '.ttf'), size)
