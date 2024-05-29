# RidePool
 RidePool 35L Final Project

 # First-Time Run:

 ## Frontend
 
 - get ipv4 address (ipconfig or ifconfig commands)
 
 - replace SERVER_IPV4_ADDRESS variable in `ridepool_mobile_frontend/config.js`

 - install expo go on your mobile device

 `cd ridepool_mobile_frontend`

 `npm install`
 
 `npx expo start`
 
 - make sure your mobile phone & PC are on the same network
 
 - use the expo go app to scan the QR code that pops up

 Alternatively, if expo doesn't connect, you can try:

 - entering the "exp:" link manually (might look like exp://172.23.53.2:8081)

 - running `npx expo --tunnel` and entering the "exp:" link (might look like exp://njzgnlw-anonymous-8081.exp.direct), but this probably means the backend won't function

 ##### Other solutions if Expo doesn't load (Expo can be finicky, it's not our fault.)

 - When you scan the QR code, half the time the expo app doesn't get the request and just times out.

 - this is often because of networking issues (subnet configurations).

 - To confirm it is indeed a networking problem, get the IP address of your phone, then do `ping < IP >` from your PC. If it can't reach, then this is indeed a networking problem. Hah.

 ###### Networking fixes.
 
 1) It may help to move both devices to a personal/Home network. UCLA Wifi and eduroam have historically been pretty bad.

 2) if you don't have access to a personal network, then:

   1) Go to ZeroTier's official website 

   2) Make a new ZeroTier network, and set it to public.

   3) Download ZeroTier apps on both your phone and PC.

   4) Get the 16-digit ZeroTier network ID and join this network from both your PC and phone. Now your PC and phone should be on the same subnet.

   5) Try running `npx expo start` again. Try the QR code again with your phone.
   
   6) If the QR code still doesn't work (UGH), take note of the PORT that your app is running on. Most likely 8081.

   7) Run `ipconfig` and find the network interface labeled something like `Ethernet adapter ZeroTier One [e5cd7a9e1cf02620]` 

   8) Copy the IPv4 address from that network interface, NOT your PC's normal IP Address.

   9) while `npx expo start` is running, manually enter in Expo Go the link: `exp://< zerotier ip address >:< port from #6 >`

   10) Make sure to restart the backend too. In the `ridepool_mobile_frontend/config.js` file, put the ZeroTier IP Address in the SERVER_IPV4_ADDRESS variable

   11) Pray.
 
 ## Backend:
 
 `cd backend`
 
 `python app.py`


 # For Developers

 Do all the above steps, but also instll SQLite browser and set it to point to backend/instance/myinstance.db to view the database while the app is running. 

 If you've made a change to the database models in model.py and would like to update the database:
 
 `flask db migrate -m "message"`

 `flask db upgrade`

 ## Token-based Authentication
 We are using token based authentication since we are a SPA \
 On successful /login and /register requests, you will get returned a token like this: \
 "auth_token": "ey......" \
 This token must be saved somewhere throughout in the frontend and used in all subsequent authenticated API calls (it also expires in 1 hour) \
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
 Now the `user` variable has all the information you'll need \
 \
 In the frontend, at the end of every request, there needs to be a check to see if the token is expiring, if it is, call `GET /refresh_token` which will return a new `auth_token`
