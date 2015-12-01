# ../most_damage/info.py

"""Provides/stores information about the plugin."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Cvars
from cvars.public import PublicConVar
#   Plugins
from plugins.info import PluginInfo


# =============================================================================
# >> PLUGIN INFO
# =============================================================================
info = PluginInfo()
info.name = 'Most Damage'
info.author = 'Satoon101'
info.version = '1.2'
info.basename = 'most_damage'
info.variable = info.basename + '_version'
info.url = 'http://www.sourcepython.com/showthread.php?85'
info.convar = PublicConVar(
    info.variable, info.version, 0, info.name + ' Version')
