""" ------------------------------------------------------------------------------------------------
This nodegraph extension allows to assign a nodegraph context to a specific desktop. It uses a 
restrictive assignment approach to prevent misleading behavior, meaning that each desktop can only 
be linked to one of its nodegraphs pane with a specific context. To take effect, at least two links 
should be specified.

Credits to ajz3d and TristanG, see: https://www.sidefx.com/forum/topic/97428/
------------------------------------------------------------------------------------------------ """
import hou

NODEGRAPHDESK: str = hou.getenv('NODEGRAPHDESK')
config_path: str = NODEGRAPHDESK + '/nodegraphdesk_config.json'


def getConfig() -> dict:
    """ ------------------------------------------------------------------------------------------------
    Returns the config dictionary from nodegraphdesk path.
    ------------------------------------------------------------------------------------------------ """
    from json import load
    with open(config_path, 'r') as file:
        return load(file)
    

def setConfig(config: dict) -> None:
    """ ------------------------------------------------------------------------------------------------
    Sets config dictionary.
    ------------------------------------------------------------------------------------------------ """
    from json import dump
    with open(config_path, 'w') as file:
        dump(config, file, indent = 4)


def getDesktopDict() -> dict:
    """ ------------------------------------------------------------------------------------------------
    Returns a desktop dictionary.
    ------------------------------------------------------------------------------------------------ """
    return dict((d.name(), d) for d in hou.ui.desktops())


def selectDesktopDialog(current_desktop: str = None) -> str:
    """ ------------------------------------------------------------------------------------------------
    Returns the name of the selected desktop from the dialog - if canceled an empty string is returned.
    ------------------------------------------------------------------------------------------------ """
    desktops: tuple = tuple(desktop.name() for desktop in hou.ui.desktops())
    desktop_index: int = 0
    if current_desktop:
        for index, desktop in enumerate(desktops):
            if desktop == current_desktop: 
                desktop_index = index

    selected_desktop: tuple = hou.ui.selectFromList(desktops, default_choices=(desktop_index, ), 
                                                    exclusive=True, message=None, title='Assign a desktop',
                                                    column_header="Desktops", clear_on_cancel=True)
    if selected_desktop: return desktops[selected_desktop[0]]
    return ''


def aliasMapping(context: list, alias_map: dict) -> list:
    """ ------------------------------------------------------------------------------------------------
    Returns a context list with aliases if some are available.
    ------------------------------------------------------------------------------------------------ """
    for node_type, alias in alias_map.items():
        if node_type == context[0]: context.append(alias)
        elif alias == context[0]: context.append(node_type)
    return context


