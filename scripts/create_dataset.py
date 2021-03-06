#!/bin/env python

from scripts.helpers import (
    write_file,
    image2dicom,
    get_name
)

from random import choice
from glob import glob
import os

here = os.getcwd()

# Dcm2k provided in this image https://www.github.com/pydicom/singularity-dicom
dcm = "%s/dcm.img" %(here)
if not os.path.exists(dcm):
    print('You must generate the dcm.img with dcm2tk to run the conversion first.')
    print('See https://www.github.com/pydicom/singularity-dicom for instructions.')
    sys.exit(1)

# These raw datasets are in wordfish standard format
# https://www.github.com/vsoch/wordfish-standard
image_folders = glob('_original/*')
output_folder = "%s/_datasets" %here
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Keep a lookup dictionary for image folders and images inside
lookup = dict()

# iterate over folders, and generate dicom datasets
for image_folder in image_folders:
    series = glob('%s/images/*' %image_folder)
    cookie_id = os.path.basename(image_folder)
    print("Processing %s" %cookie_id)
    lookup[cookie_id] = []
    patient_name = get_name()
    patient_sex = choice(["M","F"])
    cookie_output = os.path.join(output_folder,cookie_id)
    if not os.path.exists(cookie_output):
        os.mkdir(cookie_output)
    image_output = os.path.join(cookie_output,'images')
    if not os.path.exists(image_output):
        os.mkdir(image_output)
    for image_series in series:
        images = glob('%s/*.jpg' %image_series)
        for image in images:
            image_id = os.path.basename(image).replace('.jpg','')
            lookup[cookie_id].append(image_id)
            dcm_file = os.path.join(image_output,"%s.dcm" %image_id)
            image2dicom(input_image=image,
                        output_dcm=dcm_file,
                        singularity=dcm,
                        patient_sex=patient_sex,
                        patient_name=patient_name,
                        patient_id=cookie_id)
            

for cookie_name, images in lookup.items():

    # images.txt to describe all images
    template='---\ntype: images\ndataset-id: "%s"\nimages:' %(cookie_name)
    for image in images:
        template = "%s\n  - %s.dcm" %(template,image)
    template = '%s\n---' %template
    output_file = "%s/%s/images.txt" %(output_folder,cookie_name)
    write_file(output_file,template)

    # metadata,txt for cookie
    template = '---\ntype: entity\ndataset-id: "%s"\nhidden: false\n\nincludes:\n  - images\n---' %(cookie_name)
    output_file = "%s/%s/metadata.txt" %(output_folder,cookie_name)
    write_file(output_file,template)

