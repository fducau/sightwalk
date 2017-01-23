# SightWalk 
## DS-GA 1006 Final Project, Fall 2016 - Center for Data Science, NYU
- Sebastian Brarda <sb5518@nyu.edu>
- Felipe Ducau <fnd212@nyu.edu>
- Maria Elena Villalobos Ponte <mvp291@nyu.edu>

## Abstract
When providing walking directions to a destination,
web  mapping  services  usually  suggest  the  shortest  route  (in terms  of  distance  and/or  time).
The  goal  of  this  work  is  to automatically  suggest  alternative  more  enjoyable  routes,
which might take marginally more time but go through spots that would be more interesting to the user. 
In order to do that, we define a scoring  function  that  weights  each  path  based  on  social  media data.
Afterwards, we propose two new Graph based optimization algorithms  and  provide  a  demo  UI.

* [Technical Report](/SightWalk_Final_Report.pdf)
* [Poster](/docs/Capstone-poster.pdf)

## Repository Stucture
- scraper: code to get data from Flickr either by making use of the API or by directly parsing HTML data
- preprocessing: methods to associate raw data to corresponding edges and to generate data for scoring
- Graph: processed data and methods for calculating interestingness, graph search algorithm implementation
- evaluation: methods to evaluate generated paths
- sightwalk: web application to showcase results (demo)
- docs: project proposal, intermediate updates, final paper and poster.

## Demo:
[![Video](http://img.youtube.com/vi/GAvCeND9iRI/0.jpg)](http://www.youtube.com/watch?v=GAvCeND9iRI)

## Dependencies
Used versions of each library is listed.
- [Python](https://www.python.org/) v2.7.12
- [numpy](http://www.numpy.org/) v1.11.2
- [pandas](http://pandas.pydata.org/) v0.18.1
- [geopandas](http://geopandas.org/) v0.2.1
- [geojson](https://pypi.python.org/pypi/geojson/) v1.3.3
- [shapely](https://pypi.python.org/pypi/Shapely) v1.6b2
- [networkx](https://networkx.github.io/) v1.11
- [pymongo](https://api.mongodb.com/python/current/) v3.3.0

Demo
- [Django](https://www.djangoproject.com/) v1.10.3
- [bower](https://bower.io/) v1.8.0
- [jQuery](https://jquery.com/) v1.12.4
- [Bootstrap](https://getbootstrap.com/) v3.3.7
- [ion.rangeSlider](https://github.com/IonDen/ion.rangeSlider) v2.1.5


## How to run the demo
The demo is a django web application, in order to run it locally you should install all dependencies, go to the sightwalk folder and run:
```
python manage.py runserver
```
Then, access http://127.0.0.1:8000/paths/ it in your preferred browser.
