import vtk
import vtk.util.numpy_support as VN
import numpy as np
import os

# Use built-in VTK color names
#   see: https://en.wikipedia.org/wiki/Web_colors
colors = vtk.vtkNamedColors()

AIRBURST = (
    'pv_insitu_300x300x300_00000-ts00.vti',
    'pv_insitu_300x300x300_01141-ts01.vti',
    'pv_insitu_300x300x300_02286-ts02.vti',
    'pv_insitu_300x300x300_03429-ts03.vti',
    'pv_insitu_300x300x300_04617-ts04.vti',
    'pv_insitu_300x300x300_05789-ts05.vti',
    'pv_insitu_300x300x300_06813-ts06.vti',
    'pv_insitu_300x300x300_07678-ts07.vti',
    'pv_insitu_300x300x300_08415-ts08.vti',
    'pv_insitu_300x300x300_09113-ts09.vti',
    'pv_insitu_300x300x300_09709-ts10.vti',
    'pv_insitu_300x300x300_10207-ts11.vti',
    'pv_insitu_300x300x300_10642-ts12.vti',
    'pv_insitu_300x300x300_11032-ts13.vti',
    'pv_insitu_300x300x300_11370-ts14.vti',
    'pv_insitu_300x300x300_11662-ts15.vti',
    'pv_insitu_300x300x300_11910-ts16.vti',
    'pv_insitu_300x300x300_12143-ts17.vti',
    'pv_insitu_300x300x300_12364-ts18.vti',
    'pv_insitu_300x300x300_12578-ts19.vti',
    'pv_insitu_300x300x300_12806-ts20.vti',
)

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
        self.renderer.SetBackground(0.5, 0.5, 0.5)  # gray - RGB rescale of [0,255] to [0, 1]
        self.window.SetSize(800, 800)

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
        hue_lookup.SetHueRange(.6, .6)
        hue_lookup.SetSaturationRange(0, 1)
        hue_lookup.SetValueRange(1, 1)
        hue_lookup.Build()
        xy_colors = vtk.vtkImageMapToColors()
        xy_colors.SetInputConnection(self.reader.GetOutputPort())
        xy_colors.SetLookupTable(hue_lookup)
        xy_colors.Update()
        xy_slice = vtk.vtkImageActor()
        xy_slice.GetMapper().SetInputConnection(xy_colors.GetOutputPort())
        # Params (minX, maxX, minY, maxY, minZ, maxZ)
        xy_slice.SetDisplayExtent(0, 300, 0, 300, 150, 150)

        transfer_color = vtk.vtkColorTransferFunction()
        transfer_color.AddRGBPoint(min_value, 1.0, 1.0, 1.0)
        transfer_color.AddRGBPoint(max_value, 0.0, 0.0, 1.0)
        scalar_bar = vtk.vtkScalarBarActor()
        scalar_bar.SetLookupTable(transfer_color)
        scalar_bar.SetTitle("Temporary Title")
        scalar_bar.SetOrientationToHorizontal()
        scalar_bar.GetLabelTextProperty().SetColor(0, 1, 1)
        scalar_bar.GetTitleTextProperty().SetColor(0, 0, 1)
        # coord = scalar_bar.GetPositionCoordinate()
        # coord.SetCoordinateSystemToNormalizedViewport()
        # coord.SetValue(0.1, 0.05)

        self.renderer.AddActor(xy_slice)
        # self.renderer.AddActor(scalar_bar)
        return xy_slice, scalar_bar
    
    def _add_actor_isosurface(self, min_value, max_value):
        """
        Add an iso-surface based on volume thresholds
        """
        # 1. Create the low threshold
        low = vtk.vtkContourFilter()
        low.SetInputConnection(self.reader.GetOutputPort())
        low.SetValue(0, 0.1)
        low_mapper = vtk.vtkPolyDataMapper()
        low_mapper.SetInputConnection(low.GetOutputPort())
        low_mapper.ScalarVisibilityOff()
        low_actor = vtk.vtkActor()
        low_actor.SetMapper(low_mapper)
        low_actor.GetProperty().SetColor(colors.GetColor3d("Salmon"))
        low_actor.GetProperty().SetSpecular(.3)
        low_actor.GetProperty().SetSpecularPower(20)
        low_actor.GetProperty().SetOpacity(0.2)

        # 2. Create the high threshold
        high = vtk.vtkContourFilter()
        high.SetInputConnection(self.reader.GetOutputPort())
        high.SetValue(0, 0.8)
        high_mapper = vtk.vtkPolyDataMapper()
        high_mapper.SetInputConnection(high.GetOutputPort())
        high_mapper.ScalarVisibilityOff()
        high_actor = vtk.vtkActor()
        high_actor.SetMapper(high_mapper)
        high_actor.GetProperty().SetColor(colors.GetColor3d("Brown"))
        high_actor.GetProperty().SetSpecular(.3)
        high_actor.GetProperty().SetSpecularPower(20)
        high_actor.GetProperty().SetOpacity(0.8)

        # Define transfer function range
        transfer_color = vtk.vtkColorTransferFunction()
        transfer_color.AddRGBPoint(min_value, 1.0, 1.0, 1.0)
        transfer_color.AddRGBPoint(max_value, 0.0, 0.0, 1.0)

        title = vtk.vtkScalarBarActor()
        title.SetTitle("Scalar value (" + 'Test' + ")")
        title.SetOrientationToHorizontal()
        title.GetLabelTextProperty().SetColor(0, 1, 1)
        title.GetTitleTextProperty().SetColor(0, 0, 1)
        # position it in window
        coord = title.GetPositionCoordinate()
        coord.SetCoordinateSystemToNormalizedViewport()
        coord.SetValue(0.1, 0.05)
        title.SetWidth(.8)
        title.SetHeight(.15)

        self.renderer.AddActor(low_actor)
        self.renderer.AddActor(high_actor)
        self.renderer.AddActor(title)
        return low_actor, high_actor

    def _add_actor_volume_render(self, min_value, max_value):
        """
        Add a volume render.
        """
        data_range = max_value - min_value
        transfer_opacity = vtk.vtkPiecewiseFunction()
        transfer_opacity.AddPoint(min_value, 0.0)
        transfer_opacity.AddPoint(min_value + data_range / 2, 0.0000)
        transfer_opacity.AddPoint(max_value, 0.01)

        # Create transfer mapping scalar value to color
        transfer_color = vtk.vtkColorTransferFunction()
        transfer_color.AddRGBPoint(min_value, 0, 0, 0.2)
        transfer_color.AddRGBPoint(min_value + (data_range / 4) * 1, 0, 1.0, 0)
        transfer_color.AddRGBPoint(min_value + (data_range / 4) * 2, 0, 0.5, 0)
        transfer_color.AddRGBPoint(min_value + (data_range / 4) * 3, 1.0, 0, 0.0)
        transfer_color.AddRGBPoint(min_value + (data_range / 4) * 4, 0.2, 0, 0.0)

        # The property describes how the data will look
        volume_property = vtk.vtkVolumeProperty()
        volume_property.SetColor(transfer_color)
        volume_property.SetScalarOpacity(transfer_opacity)
        volume_property.ShadeOn()  # on/off shader
        volume_property.SetInterpolationTypeToLinear()

        # The mapper / ray cast function know how to render the data
        volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
        volume_mapper.SetBlendModeToComposite()
        volume_mapper.SetInputConnection(self.reader.GetOutputPort())

        volume = vtk.vtkVolume()
        volume.SetMapper(volume_mapper)
        volume.SetProperty(volume_property)
        self.renderer.AddVolume(volume)
        return volume

    def _initialize_camera(self, zpos, elevation):
        """
        Initialize the camera and view, as well as interaction.

        :return camera: (vtkOpenGLCamera)

        @use
            front
                zpos=0, elevation=-30.0
            front angle
                zpos=0.4, elevation=0
            side view
                zpos=1, elevation=0
        """
        # Camera
        #   It is convenient to create an initial view of the data.
        #   The FocalPoint and Position form a vector direction.
        #   Later on (ResetCamera() method)
        #   This vector is used to position the camera to look at the data in this direction.
        camera = vtk.vtkCamera()
        camera.SetViewUp(0, 0, 0)
        camera.SetPosition(0.5, 0.5, zpos)
        camera.SetFocalPoint(0, 0, 0)
        camera.ComputeViewPlaneNormal()
        camera.Azimuth(0)
        camera.Elevation(elevation)

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
        return camera

    def _initialize_interactor(self):
        self.interactor.Initialize()
        self.window.Render()
        self.interactor.Start()

    def _load_data(self, sourcefile, attribute):
        # Read Data
        self.reader.SetFileName(sourcefile)
        self.reader.Update()

        # Pull the data array we want to use (convert to numpy array)
        self.reader.GetOutput().GetPointData().SetActiveAttribute(attribute, 0)
        data = VN.vtk_to_numpy(self.reader.GetOutput().GetPointData().GetScalars(attribute))
        return data

    def _reset(self, camera, actors=()):
        for actor in actors:
            self.renderer.RemoveActor(actor)
        self.window.Render()
        self.renderer.ResetCamera()
        camera.Dolly(1.5)
        return camera

    def _save_image(self, outfile):
        image = vtk.vtkWindowToImageFilter()
        image.SetInput(self.window)
        writer = vtk.vtkPNGWriter()
        writer.SetInputConnection(image.GetOutputPort())
        writer.SetFileName(outfile)
        writer.Write()

    def render_iso(self, sourcefile, outfile, attribute, zpos=0, elevation=-30.0):
        data = self._load_data(sourcefile, attribute)
        min_value = np.amin(data)
        max_value = np.amax(data)
        self._add_actor_outline()
        iso_low, iso_high = self._add_actor_isosurface(min_value, max_value)
        camera = self._initialize_camera(zpos=zpos, elevation=elevation)
        self._save_image(outfile)
        self._reset(camera, [iso_low, iso_high])

    def render_sliced_iso(self, sourcefile, outfile, attribute, zpos=1, elevation=0.0):
        data = self._load_data(sourcefile, attribute)
        min_value = np.amin(data)
        max_value = np.amax(data)
        self._add_actor_outline()
        xy_slice, scalar_bar = self._add_actor_slice(min_value, max_value)
        iso_low, iso_high = self._add_actor_isosurface(min_value, max_value)
        camera = self._initialize_camera(zpos=zpos, elevation=elevation)
        self._save_image(outfile)
        self._reset(camera, [xy_slice, scalar_bar, iso_low, iso_high])

    def render_volume(self, sourcefile, outfile, attribute, zpos=0, elevation=-30.0):
        data = self._load_data(sourcefile, attribute)
        min_value = np.amin(data)
        max_value = np.amax(data)
        self._add_actor_outline()
        volume = self._add_actor_volume_render(min_value, max_value)
        camera = self._initialize_camera(zpos=zpos, elevation=elevation)
        # self._initialize_interactor()
        self._save_image(outfile)
        self._reset(camera, [volume])


