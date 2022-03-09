![Peel Orange](/img/PeelOrange-Banner01.png)
# This is a work in progress.

# OrangePeel

OrangePeel is a plugin that visualizes the scale distortion on a given region on a given projection. The difficulties and trade-offs of making flat maps from the curving globe is a famous problem in the history of cartography. 

This tool algorithmically creates a grid of points over a given region on a given projection and calculates the scale factor at each of these points. The points are then used in making isolines that visualize the gradient of change in scale distortion over that region.

This is useful for quickly comparing different projections in preparation for a new map project. OrangePeel can also provide a way of visualizing the changes in making custom projections.


> No map projection shows scale correctly throughout the map, but there are usually one or more lines on the map along which the scale remains true. By choosing the locations of these lines properly, the scale errors elsewhere may be minimized, although some errors may still be large, depending on the size of the area being mapped and the projection. 

<u>[Map Projections-A Working Manual](https://doi.org/10.3133/pp1395)</u> by John P. Snyder

