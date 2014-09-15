# ../most_damage/most_damage.py

"""Sends messages on round end about the player who caused the most damage."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Config
from config.manager import ConfigManager
#   Events
from events import Event
#   Filters
from filters.players import PlayerIter
#   Messages
from messages import HintText
from messages import KeyHintText
from messages import TextMsg
#   Players
from players.helpers import playerinfo_from_userid
#   Settings
from settings.player import PlayerSettings
#   Translations
from translations.strings import LangStrings

# Script Imports
from most_damage.info import info


# =============================================================================
# >> PUBLIC VARIABLE
# =============================================================================
# Make sure the variable is set to the proper version
info.convar.set_string(info.version)

# Make the variable public
info.convar.make_public()


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Get the translations
most_damage_strings = LangStrings('most_damage')

# Get the message instances
most_damage_messages = {
    1: HintText(message=most_damage_strings['Most Damage']),
    2: TextMsg(
        message=most_damage_strings['Most Damage'],
        destination=TextMsg.HUD_PRINTCENTER),
    4: KeyHintText(message=most_damage_strings['Most Damage']),
}

# Create the user settings
user_settings = PlayerSettings('Most Damage', 'md')

# Get the human player index iterator
_human_players = PlayerIter('human')

# Store the possible options
_options = [
    'HudHint',
    'CenterMsg',
    'HudHint & CenterMsg',
    'KeyHint',
    'HudHint & KeyHint',
    'CenterMsg & KeyHint',
    'HudHint, CenterMsg, & KeyHint',
]


# =============================================================================
# >> CONFIGURATION
# =============================================================================
# Create the most_damage.cfg file and execute it upon __exit__
with ConfigManager('most_damage') as config:

    # Create the default location convar
    default_location = config.cvar(
        'md_default_location', '1', 0, most_damage_strings['Default Location'])

    # Loop through the possible location options
    for _number, _option in enumerate(_options):

        # Add the current option to the convar's text
        default_location.Options.append(
            '{0} = {1}'.format(_number + 1, _option))


# =============================================================================
# >> CLASSES
# =============================================================================
class _MostDamage(dict):

    """Stores player damage and kills and sends message on round end."""

    def __init__(self):
        """Create the user settings."""
        # Create the location user setting
        self._location_setting = user_settings.add_string_setting(
            'Location', default_location.get_int(),
            most_damage_strings['Location'])

        # Loop through each location option
        for option in _options:

            # Add the option to the user settings
            self._location_setting.addoption(option)

    def __missing__(self, userid):
        """Add the userid to the dictionary as a _PlayerDamage instance."""
        # Get the userid's _PlayerDamage instance
        value = self[userid] = _PlayerDamage()

        # Return the _PlayerDamage instance
        return value

    def __delitem__(self, userid):
        """Verify the userid is in the dictionary before removing them."""
        # Is the userid in the dictionary?
        if userid in self:

            # Remove the userid from the dictionary
            super(_MostDamage, self).__delitem__(userid)

    def send_message(self):
        """Send messages to players depending on their individual setting."""
        # Was any damage done this round?
        if not self:

            # If not, no need to send any messages
            return

        # Sort the players by number of kills
        sorted_killers = sorted(
            self, key=lambda userid: self[userid].kills, reverse=True)

        # Get the most number of kills
        most_kills = self[sorted_killers[0]].kills

        # Get the players that had the most kills
        top_killers = [
            userid for userid in self
            if self[userid].kills == most_kills]

        # Sort the players with the most kills by the damage they did
        sorted_damage = sorted(
            top_killers, key=lambda userid: self[userid].damage, reverse=True)

        # Get the most destructive player
        top_damage = sorted_damage[0]

        # Get the player's IPlayerInfo instance
        player = playerinfo_from_userid(top_damage)

        # Get the most destructive player's name
        top_name = player.get_name()

        # Loop through the message types to add the tokens
        for message in most_damage_messages.values():

            # Set the tokens for the message
            message.tokens = {
                'name': top_name, 'kills': self[top_damage].kills,
                'damage': self[top_damage].damage}

        # Loop through all human player indexes
        for index in _human_players:

            # Get the current player's setting
            places = self._location_setting.get_setting(index)

            # Loop through the message types
            for location, message in most_damage_messages.items():

                # Does the current message need to be sent?
                if not places & location:

                    # If not, continue to the next message
                    continue

                # Send the message to the player
                message.send(index)

# Get the _MostDamage instance
most_damage = _MostDamage()


class _PlayerDamage(object):

    """Stores information on player damage and kills."""

    # Set damage and kills to 0 on instantiation
    damage = 0
    kills = 0


# =============================================================================
# >> GAME EVENTS
# =============================================================================
@Event
def player_hurt(game_event):
    """Called any time a player is hurt."""
    # Get the attacker's userid
    attacker = _get_valid_attacker(game_event)

    # Should the attack count?
    if attacker is None:

        # If not, just return
        return

    # Get the amount of damage done
    damage = game_event.get_int('dmg_health')

    # Add the amount of damage to the attacker's stats
    most_damage[attacker].damage += damage


@Event
def player_death(game_event):
    """Called any time a player dies."""
    # Get the attacker's userid
    attacker = _get_valid_attacker(game_event)

    # Should the attack count?
    if attacker is not None:

        # Add a kill to the attacker's stats
        most_damage[attacker].kills += 1


@Event
def player_disconnect(game_event):
    """Called when a player disconnects from the server."""
    # Get the player's userid
    userid = game_event.get_int('userid')

    # Remove the player from the dictionary
    del most_damage[userid]


@Event
def round_start(game_event):
    """Clear the dictionary each new round."""
    most_damage.clear()


@Event
def round_end(game_event):
    """Send messages about most damage each end of round."""
    most_damage.send_message()


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def _get_valid_attacker(game_event):
    """Return the attacker's userid if not a self or team inflicted event."""
    # Get the attacker's userid
    attacker = game_event.get_int('attacker')

    # Get the victim's userid
    victim = game_event.get_int('userid')

    # Was this self inflicted?
    if attacker in (victim, 0):

        # If self, inflicted, do not count
        return None

    # Get the victim's PlayerInfo instance
    vplayer = playerinfo_from_userid(victim)

    # Get the attacker's PlayerInfo instance
    aplayer = playerinfo_from_userid(attacker)

    # Are the player's on the same team?
    if vplayer.get_team_index() == aplayer.get_team_index():

        # Do not count
        return None

    # If all checks pass, count the attack/kill
    return attacker
