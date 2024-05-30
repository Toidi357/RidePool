import AsyncStorage from '@react-native-async-storage/async-storage';

export const saveToken = async (token) => {
  try {
    const tokenString = JSON.stringify(token);
    await AsyncStorage.setItem('token', tokenString);
    console.log("SAVED TOKEN TO 'token' KEY:", tokenString);
  } catch (error) {
    console.error("Error saving token:", error);
  }
};

export const fetchToken = async () => {
  try {
    const tokenString = await AsyncStorage.getItem('token');
    console.log("Fetched token string:", tokenString);
    return tokenString ? JSON.parse(tokenString) : null;
  } catch (error) {
    console.error("Error fetching token:", error);
    return null;
  }
};
