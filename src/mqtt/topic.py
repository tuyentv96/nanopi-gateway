class deviceTopic(object):
    def __init__(self, appID= "", devID= "", type = "", field = ""):
        self.appID = appID
        self.devID = devID
        self.type = type
        self.field = field

def parseDeviceTopic(topic):
    if len(topic)<7:
        return None

    param=topic.split("/")
    if len(param)<4:
        return None

    # check param empty
    for p in param:
        if p=="":
            return None

    x=deviceTopic()
    x.appID=param[0]
    x.obj=param[1]
    x.devID=param[2]
    x.type=param[3]
    x.field=param[4]

    return x

def generateTopic(devTopic):
    return devTopic.appID+"/"+"device"+"/"+devTopic.devID+"/"+devTopic.type+"/"+devTopic.field