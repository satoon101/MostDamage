# ../most_damage/config.py

"""Creates server configuration and user settings."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from config.manager import ConfigManager

# Plugin
from .info import info
from .strings import CONFIG_STRINGS


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = (
    'LOCATION_OPTIONS',
    'default_location',
)


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Store the possible options
LOCATION_OPTIONS = {
    int(item.split(':')[1]): value
    for item, value in CONFIG_STRINGS.items()
    if item.startswith('Option:')
}


# =============================================================================
# >> CONFIGURATION
# =============================================================================
# Create the most_damage.cfg file and execute it upon __exit__
with ConfigManager(info.name) as config:

    # Create the default location convar
    default_location = config.cvar(
        'md_default_location', 1, CONFIG_STRINGS['Default Location']
    )

    # Loop through the possible location options
    for _item, _value in sorted(LOCATION_OPTIONS.items()):

        # Add the current option to the convar's text
        default_location.Options.append(
            '{value} = {text}'.format(
                value=_item,
                text=_value.get_string()
            )
        )
