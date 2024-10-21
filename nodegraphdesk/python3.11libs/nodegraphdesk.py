
""" ------------------------------------------------------------------------------------------------
This nodegraph extension allows to assign a nodegraph context to a specific desktop. It uses a 
restrictive assignment approach to prevent misleading behavior, meaning that each desktop can only 
be linked to one of its nodegraphs (pane) with a specific context.


Install: 
1. Download the folder nodegraphdesk and place it in a desired location. 
2. The folder contains a json file with the same name as the folder. Open it and set the property: 
"NODEGRAPHDESK" with the current directory where you have opened the file and save it. 
3. Now copy and paste this file under $HOUDINI_USER_PREF_DIR/packages.
For example, under windows: C:\Users\*user\Documents\houdini20.5\packages
4. Restart Houdini.
5. To assign a nodegraph context to the desktop, you must first set a shortkey for the 'Assign 
Context' shelf tool. Press the plus button on the right-hand side of the shelftool bar and select the 
'Nodegrapthdesk' entry under Shelves. Select the tab and right-click on 'Assign Context' tool, 
select 'Edit Tool'. Go to Hotkeys and set a hotkey for Network Pane.
6. While under a nodegraph, you can now use this hotkey to map it with its context to the current 
desktop. For more details, see docstring of assignContext().

Config File ('nodegraphdesk_config.json'):
init_desktops_startup: if true all desktops are initialized at startup, which causes the annoying 
quick popups. This cannot be avoid, but can at least be done once at startup.
subnetwork_mapping: if true subnets are also adopted for assigned desktops.
subnetwork_context_map: ...
nodegraphdesk_map: ...


Credits to ajz3d and TristanG, see: https://www.sidefx.com/forum/topic/97428/
------------------------------------------------------------------------------------------------ """
import hou, nodegraph, json
from canvaseventtypes import *
import nodegraphview as view

NODEGRAPHDESK: str = hou.getenv('NODEGRAPHDESK')
config_path: str = NODEGRAPHDESK + '/nodegraphdesk_config.json'

def getConfig() -> dict:
    """ ------------------------------------------------------------------------------------------------
    Returns the config dictionary from nodegraphdesk path.
    ------------------------------------------------------------------------------------------------ """
    with open(config_path, 'r') as file:
        return json.load(file)
    

def setConfig(config: dict) -> None:
    """ ------------------------------------------------------------------------------------------------
    Sets config dictionary.
    ------------------------------------------------------------------------------------------------ """
    with open(config_path, 'w') as file:
        json.dump(config, file, indent = 4)


def getDesktopDict() -> dict:
    """ ------------------------------------------------------------------------------------------------
    Returns a desktop dictionary.
    ------------------------------------------------------------------------------------------------ """
    return dict((d.name(), d) for d in hou.ui.desktops())


def selectDesktopDialog() -> str:
    """ ------------------------------------------------------------------------------------------------
    Returns the name of the selected desktop from the dialog - if canceled an empty string is returned.
    ------------------------------------------------------------------------------------------------ """
    desktops: tuple = tuple(desktop.name() for desktop in hou.ui.desktops())
    selected_desktop: tuple = hou.ui.selectFromList(desktops, default_choices=(0, ), exclusive=True,
                                                    message=None, title='Assign a desktop',
                                                    column_header="Desktops", clear_on_cancel=True)
    if selected_desktop: return desktops[selected_desktop[0]]
    return ''


def isVailedContext(nodegraphdesk_map: dict, context: str) -> str:
    """ ------------------------------------------------------------------------------------------------
    Verifies whether the given context is vailed, if so a empty string is returned, otherwise the name 
    of the desktop to which it is already mapped.
    ------------------------------------------------------------------------------------------------ """
    for desktop in nodegraphdesk_map.keys():
        if nodegraphdesk_map[desktop][1] == context:
            return desktop
    return ''


