Nodegraphdesk is an extension for Houdini's node editor that allows to assign a particular desktop 
to a nodegraph context. It automatically switches between desktops when the user changes the path 
or dives into contexts such as DOPs or LOPs.

To prevent misleading behavior, Nodegraphdesk uses a restrictive assignment approach that allows 
each desktop to be assigned to only one of its nodegraph panes with a given context.

## Install: 
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

## Config File ('nodegraphdesk_config.json'):
init_desktops_startup: if true all desktops are initialized at startup, which causes the annoying 
quick popups. This cannot be avoid, but can at least be done once at startup.
subnetwork_mapping: if true subnets are also adopted for assigned desktops.
subnetwork_context_map: ...
nodegraphdesk_map: ...


Credits to ajz3d and TristanG, see: https://www.sidefx.com/forum/topic/97428/
