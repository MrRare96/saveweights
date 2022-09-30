# saveweights
Simple add-on for blender to help saving weights ( as json files, and load them as well :P).  Click on save weights for saving the active objects weights. Click on load weights to load any weight json file (independent of active object). 

Vertex groups are being saved and readded if they do not exist, or updated if they do.

Note that all matching vertexes in the JSON file within the existing GROUP will have their WEIGHTS overwritten!
Note 2: The ORDER for groups that are saved in the JSON file, are ABSOLUTE (thus it will overwrite/reset any existing orders in groups!).
