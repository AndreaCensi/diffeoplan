from diffeo2dds import get_conftools_uncertain_images, get_conftools_discdds
from diffeoplan import TestCase


def ManualMotion(tcname, id_discdds, id_image, planstring):
    discdds = get_conftools_discdds().instance(id_discdds)
    shape = discdds.get_shape()
    
    images = get_conftools_uncertain_images()
    y0 = images.instance(id_image).resize(shape)
    
    
    chars = "abcdefghilmnopqrst"
    char2int = dict([(c, i) for i, c in enumerate(chars)])
    plan = tuple(map(char2int.__getitem__, planstring))
    
    
    # predict the result
    y1 = discdds.predict(y0, plan)
    
    tc = TestCase(id_tc=tcname, id_discdds=id_discdds,
                  y0=y0, y1=y1, true_plan=plan)

    return tc


def FromImages(tcname, id_discdds, image1, image2, true_plan=None):
    discdds = get_conftools_discdds().instance(id_discdds)
    shape = discdds.get_shape()

    images = get_conftools_uncertain_images()
    
    y0 = images.instance(image1).resize(shape)
    y1 = images.instance(image2).resize(shape)
    
    tc = TestCase(id_tc=tcname, id_discdds=id_discdds,
                  y0=y0, y1=y1, true_plan=true_plan)

    return tc
    
