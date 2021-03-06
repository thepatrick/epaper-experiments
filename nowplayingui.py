#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import time
import logging

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in13_V2
from helpers import fonts
from PIL import Image,ImageDraw
from threading import Thread

def format_duration(duration: int):
  mm, ss = divmod(duration, 60)
  hh, mm = divmod(mm, 60)

  if hh > 0:
    s = "%d:%02d:%02d" % (hh, mm, ss)
  elif mm > 0:
    s = "%d:%02d" % (mm, ss)
  else:
    s = "%d" % ss

  return s

class NowPlayingUI:
  def __init__(self, logger: logging.Logger):
    self.epd = epd2in13_V2.EPD()

    self.logger = logger

    self.font_artist = fonts.space_mono("Bold", 16)
    self.font_title = fonts.space_mono("Bold", 20)
    self.font_duration = fonts.space_mono("Bold", 16)

    # Drawing on the image
    self.time_image = Image.new('1', (self.epd.height, self.epd.width), 255)
    self.time_draw = ImageDraw.Draw(self.time_image)

    self.artist = "(No artist)"
    self.title = "(No track)"
    self.play_duration = 0
    self.play_position = 0

    self.progress_top = self.epd.width - 20
    self.progress_left = 5
    self.progress_bottom = self.epd.width - 1

    self.needs_full_refresh = False
    self.needs_partial_refresh = False
    self.needs_sleep = False
    self.needs_ctrl_c = False

  def start(self):
    self.needs_reset = True
    self.needs_full_refresh = True
    self.needs_partial_refresh = True

    self.thread = Thread(target=self.worker)
    self.thread.daemon = True
    self.thread.start()
  
  def sleep(self):
    self.needs_sleep = True

  def update_ui(self, artist: str, title: str, position: int, duration: int):
    if position == None:
      position = 0
    if duration == None:
      duration = 0
    if artist != self.artist or title != self.title or duration != self.play_duration:
      self.artist = artist
      self.title = title
      self.play_duration = duration
      self.play_position = position
      self.needs_full_refresh = True
      self.needs_partial_refresh = True
    elif position != self.play_position:
      self.play_position = position
      self.needs_partial_refresh = True
  
  def worker(self):
    while True:
      if self.needs_reset:
        self.perform_reset()
        self.needs_reset = False
      if self.needs_full_refresh:
        self.render_everything()
        self.needs_full_refresh = False
      if self.needs_partial_refresh:
        self.render_progress()
        self.needs_partial_refresh = False
      if self.needs_sleep:
        self.logger.info("Goto Sleep...")
        self.epd.sleep()
        self.needs_sleep = False
      time.sleep(0.5)
        
  def perform_reset(self):
    self.logger.debug("init and clear")
    self.epd.init(self.epd.FULL_UPDATE)
    self.epd.Clear(0xFF)
    
  def render_everything(self):
    duration = format_duration(self.play_duration)

    (_, font_artist_height) = self.font_artist.getsize(self.artist)
    # (_, track_title_height) = self.font_title.getsize_multiline(self.title)
    (track_duration_width, track_duration_height) = self.font_duration.getsize(duration)

    self.time_draw.rectangle((0, 0, self.epd.height, self.epd.width), fill = 255)

    # Track Artist
    # TODO: If too long, truncate
    self.time_draw.text((0, 0), self.artist, font = self.font_artist, fill = 0)

    # Track Title
    # TODO: If greater than available space, truncate
    self.time_draw.text((0, font_artist_height), self.title, font = self.font_title, fill = 0)

    # Duration
    track_duration_left = 0
    progress_height = (self.progress_bottom - 1) - self.progress_top
    track_duration_top = self.progress_top + (progress_height / 2) - (track_duration_height / 2)
    self.time_draw.text((track_duration_left, track_duration_top), duration, font = self.font_duration, fill = 0)

    # Progress box
    self.progress_left = track_duration_width + 5

    self.time_draw.rectangle([(self.progress_left,self.progress_top),(self.epd.height-1,self.progress_bottom)],outline = 0)

    self.epd.init(self.epd.FULL_UPDATE)
    self.epd.displayPartBaseImage(self.epd.getbuffer(self.time_image))
    
    self.epd.init(self.epd.PART_UPDATE)
  
  def render_progress(self):
    progress_padding = 2
    available_width = self.epd.height - (self.progress_left + (progress_padding * 2) + 1)

    progress_right = self.progress_left + 2 + ((self.play_position / self.play_duration) * available_width)

    # TODO: if less than previous, we need to draw a rectangle with fill=255 to clear it
    self.time_draw.rectangle((self.progress_left + 2, self.epd.width - 18, progress_right, self.epd.width - 3), fill = 0)

    if ((self.epd.height - (1 + progress_padding)) - progress_right) > 0:
      self.logger.debug("filling empty space")
      self.time_draw.rectangle((
        progress_right,
        self.epd.width - 18,
        self.epd.height - (1 + progress_padding),
        self.epd.width - 3
      ), fill = 255)
    else:
      self.logger.debug("no empty space to fill")

    self.logger.debug("next tick...")
    self.epd.displayPartial(self.epd.getbuffer(self.time_image))
  
  def ctrl_c(self):
    self.logger.info("ctrl + c:")
    epd2in13_V2.epdconfig.module_exit()
