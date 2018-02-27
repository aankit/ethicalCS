import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate('ethicalcs-53ebd-firebase-adminsdk-82aqh-d113bb8823.json')
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://ethicalcs-53ebd.firebaseio.com'
})

