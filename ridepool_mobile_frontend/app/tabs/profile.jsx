import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, Button, ScrollView, StyleSheet } from 'react-native';
import { Card } from 'react-native-paper';
import { useNavigation, useFocusEffect, } from '@react-navigation/native';

import { clearToken } from '../components/token_funcs';
import { sendAuthorizedGetRequest } from '../components/sendRequest'
import { useAuth } from '../components/AuthContext';




export default function App(){
  const { isLoggedIn, setIsLoggedIn } = useAuth();
  const logOut = () => {
    setIsLoggedIn(false);
  }

  const [error, setError] = useState(null);
  const [username, setUsername] = useState(null);
  const [rating, setRating] = useState(null);
  const [phoneNumber, setPhoneNumber] = useState(null);
  const [email, setEmail] = useState(null);
  const [firstName, setFirstName] = useState(null);
  const [lastName, setLastName] = useState(null);
  const navigation = useNavigation();


  const fetchUserProfile = async () => {
    try {
      const response = await sendAuthorizedGetRequest('/profile');
      setUsername(response.data.username);
      setRating(response.data.average_rating);
      setPhoneNumber(response.data.phone_number);
      setEmail(response.data.email);
      setFirstName(response.data.first_name);
      setLastName(response.data.last_name);
    } catch (err) {
      console.error('Error fetching user profile:', err);
      setError(err.toString());
    }
  };

  useEffect(() => {
    fetchUserProfile();
  }, []);

  useFocusEffect(
    useCallback(() => {
      fetchUserProfile();
    }, [fetchUserProfile])
  );

  const handleLogout = async () => {
    try {
      const response = await sendAuthorizedGetRequest('/logout')
      console.log('Logout successful:', response.data.message);
      await clearToken();  // Clear the token from local storage or state
      logOut()
    } catch (err) {
      console.error('Logout failed:', err);
      setError('Failed to log out');
    }
  };
  

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.usernameText}>{username}</Text>
        <Text style={styles.ratingText}>Rating: {rating}</Text>
      </View>
      <Card style={styles.card}>
        <Card.Title 
          title="Personal Information" 
          titleStyle={styles.cardTitle} 
        />
        <Card.Content>
          <Text style={styles.infoText}>Name: {firstName} {lastName}</Text>
          <Text style={styles.infoText}>Phone: {phoneNumber}</Text>
          <Text style={styles.infoText}>Email: {email}</Text>
        </Card.Content>
        <Card.Actions>
          <Button title="Edit Profile" onPress={() => navigation.navigate('Edit Profile', { username })} />
          <Button title="Logout" onPress={handleLogout} color="#f00" />
        </Card.Actions>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  header: {
    marginBottom: 20,
  },
  usernameText: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  ratingText: {
    fontSize: 18,
    color: '#333',
  },
  card: {
    margin: 5,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  infoText: {
    fontSize: 16,
    marginBottom: 10,
  },
});