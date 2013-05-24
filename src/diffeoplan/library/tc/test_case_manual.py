from diffeoplan import TestCase

from diffeoplan.utils import assert_allclose
from diffeoplan.configuration.master import get_dp_config
from diffeo2dds.configuration.config_master import get_conftools_discdds
from diffeo2dds.model.uncertain_image import UncertainImage
from diffeo2dds.analysis.pil_utils import resize


def ManualMotion(tcname, id_discdds, id_image, planstring):
    # Get a random plan
    config = get_dp_config()
    discdds = get_conftools_discdds().instance(id_discdds)
    
    rgb = config.images.instance(id_image)
    shape = discdds.get_shape()
    image1 = resize(rgb, shape[1], shape[0])       
    assert_allclose(image1.shape[:2], shape)

    chars = "abcdefghilmnopqrst"
    char2int = dict([(c, i) for i, c in enumerate(chars)])
    plan = tuple(map(char2int.__getitem__, planstring))
    
    
    # predict the result
    y0 = UncertainImage(image1)
    y1 = discdds.predict(y0, plan)
    
    tc = TestCase(id_tc=tcname, id_discdds=id_discdds,
                  y0=y0, y1=y1, true_plan=plan)

    return tc


def FromImages(tcname, id_discdds, image1, image2, true_plan=None):
    discdds = get_conftools_discdds().instance(id_discdds)
    shape = discdds.get_shape()

    config = get_dp_config()
    rgb1 = config.images.instance(image1)
    image1 = resize(rgb1, shape[1], shape[0])       
    assert_allclose(image1.shape[:2], shape)

    rgb2 = config.images.instance(image2)
    image2 = resize(rgb2, shape[1], shape[0])       
    assert_allclose(image2.shape[:2], shape)

    
    # predict the result
    y0 = UncertainImage(image1)
    y1 = UncertainImage(image2)
    
    tc = TestCase(id_tc=tcname, id_discdds=id_discdds,
                  y0=y0, y1=y1, true_plan=true_plan)

    return tc
    
