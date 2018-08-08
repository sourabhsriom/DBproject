from dateutil.parser import _timelex, parser

import datetime


#question = input("enter your date :")
p = parser()
info = p.info

def timetoken(token):
  try:
    float(token)
    return True
  except ValueError:
    pass
  return any(f(token) for f in (info.jump,info.weekday,info.month,info.hms,info.ampm,info.pertain,info.utczone,info.tzoffset))

def timesplit(input_string):
  batch = []
  for token in _timelex(input_string):
    if timetoken(token):
      if info.jump(token):
        continue
      batch.append(token)
    else:
      if batch:
        yield " ".join(batch)
        batch = []
  if batch:
    yield " ".join(batch)

def returnDates(question):
    dates = []

    for item in timesplit(question):
        print (item)
        dd = p.parse(item).strftime('%Y-%m-%d')
        dates.append(dd)
    return dates

#print (returnDates(question)[0])