def assignContext() -> None:
    """ ------------------------------------------------------------------------------------------------
    Assigns a nodegraph context (node type) to the desktop and stores it in the config file. It also 
    checks if an assignment already exists, if so a dialog appears with the option to reassign or remove.
    ------------------------------------------------------------------------------------------------ """
    config: dict = getConfig()
    nodegraphdesk_map: dict = config['nodegraphdesk_map']

    for pane_tab in hou.ui.paneTabs():
        if pane_tab.type() == hou.paneTabType.NetworkEditor and pane_tab.isUnderCursor():
            pane_name: str = pane_tab.name()
            node: hou.Node = pane_tab.pwd()
            context: list = [pane_tab.pwd().type().name()]
            if config['alias_mapping']: context = aliasMapping(context, config['alias_map'])
            current_desktop: str = hou.ui.curDesktop().name()
            msg: str = ''
            context_icon: str = 'hicon:/SVGIcons.index?' + node.type().icon() + '.svg'

            if current_desktop not in nodegraphdesk_map.keys(): # Assign
                nodegraphdesk_map[current_desktop] = (pane_name, context[0])
                msg = f'Context {context} assigned to desktop {current_desktop}.'
            else:
                if nodegraphdesk_map[current_desktop][1] in context:
                    msg = f'Context {context} already assigned to desktop {current_desktop}.'
                    if not hou.ui.displayMessage(msg, buttons=('Remove', 'Cancel', )): # Remove
                        msg = f'Context {context} removed from desktop {current_desktop}.'
                        context_icon = 'hicon:/SVGIcons.index?COMMON_delete.svg'
                        nodegraphdesk_map.pop(current_desktop)
                    else: # Cancel
                        msg = 'Canceled'
                        context_icon = 'hicon:/SVGIcons.index?COP2_delete.svg'
                else:
                    msg = f'Context {nodegraphdesk_map[current_desktop][1]} is assigned with desktop {current_desktop}.\n Do you wish to reassign with {context}?'
                    state: int = hou.ui.displayMessage(msg, buttons=('Reassign', 'Remove', 'Cancel', ))
                    if state == 0: # Reassign
                        msg = f'Context {context} reassigned to the desktop {current_desktop}.'
                        nodegraphdesk_map.pop(current_desktop)
                        nodegraphdesk_map[current_desktop] = (pane_name, context[0])
                    elif state == 1: # Remove
                        msg = f'Context {nodegraphdesk_map[current_desktop][1]} removed from desktop {current_desktop}.'
                        context_icon = 'hicon:/SVGIcons.index?COMMON_delete.svg'
                        nodegraphdesk_map.pop(current_desktop)
                    else: # Cancel
                        msg  = 'Canceled'
                        context_icon = 'hicon:/SVGIcons.index?COP2_delete.svg'

            config['nodegraphdesk_map'] = nodegraphdesk_map
            setConfig(config)
            pane_tab.flashMessage(context_icon, msg, 3)
            break


def clearMapping() -> None:
    """ ------------------------------------------------------------------------------------------------
    Clears the entries in configs nodegraphdesk_map dictionary.
    ------------------------------------------------------------------------------------------------ """
    if not hou.ui.displayMessage('Are you sure I want to clear the mapping?', buttons=('Yes', 'Cancel', )):
        config = getConfig()
        config['nodegraphdesk_map'] = {}
        setConfig(config)


def desktopChange(uievent) -> None:
    """ ------------------------------------------------------------------------------------------------
    Updates the desktop based on the assignment specified in the config file.
    ------------------------------------------------------------------------------------------------ """
    editor: hou.NetworkEditor = uievent.editor
    context: list = [editor.pwd().type().name()]
    current_desktop: hou.Desktop = hou.ui.curDesktop()
    config: dict = getConfig()
    nodegraphdesk_map: dict = config['nodegraphdesk_map']
    if config['alias_mapping']: context = aliasMapping(context, config['alias_map'])

    if (hou.ui.paneTabUnderCursor() == editor # Verifies if change can be made
        and uievent.oldcontext != uievent.context 
        and current_desktop.name() in nodegraphdesk_map.keys()): 
            if (nodegraphdesk_map[current_desktop.name()][0] == editor.name()
                or config['arbitrary_nodegraph_change']):
                for desktop in nodegraphdesk_map.keys():
                    if nodegraphdesk_map[desktop][1] in context:
                        desktops_dict = getDesktopDict()
                        desktops_dict[desktop].setAsCurrent()
                        hou.ui.findPaneTab(nodegraphdesk_map[desktop][0]).cd(uievent.context) # Set path
                        break


def handleEventCoroutine():
    """ ------------------------------------------------------------------------------------------------
    Extends Houdinis nodegraph event handling by wrapping the handleEventCoroutine generator from 
    $HFS/houdini/pythonX.Ylibs/nodegraph.py.
    ------------------------------------------------------------------------------------------------ """
    import nodegraph
    from canvaseventtypes import ContextEvent

    def _handleEventCoroutine(handleEventCoroutine = nodegraph.handleEventCoroutine): 
        coroutine = handleEventCoroutine()
        next(coroutine)
        uievent = yield
        keep_state = True
        while keep_state:
            uievent = yield
            if isinstance(uievent, ContextEvent):
                desktopChange(uievent)
                keep_state = False
            try: coroutine.send(uievent)
            except StopIteration: break

    nodegraph.handleEventCoroutine = _handleEventCoroutine
