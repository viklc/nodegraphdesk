from canvaseventtypes import KeyboardEvent
from nodegraphdesk import getConfig, assignContext, clearMapping

def createEventHandler(uievent, pending_actions):
    if isinstance(uievent, KeyboardEvent) and uievent.eventtype == 'keyhit':
            if uievent.key == getConfig()['assign_hotkey']: assignContext()
            elif uievent.key == getConfig()['clear_mapping_hotkey']: clearMapping()
    return None, False
