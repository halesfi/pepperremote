# Pepper Remote
simple remote for Pepper

Developed at [NLP Centre](https://nlp.fi.muni.cz/en), [FI MU](https://www.fi.muni.cz/index.html.en) for [Karel Pepper](https://nlp.fi.muni.cz/trac/pepper)

## Installation

* log to the robot via `ssh`
* `mkdir /home/nao/bin /home/nao/.local/logs`
* copy `remote.py` to `/home/nao/bin/` (e.g. with `scp`)
* try to run `/home/nao/bin/remote.py` from the command line. Then
  * watch the logs via `tail -f /home/nao/.local/logs/remote.log`
  * connect from a computer or a mobile on the same network via entering `http://<robot ip>>:8088/` in a web browser
  * cancel the program with `Ctrl+C` or `kill`
* in `/home/nao/naoqi/preferences/autoload.ini` add one line to the `[program]` section 
  ```
  [program]
  #the/full/path/to/your/program            # load program
  /home/nao/bin/remote.py
  ```
  This will ensure that the `remote.py` is run automatically after booting
  
  ## Adaptations
  
  The buttons are indetified via their `id` and `label`:
  ```
  BUTTONS = {
    "forward": {"id": 1, "label": "↑", "value": None, "class": "symbol"},
    "turnleft": {"id": 2, "label": "↶", "value": None, "class": "symbol"},
    "stop": {"id": 3, "label": "⌾", "value": None, "class": "symbol"},
    "turnright": {"id": 4, "label": "↷", "value": None, "class": "symbol"},
    "left": {"id": 5, "label": "←", "value": None, "class": "symbol"},
    "backward": {"id": 6, "label": "↓", "value": None, "class": "symbol"},
    "right": {"id": 7, "label": "→", "value": None, "class": "symbol"},
    "setcz": {"id": 8, "label": "CZ", "value": None, "class": ""},
    "getl": {"id": 9, "label": "get", "value": None, "class": ""},
    "seten": {"id": 10, "label": "EN", "value": None, "class": ""},
    "aon": {"id": 11, "label": "aON", "value": None, "class": ""},
    "aoff": {"id": 12, "label": "aOFF", "value": None, "class": ""},
  }
  ```
  Their layout on the web page is defined in `def form()` in the `template` HTML string, where each button is identified via its numerial `id`:
  ```
  <input class="button-primary %(but1class)s" type="submit" name="%(but1name)s" value="%(but1value)s">
  ```
  The actual functions run on the robot are called in `def run_robot(self, action)`
