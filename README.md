![Peel Orange](/img/PeelOrange-Banner01.png)


Peel Orange is a plugin that visualizes scale distortion on a map. The difficulties and trade-offs of making flat maps from a sphere is a famous and intractable problem in cartography. 

# Installation
Peel Orange is available through the [QGIS Python Plugins
Repository](https://plugins.qgis.org/plugins/). Start QGIS3, go to the Plugins menu → Manage and Install Plugins, then search for `Peel Orange Scale Distortion Visualizer`

### Manual Installation
* Clone or download the Peel Orange GitHub repository
* Copy `PeelOrange-main` to `python/plugins/` in the current active
  profile, the location of which can be found from within QGIS3 by
  going to 'Settings &rarr; User Profiles &rarr; Open Active Profile
  Folder' (\*)
* Enable the plugin in QGIS3 by going to 'Plugins &rarr; Manage and
  Install Plugins...' and find Peel Orange (may require restarting QGIS3)

# Introducing Peel Orange

Peel Orange provides a framework for understanding where and how distortion happens. The problems of scale distortion cannot be solved: they can only be understood and reduced. Many of the dilemmas in choosing a map projection are not satisfactorily resolved because there is no easy way to check the fidelity of a given projection. Cartographers often rely on their own sense of feeling in choosing a projection. This is a flawed process because this sense is driven by preconceptions that are themselves based on popular misunderstandings.  

The solution to this problem is to provide a tool that gives the cartographer an objective and falsifiable visualization of their map's distortion. In using this tool the cartographer can pit projections against each other and make an informed choice. The right projection is the first step in making exquisite maps. 

The process for visualizing the distortion is simple. This tool algorithmically creates a grid of points over a given region. Peel Orange blankets the region with a grid of about 10,000 points. 

Before we go further though, it is important to understand how coordinate systems work. On projected coordinate systems geographic coordinates, i.e. latitude and longitude, are transformed into cartesian x, y coordinates. If you look into the documentation for these projections you'll see that they have map units such as meters or survey feet. 
If we take one point on one of these projections it will have an x and y value. If we want to go north 500 meters we can just add 500 to the y value and that will give us a new point.  If we want to go south from the original point we just subtract 500 from y. 
So what if we calculate the distance from that north point to that south point (on the ground), it should equal 1,000 meters, right? Well, actually it doesn't. In most cases it will be a bit longer than 1,000 meters. When analyzed this ratio is the means to visualizing map distortion.

![scale_factor_profile](/img/scale_factor_profile.png)

On this simplified profile you can see a cross-section of the projection surface, or map, through Earth's ellipsoid. The symbols with an apostrophe represent points on the map, the symbols with an apostrophe represent points on the Earth. As you can see the distances on the map do not match the distance across the Earth. 

## Why aren't scales true?

This break between grid and ground happens because the x and y coordinates get distorted when mapping a curved surface. It is an inescapable part of making maps. This distortion, though, is predictable and follows a pattern for any given projection. For each of those aforementioned grid points Peel Orange will calculate four supplementary points on each of the cardinal directions: north, south, east and west. Then, the distances between the north and south points are measured and same for the east and west. This is divided by the projected distance to give a scale factor. The side that has the greatest scale factor, be it north-south or east-west, will then be stored as a field in the layer row of that point.

When this is performed over thousands of neatly spaces points across a region a pattern begins to form. Certain areas will have scale factors very close to 1.000. These points have the highest scale fidelity. As we move away from these regions though, the scale distortion will progressively get worse. Peel Orange visualizes this pattern in only a few moments. 

> No map projection shows scale correctly throughout the map, but there are usually one or more lines on the map along which the scale remains true. By choosing the locations of these lines properly, the scale errors elsewhere may be minimized, although some errors may still be large, depending on the size of the area being mapped and the projection. 

<u>[Map Projections-A Working Manual](https://doi.org/10.3133/pp1395)</u> by John P. Snyder

## Thresholds
Every time Peel Orange is run it creates a dynamically calculated range of scale distortion values. 


on a given projection and calculates the scale factor at each of these points. The points are then used in making isolines that visualize the gradient of change in scale distortion over that region.

This is useful for quickly comparing different projections in preparation for a new map project. OrangePeel can also provide a way of visualizing the changes in making custom projections.

