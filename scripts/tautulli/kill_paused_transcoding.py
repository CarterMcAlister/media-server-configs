#!/usr/bin/python

"""
Kill Plex paused video transcoding streams.
Tautulli > Settings > Notification Agents > Scripts > Bell icon:
        [X] Notify on playback pause
Tautulli > Settings > Notification Agents > Scripts > Gear icon:
        Playback Pause: new_kill_trans_pause.py
"""

import requests
import platform
from uuid import getnode

################################################################################################
## PLEASE CONFIGURE ACCORDINGLY

PLEX_HOST = '127.0.0.1'
PLEX_PORT = 32400
PLEX_SSL = ''  # s or ''
PLEX_TOKEN = ''
MESSAGE = 'This stream has ended due to being paused and transcoding.'

USER_IGNORE = ('') # ('Username','User2')

################################################################################################


def fetch(path, t='GET'):
    url = 'http%s://%s:%s/' % (PLEX_SSL, PLEX_HOST, PLEX_PORT)

    headers = {'X-Plex-Token': PLEX_TOKEN,
               'Accept': 'application/json',
               'X-Plex-Provides': 'controller',
               'X-Plex-Platform': platform.uname()[0],
               'X-Plex-Platform-Version': platform.uname()[2],
               'X-Plex-Product': 'Tautulli script',
               'X-Plex-Version': '0.9.5',
               'X-Plex-Device': platform.platform(),
               'X-Plex-Client-Identifier': str(hex(getnode()))
               }

    try:
        if t == 'GET':
            r = requests.get(url + path, headers=headers, verify=False)
        elif t == 'POST':
            r = requests.post(url + path, headers=headers, verify=False)
        elif t == 'DELETE':
            r = requests.delete(url + path, headers=headers, verify=False)

        if r and len(r.content):  # incase it dont return anything

            return r.json()
        else:
            return r.content

    except Exception as e:
        print e

def kill_stream(sessionId, message):
    headers = {'X-Plex-Token': PLEX_TOKEN}
    params = {'sessionId': sessionId,
              'reason': message}
    requests.get('http://{}:{}/status/sessions/terminate'.format(PLEX_HOST, PLEX_PORT),
                     headers=headers, params=params)

if __name__ == '__main__':
    response  = fetch('status/sessions')

    for s in response['MediaContainer']['Video']:
        try:
            if s['TranscodeSession']['videoDecision'] == 'transcode' and s['User']['title'] not in USER_IGNORE \
                    and s['Player']['state'] == 'paused':
                print("Killing {}'s stream for pausing a transcode stream of {}".format(s['User']['title'], s['title']))
                kill_stream(s['Session']['id'], MESSAGE)
        except Exception:
            pass

