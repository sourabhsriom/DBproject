import re
#question = input("How can I help you? ")

coin = ['coin in', 'coinin', 'coin-in']
hourly = ['hourly', 'hour']
def isCoinIn(question):
    #question = question.lower().split()
    for word in coin :

        if bool(re.search(word, question)):
            return True
    return False

def isHourly(question):
    for word in hourly :
        if bool(re.search(word,question)):
            return True
