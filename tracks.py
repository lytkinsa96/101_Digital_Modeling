import bpy
import mathutils
import os
import math

# CONSTANTS
TRACK_GAUGE = 1.520 # meters
SLEEPER_SPACING = 0.6 # meters

def import_obj_polyline(filepath):
    # Parse OBJ file to extract vertex coordinates
    vertices = []
    with open(filepath, 'r') as file:
        for line in file:
            if line.startswith('v '):
                # Vertex line
                parts = line.strip().split()
                x, y, z = map(float, parts[1:4])
                vertices.append((x, y, z))
    if not vertices:
        print(f"No vertices found in {filepath}")
        return None
    # Create a Bezier curve from the vertices
    curve_data = bpy.data.curves.new(name=os.path.basename(filepath), type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(vertices) - 1)
    for i, coord in enumerate(vertices):
        bp = spline.bezier_points[i]
        bp.co = coord
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    curve_obj = bpy.data.objects.new(name=os.path.basename(filepath), object_data=curve_data)
    bpy.context.collection.objects.link(curve_obj)
    return curve_obj


def calculate_center_line(left, right):
    left_spline = left.data.splines[0]
    right_spline = right.data.splines[0]

    left_points = left_spline.bezier_points
    right_points = right_spline.bezier_points
    
    if len(left_points) != len(right_points):
        print("Error! Not the same number of vertices! Adjust input splines!")
        return None
    
    centerline_coords = []
    for lp, rp in zip(left_points, right_points):
        mid_point = (lp.co + rp.co) / 2
        centerline_coords.append(mid_point)
        
    # create curve
    curve_data = bpy.data.curves.new('Centerline', type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(centerline_coords) - 1)
    for i, coord in enumerate(centerline_coords):
        bp = spline.bezier_points[i]
        bp.co = coord
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    centerline_obj = bpy.data.objects.new('Centerline', curve_data)
    bpy.context.collection.objects.link(centerline_obj) # TODO
    return centerline_obj

def offset_curve(curve_obj, offset_distance):
    original_spline = curve_obj.data.splines[0]
    bezier_points = original_spline.bezier_points

    offset_curve_data = bpy.data.curves.new(curve_obj.name + "_Offset", type='CURVE')
    offset_curve_data.dimensions = '3D'
    spline = offset_curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(bezier_points) - 1)

    for i, bp in enumerate(bezier_points):
        co = bp.co.copy()
        # Calculate normal
        if i < len(bezier_points) - 1:
            next_co = bezier_points[i + 1].co
            tangent = (next_co - co).normalized()
        else:
            prev_co = bezier_points[i - 1].co
            tangent = (co - prev_co).normalized()
        normal = tangent.cross(mathutils.Vector((0, 0, 1))).normalized() # TODO
        offset = normal * offset_distance # TODO
        new_co = co + offset # TODO

        new_bp = spline.bezier_points[i]
        new_bp.co = new_co
        new_bp.handle_left_type = 'AUTO'
        new_bp.handle_right_type = 'AUTO'

    offset_curve_obj = bpy.data.objects.new(curve_obj.name + "_OffsetObj", offset_curve_data)
    bpy.context.collection.objects.link(offset_curve_obj)
    return offset_curve_obj

def create_rail(rail_curve, rail_profile):
    rail_curve.data.bevel_mode = 'OBJECT'
    rail_curve.data.bevel_object = rail_profile
    rail_curve.data.fill_mode = 'FULL'

def evaluate_bezier_curve(spline, t_normalized):
    # Number of segments in the spline
    num_segments = len(spline.bezier_points) - 1
    if num_segments <= 0:
        return None, None

    # Map t_normalized (0 to 1) to segment index and local t
    t_global = t_normalized * num_segments
    segment_index = int(t_global)
    t = t_global - segment_index

    if segment_index >= num_segments:
        segment_index = num_segments - 1
        t = 1.0

    # Get control points for the segment
    bp0 = spline.bezier_points[segment_index]
    bp1 = spline.bezier_points[segment_index + 1]
    P0 = bp0.co.copy()
    P1 = bp0.handle_right.copy()
    P2 = bp1.handle_left.copy()
    P3 = bp1.co.copy()

    # Evaluate position using the cubic Bezier formula
    u = 1 - t
    position = (u**3) * P0 + 3 * u**2 * t * P1 + 3 * u * t**2 * P2 + t**3 * P3

    # Evaluate tangent using the derivative of the Bezier curve
    tangent = 3 * u**2 * (P1 - P0) + 6 * u * t * (P2 - P1) + 3 * t**2 * (P3 - P2)
    tangent.normalize()

    return position, tangent

