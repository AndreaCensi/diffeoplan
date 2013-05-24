from conf_tools.checks import check_necessary
from conf_tools.code_desc import check_generic_code_desc


def check_valid_image_config(spec):
    check_generic_code_desc(spec, 'image')


def check_valid_image(x):
    pass  # TODO


def check_valid_diffeo_config(spec):
    check_generic_code_desc(spec, 'diffeo')


def check_valid_diffeo(x):
    pass  # TODO


def check_valid_discdds_config(spec):
    # TODO
    pass



def check_valid_set(x):
    necessary = [ 
                  ('id', str),
                  ('desc', str),
                  ('algorithms', list),
                  ('testcases', list),
              ]
    check_necessary(x, necessary)

