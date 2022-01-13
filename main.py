import PySpin
import os
from set_camera_params import camera_params
from datetime import datetime

# Set the camera parameters
parameters = camera_params()
scene                 = parameters['scene']

gain                 = parameters['gain']
white_balance        = parameters['white_balance']
short_exposure       = parameters['short_exposure']
long_exposure        = parameters['long_exposure']
gamma                = parameters['gamma']

NUM_IMAGES           = parameters['NUM_IMAGES']

PATH_CAM1            = parameters['PATH_CAM1']
PATH_CAM2            = parameters['PATH_CAM2']

PATH_SHORT_EXPOSURE  = "short_exposure"                 # Relative Path
PATH_LONG_EXPOSURE   = "long_exposure"                  # Relative Path
PATH_RGB             = "RGB"                            # Relative Path
PATH_RAW             = "RAW"                            # Relative Path



f= open("metadata.txt","w+")
f.write(str(parameters))
f.close()

def configure_settings(cam):

    try:
        result = True

        # Configuring White Balance
        print("**Configuring White Balance**")
        if cam.BalanceWhiteAuto.GetAccessMode() == PySpin.RW:
            cam.BalanceWhiteAuto.SetValue(PySpin.BalanceWhiteAuto_Off)                # Disable Auto White balance
            print('Auto White Balance disabled...')

            cam.BalanceRatio.SetValue(white_balance)
            print('White Balance set to %s.\n' % white_balance)                       # Manually set the White Balance
            #print('Unable to disable White Balance Auto. Aborting...')
            #return False
        else:
            print('Unable to disable White Balance Auto in Monochrome Camera')
        


        # Configuring Gain
        print("**Configuring Gain**")
        if cam.GainAuto.GetAccessMode() == PySpin.RW:
            cam.GainAuto.SetValue(PySpin.GainAuto_Off)                                # Disable Auto Gain 
            print('Auto Gain disabled...')

            cam.Gain.SetValue(gain)
            print('Gain set to %s.\n' % gain)                                         # Manually set the Gain
            #print('Unable to disable Gain Auto. Aborting...')
            #return False
        else:
            print('Unable to disable Auto Gain in Monochrome Camera')

        
        # Configuring Gamma Correction
        print("**Configuring Gamma Correction**")
        if cam.Gamma.GetAccessMode() == PySpin.RW:
            cam.Gamma.SetValue(gamma)
            print('Gamma set to %s.' % gamma)                                         # Manually set Gamma
            #print('Unable to disable Gamma. Aborting...')
            #return False
        else:
            print('Unable to disable Gamma in Monochrome Camera')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result



def configure_exposure(cam, exposure_val):
    try:
        result = True
        
        global exposure
        exposure = exposure_val

        # Configuring Exposure
        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            print('Unable to disable automatic exposure. Aborting the program...')
            return False

        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)                            # Disable auto-exposure       
        print('Automatic exposure disabled...')

        if cam.ExposureTime.GetAccessMode() != PySpin.RW:
            print('Unable to set exposure time. Aborting...')
            return False

        exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_val)               # Manually set the exposure (in microseconds)
        cam.ExposureTime.SetValue(exposure_time_to_set)
        print('Shutter Time set to %s us.\n' % exposure_time_to_set)

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result
        



def configure_image_setting(cam):
    
    print('\n*** CONFIGURING IMAGE SETTINGS ***\n')

    try:
        result = True

        # Apply BayerRG8 pixel format
        if cam.PixelFormat.GetAccessMode() == PySpin.RW:
            cam.PixelFormat.SetValue(PySpin.PixelFormat_BayerRG8)
            print('Pixel format set to %s.' % cam.PixelFormat.GetCurrentEntry().GetSymbolic())

        else:
            print('Pixel format not available.')
            result = False

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result



def configure_trigger_setting(cam1, cam2):

    try:
        # Set up primary camera trigger
        cam1.LineSelector.SetValue(PySpin.LineSelector_Line2)
        cam1.V3_3Enable.SetValue(True)
 
        # Set up secondary camera trigger
        cam2.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        cam2.TriggerSource.SetValue(PySpin.TriggerSource_Line3)
        cam2.TriggerOverlap.SetValue(PySpin.TriggerOverlap_ReadOut)
        cam2.TriggerMode.SetValue(PySpin.TriggerMode_On)
 

        # Set acquisition mode to acquire a single frame, this ensures acquired images are sync'd since camera 2 and 3 are setup to be triggered
        cam1.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)
        cam2.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)

        result = True

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result



