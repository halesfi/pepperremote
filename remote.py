#!/usr/bin/python
# -*- encoding: UTF-8 -*-

''' Simple Pepper remote via HTTP '''

import logging
import argparse
import sys
import BaseHTTPServer
import re
import os
try:
    import qi
except ImportError:
    pass

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
PORT = 8088
logging.basicConfig(filename=os.environ['HOME']+'/.local/log/remote.log',
        level=logging.DEBUG,
        format='[%(levelname).1s] %(asctime)s %(message)s',
        datefmt='%b %d %H:%M:%S')

class MyHTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    remote = None

    def log_message(self, format, *args):
        logging.info("%s - - %s" %
                (self.client_address[0], format%args))

    #Handler for the GET requests
    def do_GET(self):
        parmatch = re.match(r'/\?('+'|'.join(BUTTONS.keys())+')=', self.path)
        if self.path == '/':
            self.send_string('text/html', self.remote.form())
        elif parmatch:
            self.send_string('text/html', self.remote.form(parmatch.group(1)))
        else: self.send_response(404)
        return

    def send_string(self, type, text, cached = False):
        self.send_response(200)
        self.send_header('Content-type',type)
        if cached:
            self.send_header("Cache-control","max-age=2592000"); # 30days (60sec * 60min * 24hours * 30days)
        self.end_headers()
        self.wfile.write(text)


