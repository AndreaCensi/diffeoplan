from comptests.registrar import comptests_for_all
from diffeoplan import (get_conftools_planning_algos, get_conftools_batches,
    get_conftools_testcases)
 
# 
#                                                  
# for_all_images = fancy_test_decorator(lister=lambda: testconfig().images.keys(),
#             arguments=lambda id_image: (id_image, testconfig().images.instance(id_image)),
#             attributes=lambda id_image: dict(image=id_image),
#             debug=True)
# 
# for_all_dds = fancy_test_decorator(lister=lambda: testconfig().discdds.keys(),
#             arguments=lambda id_dds: (id_dds, testconfig().discdds.instance(id_dds)),
#             attributes=lambda id_dds: dict(dds=id_dds),
#             debug=True)
# 
# 
# @for_all_symdiffeos
# def check_symdiffeo_dummy(id_symdiffeo, symdiffeo):
#     pass
# 
# 
# @for_all_dds
# def check_dds_dummy(id_dds, dds):
#     pass
# 
# 
# @for_all_images
# def check_image_dummy(id_image, image):
#     pass


for_all_planning_algos = comptests_for_all(get_conftools_planning_algos())
for_all_test_cases = comptests_for_all(get_conftools_testcases())
for_all_batches = comptests_for_all(get_conftools_batches())


@for_all_planning_algos
def check_planning_algo(id_ob, ob):
    pass

@for_all_test_cases
def check_testcase(id_ob, ob):
    pass

@for_all_batches
def check_batch(id_ob, ob):
    pass
