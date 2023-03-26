import numpy as np

def find_point_on_segment(p1, p2, ratio):
    return (p1[0] + (p2[0] - p1[0]) * ratio, p1[1] + (p2[1] - p1[1]) * ratio)

def euclidean_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def subdivide_path(points, sections=10):
    # Calculate total length of the path
    total_length = sum(euclidean_distance(points[i], points[i+1]) for i in range(len(points) - 1))
    section_length = total_length / sections

    # Iterate through the path and find the points at each section
    section_points = []
    current_length = 0
    section = 1

    for i in range(len(points) - 1):
        segment_length = euclidean_distance(points[i], points[i + 1])
        remaining_length = section_length * section - current_length

        while remaining_length <= segment_length:
            ratio = remaining_length / segment_length
            point_on_segment = find_point_on_segment(points[i], points[i + 1], ratio)
            section_points.append(point_on_segment)

            section += 1
            remaining_length = section_length * section - current_length

        current_length += segment_length


    intify = lambda arr: list(map(lambda x: (int(x[0]), int(x[1])), arr))
    return intify(section_points)



# # Test the function
# path = [(0, 0), (10, 10), (20, 0), (30, 10)]
# sections = 10
# result = subdivide_path(path, sections)
# print(result)

