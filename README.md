# Statatouille
A data driven website showcasing tools I've built that perform various analysis across large sets of MLB, NFL, NHL, and NBA data. 

## Frameworks
* [Python] - data extraction, manipulation, and analysis

### Tools
An assortment of tools I've built, primarily coded in python and focused around scraping and analyzing sports data, particularly MLB, NHL, and NFL. 
Each project has a back end data refresh and a front end application that is part of the website.

## Data Flow
All MLB, NHL, and NFL data is pulled from sites such as Baseball Savant, Fangraphs, etc. using a series of Beautiful Soup web scrapers.
The data is then dumped into a MongoDB Atlas database where it can be read by the front end Node application. 
This data is refreshed in MongoDB daily at 4AM EST. 

## Authors
* **Mike Kutilek** - *All work*