class RemoteModule(object):
    """
    Simple Pepper remote
    """

    def __init__( self, app):
        """
        Initialise services and variables.
        """
        super(RemoteModule, self).__init__()
        self.app = app
        self.module_name = "RemoteModule"
        self.qi_disabled = True

    def init_qi( self):
        """
        Initialise services and variables.
        """
        self.qi_disabled = False
        try:
            self.app.start()
            session = self.app.session
        except:
            self.qi_disabled = True

        if not self.qi_disabled:
            try:
                self.tts = session.service("ALTextToSpeech")
                self.motion = session.service("ALMotion")
                self.dialog = session.service("ALDialog")
                self.aware = session.service("ALBasicAwareness")
                self.amoves = session.service("ALAutonomousMoves")
                self.posture = session.service("ALRobotPosture")
            except:
                self.qi_disabled = True

    def run_robot(self, action):
        """
        Start processing at robot
        """
        self.init_qi()
        motion_x = 0.0
        motion_y = 0.0
        motion_theta = 0.0
        if action == "forward": motion_x = 0.5
        elif action == "backward": motion_x = -0.5
        elif action == "left": motion_y = 0.5
        elif action == "right": motion_y = -0.5
        elif action == "turnleft": motion_theta = 0.5
        elif action == "turnright": motion_theta = -0.5
        if self.qi_disabled:
            return ("{} (robot not connected)".format(action))
        self.motion.moveInit();
        self.motion.moveToward(motion_x, motion_y, motion_theta)
        say_text = action
        if action == "setcz":
            self.dialog.setLanguage("Czech")
            say_text = "Přepínám na češtinu"
        elif action == "seten":
            self.dialog.setLanguage("English")
            say_text = "Switching to English"
        elif action == "getl":
            action = self.dialog.getLanguage()
            if action == "Czech":
                say_text = "Teď mám češtinu"
            elif action == "English":
                say_text = "Now I have English"
        elif action == "aon":
            self.amoves.setBackgroundStrategy("backToNeutral")
            self.aware.setEnabled(True)
            self.posture.stopMove()
            say_text = "Awarness on"
        elif action == "aoff":
            self.aware.setEnabled(False)
            self.amoves.setBackgroundStrategy("none")
            self.posture.setMaxTryNumber(3)
            self.posture.goToPosture("Stand", 0.8)
            say_text = "Awarness off"
        self.tts.say(say_text)
        return (action)


    def form(self, action = None):
        buttons = BUTTONS
        htmlvars = {
            "title": "Pepper Remote",
            "msg": ""}
        for b, par in buttons.items():
            htmlvars["but"+str(par["id"])+"name"] = b
            htmlvars["but"+str(par["id"])+"value"] = par["label"]
            htmlvars["but"+str(par["id"])+"class"] = par["class"]

        #htmlvars["msg"] = "forward='{}'".format(buttons["forward"]["value"])
        if action is not None:
            htmlvars["msg"] = self.run_robot(action)
        template="""
<!DOCTYPE html>
<html lang="en">
<head>

  <!-- Basic Page Needs
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <meta charset="utf-8">
  <title>%(title)s</title>
  <meta name="description" content="">
  <meta name="author" content="">

  <!-- Mobile Specific Metas
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <style>
    @media (min-width: 801px) {
      html { font-size: 20px; }
    }
    @media (min-width: 401px) {
      html { font-size: 16px; }
    }
    @media (min-width: 301px) {
      html { font-size: 14px; }
    }
    h1 { font-size: 1.5rem; }
    p { font-size: 1rem; }
    body {background-color: white;}
    td {text-align: center;}
    .button-primary {
        background-color: lightblue;
        padding: 0.1rem 2rem;
        font-size: 2rem;
        font-weight: 900;
    }
    .symbol { font-size: 3rem; }
  </style>

</head>
<body>

  <!-- Primary Page Layout
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <h2>%(title)s</h2>

  <p>
  <form method='GET'>
  <table border="0" width="100%%">
  <tr>
    <td colspan="3">
        %(msg)s
    </td>
  </tr>
  <tr>
	<td>
          <input class="button-primary %(but11class)s" type="submit" name="%(but11name)s" value="%(but11value)s">
	</td>
	<td>
          &nbsp;
	</td>
	<td>
          <input class="button-primary %(but12class)s" type="submit" name="%(but12name)s" value="%(but12value)s">
	</td>
  </tr>
  <tr>
    <td colspan="3">
      <p style="margin-bottom: 2rem">&nbsp;</p>
    </td>
  </tr>
  <tr>
	<td>
      &nbsp;
	</td>
	<td>
      <input class="button-primary %(but1class)s" type="submit" name="%(but1name)s" value="%(but1value)s">
	</td>
	<td>
      &nbsp;
	</td>
  </tr>
  <tr>
	<td>
      <input class="button-primary %(but2class)s" type="submit" name="%(but2name)s" value="%(but2value)s">
	</td>
	<td>
      <input class="button-primary %(but3class)s" type="submit" name="%(but3name)s" value="%(but3value)s">
	</td>
	<td>
      <input class="button-primary %(but4class)s" type="submit" name="%(but4name)s" value="%(but4value)s">
	</td>
  </tr>
  <tr>
	<td>
      <input class="button-primary %(but5class)s" type="submit" name="%(but5name)s" value="%(but5value)s">
	</td>
	<td>
      <input class="button-primary %(but6class)s" type="submit" name="%(but6name)s" value="%(but6value)s">
	</td>
	<td>
      <input class="button-primary %(but7class)s" type="submit" name="%(but7name)s" value="%(but7value)s">
	</td>
  </tr>
  <tr>
    <td colspan="3">
      <p style="margin-bottom: 2rem">&nbsp;</p>
    </td>
  </tr>
  <tr>
	<td>
      <input class="button-primary %(but8class)s" type="submit" name="%(but8name)s" value="%(but8value)s">
	</td>
	<td>
      <input class="button-primary %(but9class)s" type="submit" name="%(but9name)s" value="%(but9value)s">
	</td>
	<td>
      <input class="button-primary %(but10class)s" type="submit" name="%(but10name)s" value="%(but10value)s">
	</td>
  </tr>
  </table>
  </form>
  </p>

<!-- End Document
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
</body>
</html>
"""
        return (template % htmlvars)

    def run(self):
        """
        CGI
        """
        MyHTTPHandler.remote = self
        httpd = BaseHTTPServer.HTTPServer(("", PORT), MyHTTPHandler)
        logging.info("serving at port {}".format(PORT))
        httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default="127.0.0.1", help="Robot IP address")
    parser.add_argument("--pport", type=int, default=9559, help="Robot port number")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.pip + ":" + str(args.pport)
        app = qi.Application(["RemoteModule", "--qi-url=" + connection_url])
    except RuntimeError:
        logging.warn("Can't connect to Naoqi at ip \"" + args.pip + "\" on port " + str(args.pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        #sys.exit(1)
    except:
        app = None
        pass
    MyRemote = RemoteModule(app)
    MyRemote.run()