def acquire_images(cam1, cam2, filename):

    print('\n*** IMAGE ACQUISITION ***\n')

    try:
        result = True

        # Begin acquiring images
        cam2.BeginAcquisition()         # secondary cameras have to be started first so acquisition of primary camera triggers secondary cameras.
        cam1.BeginAcquisition()

        print('Acquiring images...')


        try:
            # Retrieve next received image and ensure image completion
            image_1 = cam1.GetNextImage()
            image_2 = cam2.GetNextImage()

            if image_1.IsIncomplete():
                print('Image incomplete with image status %d' % image_1.GetImageStatus())

            elif image_2.IsIncomplete():
                print('Image incomplete with image status %d' % image_2.GetImageStatus())

            else:
                # Convert image from camera 1 to RAW and RGB8
                image_1_raw = image_1.Convert(PySpin.PixelFormat_BayerRG8)
                image_1_rgb = image_1.Convert(PySpin.PixelFormat_RGB8)

                # Convert image from camera 2 to RAW and RGB8
                image_2_raw = image_2.Convert(PySpin.PixelFormat_BayerRG8)
                image_2_rgb = image_2.Convert(PySpin.PixelFormat_RGB8)

                # Create a unique filename
                filename_rgb = filename + '_RGBImage.png'
                filename_raw = filename + '_RAWImage.raw'

                # Save image
                if exposure==short_exposure:
                    image_1_raw.Save(os.path.join(PATH_CAM1, PATH_SHORT_EXPOSURE, PATH_RAW, filename_raw))    
                    print('Camera 1 RAW Image saved at %s' % str(os.path.join(PATH_CAM1, PATH_SHORT_EXPOSURE, PATH_RAW, filename_raw)))

                    image_1_rgb.Save(os.path.join(PATH_CAM1, PATH_SHORT_EXPOSURE, PATH_RGB, filename_rgb))
                    print('Camera 1 RGB Image saved at %s' % str(os.path.join(PATH_CAM1, PATH_SHORT_EXPOSURE, PATH_RGB, filename_rgb)))

                    image_2_raw.Save(os.path.join(PATH_CAM2, PATH_SHORT_EXPOSURE, PATH_RAW, filename_raw))    
                    print('Camera 2 RAW Image saved at %s' % str(os.path.join(PATH_CAM2, PATH_SHORT_EXPOSURE, PATH_RAW, filename_raw)))

                    image_2_rgb.Save(os.path.join(PATH_CAM2, PATH_SHORT_EXPOSURE, PATH_RGB, filename_rgb))
                    print('Camera 2 RGB Image saved at %s' % str(os.path.join(PATH_CAM2, PATH_SHORT_EXPOSURE, PATH_RGB, filename_rgb)))

                if exposure==long_exposure:
                    image_1_raw.Save(os.path.join(PATH_CAM1, PATH_LONG_EXPOSURE, PATH_RAW, filename_raw))    
                    print('Camera 1 RAW Image saved at %s' % str(os.path.join(PATH_CAM1, PATH_LONG_EXPOSURE, PATH_RAW, filename_raw)))

                    image_1_rgb.Save(os.path.join(PATH_CAM1, PATH_LONG_EXPOSURE, PATH_RGB, filename_rgb))
                    print('Camera 1 RGB Image saved at %s' % str(os.path.join(PATH_CAM1, PATH_LONG_EXPOSURE, PATH_RGB, filename_rgb)))

                    image_2_raw.Save(os.path.join(PATH_CAM2, PATH_LONG_EXPOSURE, PATH_RAW, filename_raw))    
                    print('Camera 2 RAW Image saved at %s' % str(os.path.join(PATH_CAM2, PATH_LONG_EXPOSURE, PATH_RAW, filename_raw)))

                    image_2_rgb.Save(os.path.join(PATH_CAM2, PATH_LONG_EXPOSURE, PATH_RGB, filename_rgb))
                    print('Camera 2 RGB Image saved at %s' % str(os.path.join(PATH_CAM2, PATH_LONG_EXPOSURE, PATH_RGB, filename_rgb)))

                
    

            # Release image - Images retrieved directly from the camera (i.e. non-converted images) 
            # need to be released in order to keep from filling the buffer.
            image_1.Release()
            image_2.Release()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        # End acquisition.
        # Ending acquisition appropriately helps ensure that devices clean up properly and do not need to be power-cycled to maintain integrity.
        cam1.EndAcquisition()
        cam2.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result










def main():

    f1= open("scene_value.txt","r+")
    counter= int(f1.read())
    f1.close()

    if counter<scene:
        counter=scene
        
        
    date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    filename=f"{date}_scene_{counter}"
    #print(filename)
    

    
    serial_1 = '21369579'
    serial_2 = '21369581'
    system = PySpin.System.GetInstance()

    cam_list = system.GetCameras()
    cam_1 = cam_list.GetBySerial(serial_1)
    cam_2 = cam_list.GetBySerial(serial_2)

    # Initialize cameras
    cam_1.Init()
    cam_2.Init()

    print("---------CONFIGURING CAMERA 1 SETTINGS----------")
    configure_settings(cam_1)
    configure_image_setting(cam_1)
    print("---------ENDING CONFIGURATION PROCESS---------")
    print()

    print("---------CONFIGURING CAMERA 2 SETTINGS----------")
    configure_settings(cam_2)
    configure_image_setting(cam_2)
    print("---------ENDING CONFIGURATION PROCESS---------")
    print()
    
    print("---------CONFIGURING TRIGGER SETTINGS----------")
    configure_trigger_setting(cam_1,cam_2)
    print("---------ENDING CONFIGURATION PROCESS----------")
    print()
    

    print("---------CONFIGURING CAMERA 1 SHORT EXPOSURE----")
    configure_exposure(cam_1, short_exposure)
    print("---------ENDING CONFIGURATION PROCESS----------")
    print()
    
    print("---------CONFIGURING CAMERA 2 SHORT EXPOSURE----")
    configure_exposure(cam_2, short_exposure)
    print("---------ENDING CONFIGURATION PROCESS----------")
    print()

    print("Acquiring short exposure images...")
    acquire_images(cam_1,cam_2, filename)
    print("Short exposure images acquisition ended")
    print()


    print("---------CONFIGURING CAMERA 1 LONG EXPOSURE----")
    configure_exposure(cam_1, long_exposure)
    print("---------ENDING CONFIGURATION PROCESS----------")
    print()
    
    print("---------CONFIGURING CAMERA 2 LONG EXPOSURE----")
    configure_exposure(cam_2, long_exposure)
    print("---------ENDING CONFIGURATION PROCESS----------")
    print()

    print("Acquiring long exposure images...")
    acquire_images(cam_1,cam_2, filename)
    print("Long exposure images acquisition ended")
    print()
    

    counter=counter+1
    f= open("scene_value.txt","w+")
    f.write(str(counter))
    f.close()
    
   
main()