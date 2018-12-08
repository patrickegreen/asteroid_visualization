import vtk
import numpy as np
import vtk.util.numpy_support as VN
from vtk.util.misc import vtkGetDataRoot
from urllib.request import urlopen
from vtk import vtkCamera
import re
urlString = 'http://oceans11.lanl.gov/deepwaterimpact/yA31/300x300x300-FourScalars_resolution/'
urlpath = urlopen(urlString)
string = urlpath.read().decode('utf-8')

pattern = re.compile('[a-z0-9_]*.vti"')  # the pattern actually creates duplicates in the list

filelist = pattern.findall(string)
daryName = 'v02'  # 'v03' 'prs' 'tev'
fileCounter = 1
for filename in filelist:
    filename = filename[:-1]
    print(filename)
    remotefile = (urlString + filename)
    localfile = open('Output/TempFile', 'wb')
    localfile.write(remotefile.read())
    localfile.close()
    remotefile.close()
# This example shows how to run direct volume rendering, setting the transfer function and show the color bar

# the data used in this example can be download from
# http://oceans11.lanl.gov/deepwaterimpact/yA31/300x300x300-FourScalars_resolution/pv_insitu_300x300x300_49275.vti 

# setup the dataset filepath

# the name of data array which is used in this example

# for accessing build-in color access
    colors = vtk.vtkNamedColors()
    # camera =vtkCamera ();
    # camera.SetPosition(0, 2809364 / 2, 2408026);
    # camera.SetFocalPoint(0, 0, 0);
# Create the standard renderer, render window and interactor
    ren = vtk.vtkRenderer()
    # ren.SetActiveCamera(camera)
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    ren.SetBackground(51/255, 77/255, 102/255)
    renWin.SetSize(800, 600)
# Create the reader for the data
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName('Output/TempFile')
    reader.Update()

# specify the data array in the file to process
    reader.GetOutput().GetPointData().SetActiveAttribute(daryName, 0)

# convert the data array to numpy array and get the min and maximum valule
    dary = VN.vtk_to_numpy(reader.GetOutput().GetPointData().GetScalars(daryName))
    dMax = np.amax(dary)
    dMin = np.amin(dary)
    dRange = dMax - dMin

    opacityTransferFunction = vtk.vtkPiecewiseFunction()
    opacityTransferFunction.AddPoint(dMin, 0.0)
    opacityTransferFunction.AddPoint(dMin + dRange/2, 0.005)
    opacityTransferFunction.AddPoint(dMax, 0.01)

# Create transfer mapping scalar value to color
    colorTransferFunction = vtk.vtkColorTransferFunction()
    colorTransferFunction.AddRGBPoint(dMin, 0.0, 0.0, 0.2)
    colorTransferFunction.AddRGBPoint(dMin + (dRange/4)*1, 0.0, 0.0, 1.0)
    colorTransferFunction.AddRGBPoint(dMin + (dRange/4)*2, 0.0, 0.5, 0.0)
    colorTransferFunction.AddRGBPoint(dMin + (dRange/4)*3, 0.0, 1.0, 0.0)
    colorTransferFunction.AddRGBPoint(dMin + (dRange/4)*4, 0.0, 0.2, 0.0)

# The property describes how the data will look
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorTransferFunction)
    volumeProperty.SetScalarOpacity(opacityTransferFunction)
    volumeProperty.ShadeOn()  # on/off shader
    volumeProperty.SetInterpolationTypeToLinear()

# The mapper / ray cast function know how to render the data
    volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
    volumeMapper.SetBlendModeToComposite()
    volumeMapper.SetInputConnection(reader.GetOutputPort())

    lwf = vtk.vtkContourFilter()
    lwf.SetInputConnection(reader.GetOutputPort())
    lwf.SetValue(0, 0.1)

    lwfMapper = vtk.vtkPolyDataMapper()
    lwfMapper.SetInputConnection(lwf.GetOutputPort())
    lwfMapper.ScalarVisibilityOff()

    lwfActor = vtk.vtkActor()
    lwfActor.SetMapper(lwfMapper)
    lwfActor.GetProperty().SetColor(colors.GetColor3d("Banana"))
    lwfActor.GetProperty().SetSpecular(.3)
    lwfActor.GetProperty().SetSpecularPower(20)

# An isosurface of value 0.9 which is known to correspond to
# lower water fraction.
    hwf = vtk.vtkContourFilter()
    hwf.SetInputConnection(reader.GetOutputPort())
    hwf.SetValue(0, 0.9)

    hwfMapper = vtk.vtkPolyDataMapper()
    hwfMapper.SetInputConnection(hwf.GetOutputPort())
    hwfMapper.ScalarVisibilityOff()

    hwfActor = vtk.vtkActor()
    hwfActor.SetMapper(hwfMapper)
    hwfActor.GetProperty().SetColor(colors.GetColor3d("Ivory"))
    hwfActor.GetProperty().SetSpecular(.3)
    hwfActor.GetProperty().SetSpecularPower(20)

    colorTransferFunction = vtk.vtkColorTransferFunction()
    colorTransferFunction.AddRGBPoint(dMin, 1.0, 1.0, 1.0)
    colorTransferFunction.AddRGBPoint(dMax, 0.0, 0.0, 1.0)

    scalarBar = vtk.vtkScalarBarActor()
    scalarBar.SetLookupTable(colorTransferFunction)
    scalarBar.SetTitle("Value " + daryName + " Time " + str(filename[22:-4]))
    scalarBar.SetOrientationToHorizontal()
    scalarBar.GetLabelTextProperty().SetColor(0, 1, 1)
    scalarBar.GetTitleTextProperty().SetColor(0, 0, 1)

