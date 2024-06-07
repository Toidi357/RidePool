import React, { useState, useEffect } from 'react';
import { Text, ScrollView, StyleSheet, Button } from 'react-native';
import { TextInput } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';

import { sendAuthorizedGetRequest, sendAuthorizedPostRequest } from '../components/sendRequest';

const EditProfileForm = ({ route }) => {
  const { username } = route.params;
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');

  const navigation = useNavigation();

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const response = await sendAuthorizedGetRequest('/profile')
        const { first_name, last_name, phone_number, email } = response.data;
        setFirstName(first_name);
        setLastName(last_name);
        setPhoneNumber(phone_number);
        setEmail(email);
      } catch (err) {
        console.error('Error fetching profile data:', err);
        setError('Failed to fetch profile data');
      }
    };

    fetchUserProfile();
  }, []);

  const handleUpdateProfile = async () => {
    try {
      await sendAuthorizedPostRequest('/profile/update', {
        first_name: firstName,
        last_name: lastName,
        phone_number: phoneNumber,
        email: email,
      })
      alert('Profile updated successfully!');
      navigation.navigate('Profile'); 
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('Failed to update profile');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <TextInput
        label="First Name"
        value={firstName}
        onChangeText={setFirstName}
        style={styles.input}
      />
      <TextInput
        label="Last Name"
        value={lastName}
        onChangeText={setLastName}
        style={styles.input}
      />
      <TextInput
        label="Phone Number"
        value={phoneNumber}
        onChangeText={setPhoneNumber}
        style={styles.input}
        keyboardType="phone-pad"
      />
      <TextInput
        label="Email"
        value={email}
        onChangeText={setEmail}
        style={styles.input}
        keyboardType="email-address"
      />
      {error && <Text style={styles.error}>{error}</Text>}
      <Button
        title="Save Changes"
        onPress={handleUpdateProfile}
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  input: {
    marginBottom: 10,
  },
  error: {
    color: 'red',
    marginTop: 10,
  },
});

export default EditProfileForm;
