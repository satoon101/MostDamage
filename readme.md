# MostDamage

## Introduction
MostDamage is a plugin created for [Source.Python](https://github.com/Source-Python-Dev-Team/Source.Python).  As such, it requires [Source.Python](https://github.com/Source-Python-Dev-Team/Source.Python) to be installed on your Source-engine server.  It currently only supports CS:GO and CS:S.  Further support will be added to more games in the future.

This plugin shows which player had the most kills at the end of each round.  If more than one player has the most kills, the amount of damage done to other players is used to determine which player is shown.

<br>
## Installation
To install, simply download the current release from its [release thread](http://forums.sourcepython.com/showthread.php?64) and install in into the main directory on your server.

Once you have installed MostDamage on your server, simply add the following to your autoexec.cfg file:
```
sp plugin load most_damage
```

<br>
After having loaded the plugin once, a configuration file will have been created on your server at **../cfg/source-python/most_damage.cfg**

Edit that file to your liking.  The current default configuration file looks like:
```
// Options
//   * 0 = Off
//   * 1 = HudHint
//   * 2 = CenterMsg
//   * 3 = HudHint & CenterMsg
//   * 4 = KeyHint
//   * 5 = HudHint & KeyHint
//   * 6 = CenterMsg & KeyHint
//   * 7 = HudHint, CenterMsg & KeyHint
// Default Value: 1
// Default placement of the most damage message
   md_default_location 1
```

<br>
## Screenshots
The following are screenshots of the messages that accompany this plugin:

<br>
