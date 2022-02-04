def predict(self, data):
    """ Exec prediction to recognize an activity """
    x = cv2.cvtColor(data.data, cv2.COLOR_BGR2RGB)
    x = cv2.resize(x, (256, 256), interpolation = cv2.INTER_AREA)
    x = np.expand_dims(x, axis=0)

    array = self.MODEL.predict(x)
    result = array[0]
    answer = np.argmax(result)

    dataReturn = []
    auxData = '"t":"json", "idSource":"{}"'

    dataInf = Data()
    dataInf.source_type = self.ME_TYPE
    dataInf.source_name = self.ME_NAME
    dataInf.source_item = ''
    dataInf.data = self.CLASSES[answer]
    dataInf.aux = '{' + auxData.format(data.id) + '}'
    dataReturn.append(dataInf)

    return dataReturn