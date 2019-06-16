background {
color
<1,1,1> 
}
plane {
<0,0,1>
0
texture {
pigment {
image_map {
jpeg
"/home/patrick/projects/kevin_gurney/la_hourly/basemaps/composite-crop.jpg"
once 
}
scale
<1702.4,1180.8,1>
translate
<-1702.4,-1180.8,0>
rotate
<180,180,0> 
}
finish {
emission
0.3 
} 
}
no_shadow 
}
light_source {
<254.5,171.0,1000>
color
<1,1,1> 
}
box {
<839.9000000000001,585.8,-5.0>
<1849.9,595.8,5.0>
texture {
pigment {
color
<0,1,0> 
}
finish {
emission
0.8 
} 
} 
}
box {
<839.9000000000001,585.8,-5.0>
<849.9000000000001,1595.8,5.0>
texture {
pigment {
color
<0,0,1> 
}
finish {
emission
0.8 
} 
} 
}
box {
<839.9000000000001,585.8,-5.0>
<849.9000000000001,595.8,1005.0>
texture {
pigment {
color
<1,0,0> 
}
finish {
emission
0.8 
} 
} 
}
box {
<839.9000000000001,585.8,-5.0>
<849.9000000000001,595.8,5.0>
texture {
pigment {
color
<1,1,1> 
}
finish {
emission
0.8 
} 
} 
}
camera {
orthographic
angle
60
location
<1231.8553410033383,893.8989616542092,500>
sky
<0,0,1>
look_at
<844.9000000000001,590.8,0.0>
right
<1.7777777777777777,0,0> 
}
global_settings{

}