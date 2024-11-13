# Track Modeling

## Overview

The `track_modeling.py` script automates the process of creating a 3D railway 
track model in Blender. It imports left and right rail curves, a rail profile, 
and a sleeper profile in OBJ format, performs centerline calculations, and 
generates rail paths with offsets to place sleepers at regular intervals.

## Workflow Steps

1. **Import Rail Curves**: Loads OBJ files containing the left and right rail 
curves.
2. **Calculate Centerline**: Generates a centerline based on the midpoint 
between the two curves.
3. **Offset Rail Curves**: Creates offset rail paths according to the specified 
track gauge.
4. **Generate Rails**: Extrudes the rail profile along the rail paths.
5. **Place Sleepers**: Positions sleepers along the centerline at defined 
intervals.

## Requirements and Assumptions

- Ensure that the rail and sleeper OBJ files are oriented as follows:
  - The **rail profile** should be aligned so its **top point** is centered at 
  `(0,0,0)` in the coordinate frame. This ensures that the rails are placed at 
  the correct height.
  - The **sleeper profile** should account for the **rail offset** to align 
  below the rails, since the script places it directly on the centerline.
- The rail curves should have the **exact number of vertices** in each curve. 
Ideally, trace one polyline over one rail, then duplicate it to create the 
other rail curve. This will ensure symmetry.
- **Polyline Placement Consistency**: The input polylines should represent the 
same part of each rail (e.g., if the first polyline traces the rail’s inner 
side, the second polyline should trace the inner side as well).
- **Segment Approximation**: Curves or arcs should be approximated using 
straight line segments. This is a current limitation in the algorithm.

## Options and Configuration

Adjust the following parameters in the script:

```python
# PATHS
left_curve_path = '/path/to/Left_Rail_YZ.obj'
right_curve_path = '/path/to/Right_Rail_YZ.obj'
rail_profile_path = '/path/to/Rail_Profile2D.obj'
sleeper_profile_path = '/path/to/Sleeper_Profile_Offset_ZY.obj'

# Constants
TRACK_GAUGE = 1.520  # Track width in meters
SLEEPER_SPACING = 0.6  # Sleeper spacing in meters
```

## Troubleshooting

### Alignment Issues for Rails and Sleepers

If the sleeper model does not align correctly under the rails, double-check 
that it accounts for the rail offset, as this script places it directly on the 
centerline. You can adjust rotation in the script on:

- Line 210 (for rail)
- Line 216 (for sleeper)

If alignment or orientation errors persist, check the following:

- OBJ Orientation: Verify that the OBJ files for the rail and sleeper profiles 
are correctly oriented in the 3D space.
- Rotation Parameters: Tweak the rotation adjustments on lines 210 and 216 to 
achieve the correct orientation.

### Curve and Polyline Consistency

- Ensure that both polylines (left and right curves) have the same number of 
vertices for accurate centerline calculation.
- The polyline tracing should be consistent along each rail’s side (inner or 
outer edge). If one polyline traces closer to the inner side, the second should 
follow similarly for accurate centerline calculation.

### Curve Approximation Limitation

Currently, the script approximates curves using straight line segments. For 
best results, the rail paths should consist of closely spaced, straight 
segments that approximate the desired curve shape.

## Usage Instructions

1. Open Blender:
   - Go to the Scripting workspace in Blender.

2. Load the Script:
   - Copy or download track_modeling_automation.py.
   - Open it in Blender's scripting workspace.

3. Update File Paths:
   - Modify `left_curve_path`, `right_curve_path`, `rail_profile_path`, and 
   `sleeper_profile_path` with the paths to the relevant OBJ files.

3. Run the Script:
   - Click "Run Script" in Blender's scripting interface. 
   The track model, including rails and sleepers, will be generated in the 
   Blender scene.

