import adsk.core
import adsk.fusion
import math

def run(context):
    app = adsk.core.Application.get()
    design = app.activeProduct
    root_comp = design.rootComponent
    
    # Create sketch on XY plane
    sketches = root_comp.sketches
    xy_plane = root_comp.xYConstructionPlane
    sketch = sketches.add(xy_plane)
    
    # Parameters (Fusion uses cm internally)
    x_shift = 0  # -40 mm converted to cm
    thickness = 1  # 5 mm converted to cm (radius for sweep)
    
    # Eigenvalues parameters
    real_part = 1
    imag_part = 0.6
    
    # Create points collection
    points = adsk.core.ObjectCollection.create()
    
    # Adjusted parameter range to prevent overflow
    t_start = 0
    t_end = 2*math.pi  # Reduced from 2π to control exponential growth
    num_points = 200
    
    # Generate points without numpy
    for i in range(num_points):
        t = t_start + (t_end - t_start) * (i / (num_points - 1))
        scale_factor = math.exp(real_part * t)
        x = x_shift + scale_factor * math.cos(imag_part * t)
        y = scale_factor * math.sin(imag_part * t)
        
        # Convert to cm and create point
        point = adsk.core.Point3D.create(x, y, 0)
        points.add(point)
    
    # Create spline in sketch
    spline = sketch.sketchCurves.sketchFittedSplines.add(points)
    
    # Create thickness using sweep feature
    sweeps = root_comp.features.sweepFeatures
    path = root_comp.features.createPath(spline)
    
    # Create profile (circle) perpendicular to path
    profile_sketch = sketches.add(xy_plane)
    circle = profile_sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), thickness
    )
    
    # Create sweep input
    sweep_input = sweeps.createInput(
        profile_sketch.profiles.item(0),
        path,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    sweep_input.orientation = adsk.fusion.SweepOrientationTypes.PerpendicularOrientationType
    sweeps.add(sweep_input)
    
    app.activeViewport.refresh()
