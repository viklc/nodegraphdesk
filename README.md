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
- To assign a node editor context to a desktop, press `M` while under nodegraph.
- To remove the assignment, simply press `M` again.
- You can change the hotkey by editing the `"assign_hotkey"` property in the
`$NODEGRAPHDESK/nodegraphdesk_config.json` file. For example, you can set it to `"Ctrl+Shift+M"`.
- Alternatively you can use the `Assign Context` shelf tool, but you’ll need to set a hotkey for it 
first. Click the plus button on the right side of the shelf tool bar and select `Nodegrapthdesk` 
under Shelves. Then find the `Assign Context` tool, right-click on it, and choose 'Edit Tool'. 
Navigate to Hotkeys and set a hotkey for the Network Pane. This will allow you to use it within the 
nodegraph as well.
- When switching desktop for an another assignment, ensure that the nodegraph context you want to bind 
is not already assigned. If it is, you will be forced to reassign or remove the existing assignment.

## Config File ('nodegraphdesk_config.json'):
init_desktops_startup: if true all desktops are initialized at startup, which causes the annoying 
quick popups. This cannot be avoid, but can at least be done once at startup.
subnetwork_mapping: if true subnets are also adopted for assigned desktops.
subnetwork_context_map: ...
nodegraphdesk_map: ...


Credits to ajz3d and TristanG, see: https://www.sidefx.com/forum/topic/97428/
