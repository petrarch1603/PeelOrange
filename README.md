![Peel Orange](/img/PeelOrange-Banner01.png)
This is a work in progress.



Peel Orange is a plugin that visualizes scale distortion on a map. The difficulties and trade-offs of making flat maps from a sphere is a famous and intractable problem in cartography. 

# Introducing Peel Orange

This tool doesn't solve the problem of distortion. Instead, it provides a framework for understanding where and how distortion happens. Some dilemmas in choosing a map projection are not satisfactorily resolved because there is no easy way to check the fidelity of a given projection. Many cartographers rely on their own sense of feeling in choosing a projection. This is a flawed process because this sense is driven by preconceptions that are themselves based on popular misunderstandings.  

The solution to this problem is to provide a tool that gives the cartographer an objective and falsifiable visualization of their map's distortion. In using this tool the cartographer can pit projections against each other and make an informed choice. 
This tool algorithmically creates a grid of points over a given region on a given projection and calculates the scale factor at each of these points. The points are then used in making isolines that visualize the gradient of change in scale distortion over that region.

This is useful for quickly comparing different projections in preparation for a new map project. OrangePeel can also provide a way of visualizing the changes in making custom projections.


> No map projection shows scale correctly throughout the map, but there are usually one or more lines on the map along which the scale remains true. By choosing the locations of these lines properly, the scale errors elsewhere may be minimized, although some errors may still be large, depending on the size of the area being mapped and the projection. 

<u>[Map Projections-A Working Manual](https://doi.org/10.3133/pp1395)</u> by John P. Snyder

