"""=========================
|-------Scene Browser-------|
|-----------v1.0------------|
=========================="""

"""
BSD 3-Clause License

Copyright (c) 2025, Agnibha Sen

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""


from pyfbsdk import *
from pyfbsdk_additions import *
import math

# UI Controls
lSearch = FBLabel()
eSearch = FBEdit()
bClearSearch = FBButton() 
lObjects = FBLabel()
listObjects = FBList()
bRefresh = FBButton()
cbAutoRefresh = FBButton()
cbCloseOnSelect = FBButton()

bPrevPage = FBButton()
bNextPage = FBButton()
lPageInfo = FBLabel()

lTypeFilter = FBLabel()
listTypeFilter = FBList()

# Data storage
all_objects = []
filtered_objects = []
auto_refresh_enabled = True
close_on_select_enabled = True 
last_object_count = 0

# Pagination Data
PAGE_SIZE = 50 # Number of objects to display per page
current_page = 1
total_pages = 1

# Type Filter Data
unique_object_types = []
selected_object_type = "All Types" # Default to showing all types

# Global tool reference
tool = None

## Helper Functions
def populate_objects():
    """
    Populate the list with all components in the scene and update unique types.
    """
    global all_objects, last_object_count, current_page, total_pages, unique_object_types, selected_object_type
    
    all_objects = []
    unique_object_types_set = set() # Use a set to collect unique types efficiently
    
    scene = FBSystem().Scene
    for component in scene.Components:
        # Only consider these specific types for the browser and filtering
        if isinstance(component, (FBCamera, FBLight, FBModel, FBCharacter, 
                                 FBConstraint, FBDevice, FBActorFace)):
            all_objects.append(component)
            unique_object_types_set.add(component.ClassName())
    
    if not all_objects:
        # Fallback for root models if the primary filter missed common types
        for model in scene.RootModel.Children:
            all_objects.append(model)
            unique_object_types_set.add(model.ClassName())
            
    all_objects.sort(key=lambda x: x.Name.lower())
    last_object_count = len(all_objects)
    
    # Populate the type filter dropdown
    listTypeFilter.Items.removeAll()
    unique_object_types = ["All Types"] + sorted(list(unique_object_types_set))
    for obj_type in unique_object_types:
        listTypeFilter.Items.append(obj_type)
        
    # Ensure the previously selected type is still valid, otherwise reset
    if selected_object_type in unique_object_types:
        listTypeFilter.ItemIndex = unique_object_types.index(selected_object_type)
    else:
        listTypeFilter.ItemIndex = 0 # Default to "All Types"
        selected_object_type = "All Types" # Update global variable

    # Recalculate total pages and reset current page on full re-population
    total_pages = math.ceil(len(all_objects) / PAGE_SIZE) if all_objects else 1
    current_page = 1 # Always go to the first page when objects are repopulated
    
    current_search = eSearch.Text if eSearch else ""
    update_filtered_list(current_search)
    
    print(f"Found {len(all_objects)} objects in scene. Total pages: {total_pages}")

def update_filtered_list(search_text):
    """Update the list based on search criteria and type filter, applying pagination."""
    global filtered_objects, total_pages, current_page
    
    previous_selection = ""
    if listObjects.ItemIndex >= 0 and listObjects.ItemIndex < len(filtered_objects):
        previous_selection = filtered_objects[listObjects.ItemIndex].Name
    
    listObjects.Items.removeAll()
    
    temp_filtered = [] # Temporarily hold all filtered objects
    search_lower = search_text.lower()
    
    for obj in all_objects:
        # Apply search text filter
        if search_lower in obj.Name.lower():
            # Apply type filter
            if selected_object_type == "All Types" or obj.ClassName() == selected_object_type:
                temp_filtered.append(obj)
            
    filtered_objects = temp_filtered # Update the global filtered_objects list
    
    # PAGINATION LOGIC: Determine which slice of filtered_objects to display
    total_items_filtered = len(filtered_objects)
    total_pages = math.ceil(total_items_filtered / PAGE_SIZE) if total_items_filtered else 1

    # Ensure current_page is valid after filtering or search changes
    if current_page > total_pages:
        current_page = total_pages
    if current_page < 1:
        current_page = 1

    start_index = (current_page - 1) * PAGE_SIZE
    end_index = min(start_index + PAGE_SIZE, total_items_filtered)
    
    # Populate listObjects with only the current page's items
    for i in range(start_index, end_index):
        obj = filtered_objects[i]
        display_name = f"{obj.Name} ({obj.ClassName()})"
        listObjects.Items.append(display_name)
    
    # Update page info label and button states
    lPageInfo.Caption = f"Page {current_page} / {total_pages}"
    bPrevPage.Enabled = (current_page > 1)
    bNextPage.Enabled = (current_page < total_pages)
    
    if previous_selection:
        for i, obj in enumerate(filtered_objects[start_index:end_index]):
            if obj.Name == previous_selection:
                listObjects.ItemIndex = i
                break

def check_for_new_objects():
    """Check if new objects have been added to the scene"""
    global last_object_count
    
    if not auto_refresh_enabled:
        return
    
    current_count = len([c for c in FBSystem().Scene.Components 
                         if isinstance(c, (FBCamera, FBLight, FBModel, FBCharacter, 
                                          FBConstraint, FBDevice, FBActorFace))])
    
    if current_count != last_object_count:
        print("Scene change detected - refreshing object list")
        populate_objects()

## Event Handlers
def on_search_changed(control, event):
    """Handle search text changes and reset to first page."""
    global current_page
    current_page = 1 # Reset to first page on new search
    search_text = eSearch.Text
    update_filtered_list(search_text)

def on_clear_search_clicked(control, event):
    """Handle Clear Search button click"""
    global current_page
    eSearch.Text = "" # Clear the text in the edit box
    current_page = 1 # Reset to first page when search is cleared
    update_filtered_list("") # Update the list to show all objects
    print("Search cleared.")

def on_list_selection_changed(control, event):
    """Handle list selection changes - select object in scene and optionally close"""
    if listObjects.ItemIndex >= 0:
        
        absolute_index = (current_page - 1) * PAGE_SIZE + listObjects.ItemIndex
        
        if absolute_index < len(filtered_objects):
            selected_obj = filtered_objects[absolute_index]
            
            for component in FBSystem().Scene.Components:
                component.Selected = False
            
            selected_obj.Selected = True
            
            print(f"Selected object: {selected_obj.Name}")

            if close_on_select_enabled:
                CloseTool(tool)

def on_refresh_clicked(control, event):
    """Handle manual refresh button click"""
    print("Manual refresh requested")
    populate_objects()

def on_auto_refresh_toggled(control, event):
    """Handle auto-refresh toggle"""
    global auto_refresh_enabled
    auto_refresh_enabled = not auto_refresh_enabled
    
    if auto_refresh_enabled:
        cbAutoRefresh.Caption = "Auto-Refresh: ON"
        cbAutoRefresh.State = 1
        print("Auto-refresh enabled")
    else:
        cbAutoRefresh.Caption = "Auto-Refresh: OFF"
        cbAutoRefresh.State = 0
        print("Auto-refresh disabled")

def on_close_on_select_toggled(control, event):
    """Handle close-on-select toggle"""
    global close_on_select_enabled
    close_on_select_enabled = not close_on_select_enabled
    
    if close_on_select_enabled:
        cbCloseOnSelect.Caption = "Close on Select: ON" 
        cbCloseOnSelect.State = 1 
        print("Close on Select enabled")
    else:
        cbCloseOnSelect.Caption = "Close on Select: OFF"
        cbCloseOnSelect.State = 0
        print("Close on Select disabled")

def on_tool_idle(control, event):
    """Handle tool idle events for auto-refresh"""
    check_for_new_objects()

def on_prev_page_clicked(control, event):
    """Go to the previous page of objects."""
    global current_page
    if current_page > 1:
        current_page -= 1
        update_filtered_list(eSearch.Text)
        print(f"Moved to Page {current_page}")

def on_next_page_clicked(control, event):
    """Go to the next page of objects."""
    global current_page, total_pages
    if current_page < total_pages:
        current_page += 1
        update_filtered_list(eSearch.Text)
        print(f"Moved to Page {current_page}")

def on_type_filter_changed(control, event):
    """Handle type filter dropdown selection change."""
    global selected_object_type, current_page
    if listTypeFilter.ItemIndex >= 0:
        selected_object_type = listTypeFilter.Items[listTypeFilter.ItemIndex]
        current_page = 1 # Reset to first page on new type filter
        print(f"Filter by type: {selected_object_type}")
        update_filtered_list(eSearch.Text) # Re-filter and refresh display

## UI Population and Tool Creation
def PopulateTool(t):
    """Populate the tool with UI regions and controls"""
    # Search label
    x = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(100, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    t.AddRegion("lSearch", "lSearch", x, y, w, h)
    t.SetControl("lSearch", lSearch)
    lSearch.Visible = True
    lSearch.ReadOnly = False
    lSearch.Enabled = True
    lSearch.Caption = "Search:"
    lSearch.Style = FBTextStyle.kFBTextStyleNone
    lSearch.Justify = FBTextJustify.kFBTextJustifyLeft
    lSearch.WordWrap = True
    
    # Search edit field
    x = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(45, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(220, FBAttachType.kFBAttachNone, "") 
    h = FBAddRegionParam(25, FBAttachType.kFBAttachNone, "")
    t.AddRegion("eSearch", "eSearch", x, y, w, h)
    t.SetControl("eSearch", eSearch)
    eSearch.Visible = True
    eSearch.ReadOnly = False
    eSearch.Enabled = True
    eSearch.Text = ""
    eSearch.PasswordMode = False
    eSearch.OnChange.Add(on_search_changed)
    
    # Clear Search button (X button)
    x = FBAddRegionParam(250, FBAttachType.kFBAttachNone, "") 
    y = FBAddRegionParam(45, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(25, FBAttachType.kFBAttachNone, "") 
    h = FBAddRegionParam(25, FBAttachType.kFBAttachNone, "")
    t.AddRegion("bClearSearch", "bClearSearch", x, y, w, h)
    t.SetControl("bClearSearch", bClearSearch)
    bClearSearch.Visible = True
    bClearSearch.ReadOnly = False
    bClearSearch.Enabled = True
    bClearSearch.Caption = "x" 
    bClearSearch.State = 0
    bClearSearch.Style = FBButtonStyle.kFBPushButton
    bClearSearch.Justify = FBTextJustify.kFBTextJustifyCenter
    bClearSearch.Look = FBButtonLook.kFBLookNormal
    bClearSearch.OnClick.Add(on_clear_search_clicked) 

    # Manual refresh button
    x = FBAddRegionParam(285, FBAttachType.kFBAttachNone, "") 
    y = FBAddRegionParam(45, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(80, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(25, FBAttachType.kFBAttachNone, "")
    t.AddRegion("bRefresh", "bRefresh", x, y, w, h)
    t.SetControl("bRefresh", bRefresh)
    bRefresh.Visible = True
    bRefresh.ReadOnly = False
    bRefresh.Enabled = True
    bRefresh.Caption = "Refresh"
    bRefresh.State = 0
    bRefresh.Style = FBButtonStyle.kFBPushButton
    bRefresh.Justify = FBTextJustify.kFBTextJustifyCenter
    bRefresh.Look = FBButtonLook.kFBLookNormal
    bRefresh.OnClick.Add(on_refresh_clicked)

    # Type Filter Label
    x = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(80, FBAttachType.kFBAttachNone, "") 
    w = FBAddRegionParam(100, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    t.AddRegion("lTypeFilter", "lTypeFilter", x, y, w, h)
    t.SetControl("lTypeFilter", lTypeFilter)
    lTypeFilter.Caption = "Filter by Type:"

    # Type Filter Dropdown
    x = FBAddRegionParam(125, FBAttachType.kFBAttachNone, "") 
    y = FBAddRegionParam(80, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(255, FBAttachType.kFBAttachNone, "") 
    h = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    t.AddRegion("listTypeFilter", "listTypeFilter", x, y, w, h)
    t.SetControl("listTypeFilter", listTypeFilter)
    listTypeFilter.Style = FBListStyle.kFBDropDownList 
    listTypeFilter.OnChange.Add(on_type_filter_changed) 

    # Objects list label
    x = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(110, FBAttachType.kFBAttachNone, "") 
    w = FBAddRegionParam(150, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    t.AddRegion("lObjects", "lObjects", x, y, w, h)
    t.SetControl("lObjects", lObjects)
    lObjects.Visible = True
    lObjects.ReadOnly = False
    lObjects.Enabled = True
    lObjects.Caption = "Components in Scene:"
    lObjects.Style = FBTextStyle.kFBTextStyleNone
    lObjects.Justify = FBTextJustify.kFBTextJustifyLeft
    lObjects.WordWrap = True
    
    # Objects list
    x = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(135, FBAttachType.kFBAttachNone, "") 
    w = FBAddRegionParam(360, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(230, FBAttachType.kFBAttachNone, "") 
    t.AddRegion("listObjects", "listObjects", x, y, w, h)
    t.SetControl("listObjects", listObjects)
    listObjects.Visible = True
    listObjects.ReadOnly = False
    listObjects.Enabled = True
    listObjects.Style = FBListStyle.kFBVerticalList
    listObjects.MultiSelect = False
    listObjects.OnChange.Add(on_list_selection_changed)
    
    # Pagination Controls Positioning
    y_pagination_base = 375

    # Previous Page Button
    x = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(y_pagination_base, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(60, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    t.AddRegion("bPrevPage", "bPrevPage", x, y, w, h)
    t.SetControl("bPrevPage", bPrevPage)
    bPrevPage.Caption = "< Prev"
    bPrevPage.OnClick.Add(on_prev_page_clicked)
    bPrevPage.Enabled = False 

    # Page Info Label
    x = FBAddRegionParam(85, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(y_pagination_base, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(120, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    t.AddRegion("lPageInfo", "lPageInfo", x, y, w, h)
    t.SetControl("lPageInfo", lPageInfo)
    lPageInfo.Caption = "Page 1 / 1"
    lPageInfo.Justify = FBTextJustify.kFBTextJustifyCenter

    # Next Page Button
    x = FBAddRegionParam(210, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(y_pagination_base, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(60, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    t.AddRegion("bNextPage", "bNextPage", x, y, w, h)
    t.SetControl("bNextPage", bNextPage)
    bNextPage.Caption = "Next >"
    bNextPage.OnClick.Add(on_next_page_clicked)
    bNextPage.Enabled = False 

    # Auto-refresh toggle button
    y_toggle_base = y_pagination_base + 30 

    x = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(y_toggle_base, FBAttachType.kFBAttachNone, "") 
    w = FBAddRegionParam(120, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(25, FBAttachType.kFBAttachNone, "")
    t.AddRegion("cbAutoRefresh", "cbAutoRefresh", x, y, w, h)
    t.SetControl("cbAutoRefresh", cbAutoRefresh)
    cbAutoRefresh.Visible = True
    cbAutoRefresh.ReadOnly = False
    cbAutoRefresh.Enabled = True
    cbAutoRefresh.Caption = "Auto-Refresh: ON"
    cbAutoRefresh.State = 1
    cbAutoRefresh.Style = FBButtonStyle.kFBCheckbox
    cbAutoRefresh.Justify = FBTextJustify.kFBTextJustifyLeft
    cbAutoRefresh.Look = FBButtonLook.kFBLookNormal
    cbAutoRefresh.OnClick.Add(on_auto_refresh_toggled)

    # Close on Select toggle button
    x = FBAddRegionParam(160, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(y_toggle_base, FBAttachType.kFBAttachNone, "") 
    w = FBAddRegionParam(150, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(25, FBAttachType.kFBAttachNone, "")
    t.AddRegion("cbCloseOnSelect", "cbCloseOnSelect", x, y, w, h)
    t.SetControl("cbCloseOnSelect", cbCloseOnSelect)
    cbCloseOnSelect.Visible = True
    cbCloseOnSelect.ReadOnly = False
    cbCloseOnSelect.Enabled = True
    cbCloseOnSelect.Caption = "Close on Select: ON" 
    cbCloseOnSelect.State = 1 
    cbCloseOnSelect.Style = FBButtonStyle.kFBCheckbox
    cbCloseOnSelect.Justify = FBTextJustify.kFBTextJustifyLeft
    cbCloseOnSelect.Look = FBButtonLook.kFBLookNormal
    cbCloseOnSelect.OnClick.Add(on_close_on_select_toggled)
    
    # Adding the idle event handler for auto-refresh
    t.OnIdle.Add(on_tool_idle)

def CreateTool():
    """Create and show the scene browser tool"""
    global tool
    tool = FBCreateUniqueTool("Scene Browser v1.0") # Current version
    tool.StartSizeX = 400
    tool.StartSizeY = 490 
    
    PopulateTool(tool)
    populate_objects() 
    ShowTool(tool)

# Creating the tool
CreateTool()