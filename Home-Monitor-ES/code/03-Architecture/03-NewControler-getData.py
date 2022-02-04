def getData(self, device):
    """ Returns a list of tuples like {controller, device, data} with data elements """

    cam = self.Devices[device["id"]]['objOfCapture']
    _, frame = cam.read()

    if frame is None:
        return []

    height = np.size(frame, 0)
    width = np.size(frame, 1)
    deviceName = Misc.hasKey(device, 'name', device["id"])

    dataReturn = []
    auxData = '"t":"{}", "ext":"{}", "W":"{}", "H":"{}"'
    
    if self.getRGB:
        dataRgb = Data()
        dataRgb.source_type = self.ME_TYPE
        dataRgb.source_name = 'CamController'
        dataRgb.source_item = deviceName
        dataRgb.data = frame
        dataRgb.aux = '{' + auxData.format('image', 'png', width, height) + '}'
        dataReturn.append(dataRgb)
    
    return dataReturn