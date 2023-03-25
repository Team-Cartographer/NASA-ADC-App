from math import sin, cos, radians, degrees, atan2, asin, sqrt

lat = -89.22993678059875  # IN DEGREES (p 16)
long = -30.9805884292136  # IN DEGREES (p 16)
height = -1345.5  # IN METERS (p 16)
slope = 24.0


lunar_rad = 1737.4  # IN KM (p 32)

rad = (lunar_rad * 1000) + height

lat_radians = radians(lat)
long_radians = radians(long)

earth_x = 361000  # IN KM (p 17)
earth_y = 0  # IN KM (p 17)
earth_z = -42100  # IN KM (p 17)

x = rad * cos(lat_radians) * cos(long_radians)
y = rad * cos(lat_radians) * sin(long_radians)
z = rad * sin(lat_radians)

dx = (earth_x * 1000) - x
dy = (earth_y * 1000) - y
dz = (earth_z * 1000) - z

r = sqrt(dx**2 + dy**2 + dz**2)
elev = asin(dz / r)
azi = atan2(dy, dx)

elev_deg = degrees(elev)
azi_deg = degrees(azi)

print(elev_deg)
print(azi_deg)

"""
x = 20003.59247405839
y = -12010.148927981112
z = -1735897.704238677

azi = -30.98058842921374
elev = -1.3606133553021384   
"""