# from src.airburst import run; run()
def run(sample=True, iso=False, sliced=False, volume=False):
    attribute = 'v03'
    ast = AsteroidVTK()
    root_folder = 'D:/Downloads/Asteroid Ensemble - Airburst/'

    if sample:
        image = AIRBURST[8]
        tag = image.split('.')[0].split('_')[-1]  # timestamp + step
        sourcefile = os.path.join(root_folder, image)
        outfilename = 'sample_{0}.png'.format(tag)
        outfile = os.path.join('{0}output/'.format(root_folder), outfilename)
        ast.render_volume(sourcefile, outfile, attribute)

    # ISO_RENDER
    if iso:
        total_images = len(AIRBURST)
        for i, image in enumerate(AIRBURST):
            print('Processing iso: {0} of {1}'.format(i, total_images))
            tag = image.split('.')[0].split('_')[-1]  # timestamp + step
            sourcefile = os.path.join(root_folder, image)
            outfilename = 'output_{0}.png'.format(tag)
            outfile = os.path.join('{0}output/iso/'.format(root_folder), outfilename)
            ast.render_iso(sourcefile, outfile, attribute)

    # SLICED ISO RENDER
    if sliced:
        total_images = len(AIRBURST)
        for i, image in enumerate(AIRBURST):
            print('Processing sliced iso: {0} of {1}'.format(i, total_images))
            tag = image.split('.')[0].split('_')[-1]  # timestamp + step
            sourcefile = os.path.join(root_folder, image)
            outfilename = 'output_{0}.png'.format(tag)
            outfile = os.path.join('{0}output/sliced/'.format(root_folder), outfilename)
            ast.render_sliced_iso(sourcefile, outfile, attribute)

    # VOLUME
    if volume:
        total_images = len(AIRBURST)
        for i, image in enumerate(AIRBURST):
            print('Processing volume render: {0} of {1}'.format(i, total_images))
            tag = image.split('.')[0].split('_')[-1]  # timestamp + step
            sourcefile = os.path.join(root_folder, image)
            outfilename = 'output_{0}.png'.format(tag)
            outfile = os.path.join('{0}output/volume/'.format(root_folder), outfilename)
            ast.render_volume(sourcefile, outfile, attribute)
