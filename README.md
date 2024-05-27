# RidePool
 RidePool 35L Final Project

 ## First-Time Run:
 

 ### Frontend
 
 - get ipv4 address (ipconfig or ifconfig commands)
 
 - replace PC_IPV4_ADDRESS variable in ridepool_mobile_frontend/.env

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

 Do all the above steps, but also instll SQL Lite browser and set it to point to backend/instance/myinstance.db to view the database while the app is running. 
