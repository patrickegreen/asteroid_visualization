import vtk
import vtk.util.numpy_support as VN
import numpy as np

filename = 'D:/Downloads/Asteroid Ensemble - Airburst/pv_insitu_300x300x300_09709-ts08.vti'
# Attribute on the dataset that is being rendered
attribute = 'v03'

# Use built-in VTK color names
colors = vtk.vtkNamedColors()

# Create the renderer, the render window, and the interactor.
#   The renderer draws into the render window
#   The interactor enables mouse- and keyboard-based interaction
renderer = vtk.vtkRenderer()
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(window)

# Set a background color for the renderer and set the size of the window
renderer.SetBackground(51/255, 77/255, 102/255)
window.SetSize(1000, 1000)

# Read Data
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName(filename)
reader.Update()

# Pull the data array we want to use
raw_data = reader.GetOutput().GetPointData()
raw_data.SetActiveAttribute(attribute, 0)

# Convert the data array to numpy array and get the min and maximum valule
data = VN.vtk_to_numpy(raw_data.GetScalars(attribute))
dataMin = np.amin(data)
dataMax = np.amax(data)
dataRange = dataMax - dataMin
print("Data array max: ", dataMax)
print("Data array min: ", dataMin)

# Define color map
# Now create a lookup table that consists of the full hue circle (from HSV)
hueLut = vtk.vtkLookupTable()
hueLut.SetTableRange(dataMin, dataMax)
# hueLut.SetHueRange(0, 1)  # comment these three line to default color map, rainbow
# hueLut.SetSaturationRange(1, 1)
# hueLut.SetValueRange(1, 1)
hueLut.Build()

# Actor - outline provides context around the data.
outlineData = vtk.vtkOutlineFilter()
outlineData.SetInputConnection(reader.GetOutputPort())
outlineData.Update()
mapOutline = vtk.vtkPolyDataMapper()
mapOutline.SetInputConnection(outlineData.GetOutputPort())
outline = vtk.vtkActor()
outline.SetMapper(mapOutline)
outline.GetProperty().SetColor(colors.GetColor3d("Black"))

# Actor - slice (xy plane)
xyColors = vtk.vtkImageMapToColors()
xyColors.SetInputConnection(reader.GetOutputPort())
xyColors.SetLookupTable(hueLut)
xyColors.Update()
xy = vtk.vtkImageActor()
xy.GetMapper().SetInputConnection(xyColors.GetOutputPort())
xy.SetDisplayExtent(0, 300, 0, 300, 150, 150)

# Actor - skin
# An isosurface, or contour value of 500 is known to correspond to the
# skin of the patient.
# The triangle stripper is used to create triangle strips from the
# isosurface these render much faster on many systems.
skinExtractor = vtk.vtkMarchingCubes()
skinExtractor.SetInputConnection(reader.GetOutputPort())
skinExtractor.SetValue(0, 500)
skinStripper = vtk.vtkStripper()
skinStripper.SetInputConnection(skinExtractor.GetOutputPort())
skinMapper = vtk.vtkPolyDataMapper()
skinMapper.SetInputConnection(skinStripper.GetOutputPort())
skinMapper.ScalarVisibilityOff()
skin = vtk.vtkActor()
skin.SetMapper(skinMapper)
skin.GetProperty().SetDiffuseColor(colors.GetColor3d("SkinColor"))
skin.GetProperty().SetSpecular(.3)
skin.GetProperty().SetSpecularPower(20)
skin.GetProperty().SetOpacity(.5)

# Actor - bone
# An isosurface, or contour value of 1150 is known to correspond to the
# bone of the patient.
# The triangle stripper is used to create triangle strips from the
# isosurface these render much faster on may systems.
boneExtractor = vtk.vtkMarchingCubes()
boneExtractor.SetInputConnection(reader.GetOutputPort())
boneExtractor.SetValue(0, 1150)
boneStripper = vtk.vtkStripper()
boneStripper.SetInputConnection(boneExtractor.GetOutputPort())
boneMapper = vtk.vtkPolyDataMapper()
boneMapper.SetInputConnection(boneStripper.GetOutputPort())
boneMapper.ScalarVisibilityOff()
bone = vtk.vtkActor()
bone.SetMapper(boneMapper)
bone.GetProperty().SetDiffuseColor(colors.GetColor3d("Ivory"))

# Camera
#   It is convenient to create an initial view of the data.
#   The FocalPoint and Position form a vector direction.
#   Later on (ResetCamera() method)
#   This vector is used to position the camera to look at the data in this direction.
camera = vtk.vtkCamera()
camera.SetViewUp(0, 0, -1)
camera.SetPosition(0, -1, 0)
camera.SetFocalPoint(0, 0, 0)
camera.ComputeViewPlaneNormal()
camera.Azimuth(30.0)
camera.Elevation(30.0)

# Add - actors are added to the renderer.
renderer.AddActor(outline)
renderer.AddActor(xy)
renderer.AddActor(skin)
renderer.AddActor(bone)

# An initial camera view is created.  The Dolly() method moves
# the camera towards the FocalPoint, thereby enlarging the image.
renderer.SetActiveCamera(camera)

# Calling Render() directly on a vtkRenderer is strictly forbidden.
# Only calling Render() on the vtkRenderWindow is a valid call.
window.Render()
renderer.ResetCamera()
camera.Dolly(1.5)

# Note that when camera movement occurs (as it does in the Dolly()
# method), the clipping planes often need adjusting. Clipping planes
# consist of two planes: near and far along the view direction. The
# near plane clips out objects in front of the plane; the far plane
# clips out objects behind the plane. This way only what is drawn
# between the planes is actually rendered.
renderer.ResetCameraClippingRange()

# Interact with the data.
window.Render()
iren.Initialize()
iren.Start()
