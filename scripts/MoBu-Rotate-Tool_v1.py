"""
MotionBuilder Rotation Tool
A tool for rotating selected objects by specified X, Y, Z values
"""

from pyfbsdk import *
from pyfbsdk_additions import *

# Global tool reference
tool = None

# UI Controls
lXRotation = FBLabel()
eXRotation = FBEdit()
lYRotation = FBLabel()
eYRotation = FBEdit()
lZRotation = FBLabel()
eZRotation = FBEdit()
bApplyRotation = FBButton()
bResetValues = FBButton()
lSelectedObject = FBLabel()

def get_selected_objects():
    """Get currently selected objects in the scene"""
    selected_objects = []
    for obj in FBSystem().Scene.Components:
        if obj.Selected and hasattr(obj, 'Rotation'):
            selected_objects.append(obj)
    return selected_objects

def update_selected_object_label():
    """Update the label showing currently selected object(s)"""
    selected_objects = get_selected_objects()
    if not selected_objects:
        lSelectedObject.Caption = "Selected: None"
    elif len(selected_objects) == 1:
        lSelectedObject.Caption = "Selected: " + selected_objects[0].Name
    else:
        lSelectedObject.Caption = "Selected: " + str(len(selected_objects)) + " objects"

def on_apply_rotation_clicked(control, event):
    """Apply rotation to selected objects"""
    selected_objects = get_selected_objects()
    
    if not selected_objects:
        FBMessageBox("Rotation Tool", "No objects selected. Please select an object first.", "OK")
        return
    
    try:
        # Get rotation values from edit fields
        x_rot = float(eXRotation.Text) if eXRotation.Text else 0.0
        y_rot = float(eYRotation.Text) if eYRotation.Text else 0.0
        z_rot = float(eZRotation.Text) if eZRotation.Text else 0.0
        
        # Apply rotation to each selected object
        for obj in selected_objects:
            # Check if object has rotation properties
            if hasattr(obj, 'Rotation'):
                # Get current rotation
                current_rotation = obj.Rotation
                
                # Add the new rotation values
                new_x = current_rotation[0] + x_rot
                new_y = current_rotation[1] + y_rot
                new_z = current_rotation[2] + z_rot
                
                # Apply new rotation
                obj.Rotation = FBVector3d(new_x, new_y, new_z)
        
        # Refresh the scene
        FBSystem().Scene.Evaluate()
        
        # Show success message
        object_text = "object" if len(selected_objects) == 1 else "objects"
        FBMessageBox("Rotation Tool", 
                    f"Successfully rotated {len(selected_objects)} {object_text} by X:{x_rot}°, Y:{y_rot}°, Z:{z_rot}°", 
                    "OK")
        
    except ValueError:
        FBMessageBox("Rotation Tool", "Please enter valid numeric values for X, Y, and Z rotation.", "OK")
    except Exception as e:
        FBMessageBox("Rotation Tool", f"Error applying rotation: {str(e)}", "OK")

def on_reset_values_clicked(control, event):
    """Reset all rotation input fields to zero"""
    eXRotation.Text = "0.0"
    eYRotation.Text = "0.0"
    eZRotation.Text = "0.0"

def on_tool_idle(control, event):
    """Called when tool is idle - update selected object label"""
    update_selected_object_label()

