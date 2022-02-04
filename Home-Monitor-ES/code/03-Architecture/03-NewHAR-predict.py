def predict(self, data):
    """ Returns values predicted """
    array = self.MODEL.predict(data)
    result = array[0]
    answer = np.argmax(result)
    return self.CLASSES[answer]