# An outline provides context around the data.
    outlineData = vtk.vtkOutlineFilter()
    outlineData.SetInputConnection(reader.GetOutputPort())
    outlineData.Update()

    mapOutline = vtk.vtkPolyDataMapper()
    mapOutline.SetInputConnection(outlineData.GetOutputPort())

    outline = vtk.vtkActor()
    outline.SetMapper(mapOutline)
    outline.GetProperty().SetColor(colors.GetColor3d("Black"))

    coord = scalarBar.GetPositionCoordinate()
    coord.SetCoordinateSystemToNormalizedViewport()
    coord.SetValue(0.1, 0.05)
    scalarBar.SetWidth(.8)
    scalarBar.SetHeight(.15)

# setup three color maps

# Finally, create a lookup table with a single hue but having a range
# in the saturation of the hue.
    satLut = vtk.vtkLookupTable()
    satLut.SetTableRange(dMin, dMax)
    satLut.SetHueRange(.6, .6)
    satLut.SetSaturationRange(0, 1)
    satLut.SetValueRange(1, 1)
    satLut.Build()  # effective built

# create three plane (slices)

    xyColors = vtk.vtkImageMapToColors()
    xyColors.SetInputConnection(reader.GetOutputPort())
    xyColors.SetLookupTable(satLut)
    xyColors.Update()

    xy = vtk.vtkImageActor()
    xy.GetMapper().SetInputConnection(xyColors.GetOutputPort())
    xy.SetDisplayExtent(0, 300, 0, 300, 150, 150)

# It is convenient to create an initial view of the data. The
# FocalPoint and Position form a vector direction. Later on
# (ResetCamera() method) this vector is used to position the camera
# to look at the data in this direction.
    aCamera = vtk.vtkCamera()
    aCamera.SetViewUp(0, 1, 0)
    aCamera.SetPosition(0, 0, -1)
    aCamera.SetFocalPoint(0, 0, 0)
    aCamera.ComputeViewPlaneNormal()
    aCamera.Azimuth(30.0)
    aCamera.Elevation(30.0)

# Actors are added to the renderer.
    ren.AddActor(lwfActor)
    ren.AddActor(hwfActor)
    ren.AddActor(scalarBar)
    ren.AddActor(outline)
    ren.AddActor(xy)

# Set the two isosurfaces to semi-transparent.
    lwfActor.GetProperty().SetOpacity(0.2)
    hwfActor.GetProperty().SetOpacity(0.8)

# An initial camera view is created.  The Dolly() method moves
# the camera towards the FocalPoint, thereby enlarging the image.
    ren.SetActiveCamera(aCamera)

# Calling Render() directly on a vtkRenderer is strictly forbidden.
# Only calling Render() on the vtkRenderWindow is a valid call.
    renWin.Render()

    ren.ResetCamera()
    aCamera.Dolly(1.5)
    w2image = vtk.vtkWindowToImageFilter()
    w2image.SetInput(renWin)

    writer = vtk.vtkPNGWriter()
    writer.SetInputConnection(w2image.GetOutputPort())
    writer.SetFileName('Output/outputSlice' + str(fileCounter) + '.png')
    writer.Write()

    ren.RemoveActor(xy)
    lwfActor.GetProperty().SetOpacity(0.5)
    hwfActor.GetProperty().SetOpacity(1.0)
    renWin.Render()
    ren.ResetCamera()
    aCamera.Dolly(1.5)

    w2image = vtk.vtkWindowToImageFilter()
    w2image.SetInput(renWin)

    writer = vtk.vtkPNGWriter()
    writer.SetInputConnection(w2image.GetOutputPort())
    writer.SetFileName('Output/outputISOSurface' + str(fileCounter) + '.png')
    writer.Write()

    ren.RemoveActor(xy)
    ren.RemoveActor(lwfActor)
    ren.RemoveActor(hwfActor)

    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    ren.AddVolume(volume)
    renWin.Render()
    ren.ResetCamera()
    aCamera.Dolly(1.5)

    w2image = vtk.vtkWindowToImageFilter()
    w2image.SetInput(renWin)

    writer = vtk.vtkPNGWriter()
    writer.SetInputConnection(w2image.GetOutputPort())
    writer.SetFileName('Output/outputVolume' + str(fileCounter) + '.png')
    writer.Write()

    fileCounter = fileCounter + 1

iren.Initialize()
renWin.Render()
iren.Start()
