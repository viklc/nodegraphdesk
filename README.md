# Nodegraphdesk
Nodegraphdesk is an extension for Houdini's node editor that allows to assign a particular desktop 
to a nodegraph context. It automatically switches between desktops when the user changes the path 
or dives into contexts such as DOPs or LOPs.

To prevent misleading behavior, Nodegraphdesk uses a restrictive assignment approach that allows 
each desktop to be assigned to only one of its nodegraph panes with a given context.

## Install Package: 
1. Download the `nodegraphdesk` folder and place it in your desired location.
2. Inside the folder, you’ll find a JSON file named `nodegraphdesk.json`. Open this file and set
the property `"NODEGRAPHDESK"` to reflect the current directory where the file is located, then save
the changes.
4. Copy and paste the JSON file into the `$HOUDINI_USER_PREF_DIR/packages` directory. For example on
Windows: `C:\Users\<username>\Documents\houdini20.5\packages`
5. Restart Houdini.

## Usage
To assign a nodegraph context to the desktop, you must first set a shortkey for the 'Assign 
Context' shelf tool. Press the plus button on the right-hand side of the shelftool bar and select the 
'Nodegrapthdesk' entry under Shelves. Select the tab and right-click on 'Assign Context' tool, 
select 'Edit Tool'. Go to Hotkeys and set a hotkey for Network Pane.

While under a nodegraph, you can now use this hotkey to map it with its context to the current 
desktop. For more details, see docstring of assignContext().

## Config File ('nodegraphdesk_config.json'):
init_desktops_startup: if true all desktops are initialized at startup, which causes the annoying 
quick popups. This cannot be avoid, but can at least be done once at startup.
subnetwork_mapping: if true subnets are also adopted for assigned desktops.
subnetwork_context_map: ...
nodegraphdesk_map: ...


Credits to ajz3d and TristanG, see: https://www.sidefx.com/forum/topic/97428/
