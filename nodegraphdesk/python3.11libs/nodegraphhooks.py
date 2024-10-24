from canvaseventtypes import KeyboardEvent
from nodegraphdesk import getConfig, assignContext

def createEventHandler(uievent, pending_actions):
    if (isinstance(uievent, KeyboardEvent) 
        and uievent.eventtype == 'keyhit'
        and uievent.key == getConfig()['assign_hotkey']): assignContext()
    return None, False