def assignContext() -> None:
    """ ------------------------------------------------------------------------------------------------
    Assigns a nodegraph context to the desktop and stores it in the config file. It also checks if an 
    assignment already exists, if so a dialog appears with the option to reassign or remove.
    ------------------------------------------------------------------------------------------------ """
    config = getConfig()
    nodegraphdesk_map: dict = config['nodegraphdesk_map']

    for pane_tab in hou.ui.paneTabs():
        if pane_tab.isCurrentTab() and pane_tab.type() == hou.paneTabType.NetworkEditor:
            if pane_tab.isUnderCursor():
                # pane_id: str = str(pane_tab.pane().id())
                pane_name: str = pane_tab.name()
                network_context: str = pane_tab.pwd().path().split('/')[1]
                current_desktop: str = hou.ui.curDesktop().name()
                is_vailed_context: str = isVailedContext(nodegraphdesk_map, network_context)
                def _setConfig():
                    config['nodegraphdesk_map'] = nodegraphdesk_map
                    setConfig(config)
                if is_vailed_context:
                    msg: str = f'Context {network_context} already assigned to the desktop {is_vailed_context}.'
                    state: int = hou.ui.displayMessage(msg, buttons=('Reassign', 'Remove', 'Cancel', ))
                    if state == 0: 
                        nodegraphdesk_map.pop(is_vailed_context)
                        nodegraphdesk_map[current_desktop] = (pane_name, network_context)
                        _setConfig()
                    elif state == 1:
                        nodegraphdesk_map.pop(is_vailed_context)
                        _setConfig()
                    else:
                        break
                else:
                    nodegraphdesk_map[current_desktop] = (pane_name, network_context)
                    _setConfig()
                break


def resetPath(pane_name: str, path: str) -> None:
    """ ------------------------------------------------------------------------------------------------
    Resets the nodegraph path based on the mapping from config file. This is necessary to update the 
    path after changing context, as the nodegraph path may no longer align with the mapping otherwise. 
    It is also maintain the subdirectories when switching from subnetworks.
    ------------------------------------------------------------------------------------------------ """
    for pane in hou.ui.paneTabs():
        if pane.name() == pane_name:
            pane.cd(path)


def nodegraphdesk(uievent) -> None:
    """ ------------------------------------------------------------------------------------------------
    Updates the desktop based on the assignment specified in the config file.
    ------------------------------------------------------------------------------------------------ """
    editor = uievent.editor
    current_desktop = hou.ui.curDesktop()

    config: dict = getConfig()
    nodegraphdesk_map: dict = config['nodegraphdesk_map']
    
    for desktop in nodegraphdesk_map.keys():
        if desktop == current_desktop.name() and nodegraphdesk_map[desktop][0] == editor.name():
            oldpath = uievent.oldcontext
            newpath = uievent.context
            if oldpath != newpath:
                new_context: list = newpath.split('/')
                if len(new_context) > 2 and config['subnetwork_mapping']:
                    for sub_context in config['subnetwork_context_map'].keys():
                        if config['subnetwork_context_map'][sub_context] in new_context[-1]:
                            new_context = sub_context
                else: 
                    new_context: str = new_context[1]
                for _desktop in nodegraphdesk_map.keys():
                    if new_context == nodegraphdesk_map[_desktop][1]:
                        desktops_dict = getDesktopDict()
                        desktops_dict[_desktop].setAsCurrent()
                        resetPath(nodegraphdesk_map[_desktop][0], newpath)
            break


handleEventCoroutine = nodegraph.handleEventCoroutine


def _handleEventCoroutine(): 
    """ ------------------------------------------------------------------------------------------------
    Extends Houdinis nodegraph event handling by wrapping the handleEventCoroutine generator from 
    $HFS/houdini/pythonX.Ylibs/nodegraph.py.
    ------------------------------------------------------------------------------------------------ """
    coroutine = handleEventCoroutine()
    next(coroutine)

    uievent = yield
    editor = uievent.editor
    keep_state = True

    while keep_state and editor.isUnderCursor():
        uievent = yield
        if isinstance(uievent, ContextEvent):
            # event_handler = None
            # keep_state = False
            nodegraphdesk(uievent)
        # elif isinstance(uievent, MouseEvent):
        #     ...
        
        try: coroutine.send(uievent)
        except StopIteration: break


nodegraph.handleEventCoroutine = _handleEventCoroutine