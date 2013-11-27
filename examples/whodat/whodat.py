import sage
from sage.signals.gmcp import room as room_signal
from sage import player, aliases

# Create an alias group for whodat
who_aliases = aliases.create_group('whodat', app='whodat')

# store in the app what our last room id was so we know when we change rooms
last_room = None

def write_players():
    if len(player.room.players) > 0:  # if there are players in the room
        players = ', '.join(player.room.players)  # format players into CSV
        sage.buffer.insert(len(sage.buffer) - 1, 'Who: ' + players)  # Insert line above exits in QL


def on_room_update(signal, room):

    def update_players():
        # use of global isn't encouraged, but in this case it was a simple solution
        global last_room

        # we get room events even if we don't change rooms. eg: squinting.
        if player.room.id == last_room:
            return

        last_room = player.room.id
        write_players()

    # Why defer to prompt? Because GMCP data and the actual lines from Achaea don't always come
    # at the same time. To make sure we don't get out of sync, we defer to the prompt when
    # everything should be ready.
    sage.defer_to_prompt(update_players)


# Connect to the GMCP Room.Info signal
room_signal.connect(on_room_update)


# Write players when we just do QL as well
@who_aliases.exact(pattern='ql', intercept=False)
def ql(alias):
    sage.defer_to_prompt(write_players)
