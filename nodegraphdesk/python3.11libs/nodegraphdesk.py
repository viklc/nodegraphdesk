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


def aliasMapping(node_type: list, alias_map: dict) -> list:
    """ ------------------------------------------------------------------------------------------------
    Returns a node_type list with aliases if some are available.
    ------------------------------------------------------------------------------------------------ """
    if node_type[0] in alias_map.keys():
        node_type.append(alias_map[node_type[0]])
    elif node_type[0] in alias_map.values():
        for k, v in alias_map.items():
            if v == node_type[0]: node_type.append(k)
    return node_type


def assignContext() -> None:
    """ ------------------------------------------------------------------------------------------------
    Assigns a nodegraph context (node type) to the desktop and stores it in the config file. It also 
    checks if an assignment already exists, if so a dialog appears with the option to reassign or remove.
    ------------------------------------------------------------------------------------------------ """
    config: dict = getConfig()
    nodegraphdesk_map: dict = config['nodegraphdesk_map']

    for pane_tab in hou.ui.paneTabs():
        if pane_tab.isCurrentTab() and pane_tab.type() == hou.paneTabType.NetworkEditor:
            if pane_tab.isUnderCursor():
                pane_name: str = pane_tab.name()
                node: hou.Node = pane_tab.pwd()
                node_type: str = [pane_tab.pwd().type().name()]
                if config['alias_mapping']:
                    node_type = aliasMapping(node_type, config['alias_map'])
                current_desktop: str = hou.ui.curDesktop().name()
                msg: str = ''
                node_type_icon: str = 'hicon:/SVGIcons.index?' + node.type().icon() + '.svg'
                if current_desktop not in nodegraphdesk_map.keys(): # Assign
                    nodegraphdesk_map[current_desktop] = (pane_name, node_type[0])
                    msg: str = f'Context {node_type} assigned to desktop {current_desktop}.'
                else:
                    if nodegraphdesk_map[current_desktop][1] in node_type:
                        msg: str = f'Context {node_type} already assigned to desktop {current_desktop}.'
                        if not hou.ui.displayMessage(msg, buttons=('Remove', 'Cancel', )):
                            msg: str = f'Context {node_type} removed from desktop {current_desktop}.'
                            node_type_icon: str = 'hicon:/SVGIcons.index?COMMON_delete.svg'
                            nodegraphdesk_map.pop(current_desktop)
                        else: # Cancel
                            msg: str = 'Canceled'
                            node_type_icon: str = 'hicon:/SVGIcons.index?COP2_delete.svg'
                    else:
                        msg: str = f'Context {nodegraphdesk_map[current_desktop][1]} is assigned with desktop {current_desktop}.\n Do you wish to reassign with {node_type}?'
                        state: int = hou.ui.displayMessage(msg, buttons=('Reassign', 'Remove', 'Cancel', ))
                        if state == 0: # Reassign
                            msg: str = f'Context {node_type} reassigned to the desktop {current_desktop}.'
                            nodegraphdesk_map.pop(current_desktop)
                            nodegraphdesk_map[current_desktop] = (pane_name, node_type[0])
                        elif state == 1: # Remove
                            msg: str = f'Context {nodegraphdesk_map[current_desktop][1]} removed from desktop {current_desktop}.'
                            node_type_icon: str = 'hicon:/SVGIcons.index?COMMON_delete.svg'
                            nodegraphdesk_map.pop(current_desktop)
                        else: # Cancel
                            msg: str = 'Canceled'
                            node_type_icon: str = 'hicon:/SVGIcons.index?COP2_delete.svg'

                config['nodegraphdesk_map'] = nodegraphdesk_map
                setConfig(config)
                pane_tab.flashMessage(node_type_icon, msg, 3)
                break


def clearMapping() -> None:
    """ ------------------------------------------------------------------------------------------------
    Clears the entries in configs nodegraphdesk_map dictionary.
    ------------------------------------------------------------------------------------------------ """
    if not hou.ui.displayMessage('Are you sure I want to clear the mapping?', buttons=('Yes', 'Cancel', )):
        config = getConfig()
        config['nodegraphdesk_map'] = {}
        setConfig(config)


def setPath(pane_name: str, path: str) -> None:
    """ ------------------------------------------------------------------------------------------------
    Sets nodegraph path.
    ------------------------------------------------------------------------------------------------ """
    for pane in hou.ui.paneTabs():
        if pane.name() == pane_name:
            pane.cd(path)


def nodegraphdesk(uievent) -> None:
    """ ------------------------------------------------------------------------------------------------
    Updates the desktop based on the assignment specified in the config file.
    ------------------------------------------------------------------------------------------------ """
    editor = uievent.editor
    node_type: list = [editor.pwd().type().name()]
    current_desktop = hou.ui.curDesktop()
    config: dict = getConfig()
    nodegraphdesk_map: dict = config['nodegraphdesk_map']
    if config['alias_mapping']:
        node_type = aliasMapping(node_type, config['alias_map'])
    nodegraph_change_state: bool = True
    for desktop in nodegraphdesk_map.keys():
        if not config['arbitrary_nodegraph_change']:
            nodegraph_change_state = nodegraphdesk_map[desktop][0] == editor.name()
        if desktop == current_desktop.name() and nodegraph_change_state:
            oldpath = uievent.oldcontext
            newpath = uievent.context
            if oldpath != newpath:
                for _desktop in nodegraphdesk_map.keys():
                    if nodegraphdesk_map[_desktop][1] in node_type:
                        desktops_dict = getDesktopDict()
                        desktops_dict[_desktop].setAsCurrent()
                        setPath(nodegraphdesk_map[_desktop][0], newpath)
            break


def handleEventCoroutine():
    """ ------------------------------------------------------------------------------------------------
    Extends Houdinis nodegraph event handling by wrapping the handleEventCoroutine generator from 
    $HFS/houdini/pythonX.Ylibs/nodegraph.py.
    ------------------------------------------------------------------------------------------------ """
    import nodegraph
    from canvaseventtypes import ContextEvent
    # import nodegraphview as view

    def _handleEventCoroutine(handleEventCoroutine = nodegraph.handleEventCoroutine): 
        coroutine = handleEventCoroutine()
        next(coroutine)
        uievent = yield
        keep_state = True
        while keep_state:
            uievent = yield
            if isinstance(uievent, ContextEvent):
                nodegraphdesk(uievent)
                # event_handler = None
                # keep_state = False

            try: coroutine.send(uievent)
            except StopIteration: break

    nodegraph.handleEventCoroutine = _handleEventCoroutine
