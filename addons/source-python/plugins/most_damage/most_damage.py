# ../most_damage/most_damage.py

"""Sends messages on round end about the player who caused the most damage."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from events import Event
from filters.players import PlayerIter
from messages import HintText, HudDestination, KeyHintText, TextMsg
from players.entity import Player
from settings.player import PlayerSettings

# Plugin
from .config import LOCATION_OPTIONS, default_location
from .info import info
from .strings import MESSAGE_STRINGS

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Get the message instances
most_damage_messages = {
    1: HintText(MESSAGE_STRINGS[info.verbose_name]),
    2: TextMsg(MESSAGE_STRINGS[info.verbose_name], HudDestination.CENTER),
    4: KeyHintText(MESSAGE_STRINGS[info.verbose_name]),
}

# Create the user settings
user_settings = PlayerSettings(info.verbose_name, "md")

# Get the human player index iterator
_human_players = PlayerIter("human")


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
            "Location",
            str(default_location),
            MESSAGE_STRINGS["Location"],
        )

        # Loop through each location option
        for item, value in sorted(LOCATION_OPTIONS.items()):

            # Add the option to the user settings
            self.location_setting.add_option(str(item), value)

    def __missing__(self, userid):
        """Add the userid to the dictionary with the default values."""
        value = self[userid] = {"kills": 0, "damage": 0}
        return value

    def __delitem__(self, userid):
        """Verify the userid is in the dictionary before removing them."""
        if userid in self:
            super().__delitem__(userid)

    def add_damage(self, game_event):
        """Add the damage or kill for the player."""
        attacker = game_event["attacker"]
        victim = game_event["userid"]

        # Is this self inflicted?
        if attacker in (victim, 0):
            return

        # Was this a team inflicted?
        attacker_team = Player.from_userid(attacker).team
        victim_team = Player.from_userid(victim).team
        if attacker_team == victim_team:
            return

        # Is this player_death?
        if game_event.name == "player_death":

            # Add a kill to the attacker's stats
            self[attacker]["kills"] += 1
            return

        # This is player_hurt, so add the damage
        self[attacker]["damage"] += game_event["dmg_health"]

    def send_message(self):
        """Send messages to players depending on their individual setting."""
        # Was any damage done this round?
        if not self:
            return

        # Sort the players by kills/damage
        sorted_players = sorted(
            self,
            key=lambda userid: (self[userid]["kills"], self[userid]["damage"]),
            reverse=True,
        )

        # Get the userid of the most destructive player
        top_userid = sorted_players[0]

        # Set the tokens for the message
        tokens = {
            "name": Player.from_userid(top_userid).name,
            "kills": self[top_userid]["kills"],
            "damage": self[top_userid]["damage"],
        }

        # Loop through all human player indexes
        for player in _human_players:

            # Get the current player's setting
            places = int(self.location_setting.get_setting(player.index))

            # Loop through the message types
            for location, message in most_damage_messages.items():

                # Does the current message need to be sent?
                if places & location:
                    message.send(player.index, **tokens)


most_damage = _MostDamage()


# =============================================================================
# >> GAME EVENTS
# =============================================================================
@Event("player_hurt", "player_death")
def _player_action(game_event):
    most_damage.add_damage(game_event)


@Event("player_disconnect")
def _player_disconnect(game_event):
    """Remove the player from the dictionary."""
    del most_damage[game_event["userid"]]


@Event("round_start")
def _round_start(game_event):
    """Clear the dictionary each new round."""
    most_damage.clear()


@Event("round_end")
def _round_end(game_event):
    """Send messages about most damage each end of round."""
    most_damage.send_message()
