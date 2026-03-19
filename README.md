simple flask app to display who is fronting from simplyplural in a 320x240 iframe, used on my personal website.

how to deploy, i'd hope:
1. declare the following environment variables
   SP_API_TOKEN
   SP_PRIVACY_BUCKET
   SP_USERID
   SP_ALLOWED_ORIGINS

2. pip install -r requirements.txt
   note: there are too many requirements because i use my pip install for other things and i am too greedy to clean it
3. run the server, or `python server.py`

it is setup to only expose the name, pronouns, and custom status as concisely as possible, while protecting the user id, bucket id, and api token. this app was inspired by fronters.cc but redesigned for personal use.
