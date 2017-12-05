#!/usr/bin/env bash
# Made with RRD Wizard.
# http://rrdwizard.appspot.com/
# https://github.com/famzah/rrdwizard

# 2 days - 5 minute resolution
# 7 days - 10 minute resolution
# 1 year - 1 hour resolution
rrdtool create ~/.chimera/temperatures.rrd \
--step '300' \
'DS:M1:GAUGE:300:-20:60' \
'DS:M2:GAUGE:300:-20:60' \
'DS:FrontRing:GAUGE:300:-20:60' \
'DS:TubeRod:GAUGE:300:-20:60' \
'DS:External:GAUGE:300:-20:60' \
'DS:DewPoint:GAUGE:300:-60:60' \
'RRA:MIN:0.5:1:576' \
'RRA:MIN:0.5:2:1008' \
'RRA:MIN:0.5:12:8640' \
'RRA:MAX:0.5:1:576' \
'RRA:MAX:0.5:2:1008' \
'RRA:MAX:0.5:12:8640' \
'RRA:AVERAGE:0.5:1:576' \
'RRA:AVERAGE:0.5:2:1008' \
'RRA:AVERAGE:0.5:12:8640'

#rrdtool graph ~/.chimera/temperatures.png \
#--title "Telescope Temperatures" \
#--vertical-label "Temperature oC" \
#--width "400" \
#--height "100" \
#--start end-3d \
#"DEF:M1=$HOME/.chimera/temperatures.rrd:M1:AVERAGE" \
#"DEF:M2=$HOME/.chimera/temperatures.rrd:M2:AVERAGE" \
#"DEF:FrontRing=$HOME/.chimera/temperatures.rrd:FrontRing:AVERAGE" \
#"DEF:TubeRod=$HOME/.chimera/temperatures.rrd:TubeRod:AVERAGE" \
#"DEF:External=$HOME/.chimera/temperatures.rrd:External:AVERAGE" \
#"DEF:DewPoint=$HOME/.chimera/temperatures.rrd:DewPoint:AVERAGE" \
#"AREA:External#404040:External" \
#"AREA:DewPoint#808080:Dew" \
#"LINE1:M1#FF0000:M1" \
#"LINE1:M2#0000FF:M2" \
#"LINE1:FrontRing#00FF00:Front Ring" \
#"LINE1:TubeRod#CC33FF:Tube Rod"