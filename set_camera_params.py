# Set camera parameters 

def camera_params():
    gain                 = 0
    white_balance        = 1.32
    short_exposure       = 100000.0               # in microseconds (us)
    long_exposure        = 10000000.0             # in microseconds (us)
    gamma                = 1

    PATH_CAM1            = "D:\dataset\cam1"     # Absolute Path
    PATH_CAM2            = "D:\dataset\cam2"     # Absolute Path
    scene = 1

    return {'gain':gain, 'white_balance':white_balance, 'short_exposure':short_exposure, 'long_exposure':long_exposure, 'gamma':gamma, 'PATH_CAM1':PATH_CAM1, 'PATH_CAM2':PATH_CAM2, 'scene':scene}



