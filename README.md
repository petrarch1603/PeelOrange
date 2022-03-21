![Peel Orange](/img/PeelOrange-Banner01.png)


Peel Orange is a plugin that visualizes scale distortion on a map. The difficulties and trade-offs of making flat maps from a sphere is a famous and intractable problem in cartography. 

# Installation
Peel Orange is available through the [QGIS Python Plugins
Repository](https://plugins.qgis.org/plugins/). Start QGIS3, go to the Plugins menu → Manage and Install Plugins, then search for `Peel Orange Scale Distortion Visualizer`

### Manual Installation
* Clone or download the Peel Orange GitHub repository
* Copy `PeelOrange-main` to `python/plugins/` in the current active
  profile, the location of which can be found from within QGIS3 by
  going to `Settings` &rarr; `User Profiles` &rarr; `Open Active Profile
  Folder`
* Enable the plugin in QGIS3 by going to `Plugins` &rarr; `Manage and
  Install Plugins` and find Peel Orange (may require restarting QGIS3)

# Introducing Peel Orange

Peel Orange provides a framework for understanding where and how distortion happens. The problems of scale distortion cannot be solved: they can only be understood and reduced. Many of the dilemmas in choosing a map projection are not satisfactorily resolved because there is no easy way to check the fidelity of a given projection. Cartographers often rely on their own sense of feeling in choosing a projection. This is a flawed process because this sense is driven by preconceptions that are themselves based on popular misunderstandings.  

The solution to this problem is to provide a tool that gives the cartographer an objective and falsifiable visualization of their map's distortion. In using this tool the cartographer can pit projections against each other and make an informed choice. The right projection is the first step in making exquisite maps. 

The process for visualizing the distortion is simple. This tool algorithmically creates a grid of points over a given region. Peel Orange blankets the region with a grid of about 10,000 points. 

Before we go further though, it is important to understand how coordinate systems work. On projected coordinate systems geographic coordinates, i.e. latitude and longitude, are transformed into cartesian x, y coordinates. If you look into the documentation for these projections you'll see that they have map units such as meters or survey feet. 
If we take one point on one of these projections it will have an x and y value. If we want to go north 500 meters we can just add 500 to the y value and that will give us a new point.  If we want to go south from the original point we just subtract 500 from y. 
So what if we calculate the distance from that north point to that south point (on the ground), it should equal 1,000 meters, right? Well, actually it doesn't. In most cases it will be a bit longer than 1,000 meters. When analyzed this ratio is the means to visualizing map distortion.

![scale_factor_profile](/img/scale_factor_profile.png)

On this simplified profile you can see a cross-section of the projection surface, or map, through Earth's ellipsoid. The symbols with an apostrophe (A'B'C'D') represent points on the map, the symbols without an apostrophe (ABCD) represent points on the Earth. As you can see the distances on the map do not match the distance across the Earth. 

## Why aren't scales true?

This break between grid and ground happens because the x and y coordinates get distorted when mapping a curved surface. It is an inescapable part of making maps. This distortion, though, is predictable and follows a pattern for any given projection. For each of those aforementioned grid points Peel Orange will calculate four supplementary points on each of the cardinal directions: north, south, east and west. Then, the distances between the north and south points are measured and same for the east and west. This is divided by the projected distance to give a scale factor. The side that has the greatest scale factor, be it north-south or east-west, will then be stored as a field in the layer row of that point.

When this is performed over thousands of neatly spaces points across a region a pattern begins to form. Certain areas will have scale factors very close to 1.000. These points have the highest scale fidelity. As we move away from these regions though, the scale distortion will progressively get worse. Peel Orange visualizes this pattern in only a few moments. 

> No map projection shows scale correctly throughout the map, but there are usually one or more lines on the map along which the scale remains true. By choosing the locations of these lines properly, the scale errors elsewhere may be minimized, although some errors may still be large, depending on the size of the area being mapped and the projection. 

<u>[Map Projections-A Working Manual](https://doi.org/10.3133/pp1395)</u> by John P. Snyder

## Peel Orange is easy to use
To run Peel Orange go to the `Plugins` dropdown menu and click on `Peel Orange Scale Distortion Visualizer`.

<p align="center">
  <img width="597" height="607" src="/img/dialog_example.png">
</p>

First select a layer to use as the bounding box for Peel Orange analysis. This layer must be on the same projection as the project projection. Additionally this projection cannot use a geographic coordinate system (i.e. using degrees as distant units, the projection should be meters or feet instead). This layer must also have enough features to use as a rectangular bounding box. 

If you do not have such a layer, creating one is easy. Create a temporary scratch layer by going to the `Layer` pulldown menu &rarr; `New Temporary Scratch Layer`. Select Polygon `Geometry Type` and make sure the projection is the same as the project. 

Next go to the `Edit` pulldown menu and select `Add Rectangle` to draw a rectangle on the map. Now you can use this layer as your bounding box. 

### Statistical Analysis
This option plots a statistical distribution of scale distortions. The ideal projection will have a concentration of points that are close to 1.00. The further the numbers are from 1.00 the more distortion there is in the map.


### Thresholds
<img align="right" width="217" height="219" src="/img/legend_thres_off.png">
Every time Peel Orange is executed it creates a dynamically calculated range of scale distortion values. Because of this it is not convenient to compare gradients from one projection to another. To mitigate this the Threshold feature was introduced.


The threshold value represents a percentage of scale distortion that is an acceptable tolerance to the mapmaker. When Peel Orange finishes its calculations the regions that are below the threshold will be turned off in the legend. 


## Understanding the results

<p align="center">
  <img width="773" height="384" src="/img/3376_example.png">
</p>

Peel Orange creates a new hex grid layer. The layer styling is graduated with reference to the absolute delta of the scale distortion. That number represents the delta from 1.00. For example a scale distortion with a value of 1.02 will have an absolute delta of 0.02. The lower this number the closer its fidelity is to the scale on the Earth. A color ramp is automatically created with white representing lower distortion and black representing higher distortion. This color ramp and the number of classes can be fine-tuned after Peel Orange is executed.   

    
Consider the salient features of the region you wish to map. Are they within the threshold areas of the map? If they are not, then it might be worth considering another projection and running Peel Orange on that new projection. 

## Stylizing the results

<p align="center">
  <img width="528" height="483" src="/img/understanding_results.png">
</p>

You can make the style of the hex layer look transparent with a subtle blur effect. In the layer styling click on `Symbol`, under `Fill` click on `Simple Fill` and change the `Stroke Style` to `No Pen`. Click on the back arrow to get back to the Graduated symbol settings. Under `Layer Rendering` check `Draw Effects` and click on the 'Star' button. Change `Effect Type` to `Blur`. 

Lastly go to the `Color Ramp` and make the white stop completely transparent (opacity = 0%). Fine-tune these settings to find a suitable style. 