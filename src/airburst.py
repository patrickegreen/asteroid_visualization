import vtk
import vtk.util.numpy_support as VN
import numpy as np


# Use built-in VTK color names
colors = vtk.vtkNamedColors()


class AsteroidVTK(object):

    def __init__(self):
        # Create the renderer, the render window, and the interactor.
        #   The renderer draws into the render window
        #   The interactor enables mouse- and keyboard-based interaction
        self.renderer = vtk.vtkRenderer()
        self.window = vtk.vtkRenderWindow()
        self.window.AddRenderer(self.renderer)
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.window)

        # Set a background color for the renderer and set the size of the window
        self.renderer.SetBackground(51/255, 77/255, 102/255)
        self.window.SetSize(1000, 1000)

        self.reader = vtk.vtkXMLImageDataReader()

    def _add_actor_outline(self):
        """Add outline for context of data."""
        # Actor - outline provides context around the data.
        data = vtk.vtkOutlineFilter()
        data.SetInputConnection(self.reader.GetOutputPort())
        data.Update()
        map_outline = vtk.vtkPolyDataMapper()
        map_outline.SetInputConnection(data.GetOutputPort())
        outline = vtk.vtkActor()
        outline.SetMapper(map_outline)
        outline.GetProperty().SetColor(colors.GetColor3d("Black"))
        self.renderer.AddActor(outline)

    def _add_actor_slice(self, min_value, max_value):
        """
        Slice in the XY plane

        :param min_value: (int)
            minimum value in data array
        :param max_value: (int)
            maximum value in data array
        """
        # Define color map
        # Now create a lookup table that consists of the full hue circle (from HSV)
        hue_lookup = vtk.vtkLookupTable()
        hue_lookup.SetTableRange(min_value, max_value)
        # hueLut.SetHueRange(0, 1)  # comment these three line to default color map, rainbow
        # hueLut.SetSaturationRange(1, 1)
        # hueLut.SetValueRange(1, 1)
        hue_lookup.Build()
        xy_colors = vtk.vtkImageMapToColors()
        xy_colors.SetInputConnection(self.reader.GetOutputPort())
        xy_colors.SetLookupTable(hue_lookup)
        xy_colors.Update()
        xy = vtk.vtkImageActor()
        xy.GetMapper().SetInputConnection(xy_colors.GetOutputPort())
        # Params (minX, maxX, minY, maxY, minZ, maxZ)
        xy.SetDisplayExtent(0, 300, 0, 300, 150, 150)
        self.renderer.AddActor(xy)

    def _initialize_camera(self):
        """
        Initialize the camera and view, as well as interaction.

        :return camera: (vtk.
        """
        # Camera
        #   It is convenient to create an initial view of the data.
        #   The FocalPoint and Position form a vector direction.
        #   Later on (ResetCamera() method)
        #   This vector is used to position the camera to look at the data in this direction.
        camera = vtk.vtkCamera()
        print(type(camera))
        camera.SetViewUp(0, 0, -1)
        camera.SetPosition(0, -1, 0)
        camera.SetFocalPoint(0, 0, 0)
        camera.ComputeViewPlaneNormal()
        camera.Azimuth(30.0)
        camera.Elevation(30.0)

        # An initial camera view is created.  The Dolly() method moves
        # the camera towards the FocalPoint, thereby enlarging the image.
        self.renderer.SetActiveCamera(camera)

        # Calling Render() directly on a vtkRenderer is strictly forbidden.
        # Only calling Render() on the vtkRenderWindow is a valid call.
        self.window.Render()
        self.renderer.ResetCamera()
        camera.Dolly(1.5)

        # Note that when camera movement occurs (as it does in the Dolly()
        # method), the clipping planes often need adjusting. Clipping planes
        # consist of two planes: near and far along the view direction. The
        # near plane clips out objects in front of the plane; the far plane
        # clips out objects behind the plane. This way only what is drawn
        # between the planes is actually rendered.
        self.renderer.ResetCameraClippingRange()

        # Interact with the data.
        self.window.Render()
        self.interactor.Initialize()
        self.interactor.Start()
        return camera

    def _load_data(self, filename, attribute):
        # Read Data
        self.reader.SetFileName(filename)
        self.reader.Update()

        # Pull the data array we want to use (convert to numpy array)
        self.reader.GetOutput().GetPointData().SetActiveAttribute(attribute, 0)
        data = VN.vtk_to_numpy(self.reader.GetOutput().GetPointData().GetScalars(attribute))
        return data

    def render(self, filename, attribute):
        data = self._load_data(filename, attribute)
        min_value = np.amin(data)
        max_value = np.amax(data)
        data_range = max_value - min_value
        self._add_actor_outline()
        self._add_actor_slice(min_value, max_value)
        camera = self._initialize_camera()


# from src.airburst import run; run()
# from src.airburst import run; a, filename, attr = run()
def run(filename='D:/Downloads/Asteroid Ensemble - Airburst/pv_insitu_300x300x300_08415-ts08.vti', attribute='v03'):
    ast = AsteroidVTK()
    ast.render(filename, attribute)
    # return ast, filename, attribute
