import AsyncStorage from '@react-native-async-storage/async-storage';

export const saveToken = async (token) => {
  try {
    const tokenString = JSON.stringify(token);
    await AsyncStorage.setItem('token', tokenString);
  } catch (error) {
    console.error("Error saving token:", error);
  }
};

export const fetchToken = async () => {
  try {
    const tokenString = await AsyncStorage.getItem('token');
    return tokenString ? JSON.parse(tokenString) : null;
  } catch (error) {
    console.error("Error fetching token:", error);
    return null;
  }
};

export const clearToken = async () => {
  try {
    await AsyncStorage.removeItem('token');
    console.log("Token cleared successfully");
  } catch (error) {
    console.error("Error clearing token:", error);
  }
};

export const storeUserDetails = async (userDetails) => {
  try {
    await AsyncStorage.setItem('userDetails', JSON.stringify(userDetails));
    console.log("User details saved successfully");
  } catch (error) {
    console.error("Error saving user details:", error);
  }
};

export const clearUserDetails = async () => {
  try {
    await AsyncStorage.removeItem('userDetails');
    console.log("User details cleared successfully");
  } catch (error) {
    console.error("Error clearing user details:", error);
  }
};

export const getUserDetails = async () => {
  try {
    const userDetails = await AsyncStorage.getItem('userDetails');
    return userDetails ? JSON.parse(userDetails) : null;
  } catch (error) {
    console.error("Error retrieving user details:", error);
    return null;
  }
};