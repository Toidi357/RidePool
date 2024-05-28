# RidePool
 RidePool 35L Final Project

 ## First-Time Run:
 

 ### Frontend
 
 - get ipv4 address (ipconfig or ifconfig commands)
 
 - replace SERVER_IPV4_ADDRESS variable in ridepool_mobile_frontend/.env

 - install expo go on your mobile device

 `cd ridepool_mobile_frontend`

 `npm install`
 
 `npx expo start`
 
 - make sure your mobile phone & PC are on the same network
 
 - use the expo go app to scan the QR code that pops up

 Alternatively, if expo doesn't connect, you can try:

 - entering the "exp:" link manually (might look like exp://172.23.53.2:8081)

 - running `npx expo --tunnel` and entering the "exp:" link (might look like exp://njzgnlw-anonymous-8081.exp.direct)
 
 ### Backend:
 
 `cd backend`
 
 `python app.py`


 ## For Developers

 Do all the above steps, but also instll SQLite browser and set it to point to backend/instance/myinstance.db to view the database while the app is running. 

 If you've made a change to the database models in model.py and would like to update the database:
 
 `flask db migrate -m "message"`

 `flask db upgrade`

 ## Development Notes
 We are using token based authentication since we are a SPA \
 On successful /login and /register requests, you will get returned a token like this: \
 "auth_token": "ey......" \
 This token must be saved somewhere throughout in the frontend and used in all subsequent authenticated API calls \
 You must have this request header to be authenticated: \
 "Authorization": "Bearer {token}" \
 \
 When developing on the backend, I've created a function called check_authenication that automatically checks if the user is authenticated and if they are, then it returns a User object \
 When developing protected API endpoints, add this code at the beginning:
 ```
 try:
    user = check_authentication(request)
 except Unauthorized as e:
    return jsonify({"message": e.args[0]})
 ```
 Now the `user` variable has all the information you'll need