def place_sleepers(centerline_curve, sleeper_obj):
    spline = centerline_curve.data.splines[0]
    total_length = spline.calc_length()
    num_sleepers = int(total_length // SLEEPER_SPACING)

    # Place sleepers along the curve
    for i in range(num_sleepers + 1):
        distance = i * SLEEPER_SPACING
        t_normalized = distance / total_length
        if t_normalized > 1.0:
            t_normalized = 1.0  # Clamp to the curve's end

        position, tangent = evaluate_bezier_curve(spline, t_normalized)
        if position is None or tangent is None:
            continue  # Skip if evaluation failed

        # Create a rotation quaternion
        rotation = tangent.to_track_quat('-Z', 'Y')

        # Duplicate and place the sleeper
        sleeper_instance = sleeper_obj.copy()
        sleeper_instance.data = sleeper_obj.data.copy()
        bpy.context.collection.objects.link(sleeper_instance)
        sleeper_instance.location = position
        sleeper_instance.rotation_mode = 'QUATERNION'
        sleeper_instance.rotation_quaternion = rotation

def main(left_curve_path, right_curve_path, rail_profile_path, sleeper_profile_path):
    # Import left and right curves from OBJ files
    left_curve = import_obj_polyline(left_curve_path)
    right_curve = import_obj_polyline(right_curve_path)
    if not left_curve or not right_curve:
        print("Error: Could not find curves in imported OBJ files.")
        return
    
    # Import rail profile
    bpy.ops.wm.obj_import(filepath=rail_profile_path)
    rail_profile = bpy.context.selected_objects[0]

    # Convert rail_profile to curve if it's a mesh
    if rail_profile.type == 'MESH':
        bpy.context.view_layer.objects.active = rail_profile
        bpy.ops.object.convert(target='CURVE')

    # # Set the origin to the geometry center
    # bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

    # Ensure the rail_profile is oriented in the XY plane
    # Adjust rotation if necessary (e.g., rotate around X-axis by 90 degrees)
    rail_profile.rotation_euler = (math.radians(90), 0, 0)  # Adjust as needed
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # # Apply transformations
    # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bpy.ops.wm.obj_import(filepath=sleeper_profile_path)
    sleeper_obj = bpy.context.selected_objects[0]

    # sleeper_obj.rotation_euler = (math.radians(-90), 0, 0)  # Adjust as needed
    # bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    # Step 1: Calc centerline
    centerline = calculate_center_line(left_curve, right_curve)
    if not centerline:
        print("Error in centerline calc!")
        return
    
    # Step 2: Calc rail paths
    left_rail_curve = offset_curve(centerline, -TRACK_GAUGE / 2) # TODO: signs
    right_rail_curve = offset_curve(centerline, TRACK_GAUGE / 2)
    
    # Step 3: Create rails
    create_rail(left_rail_curve, rail_profile)
    create_rail(right_rail_curve, rail_profile)
    
    # Step 4: Place sleepers
    place_sleepers(centerline, sleeper_obj)

# PATHS
left_curve_path = '/home/sergey/Documents/2024_teaching/Blender/Left_Rail_YZ.obj'
right_curve_path = '/home/sergey/Documents/2024_teaching/Blender/Right_Rail_YZ.obj'
rail_profile_path = '/home/sergey/Documents/2024_teaching/Blender/Rail_Profile2D.obj'
sleeper_profile_path = '/home/sergey/Documents/2024_teaching/Blender/Sleeper_Profile_Offset_ZY.obj'

main(left_curve_path, right_curve_path, rail_profile_path, sleeper_profile_path)
