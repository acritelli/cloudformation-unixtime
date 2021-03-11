import json
import requests
import crhelper

helper = crhelper.CfnResource()

@helper.create
@helper.update
def get_unix_time(event, _):

  # Attempt to make a request of the World Time API, bubbling up exceptions as needed
  # The crhelper will catch the exceptions and bubble up the message to CloudFormation
  try:
    request = requests.get(f"https://worldtimeapi.org/api/timezone/Europe/{event['ResourceProperties']['State']}.json")
  except requests.exceptions.RequestException as e:
    raise Exception('Something went wrong making a request to the World Time API.')
  except KeyError:
    raise Exception('No "state" key provided in invocation parameters.')
  except Exception as e:
    raise


  # Catch any errors sent to us by the API and bubble them up
  if 'error' in request.json():
    raise Exception ('Error making request to World Time API: ' + request.json()['error'])

  # Provide the time, assuming it came back in the response
  try:
    helper.Data['Unixtime'] = request.json()['unixtime']
  except KeyError:
    raise Exception('API response seems to have been malformed and is missing keys.')

  return

# Delete operations don't need to do anything to "delete" the unixtime resource
# so just pass here.
@helper.delete
def do_nothing(_, __):
    pass

def lambda_handler(event, context):
    helper(event, context)
