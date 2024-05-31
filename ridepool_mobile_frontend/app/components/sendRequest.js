import { saveToken, fetchToken } from './token_funcs';
import { SERVER_IPV4_ADDRESS, SERVER_PORT } from '../../config';
import { jwtDecode } from "jwt-decode";
import axios from 'axios';

const BASEURL = `http://${SERVER_IPV4_ADDRESS}:${SERVER_PORT}`

async function getRefreshToken(token) {
    let url = BASEURL + "/refresh_token"

    const response = await axios.get(url, {headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    }});
    return response
}

export const sendAuthorizedGetRequest = async (url, headers = {}) => {
    let token = await fetchToken()

    // check if token is expired or within 30 minutes so refresh
    const decoded = jwtDecode(token);
    var currentTime = new Date().getTime();
    currentTime /= 1000; // convert to seconds
    var difference = decoded.exp - currentTime;

    if (difference <= 0) {
        throw Error('Token Expired')
    }

    if (difference <= 30 * 60) { // if difference is within 30 minutes
        const response = await getRefreshToken(token);
        await saveToken(response.data.auth_token);
        token = response.data.auth_token;
    }

    headers['Authorization'] = `Bearer ${token}`
    headers['Content-Type'] = 'application/json';

    const response = await axios.get(BASEURL + url, {headers: headers})

    return response
}

export const sendAuthorizedPostRequest = async (url, headers, body) => {
    let token = await fetchToken()

    // check if token is expired or within 30 minutes so refresh
    const decoded = jwtDecode(token);
    var currentTime = new Date().getTime();
    currentTime /= 1000; // convert to seconds
    var difference = decoded.exp - currentTime;

    if (difference <= 0) {
        throw Error('Token Expired')
    }

    if (difference <= 30 * 60) { // if difference is within 30 minutes
        const response = await getRefreshToken(token);
        await saveToken(response.data.auth_token);
        token = response.data.auth_token;
    }

    headers['Authorization'] = `Bearer ${token}`
    headers['Content-Type'] = 'application/json';
    const response = await axios.post(BASEURL + url, body, {headers: headers});

    return response
}