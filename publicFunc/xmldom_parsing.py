
def xmldom(collection, data):
    data_dict = {}
    for i in data:
        data_dict['{}'.format(i)] = collection.getElementsByTagName("{}".format(i))[0].childNodes[0].data

    return data_dict






