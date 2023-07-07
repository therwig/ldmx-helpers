ele_50e4000_0pt800=[ # appears not to populate high-pt well
     "/gps/particle e-",
     "/gps/pos/type Plane",
     "/gps/direction 0 0 1",
     # Mono energy
     # "/gps/ene/mono 4 GeV",
     # Linear energy
     "/gps/ene/type Lin",
     "/gps/ene/min 0.05 GeV",
     "/gps/ene/max 4 GeV",
     "/gps/ene/gradient 0",
     "/gps/ene/intercept 1",
     # circle
     # "/gps/pos/shape Circle",
     # "/gps/pos/centre 0 0 240 mm",
     # "/gps/pos/radius 50 mm", #50 or 150
     # Square
     "/gps/pos/shape Square",
     "/gps/pos/centre 0 0 0 mm",
     "/gps/pos/halfx 1 mm",
     "/gps/pos/halfy 1 mm",
     # angles
     # "/gps/ang/type cos",
     "/gps/ang/type iso",
     "/gps/ang/mintheta 2.94 rad", # = atan(0.2)*4 GeV = pt of ~800 MeV
     #"/gps/ang/mintheta 1 rad", # = pi is down the beamline
     # number of particles
     #"/gps/number "+str(nPart), # shoots at same location
]

ele_500e4000_5deg20=[
     "/gps/particle e-",
     "/gps/pos/type Plane",
     "/gps/direction 0 0 1",
     # Mono energy
     # "/gps/ene/mono 4 GeV",
     # Linear energy
     "/gps/ene/type Lin",
     "/gps/ene/min 0.5 GeV",
     "/gps/ene/max 4 GeV",
     "/gps/ene/gradient 0",
     "/gps/ene/intercept 1",
     # circle
     # "/gps/pos/shape Circle",
     # "/gps/pos/centre 0 0 240 mm",
     # "/gps/pos/radius 50 mm", #50 or 150
     # Square
     "/gps/pos/shape Square",
     "/gps/pos/centre 0 0 0 mm",
     "/gps/pos/halfx 1 mm",
     "/gps/pos/halfy 1 mm",
     # angles
     # "/gps/ang/type cos",
     "/gps/ang/type iso",
     "/gps/ang/mintheta 2.8 rad", # about 20 deg
     "/gps/ang/maxtheta 3.05 rad", # about 5 deg
     #"/gps/ang/mintheta 1 rad", # = pi is down the beamline
     # number of particles
     #"/gps/number "+str(nPart), # shoots at same location
]

ele_0e500_0deg20=[
     "/gps/particle e-",
     "/gps/pos/type Plane",
     "/gps/direction 0 0 1",
     # Mono energy
     # "/gps/ene/mono 4 GeV",
     # Linear energy
     "/gps/ene/type Lin",
     "/gps/ene/min 0 GeV",
     "/gps/ene/max 0.5 GeV",
     "/gps/ene/gradient 0",
     "/gps/ene/intercept 1",
     # circle
     # "/gps/pos/shape Circle",
     # "/gps/pos/centre 0 0 240 mm",
     # "/gps/pos/radius 50 mm", #50 or 150
     # Square
     "/gps/pos/shape Square",
     "/gps/pos/centre 0 0 0 mm",
     "/gps/pos/halfx 1 mm",
     "/gps/pos/halfy 1 mm",
     # angles
     # "/gps/ang/type cos",
     "/gps/ang/type iso",
     "/gps/ang/mintheta 2.8 rad", # about 20 deg
     "/gps/ang/maxtheta 3.1415 rad", # about 5 deg
     #"/gps/ang/mintheta 1 rad", # = pi is down the beamline
     # number of particles
     #"/gps/number "+str(nPart), # shoots at same location
]

neu_50e4000_pt0=[
     "/gps/particle neutron",
     "/gps/pos/type Plane",
     "/gps/direction 0 0 1",
     # Mono energy
     # "/gps/ene/mono 4 GeV",
     # Linear energy
     "/gps/ene/type Lin",
     "/gps/ene/min 0.05 GeV",
     "/gps/ene/max 4 GeV",
     "/gps/ene/gradient 0",
     "/gps/ene/intercept 1",
     # circle
     # "/gps/pos/shape Circle",
     # "/gps/pos/centre 0 0 240 mm",
     # "/gps/pos/radius 50 mm", #50 or 150
     # Square
     "/gps/pos/shape Square",
     "/gps/pos/centre 0 0 0 mm",
     "/gps/pos/halfx 1 mm",
     "/gps/pos/halfy 1 mm",
     # angles
     # "/gps/ang/type cos",
     "/gps/ang/type iso",
     "/gps/ang/mintheta 3.1415 rad",
    #"/gps/ang/mintheta 1 rad", # = pi is down the beamline
     # number of particles
     #"/gps/number "+str(nPart), # shoots at same location
]

pro_50e4000_pt0=[
     "/gps/particle proton",
     "/gps/pos/type Plane",
     "/gps/direction 0 0 1",
     # Mono energy
     # "/gps/ene/mono 4 GeV",
     # Linear energy
     "/gps/ene/type Lin",
     "/gps/ene/min 0.05 GeV",
     "/gps/ene/max 4 GeV",
     "/gps/ene/gradient 0",
     "/gps/ene/intercept 1",
     # circle
     # "/gps/pos/shape Circle",
     # "/gps/pos/centre 0 0 240 mm",
     # "/gps/pos/radius 50 mm", #50 or 150
     # Square
     "/gps/pos/shape Square",
     "/gps/pos/centre 0 0 0 mm",
     "/gps/pos/halfx 1 mm",
     "/gps/pos/halfy 1 mm",
     # angles
     # "/gps/ang/type cos",
     "/gps/ang/type iso",
     "/gps/ang/mintheta 3.1415 rad",
    #"/gps/ang/mintheta 1 rad", # = pi is down the beamline
     # number of particles
     #"/gps/number "+str(nPart), # shoots at same location
]


pi_50e4000_60deg=[
     "/gps/particle pi-",
     "/gps/pos/type Plane",
     "/gps/direction 0 0 1",
     # Mono energy
     # "/gps/ene/mono 4 GeV",
     # Linear energy
     "/gps/ene/type Lin",
     "/gps/ene/min 0.05 GeV",
     "/gps/ene/max 4 GeV",
     "/gps/ene/gradient 0",
     "/gps/ene/intercept 1",
     # circle
     # "/gps/pos/shape Circle",
     # "/gps/pos/centre 0 0 240 mm",
     # "/gps/pos/radius 50 mm", #50 or 150
     # Square
     "/gps/pos/shape Square",
     "/gps/pos/centre 0 0 0 mm",
     "/gps/pos/halfx 1 mm",
     "/gps/pos/halfy 1 mm",
     # angles
     # "/gps/ang/type cos",
     "/gps/ang/type iso",
     "/gps/ang/mintheta 2.1 rad",
    #"/gps/ang/mintheta 1 rad", # = pi is down the beamline
     # number of particles
     #"/gps/number "+str(nPart), # shoots at same location
]