def PopulateTool(t):
    """Populate the tool with UI regions and controls"""
    
    # Selected object label
    x = FBAddRegionParam(10, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(10, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(220, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    t.AddRegion("lSelectedObject", "lSelectedObject", x, y, w, h)
    t.SetControl("lSelectedObject", lSelectedObject)
    lSelectedObject.Visible = True
    lSelectedObject.Caption = "Selected: None"
    lSelectedObject.Style = FBTextStyle.kFBTextStyleBold
    lSelectedObject.Justify = FBTextJustify.kFBTextJustifyLeft

    # X Rotation Label
    x = FBAddRegionParam(10, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(40, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(80, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    t.AddRegion("lXRotation", "lXRotation", x, y, w, h)
    t.SetControl("lXRotation", lXRotation)
    lXRotation.Visible = True
    lXRotation.Caption = "X Rotation (°):"
    lXRotation.Style = FBTextStyle.kFBTextStyleNone
    lXRotation.Justify = FBTextJustify.kFBTextJustifyLeft

    # X Rotation Edit Field
    x = FBAddRegionParam(95, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(40, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(80, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(25, FBAttachType.kFBAttachNone, "")
    t.AddRegion("eXRotation", "eXRotation", x, y, w, h)
    t.SetControl("eXRotation", eXRotation)
    eXRotation.Visible = True
    eXRotation.Text = "0.0"
    eXRotation.PasswordMode = False

    # Y Rotation Label
    x = FBAddRegionParam(10, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(70, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(80, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    t.AddRegion("lYRotation", "lYRotation", x, y, w, h)
    t.SetControl("lYRotation", lYRotation)
    lYRotation.Visible = True
    lYRotation.Caption = "Y Rotation (°):"
    lYRotation.Style = FBTextStyle.kFBTextStyleNone
    lYRotation.Justify = FBTextJustify.kFBTextJustifyLeft

    # Y Rotation Edit Field
    x = FBAddRegionParam(95, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(70, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(80, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(25, FBAttachType.kFBAttachNone, "")
    t.AddRegion("eYRotation", "eYRotation", x, y, w, h)
    t.SetControl("eYRotation", eYRotation)
    eYRotation.Visible = True
    eYRotation.Text = "0.0"
    eYRotation.PasswordMode = False

    # Z Rotation Label
    x = FBAddRegionParam(10, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(100, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(80, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(20, FBAttachType.kFBAttachNone, "")
    t.AddRegion("lZRotation", "lZRotation", x, y, w, h)
    t.SetControl("lZRotation", lZRotation)
    lZRotation.Visible = True
    lZRotation.Caption = "Z Rotation (°):"
    lZRotation.Style = FBTextStyle.kFBTextStyleNone
    lZRotation.Justify = FBTextJustify.kFBTextJustifyLeft

    # Z Rotation Edit Field
    x = FBAddRegionParam(95, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(100, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(80, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(25, FBAttachType.kFBAttachNone, "")
    t.AddRegion("eZRotation", "eZRotation", x, y, w, h)
    t.SetControl("eZRotation", eZRotation)
    eZRotation.Visible = True
    eZRotation.Text = "0.0"
    eZRotation.PasswordMode = False

    # Apply Rotation Button
    x = FBAddRegionParam(10, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(135, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(85, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(30, FBAttachType.kFBAttachNone, "")
    t.AddRegion("bApplyRotation", "bApplyRotation", x, y, w, h)
    t.SetControl("bApplyRotation", bApplyRotation)
    bApplyRotation.Visible = True
    bApplyRotation.Caption = "Apply Rotation"
    bApplyRotation.Style = FBButtonStyle.kFBPushButton
    bApplyRotation.Justify = FBTextJustify.kFBTextJustifyCenter
    bApplyRotation.Look = FBButtonLook.kFBLookNormal
    bApplyRotation.OnClick.Add(on_apply_rotation_clicked)

    # Reset Values Button
    x = FBAddRegionParam(100, FBAttachType.kFBAttachNone, "")
    y = FBAddRegionParam(135, FBAttachType.kFBAttachNone, "")
    w = FBAddRegionParam(75, FBAttachType.kFBAttachNone, "")
    h = FBAddRegionParam(30, FBAttachType.kFBAttachNone, "")
    t.AddRegion("bResetValues", "bResetValues", x, y, w, h)
    t.SetControl("bResetValues", bResetValues)
    bResetValues.Visible = True
    bResetValues.Caption = "Reset Values"
    bResetValues.Style = FBButtonStyle.kFBPushButton
    bResetValues.Justify = FBTextJustify.kFBTextJustifyCenter
    bResetValues.Look = FBButtonLook.kFBLookNormal
    bResetValues.OnClick.Add(on_reset_values_clicked)

    # Add idle event handler to update selected object display
    t.OnIdle.Add(on_tool_idle)

def CreateTool():
    """Create and show the rotation tool"""
    global tool
    tool = FBCreateUniqueTool("Object Rotation Tool v1.0")
    tool.StartSizeX = 190
    tool.StartSizeY = 180
    tool.MaxSizeX = 190
    tool.MaxSizeY = 180
    tool.MinSizeX = 190
    tool.MinSizeY = 180
    
    PopulateTool(tool)
    ShowTool(tool)

# Create the tool
CreateTool()