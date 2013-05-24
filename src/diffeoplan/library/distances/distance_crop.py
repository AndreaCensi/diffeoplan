from contracts import contract
from diffeo2dds import (UncertainImageDistance,
    get_conftools_uncertain_image_distances)
from diffeoplan import logger

__all__ = ['DistanceCrop']

class DistanceCrop(UncertainImageDistance):

    @contract(top='>=0,<0.5', right='>=0,<0.5',
              bottom='>=0,<0.5', left='>=0,<0.5',
              distance='str')
    def __init__(self, top, right, bottom, left, distance):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
        self.id_distance = distance
        
        l = get_conftools_uncertain_image_distances()
        self.other = l.instance(self.id_distance)
        self.other2 = l.instance(self.id_distance)
        
    def distance(self, y0, y1):
        y0c = y0.crop(self.top, self.right, self.bottom, self.left)
        y1c = y1.crop(self.top, self.right, self.bottom, self.left)
        d = self.other2.distance(y0, y1)  # TMP
        dc = self.other.distance(y0c, y1c)
        logger.debug('Distance cropped %s: %s  uncropped %s' % 
                     (self.id_distance, dc, d))
        return dc
