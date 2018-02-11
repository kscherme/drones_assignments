from math import sin, cos, sqrt, atan2, radians

R = 6373.0

rad = .00007

def get_distance_meters(latitude1, longitude1, latitude2, longitude2):
	lat1 = radians(latitude1)
	lon1 = radians(longitude1)
	lat2 = radians(latitude2)
	lon2 = radians(longitude2)

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * atan2(sqrt(a), sqrt(1-a))

	distance = R * c * 1000

	print("Result: ", distance)

def get_circle_coords(center_lat, center_long):

	sqrt_3_2 = (sqrt(3)/2)*rad
	sqrt_2_2 = (sqrt(2)/2)*rad
	half = rad/2

	print (center_lat),(center_long-rad)
	print (center_lat+half),(center_long-sqrt_3_2)
	print (center_lat+sqrt_2_2),(center_long-sqrt_2_2)
	print (center_lat+sqrt_3_2),(center_long-half)
	print (center_lat+rad),(center_long)
	print (center_lat+sqrt_3_2),(center_long+half)
	print (center_lat+sqrt_2_2),(center_long+sqrt_2_2)
	print (center_lat+half),(center_long+sqrt_3_2)
	print (center_lat),(center_long+rad)





get_circle_coords(41.71480,-86.24100)



get_distance_meters(41.71480,-86.24307, 41.71480,-86.24300)


