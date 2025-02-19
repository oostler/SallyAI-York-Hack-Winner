# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Set environment variables for your credentials
# Read more at http://twil.io/secure

account_sid = "ACd66395185dc089fe6e791805abb1f646"
auth_token = "f1f342988239a716d657533a631d7967"
client = Client(account_sid, auth_token)

call = client.calls.create(
  url="https://4b60-199-212-64-225.ngrok-free.app/incoming-call",
  to="+14168032939",
  from_="+19893403576"
)

print(call.sid)