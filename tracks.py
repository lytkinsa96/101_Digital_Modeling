import bpy
import mathutils
import os
import math

# PATHS
left_curve_path = '/home/sergey/Documents/2024_teaching/Blender/Left_Rail_YZ.obj'
right_curve_path = '/home/sergey/Documents/2024_teaching/Blender/Right_Rail_YZ.obj'
rail_profile_path = '/home/sergey/Documents/2024_teaching/Blender/Rail_Profile2D.obj'
sleeper_profile_path = '/home/sergey/Documents/2024_teaching/Blender/Sleeper_Profile_Offset_ZY.obj'

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

def smooth_curve(curve_obj, iterations=5):
    bpy.context.view_layer.objects.active = curve_obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.curve.select_all(action='SELECT')
    for _ in range(iterations):
        bpy.ops.curve.smooth()
    bpy.ops.object.mode_set(mode='OBJECT')

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

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    rail_curve.select_set(True)
    bpy.context.view_layer.objects.active = rail_curve
    bpy.ops.object.convert(target='MESH')

    # Enter edit mode to fill the open ends
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.select_non_manifold()
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode='OBJECT')

def place_sleepers(centerline_curve, sleeper_obj):
    spline = centerline_curve.data.splines[0]
    spline.resolution_u = 64  # Increase as needed for smoother sampling

    # Convert the curve to a temporary mesh to access evaluated points
    temp_curve = centerline_curve.copy()
    temp_curve.data = centerline_curve.data.copy()
    bpy.context.collection.objects.link(temp_curve)
    bpy.ops.object.select_all(action='DESELECT')
    temp_curve.select_set(True)
    bpy.context.view_layer.objects.active = temp_curve
    bpy.ops.object.convert(target='MESH')

    # Get the vertices of the mesh
    mesh = temp_curve.data
    verts = [v.co.copy() for v in mesh.vertices]

    # Calculate cumulative distances along the vertices
    distances = [0]
    for i in range(1, len(verts)):
        seg_length = (verts[i] - verts[i - 1]).length
        distances.append(distances[-1] + seg_length)
    total_length = distances[-1]

    # Remove the temporary mesh
    bpy.data.objects.remove(temp_curve, do_unlink=True)

    # Place sleepers at regular intervals along the total length
    num_sleepers = int(total_length // SLEEPER_SPACING) + 1
    for i in range(num_sleepers):
        distance = i * SLEEPER_SPACING

        # Find the segment where the desired distance falls
        for j in range(1, len(distances)):
            if distances[j] >= distance:
                break
        else:
            j = len(distances) - 1

        # Interpolate between verts[j - 1] and verts[j]
        t = (distance - distances[j - 1]) / (distances[j] - distances[j - 1])
        position = verts[j - 1].lerp(verts[j], t)

        # Calculate the tangent for orientation
        tangent = (verts[j] - verts[j - 1]).normalized()

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

    # Smooth both curves
    smooth_curve(left_curve)
    smooth_curve(right_curve)
    
    # Import rail profile
    bpy.ops.wm.obj_import(filepath=rail_profile_path)
    rail_profile = bpy.context.selected_objects[0]

    # Convert rail_profile to curve if it's a mesh
    if rail_profile.type == 'MESH':
        bpy.context.view_layer.objects.active = rail_profile
        bpy.ops.object.convert(target='CURVE')

    # Ensure the rail_profile is oriented in the XY plane
    rail_profile.rotation_euler = (math.radians(90), 0, 0)  # Adjust as needed
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

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

main(left_curve_path, right_curve_path, rail_profile_path, sleeper_profile_path)
