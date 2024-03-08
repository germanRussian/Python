'''
OpenCV에서 포인트 읽어와서 Spline curve fitting 알고리즘
'''

import numpy as np
import cv2
from scipy.interpolate import interp1d
from scipy.optimize import minimize

# Read an image from file
# image_name = 'DS_t2.bmp'
image_name = 'DS_t6.bmp'
# image_name = 'DS_t8.bmp'
# image_name = 'DS_t10.bmp'
# image_name = 'DS_t12.bmp'
# image_name = 'OS_t1.bmp'
# # image_name = 'OS_t7.bmp'
# # image_name = 'OS_t9.bmp'
# image_name = 'OS_t11.bmp'
image_path = "C:\\Users\\LEE JONGHYUK\\Desktop\\CGP_Poland_fac3\\testingImages\\" + image_name
image = cv2.imread(image_path)

if image is None:
    print("Error: Image not found.")
    exit()



#
# Define your three points (x1, y1), (x2, y2), (x3, y3)
points = np.array([[1898,29], [1906,436], [1914,790], [1923,1132], [1926,1511], [1921, 1923], [1922, 2141]])  # Example points



# Define your single point (x, y)
single_point = np.array([2110, 836])

# Extract x and y coordinates
x_coords, y_coords = points[:, 0], points[:, 1]
print(f'x_coords={x_coords}, y_coords={y_coords}')


# Create the spline
spline = interp1d(x_coords, y_coords, kind='linear')

# Function to calculate distance from a point on the spline to the single point
def distance_from_point(x):
    y = spline(x)
    return np.sqrt((x - single_point[0])**2 + (y - single_point[1])**2)



# Find the point on the spline that is closest to the single point
result = minimize(distance_from_point, x0=single_point[0], bounds=[(min(x_coords), max(x_coords))])
print(result)
closest_point_on_spline = (result.x[0], spline(result.x[0]))
print(closest_point_on_spline)
shortest_distance = distance_from_point(result.x[0])
print(shortest_distance)




# Function to scale and fit the curve within the image dimensions
height, width = image.shape[:2]

def scale_and_fit(x, y):
    x_scaled = int(1 * x)  # Scale factor for x
    # y_scaled = height - int(1 * y)  # Scale factor for y, invert y-axis for proper visualization
    y_scaled = int(1 * y)  # Scale factor for y, invert y-axis for proper visualization
    return x_scaled, y_scaled

# Draw the spline curve
x_range = np.linspace(min(x_coords), max(x_coords), 3000)
for x in x_range:
    y = spline(x)
    x_scaled, y_scaled = scale_and_fit(x, y)
    cv2.circle(image, (x_scaled, y_scaled), 1, (0, 0, 255), -1)  # Red curve



# Draw the original points
for point in points:
    x, y = scale_and_fit(point[0], point[1])
    cv2.circle(image, (x, y), 5, (0, 0, 255), 30)  # Red points



# Draw the single point
single_point_scaled = scale_and_fit(single_point[0], single_point[1])
cv2.circle(image, single_point_scaled, 3, (0, 255, 0), 30)  # Green point



# Draw the closest point on the spline
closest_point_scaled = scale_and_fit(closest_point_on_spline[0], closest_point_on_spline[1])
cv2.circle(image, closest_point_scaled, 3, (255, 255, 0), 30) #sky Point



# Draw the line segment between the single point and the closest point on the spline
cv2.line(image, single_point_scaled, closest_point_scaled, (255, 0, 0), 5)  # Blue line



#distance between single point and closest point on spline
dst = cv2.resize(image, dsize=(960, 540), interpolation=cv2.INTER_AREA) 



# Prepare text for displaying the shortest distance
distance_text = f"Distance: {shortest_distance:.2f}"
font = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10, 30)
fontScale = 1
fontColor = (255,255,255)
lineType = 2




#
cv2.putText(dst, distance_text, 
    bottomLeftCornerOfText, 
    font, 
    fontScale,
    fontColor,
    lineType)
#
# Display the image
cv2.imshow('Quadratic Curve on Image', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
