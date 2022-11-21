# SVL_BeamAnalysis
## Overview
Written for Smart Vision Lights, This application captures cross sections of light beams and peak driver current measurments for in depth Pass/Fail product validation.

For example, AVT_BeamAnalysis.py is a script that captures a cross section of a beam at Xmm away, and finds 80% unifmormity in the beam, takes a horizontal and vertical profile of the 80% unifmormity, and plots the curves to find irregular patterns. This data is then compared to a threshold for Pass/Fail verification.

## Python Side
The Python side of this application handles all of the optical measurments done to our lights. The software uses and performs analysis on four metrics in order to decide if a product passes or fails quality standards.

**Testing Metrics:**
- Beam Size
- Uniformity
- Intensity
- Symmetry

## Hardware Side
***USES ARDUINO NANO PAIRED WITH PEAK CURRENT MEASURMENT***
