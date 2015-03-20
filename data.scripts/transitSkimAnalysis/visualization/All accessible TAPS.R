#'  Script for visualizing set of accessible TAPs in MTC TM2 transit network
#'  
#'  The useR has to specify the following parameters
#'  @param period Skim time period to use ['EA','AM','MD','PM','EV']
#'  @param TAP_BEING_QUERIED tap id for which we want to plot the accessible set of taps
#'  @param TAP_NAME name of the tap give the user a general idea of the origin tap area. For pretty plotting
#'      
#'  The script produces a map showing TAPs colored based on whether or not they are accessible from TAP_BEING_QUERIED
#'  Green - TAP is accessible; Red - TAP is not accessible; Blue - TAP_BEING_QUERIED
#'        
#'  @date: 2013-11-07
#'  @author: sn, narayanamoorthys AT pbworld DOT com

library(maptools)
library(sp)
library(dplyr)
library(ggplot2)
library(RColorBrewer)
library(rgdal)
library(ggmap)

#Specify input parameters
PERIOD = 'AM'
TAP_BEING_QUERIED = 487
TAP_NAME = "Near Trans Bay Terminal"   #Just for making the plot title nice

#Reading skim csvs using pandas csv reader (fastest option available)
cmd <- "C:\\Python27\\python.exe quickSkimRead.py @@TAP@@ @@PERIOD@@"
cmd <- gsub("@@TAP@@",TAP_BEING_QUERIED,cmd)
cmd <- gsub("@@PERIOD@@",PERIOD,cmd)
system(cmd, intern=FALSE, show.output.on.console=TRUE)

# Create a blank theme for plotting the map
blankMapTheme <- theme_grey()
blankMapTheme$axis.text <- element_blank()
blankMapTheme$axis.title <- element_blank()

#Read in shapefile and unproject
taps <- readOGR("shapefiles","mtc_tap_nodes")
if (is.projected(taps)) taps <- spTransform(taps, CRS("+proj=longlat +ellps=WGS84"))

#Read in skim data to get accessible TAPs
skimSet1 = read.csv(gsub("@@TAP@@", TAP_BEING_QUERIED, gsub("@@PERIOD@@",PERIOD, gsub("@@SET@@","SET1","./plot_csv/ts_plot_@@SET@@_@@PERIOD@@_@@TAP@@.csv"))))
skimSet2 = read.csv(gsub("@@TAP@@", TAP_BEING_QUERIED, gsub("@@PERIOD@@",PERIOD, gsub("@@SET@@","SET2","./plot_csv/ts_plot_@@SET@@_@@PERIOD@@_@@TAP@@.csv"))))
skimSet3 = read.csv(gsub("@@TAP@@", TAP_BEING_QUERIED, gsub("@@PERIOD@@",PERIOD, gsub("@@SET@@","SET3","./plot_csv/ts_plot_@@SET@@_@@PERIOD@@_@@TAP@@.csv"))))

zone_list = unique(c(skimSet1$DTAP,skimSet2$DTAP,skimSet3$DTAP))

#Create plot layers
accessible_taps = taps[taps@data$TAPSEQ %in% zone_list,]
accessible_taps.df <- as.data.frame(accessible_taps@coords)
inaccessible_taps = taps[!(taps@data$TAPSEQ %in% zone_list),]
inaccessible_taps.df <- as.data.frame(inaccessible_taps@coords)
query_tap = taps[taps@data$TAPSEQ %in% c(TAP_BEING_QUERIED),]
query_tap.df <- as.data.frame(query_tap@coords)

#Fetch basemap for the Bay Area
mtc_baseMap = get_googlemap(center = c(lon = mean(taps@coords[,"coords.x1"]), lat = mean(taps@coords[,"coords.x2"]))
                       ,zoom = 8
                       ,scale = 4
                       ,maptype="roadmap"
                       ,size = c(640, 640))

#Plot
p1 <- ggmap(mtc_baseMap) + 
  geom_point(data = inaccessible_taps.df, aes(x=coords.x1, y=coords.x2), inherit.aes=FALSE,fill="red",pch=21,size=1) +
  geom_point(data = accessible_taps.df, aes(x=coords.x1, y=coords.x2), inherit.aes=FALSE,fill="Lawn Green",pch=21,size=1) +
  geom_point(data = query_tap.df, aes(x=coords.x1, y=coords.x2), inherit.aes=FALSE,fill="#377eb8",size=4,pch=21,size=1) +
  blankMapTheme+
  labs(title = paste(TAP_NAME, "All Sets :",PERIOD, TAP_BEING_QUERIED,sep=" "))
ggsave(file = paste(TAP_NAME, " All Sets  ",PERIOD, TAP_BEING_QUERIED,".png",sep=""), width=10,height=10,dpi = 1080)

