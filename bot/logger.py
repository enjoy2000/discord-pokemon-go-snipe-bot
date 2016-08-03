from __future__ import unicode_literals
import time

def log(string, color='white'):
    color_hex = {
        'red': '91m',
        'green': '92m',
        'yellow': '93m',
        'blue': '94m',
        'cyan': '96m'
    }
    if color not in color_hex:
        print('[{time}]  {string}'.format(
            time=time.strftime("%H:%M:%S"),
            string=string
        ))
    else:
        print(
            '[{time}] \033[{color} {string} \033[0m'.format(
                time=time.strftime("%H:%M:%S"),
                color=color_hex[color],
                string=string
            )
        )