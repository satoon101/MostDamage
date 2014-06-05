# ../most_damage/info.py

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
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
info.convar = ServerVar(info.variable, info.version, 0, info.name + ' Version')
