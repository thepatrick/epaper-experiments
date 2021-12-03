import os
import time
import logging
from roonapi import RoonApi

from appinfo import AppInfo
from nowplayingui import NowPlayingUI

log_level = os.environ.get('LOG_LEVEL', 'info')

token_path = os.environ['ROON_TOKEN_PATH']
server = os.environ['ROON_CORE']
my_zone_id = os.environ['ROON_ZONE_ID']
LOG_FORMAT = logging.Formatter(
    "%(asctime)-15s %(levelname)-5s  %(module)s -- %(message)s"
)
LOGGER = logging.getLogger(__name__)
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(LOG_FORMAT)
LOGGER.addHandler(CONSOLE_HANDLER)

if log_level == 'debug':
  LOGGER.setLevel(logging.DEBUG)
else:
  LOGGER.setLevel(logging.INFO)

# Can be None if you don't yet have a token
try:
  token = open(token_path).read()
except IOError as e:
  LOGGER.warn("Unable to read %s, will attempt to recreate %s", token_path, e)
  token = None


LOGGER.debug("Create RoonApi...")
roonapi = RoonApi(AppInfo, token, server)
LOGGER.debug("...created.")

LOGGER.debug("Write token")

if roonapi.token != token:
  # save the token for next time
  with open(token_path, "w") as f:
      f.write(roonapi.token)
  LOGGER.info("Token written to %s", token_path)
else:
  LOGGER.debug("Token unchanged, not writing again")

try:
  LOGGER.info("NowPlaying()")
  ui = NowPlayingUI(LOGGER.getChild("NowPlaying"))

  LOGGER.info("start...")
  ui.start()

  def update_ui():
      zone = roonapi.zones[my_zone_id]
      track = zone['now_playing']['two_line']['line1']
      artist = zone['now_playing']['two_line']['line2']

      LOGGER.debug(zone)

      if "seek_position" in zone:
        pos = zone['seek_position']
      elif "now_playing" in zone and "seek_position" in zone["now_playing"]:
        pos = zone['now_playing']["seek_position"]

      length = zone['now_playing']['length']

      if pos == None or length == None:
        progress = "0%"
      else:
        progress = "{:.1f}%".format(((pos / length) * 100))


      LOGGER.debug("[%s (%s)] %s: %s %s" % (zone['display_name'], zone['state'], artist, track, progress))

      ui.update_ui(artist, track, pos, length)

  def my_state_callback(event, changed_ids):
    """Call when something changes in roon."""
    LOGGER.debug("my_state_callback event:%s changed_ids: %s", event, changed_ids)
    for zone_id in changed_ids:
      if zone_id == my_zone_id:
        update_ui()

  # receive state updates in your callback
  roonapi.register_state_callback(my_state_callback)
  update_ui()

  LOGGER.info("Begin sleep")

  while True:
    time.sleep(500)
        
except IOError as e:
    LOGGER.info(e)
    
except KeyboardInterrupt:
    ui.sleep()
    ui.ctrl_c()
    exit()

# zones_seek_changed
# zones_changed

LOGGER.info("End sleep")

# 'display_name': 'Schiit', 
# 'state': 'playing',
# 'queue_items_remaining': 4990,
# 'queue_time_remaining': 1245257,
# 'seek_position': 136
# 'now_playing': {
#   'length': 161,
#     'two_line': {
#       'line1': 'Gonna Walk',
#       'line2': 'Barenaked Ladies'
#     },
# }

# {
#   'zone_id': '1601943ba14655923bde8b7420e02f14b13f', 
#   'display_name': 'Schiit', 
#   'outputs': [
#     {
#       'output_id': '1701943ba14655923bde8b7420e02f14b13f',
#       'zone_id': '1601943ba14655923bde8b7420e02f14b13f',
#       'can_group_with_output_ids': ['1701943ba14655923bde8b7420e02f14b13f'],
#       'display_name': 'Schiit',
#       'source_controls': [
#         {'control_key': '1',
#         'display_name': 'snd_rpi_hifiberry_digi',
#         'supports_standby': False,
#         'status': 'indeterminate'
#         }
#       ]
#     }
#   ],
#   'state': 'playing',
#   'is_next_allowed': True,
#   'is_previous_allowed': True,
#   'is_pause_allowed': True,
#   'is_play_allowed': False,
#   'is_seek_allowed': True,
#   'queue_items_remaining': 4990,
#   'queue_time_remaining': 1245257,
#   'settings': {'loop': 'disabled', 'shuffle': False, 'auto_radio': True},
#   'now_playing': {
#     'seek_position': 116,
#     'length': 161,
#     'one_line': {
#       'line1': 'Gonna Walk - Barenaked Ladies'
#     },
#     'two_line': {
#       'line1': 'Gonna Walk',
#       'line2': 'Barenaked Ladies'
#     },
#     'three_line': {
#       'line1': 'Gonna Walk',
#       'line2': 'Barenaked Ladies',
#       'line3': 'Grinning Streak'
#     },
#     'image_key': '3bb474345391e0665d49f9415798ccc1',
#     'artist_image_keys': ['0043da450d54f8317e9ee556ae7f9952']
#   },
#   'seek_position': 136
# }

# {'zone_id': '1601943ba14655923bde8b7420e02f14b13f', 'display_name': 'Schiit', 'outputs': [{'output_id': '1701943ba14655923bde8b7420e02f14b13f', 'zone_id': '1601943ba14655923bde8b7420e02f14b13f', 'can_group_with_output_ids': ['1701943ba14655923bde8b7420e02f14b13f'], 'display_name': 'Schiit', 'source_controls': [{'control_key': '1', 'display_name': 'snd_rpi_hifiberry_digi', 'supports_standby': False, 'status': 'indeterminate'}]}], 'state': 'playing', 'is_next_allowed': True, 'is_previous_allowed': True, 'is_pause_allowed': True, 'is_play_allowed': False, 'is_seek_allowed': True, 'queue_items_remaining': 4966, 'queue_time_remaining': 1239308, 'settings': {'loop': 'disabled', 'shuffle': False, 'auto_radio': True}, 'now_playing': {'seek_position': None, 'length': 281, 'one_line': {'line1': 'Love on Display - Trip Lee / Andy Mineo'}, 'two_line': {'line1': 'Love on Display', 'line2': 'Trip Lee / Andy Mineo'}, 'three_line': {'line1': 'Love on Display', 'line2': 'Trip Lee / Andy Mineo', 'line3': 'The Good Life'}, 'image_key': '5277e87fd218226e047c257df269259d', 'artist_image_keys': ['96cbd0876317b528b19dc7733a5e2a39', 'c013ffa439a88ecdf80c944ea34a3e69']}, 'seek_position': None}