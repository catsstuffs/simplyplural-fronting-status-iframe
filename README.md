simple flask app to display who is fronting from simplyplural in a 320x240 iframe, used on my personal website.

<img width="502" height="382" alt="image" src="https://github.com/user-attachments/assets/b786a76b-7407-4adc-a1f5-71a6b1d2a07d" />


how to deploy, i'd hope:
1. declare the following environment variables\
   SP_API_TOKEN - api token from simplyplural (do not hardcode this, do not set to anything besides readonly, do not share)\
   SP_PRIVACY_BUCKET - privacy bucket **id** that you would like to display. get bucket ids by calling the api\
   you can do this easily [here](https://docs.apparyllis.com/docs/api/get-all-members)\
   SP_USERID - your userid, not username.\
   SP_ALLOWED_ORIGINS - add all applicable website urls here to prevent cors issues.
3. pip install -r requirements.txt\
   *note: there may be an excess of requirements, i did not check this file.*
4. run the server, or `python server.py`

it is setup to only expose the name, pronouns, and custom status as concisely as possible, while protecting the user id, bucket id, and api token. it also includes rate-limiting, though it may need to be removed depending on the configuration.\
this app was inspired by fronters.cc but redesigned for personal use.
