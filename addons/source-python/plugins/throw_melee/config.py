# ../throw_melee/config.py

"""Contains all translation variables for the plugin."""

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
    "allow_pickup",
    "melee_damage",
    "remove_delay",
    "total_max",
)


# =============================================================================
# >> CONFIGURATION
# =============================================================================
with ConfigManager(info.name, "throw_melee_") as _config:
    remove_delay = _config.cvar(
        name="remove_delay",
        default=10,
        description=CONFIG_STRINGS["remove_delay"],
        min_value=1,
    )
    total_max = _config.cvar(
        name="total_max",
        default=3,
        description=CONFIG_STRINGS["total_max"],
        min_value=1,
    )
    allow_pickup = _config.cvar(
        name="allow_pickup",
        default=1,
        description=CONFIG_STRINGS["allow_pickup"],
    )
    melee_damage = _config.cvar(
        name="melee_damage",
        default=100,
        description=CONFIG_STRINGS["melee_damage"],
        min_value=0,
    )
    advert_delay = _config.cvar(
        name="advert_delay",
        default=5,
        description=CONFIG_STRINGS["advert_delay"],
        min_value=0,
    )
