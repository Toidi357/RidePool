# RidePool
 RidePool 35L Final Project

 ### Mappings of Group Members to Emails used in Commits

 Minh Trinh (MT-GoCode)

 tminh.us@gmail.com

 Guatam Nair (gnair11)
 
 gnair11@g.ucla.edu
 
 Kevin Lu (Toidi357)
 
 toidi357@gmail.com
 
 Harsh Patil (HarshPatil32)
 
 patilsharsh@gmail.com

 Aditya Gupta (agupta2025)

 agupta25@g.ucla.edu



 # First-Time Run:

 `git clone https://github.com/agupta2025/RidePool.git`

 `cd RidePool`

 ## Frontend
 
 - Get your computer's ipv4 address (ipconfig or ifconfig commands)
 
 - replace SERVER_IPV4_ADDRESS variable in `ridepool_mobile_frontend/config.js`

 - Install Expo Go on your mobile device

 Run these commands in terminal:

 `cd ridepool_mobile_frontend`

 `npm install`
 
 `npx expo start`
 
 - Make sure your mobile phone & PC are on the same network. Personal network will work much better than UCLA WIFI or eduroam. Starting a hotspot on your phone and joining with your PC can also work well.
 
 - use the Expo Go app to scan the QR code that pops up after running `npx expo start`

 ## Backend:

 In a separate terminal, please run this. We used Python version >= 3.7
 
 `cd backend`

 `python3 -m venv myenv`

 `source myenv/bin/activate` (or for Windows, `myenv\Scripts\activate`)

 `pip install -r requirements.txt`
 
 `python app.py`

 ## Playing around / testing

 Please follow along to [this demo video](https://drive.google.com/file/d/11wAhnkslSvtbh3b5Xt075JrLjpx4Moht/view?usp=drive_link)

 There should already be some sample data and users to play around with. You can log in with username "u1", password "p1", to get started.

 ### This is the end of instructions to run the app. Below are more troubleshooting tips and info for developers.

 ## Other solutions if Expo doesn't load (Expo can be finicky, it's not our fault.)

  Alternatively, if expo doesn't connect, you can try:

 - entering the "exp:" link manually (might look like exp://172.23.53.2:8081)

 - running `npx expo --tunnel` and entering the "exp:" link (might look like exp://njzgnlw-anonymous-8081.exp.direct), but this probably means the backend won't function

 - When you scan the QR code, half the time the expo app doesn't get the request and just times out.

 - this is often because of networking issues (subnet configurations).

 - To confirm it is indeed a networking problem, get the IP address of your phone, then do `ping < IP >` from your PC. If it can't reach, then this is indeed a networking problem. Hah.

 ### Networking fixes.
 
 - It may help to move both devices to a personal/Home network. UCLA Wifi and eduroam have historically been pretty bad.

 - if you don't have access to a personal network, then:

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
 
 # For Developers

 Do all the above steps, but also instll SQLite browser and set it to point to backend/instance/myinstance.db to view the database while the app is running. 

 If you've made a change to the database models in model.py and would like to update the database:
 
 `flask db migrate -m "message"`

 `flask db upgrade`

 ## Token-based Authentication

 ### How it works
 We are using token based authentication since we are a SPA \
 On successful /login and /register requests, you will get returned a token like this: \
 "auth_token": "ey......" \
 This token must be saved somewhere throughout in the frontend and used in all subsequent authenticated API calls (it also expires in 1 hour) \
 You must have this request header to be authenticated: \
 "Authorization": "Bearer {token}" \
 \

 ### Backend
 When developing on the backend, I've created a function called check_authenication that automatically checks if the user is authenticated and if they are, then it returns a User object \
 When developing protected API endpoints, add this code at the beginning:
 ```
 try:
    user = app.config.check_authentication(request)
 except app.config.Unauthorized as e:
    return jsonify({"message": e.args[0]})
 ```
 Now the `user` variable has all the information you'll need \
 \

 ### Frontend
 
 To use the token in your components, do this:

 ```javascript
 
 import { saveToken, fetchToken } from '../components/token_funcs';

 export default function App() {

  const handleSaveToken = async (token) => {
    await saveToken(newToken);
  };

  const handleFetchToken = async () => {
    return await fetchToken();
  };


  const getUserRides = async (time, setWhat) => {
    let token = await handleFetchToken();

    // make backend requests here...

   ```

 In the frontend, at the end of every request, there needs to be a check to see if the token is expiring, if it is, call `GET /refresh_token` which will return a new `auth_token`