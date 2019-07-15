print("\n\n","::::::::::::: Validing requirements :::::::::::::::")

"""
conda create -n HM
y
conda activate HM
conda install pillow cudnn matplotlib cudatoolkit h5py opencv
y
conda install flask flask-jsonpify flask-sqlalchemy flask-restful
y
conda install tensorflow tensorflow-base tensorflow-gpu tensorboard
y
conda install keras keras-base keras-gpu
y

"""
try:
    import tensorflow as tf
    version = tf.__version__
    major, minor, small = version.split('.')
    status = "Wrong. Need 1.12.0 or above."
    if int(major) * 10000 + int(minor) * 100 + int(small) >= 11200:
        status = "OK."
    print("\tTensorflow:", version, "\tStatus:", status)
except:
    print("\tExec conda install tensorflow")

try:
    import tensorflow.keras as k
    version = k.__version__
    major, minor, small = version.replace('-tf','').split('.')
    status = "Wrong. Need 2.1.6 or above."
    if int(major) * 10000 + int(minor) * 100 + int(small) >= 20106:
        status = "OK."
    print("\tKeras:", version, "\tStatus:", status)
except:
    print("\tExec conda install keras")

try:
    import PIL as p
    version = p.__version__
    major, minor, small = version.split('.')
    status = "Wrong. Need 5.2.0 or above."
    if int(major) * 10000 + int(minor) * 100 + int(small) >= 50200:
        status = "OK."
    print("\tPIL / Pillow:", version, "\tStatus:", status)
except:
    print("\tExec conda install pillow")

"""
# Devices in this machine
sess = tf.Session()
devices = sess.list_devices()
for d in devices:
    print("\t"+d.name)
"""