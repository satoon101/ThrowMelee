# ../throw_melee/throw_melee.py

"""."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
from collections import defaultdict

# Source.Python
from commands.client import ClientCommand
from entities.constants import DamageTypes
from entities.entity import Entity
from entities.hooks import EntityCondition, EntityPreHook
from events import Event
from filters.weapons import WeaponClassIter
from listeners import OnEntityDeleted
from listeners.tick import Delay
from memory import make_object
from messages import SayText2, TextMsg
from players.constants import HitGroup
from players.entity import Player
from players.helpers import index_from_userid
from weapons.entity import Weapon

# Plugin
from .config import allow_pickup, melee_damage, remove_delay, total_max
from .strings import MESSAGE_STRINGS


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
_melee_weapons = [weapon.name for weapon in WeaponClassIter('melee')]

_available_count = defaultdict(int)
_throwers = {}
_marked_for_removal = set()


# =============================================================================
# >> CLIENT COMMANDS
# =============================================================================
@ClientCommand('drop')
def _drop_command(command, index):
    """Throw melee weapon on 'drop'."""
    player = Player(index)
    class_name = getattr(player.active_weapon, 'classname', None)
    if class_name not in _melee_weapons:
        return True

    if not _available_count[player.userid]:
        TextMsg(MESSAGE_STRINGS['Empty']).send(index)
        return

    _available_count[player.userid] -= 1
    TextMsg(MESSAGE_STRINGS['Remaining']).send(
        index,
        current=_available_count[player.userid],
        total=int(total_max),
    )

    start_location = player.eye_location
    velocity = player.view_coordinates - start_location
    weapon = Weapon.create(class_name)
    weapon.spawn()
    weapon.teleport(origin=start_location, velocity=velocity * 200)
    _throwers[weapon.index] = player.userid

    delay = int(remove_delay)
    weapon.delay(delay, weapon.remove)


# =============================================================================
# >> ENTITY HOOKS
# =============================================================================
@EntityPreHook(EntityCondition.is_bot_player, 'bump_weapon')
@EntityPreHook(EntityCondition.is_human_player, 'bump_weapon')
def _pre_bump_weapon(stack_data):
    """Damage player or give extra if bump is from thrown weapon."""
    weapon = make_object(Entity, stack_data[1])
    if weapon.classname not in _melee_weapons:
        return

    index = weapon.index
    if index not in _throwers:
        return

    if index in _marked_for_removal:
        return

    player = make_object(Player, stack_data[0])
    asleep = weapon.physics_object.asleep
    attacker_userid = _throwers[index]
    if attacker_userid == player.userid and not asleep:
        return

    weapon.delay(0, weapon.remove)
    _marked_for_removal.add(weapon.index)
    Delay(0, _marked_for_removal.remove, (weapon.index,))

    if not asleep:
        player.take_damage(
            damage=int(melee_damage),
            # TODO: verify damage type
            damage_type=DamageTypes.SLASH,
            attacker_index=index_from_userid(attacker_userid),
            weapon_index=weapon.index,
            # TODO: determine how to find hitgroup
            hitgroup=HitGroup.CHEST,
        )
        return

    if not bool(allow_pickup):
        return

    TextMsg(MESSAGE_STRINGS['Gained']).send(player.index)
    _available_count[player.userid] += 1


# =============================================================================
# >> GAME EVENTS
# =============================================================================
@Event('player_spawn')
def _reset_count_on_spawn(game_event):
    """Reset the player's count."""
    _available_count[game_event['userid']] = int(total_max)


@Event('player_activate')
def _send_advert_on_connect(game_event):
    """Send a message about the plugin."""
    SayText2(MESSAGE_STRINGS['Advert']).send(
        index_from_userid(game_event['userid'])
    )


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnEntityDeleted
def _remove_index_from_throwers(base_entity):
    """Remove item from dictionary when entity is removed."""
    if not base_entity.is_networked():
        return

    index = base_entity.index
    if index in _throwers:
        del _throwers[index]
