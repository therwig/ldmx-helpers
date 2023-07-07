tag2part={
    'ele':'e-',
    'piM':'pi-',
    'pro':'proton',
    'neu':'neutron',
    'pho':'gamma',
}

class gpsCmds(object):
    def __init__(self, p='e-', eRange=(0.1,4), thetaRangeDeg=(0,20), zpos='1'):
        self.particle = p
        self.eRange = eRange
        self.thetaRangeDeg = thetaRangeDeg
        self.zpos=zpos
    def getCmds(self):
        PI = 3.1415
        radNearBeam = PI - PI/180. * self.thetaRangeDeg[0]
        radFarBeam  = PI - PI/180. * self.thetaRangeDeg[1]
        cmds=[
            "/gps/particle "+self.particle,
            "/gps/pos/type Plane",
            "/gps/direction 0 0 1",
            # Mono energy
            # "/gps/ene/mono 4 GeV",
            # Linear energy
            "/gps/ene/type Lin",
            "/gps/ene/min {} GeV".format(self.eRange[0]),
            "/gps/ene/max {} GeV".format(self.eRange[1]),
            "/gps/ene/gradient 0",
            "/gps/ene/intercept 1",
            # circle
            # "/gps/pos/shape Circle",
            # "/gps/pos/centre 0 0 240 mm",
            # "/gps/pos/radius 50 mm", #50 or 150
            # Square
            "/gps/pos/shape Square",
            "/gps/pos/centre 0 0 {} mm".format(self.zpos),
            "/gps/pos/halfx 1 mm",
            "/gps/pos/halfy 1 mm",
            # angles
            # "/gps/ang/type cos",
            "/gps/ang/type iso",
            "/gps/ang/mintheta {} rad".format(radFarBeam),
            "/gps/ang/maxtheta {} rad".format(radNearBeam),
            # number of particles
            #"/gps/number "+str(nPart), # shoots at same location
        ]
        return cmds
