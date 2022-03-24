![Peel Orange](/img/PeelOrange-Banner01.png)


Peel Orange is a QGIS3 plugin that visualizes scale distortion on a map. The difficulties and trade-offs of making flat maps from a sphere is a famous and intractable problem in cartography. 

# Installation
Peel Orange is available through the [QGIS Python Plugins
Repository](https://plugins.qgis.org/plugins/). Start QGIS3, go to the `Plugins` menu → `Manage and Install Plugins`, then search for `Peel Orange Scale Distortion Visualizer`

### Manual Installation

Alternatively install manually install for the latest update.
* Clone or download the Peel Orange GitHub repository
* Copy `PeelOrange-main` to `python/plugins/` in the current active
  profile, the location of which can be found from within QGIS3 by
  going to `Settings` &rarr; `User Profiles` &rarr; `Open Active Profile
  Folder`
* Enable the plugin in QGIS3 by going to `Plugins` &rarr; `Manage and
  Install Plugins` and find Peel Orange (may require restarting QGIS3)

# Introducing Peel Orange

<p align="center">
  <img width="1262" height="406" src="/img/supplemental/spain3examples.png">
</p>


Peel Orange provides a framework for understanding where and how distortion happens. The problems of scale distortion cannot be solved: they can only be understood and reduced. Many of the dilemmas in choosing a map projection are not satisfactorily resolved because there is no easy way to check the fidelity of a given projection. Cartographers often rely on their own sense of feeling in choosing a projection. This is a flawed process because this sense is driven by preconceptions that are themselves based on popular misunderstandings.  

The solution to this problem is to provide a tool that gives the cartographer an objective and falsifiable visualization of their map's distortion. In using this tool the cartographer can pit projections against each other and make an informed choice. The right projection is the first step in making exquisite maps. 

The process for visualizing the distortion is simple. This tool algorithmically creates a grid  over a given region. Peel Orange blankets the region with a grid of about 10,000 points. 

To understand how Peel Orange works, first it is important to understand how coordinate systems work. On any flat map the coordinates, i.e. latitude and longitude, are transformed into cartesian x, y coordinates. 

If we take one point on a map it will have an x and y value. If we want to go north 500 meters we can just add 500 to the y value and that will give us a new point.  If we want to go south from the original point we just subtract 500 from y. 
So what if we go out in the real world and measure the distance from that north point to that south point, it should equal 1,000 meters, right? Well, actually it doesn't. In most cases it will be a bit longer than 1,000 meters. Peel Orange quickly analyzes this ratio for thousands of points. When we plot these numbers we get a clear pattern of scale distortion.

![scale_factor_profile](/img/scale_factor_profile.png)

On this simplified profile you can see a cross-section of the projection surface, or map, through Earth's ellipsoid. The symbols with an apostrophe (A'B'C'D') represent points on the map, the symbols without an apostrophe (ABCD) represent points on the Earth. As you can see the distances on the map do not match the distances across the Earth. This is a simple model and there are ways that cartographers can ameliorate this distortion, but no projection is able to escape these aberrations. 

## Why aren't scales true?

This break between grid and ground happens because the x and y coordinates get distorted when mapping a curved surface. It is an inescapable part of making maps. This distortion, though, is predictable and follows a pattern for any given projection. For each of those aforementioned grid points Peel Orange will calculate four supplementary points on each of the cardinal directions: north, south, east and west. Then, the distances between the north and south points are measured and same for the east and west. This is divided by the projected distance to give a scale factor. The side that has the greatest scale factor, be it north-south or east-west, will then be stored as a field in the layer row of that point.

When this is performed over thousands of neatly spaces points across a region a pattern begins to form. Certain areas will have scale factors very close to 1.000. These points have the highest scale fidelity. As we move away from these regions though, the scale distortion will progressively get worse. 

> No map projection shows scale correctly throughout the map, but there are usually one or more lines on the map along which the scale remains true. By choosing the locations of these lines properly, the scale errors elsewhere may be minimized, although some errors may still be large, depending on the size of the area being mapped and the projection. 

<u>[Map Projections-A Working Manual](https://doi.org/10.3133/pp1395)</u> by John P. Snyder

## Peel Orange is easy to use
To run Peel Orange go to the `Plugins` dropdown menu and click on `Peel Orange Scale Distortion Visualizer`.

<p align="center">
  <img width="597" height="607" src="/img/dialog_example.png">
</p>

First select a layer to use as the bounding box for Peel Orange analysis. This layer must be on the same projection as the project projection. Additionally, this projection cannot use a geographic coordinate system (i.e. using degrees as distant units, the projection should be meters or feet instead). This layer must also have enough features to use as a rectangular bounding box. 

If you do not have such a layer, creating one is easy. Create a temporary scratch layer by going to the `Layer` pulldown menu &rarr; `New Temporary Scratch Layer`. Select Polygon `Geometry Type` and make sure the projection is the same as the project. 

Next go to the `Edit` pulldown menu and select `Add Rectangle` to draw a rectangle on the map. Now you can use this layer as your bounding box. 

### Statistical Analysis
This option plots a statistical distribution of scale distortions. The ideal projection will have a concentration of points with values that are close to 1.00. The further the numbers are from 1.00 the more distortion there is in the map.


### Thresholds
<img align="right" width="217" height="219" src="/img/legend_thres_off.png">
Every time Peel Orange is executed it creates a dynamically calculated range of scale distortion values. Because of this it is not convenient to compare gradients from one projection to another. To mitigate this the Threshold feature was introduced.


The threshold value represents a percentage of scale distortion that is an acceptable tolerance to the mapmaker. When Peel Orange finishes its calculations the regions that are below the threshold will be turned off in the legend. 


## Understanding the results

<p align="center">
  <img width="774" height="385" src="/img/understanding_results.png">
</p>

Peel Orange creates a new hex grid layer. The layer styling is graduated with reference to the absolute delta of the scale distortion. That number represents the delta from 1.00. For example a scale distortion with a value of 1.02 will have an absolute delta of 0.02, a scale distortion of 0.99 will have an absolute delta of 0.01. The lower this number the closer its fidelity is to the scale on the Earth. A color ramp is automatically created with white representing lower distortion and black representing higher distortion. This color ramp and the number of classes can be fine-tuned after Peel Orange is executed.   

    
Consider the salient features of the region you wish to map. Are they within the threshold areas of the map? If they are not, then it might be worth considering another projection and running Peel Orange on that new projection. 

## Stylizing the results

<p align="center">
  <img width="528" height="483" src="/img/3376_example.png">
</p>

You can make the style of the hex layer look transparent with a subtle blur effect. In the layer styling click on `Symbol`, under `Fill` click on `Simple Fill` and change the `Stroke Style` to `No Pen`. Click on the back arrow to get back to the Graduated symbol settings. Under `Layer Rendering` check `Draw Effects` and click on the 'Star' button. Change `Effect Type` to `Blur`. 

Lastly go to the `Color Ramp` and make the white stop completely transparent (opacity = 0%). Fine-tune these settings to find a suitable style. 

# Further Thoughts on Projections

## What about the Tissot Indicatrix

<p align="center">
  <img width="400" height="400" src="/img/supplemental/peirce_tissot.png">
</p>

> In cartography, a Tissot's indicatrix (Tissot indicatrix, Tissot's ellipse, Tissot ellipse, ellipse of distortion) (plural: "Tissot's indicatrices") is a mathematical contrivance presented by French mathematician Nicolas Auguste Tissot in 1859 and 1871 in order to characterize local distortions due to map projection. It is the geometry that results from projecting a circle of infinitesimal radius from a curved geometric model, such as a globe, onto a map. Tissot proved that the resulting diagram is an ellipse whose axes indicate the two principal directions along which scale is maximal and minimal at that point on the map.
([Wikipedia](https://en.wikipedia.org/wiki/Tissot%27s_indicatrix))

The Tissot indicatrix is a legendary breakthrough in understanding map projections. There is an [excellent QGIS plugin](https://plugins.qgis.org/plugins/tiss/) by Ervin Wirth and Péter Kun for plotting these indicatrices in QGIS.

However, these indicatrices do not visualize the subtle granularity in scale distortions on different projections. If the cartographer is trying to fine-tune their projection to contain their distortion under 10% it will be difficult to uncover this by looking at widely spaced ellipses. 
These indicatrices are generally plotted on fixed meridians and parallels and number in the dozens. Peel Orange calculates thousands of points and assigns them a scale distortion. This blanket of information gives the cartographer a better understanding of the distortion.


## Why Not An Equal Area Index?

<p align="center">
  <img width="735" height="373" src="/img/supplemental/hourglass.png">
</p>
   
   

<p style="text-align: center;">Equal area Projection invented by John Snyder as a joke.</p>
   
    

Equal-Area (also known as Equivalent) maps still have distortion. The surface is stretched in one direction and shrunk in another to compensate.

The above hourglass projection by John Snyder was referenced in Mark Monmonier's *How to Lie with Maps*:
> “John Snyder, himself a developer of several useful as well as innovative map projections, offered yet another equal-area projection to underscore his cartographic colleagues’ point that an equal-area map is not necessarily a good map. Snyder’s hourglass equal-area projection...preserves areal relationships. But it also demonstrates dramatically that areal fidelity does not mean shape fidelity.”
(3rd Edition, Page 111)

On this Gall-Peters map with Tissot indicatrices [from Wikipedia](https://commons.wikimedia.org/wiki/Category:Gall-Peters_projection#/media/File:Tissot_indicatrix_world_map_Gall-Peters_equal-area_proj.svg) we can see this distortion in action:

<p align="center">
  <img width="640" height="406" src="/img/supplemental/gall-peters-tissot.png">
</p>

Each ellipse contains the same area, but the shape is greatly distorted. We could easily write a script to compare area at different points on the globe, but the results would be misleading. For a map to show scale fidelity, a given point should have consistent scale in all directions. 

In conformal maps the scale *is* consistent in every direction. The ellipse in the map above will no longer be an oval, but a circle. Observe the Tissot indicatrices on the Mercator projection. 

<p align="center">
  <img width="777" height="720" src="/img/supplemental/Tissot_mercator.png">
</p>

However, Peel Orange was designed to work on most conventional projections, including non-conformal. For such projections the script will compare the ratio of the distances of each of the axes ([From Wikipedia](https://en.wikipedia.org/wiki/Tissot%27s_indicatrix#/media/File:Indicatrix.png)):

<p align="center">
  <img width="308" height="325" src="/img/supplemental/Indicatrix.png">
</p>

Consider the ratio of A' to A (*k*). This will be a number over 1.00 and represents a scale factor. Now consider the ratio of B' to B (*h*). Which ratio is further away from 1.00? The script will select this value and use it for the scale distortion of that point. This kind of analysis would be missing from an area comparison. 

# Examples

<p align="center">
  <img width="640" height="540" src="/img/supplemental/example_polyconic.png">
</p>

<p align="center">
  <img width="640" height="540" src="/img/supplemental/azi_equi.png">
</p>

<p align="center">
  <img width="641" height="541" src="/img/supplemental/miller_cylindrical.png">
</p>
