import time

import logging
from roonapi import RoonApi
import nowplaying

logging.basicConfig(level=logging.DEBUG)

appinfo = {
    "extension_id": "io.thepatrick.epaper-experiments",
    "display_name": "e-paper experiments",
    "display_version": "1.0.0",
    "publisher": "thepatrick",
}

# Can be None if you don't yet have a token
token = open("mytokenfile").read()

# Take a look at examples/discovery if you want to use discovery.
server = "10.2.8.10"

roonapi = RoonApi(appinfo, token, server)

try:
  ui = nowplaying.NowPlaying()
  ui.start()

  def my_state_callback(event, changed_ids):
    """Call when something changes in roon."""
    print("my_state_callback event:%s changed_ids: %s" % (event, changed_ids))
    for zone_id in changed_ids:
      zone = roonapi.zones[zone_id]

      if zone_id == '1601943ba14655923bde8b7420e02f14b13f':
        track = zone['now_playing']['two_line']['line1']
        artist = zone['now_playing']['two_line']['line2']

        pos = zone['seek_position']
        length = zone['now_playing']['length']

        if pos == None or length == None:
          progress = "0%"
        else:
          progress = "{:.1f}%".format(((pos / length) * 100))

        print("[%s (%s)] %s: %s %s" % (zone['display_name'], zone['state'], artist, track, progress))

        ui.update_ui(artist, track, pos, length)

  # receive state updates in your callback
  roonapi.register_state_callback(my_state_callback)
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:
    ui.sleep()
    ui.ctrl_c()
    exit()


# zones_seek_changed
# zones_changed

time.sleep(500)

# save the token for next time
with open("mytokenfile", "w") as f:
    f.write(roonapi.token)


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