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
from messages import HudDestination
from messages import KeyHintText
from messages import TextMsg
#   Players
from players.entity import Player
from players.helpers import index_from_userid
#   Settings
from settings.player import PlayerSettings
#   Translations
from translations.strings import LangStrings

# Script Imports
from most_damage.info import info


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Get the translations
most_damage_strings = LangStrings(info.basename)

# Get the message instances
most_damage_messages = {
    1: HintText(most_damage_strings[info.name]),
    2: TextMsg(most_damage_strings[info.name], HudDestination.CENTER),
    4: KeyHintText(most_damage_strings[info.name]),
}

# Create the user settings
user_settings = PlayerSettings(info.name, 'md')

# Get the human player index iterator
_human_players = PlayerIter('human')

# Store the possible options
_options = {int(
    item.split(':')[1]): value for item, value in most_damage_strings.items(
        ) if item.startswith('Option:')}


# =============================================================================
# >> CONFIGURATION
# =============================================================================
# Create the most_damage.cfg file and execute it upon __exit__
with ConfigManager(info.basename) as config:

    # Create the default location convar
    default_location = config.cvar(
        'md_default_location', 1, most_damage_strings['Default Location'])

    # Loop through the possible location options
    for _item, _value in sorted(_options.items()):

        # Add the current option to the convar's text
        default_location.Options.append(
            '{0} = {1}'.format(_item, _value.get_string()))


# =============================================================================
# >> CLASSES
# =============================================================================
class _MostDamage(dict):
    """Stores player damage and kills and sends message on round end."""

    def __init__(self):
        """Create the user settings."""
        # Call super class' init
        super().__init__()

        # Create the location user setting
        self.location_setting = user_settings.add_string_setting(
            'Location', default_location.get_string(),
            most_damage_strings['Location'])

        # Loop through each location option
        for item, value in sorted(_options.items()):

            # Add the option to the user settings
            self.location_setting.add_option(str(item), value)

    def __missing__(self, userid):
        """Add the userid to the dictionary with the default values."""
        # Get the userid's dictionary
        value = self[userid] = {'kills': 0, 'damage': 0}

        # Return the dictionary
        return value

    def __delitem__(self, userid):
        """Verify the userid is in the dictionary before removing them."""
        # Is the userid in the dictionary?
        if userid in self:

            # Remove the userid from the dictionary
            super().__delitem__(userid)

    def send_message(self):
        """Send messages to players depending on their individual setting."""
        # Was any damage done this round?
        if not self:

            # If not, no need to send any messages
            return

        # Sort the players by kills/damage
        sorted_players = sorted(self, key=lambda userid: (
            self[userid]['kills'], self[userid]['damage']), reverse=True)

        # Get the userid of the most destructive player
        top_userid = sorted_players[0]

        # Set the tokens for the message
        tokens = {
            'name': Player(index_from_userid(top_userid)).name,
            'kills': self[top_userid]['kills'],
            'damage': self[top_userid]['damage']}

        # Loop through all human player indexes
        for player in _human_players:

            # Get the current player's setting
            places = int(self.location_setting.get_setting(player.index))

            # Loop through the message types
            for location, message in most_damage_messages.items():

                # Does the current message need to be sent?
                if not places & location:

                    # If not, continue to the next message
                    continue

                # Send the message to the player
                message.send(player.index, **tokens)

# Get the _MostDamage instance
most_damage = _MostDamage()


# =============================================================================
# >> GAME EVENTS
# =============================================================================
@Event('player_hurt', 'player_death')
def player_action(game_event):
    """Called any time a player is hurt or killed."""
    # Get the attacker's userid
    attacker = game_event['attacker']

    # Get the victim's userid
    victim = game_event['userid']

    # Is this self inflicted?
    if attacker in (victim, 0):
        return

    # Was this a team inflicted?
    if Player(index_from_userid(
            attacker)).team == Player(index_from_userid(victim)).team:
        return

    # Is this player_death?
    if game_event.name == 'player_death':

        # Add a kill to the attacker's stats
        most_damage[attacker]['kills'] += 1

        # Go no further
        return

    # This is player_hurt, so add the damage
    most_damage[attacker]['damage'] += game_event['dmg_health']


@Event('player_disconnect')
def player_disconnect(game_event):
    """Remove the player from the dictionary."""
    del most_damage[game_event['userid']]


@Event('round_start')
def round_start(game_event):
    """Clear the dictionary each new round."""
    most_damage.clear()


@Event('round_end')
def round_end(game_event):
    """Send messages about most damage each end of round."""
    most_damage.send_message()
