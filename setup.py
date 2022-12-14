import glob, os
import cv2
import numpy as np
from PIL import Image
from generate_labels import pascal_voc_to_yolo
import PySimpleGUI as sg
from tqdm import tqdm
import datetime as dt

global coordinates, fore_g_image, dir_fg_img, list_
coordinates = []
date_time_id = dt.datetime.now().strftime("%d%m%y%H%M")

def popup_wind():
    layout = [[sg.Text('Select the Object Image to be placed')],
                    # [sg.Combo(['1','2' ], size=(20, 1), key='object', default_value='0-non')],
                    [sg.InputText(key='inputxt'), sg.FileBrowse()],
                    [sg.Button('Ok'), sg.Button('Cancel')]
                    ]
    # Set dimensions of the window
    window = sg.Window('Select the object to be placed', layout)
    event, values = window.read()
    window.close()
    # print(values)
    dir_ = values['inputxt']
    return dir_

list_ = []
def coordinates_on_click(event, x, y, flags, params, offset=5, object_dim=[40,40]):

    if event == cv2.EVENT_LBUTTONUP:
        font = cv2.FONT_HERSHEY_SIMPLEX

        cv2.putText(bg_images_, str('.'), (x-5,y), font, 1, (255, 255, 0), 6)
        cv2.imshow('image', bg_images_)
        list_.append(dir_fg_img)
        
        coord = [x,y]
        coordinates.append(coord)

    if event == cv2.EVENT_MBUTTONDOWN:
        cv2.destroyWindow('image')

# remove folder if exists
if os.path.exists('Dataset/Dataset_output'):
    os.system('rm -r Dataset/Dataset_output')
os.mkdir('Dataset/Dataset_output')

def destroy_window(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.destroyWindow('image')
        

imgs = glob.glob('Dataset/background_images/*.jpg')
for bg_images in tqdm(imgs):
    base_name = os.path.basename(bg_images)
    bg_images_ = cv2.imread(bg_images)
    H, W, _ = bg_images_.shape
    # print('Base Image:',base_name,'==> Dim =',H,'x',W)
    cv2.imshow('image', bg_images_)
    cv2.setMouseCallback('image', destroy_window)
    cv2.waitKey(0)
    

    dir_fg_img = popup_wind()
    cv2.imshow('image', bg_images_)
    cv2.setMouseCallback('image', coordinates_on_click)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    txt_file = open('Dataset/Dataset_output/'+date_time_id+'_syn_'+base_name[:-4]+'.txt', 'w')
    for jj in list_:
        fg_base_name = os.path.basename(jj)
        fg_img = Image.open(jj, 'r').convert("RGBA")
        bg_img = Image.open(bg_images, 'r').convert("RGBA")
            
        obj_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        obj_img.paste(bg_img, (0, 0))
        
        i = 0
        for img, obj_pt in zip(list_, coordinates):
            fg_image_size = cv2.imread(img)
            fh, fw, f_ = fg_image_size.shape
            img_ = Image.open(img, 'r').convert("RGBA") 
            
            obj_img.paste(img_, (obj_pt[0] - (fw//2), obj_pt[1] - (fh//2)), mask=img_)
            obj_img_cv = np.array(obj_img)
            obj_img_cv_bgr = cv2.cvtColor(obj_img_cv, cv2.COLOR_RGB2BGR)
            
            bb = pascal_voc_to_yolo(obj_pt[0] - (fw//2) , obj_pt[1] - (fh//2),
                                    obj_pt[0]+ (fw//2), obj_pt[1]+ (fh//2),
                                    W, H)
            
            # print(dir_fg_img.split('/')[-2][0])
            class_no = dir_fg_img.split('/')[-2][0]

            
            txt_file = open('Dataset/Dataset_output/'+date_time_id+'_syn_'+base_name[:-4]+'.txt', 'a')
            txt_file.write(class_no+' '+str(bb[0])+' '+str(bb[1])+' '+str(bb[2])+' '+str(bb[3])+'\n')
            txt_file.close()

        cv2.imwrite('Dataset/Dataset_output/'+date_time_id+'_syn_'+base_name,obj_img_cv_bgr)
        coordinates.clear()
        list_.clear()
