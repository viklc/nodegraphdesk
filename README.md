# Nodegraphdesk
Nodegraphdesk is an extension for Houdini's node editor that allows to assign a particular desktop 
to a nodegraph context. It automatically switches between desktops when the user changes the path 
or dives into contexts such as DOPs or LOPs.
https://github.com/user-attachments/assets/b9927cae-d4a4-4811-9907-4959de5d8850

## Install
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
`$NODEGRAPHDESK/nodegraphdesk_config.json` file. Alternatively you can use the `Assign Context` shelf
tool, but you’ll need to set a hotkey for it first. You can find it under shelves `Nodegrapthdesk`.
- When switching desktop for an another assignment, ensure that the nodegraph context you want to bind 
is not already assigned. If it is, you will be forced to reassign or remove the existing assignment.
- To clear all assignments, you can press Ctrl+Shift+M. There is also a shelf tool for this.

## Config
You can find the configuration file under `$NODEGRAPHDESK/nodegraphdesk_config.json`.
- **init_desktops_startup:** If true all desktops are initialized at startup.
- **assign_hotkey:** Hotkey for the assignment.
- **clear_mapping_hotkey:** Hotkey to clear all assignments.
- **arbitrary_nodegraph_change:** Despite the restrictive assignment, this option allows changes
to be made from any node editor of an assigned desktop. It is not recommended though, as it could
become quite confusing.
- **alias_mapping:** Allows the use of aliases, meaning that objnet behaves in the same way when
assigning the root context obj, and the other way around. You can also remove or set custom aliases as
long as they are vailed node types.
- **alias_map:** Alias dictionary map.
- **nodegraphdesk_map:** The actual nodegraph context desktop map.
---
Credits to ajz3d and TristanG, see [Is it possible to auto change Desktops depending on context?](https://www.sidefx.com/forum/topic/97428/) 
