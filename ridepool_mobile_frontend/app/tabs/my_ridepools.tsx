import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, Button } from 'react-native';
import axios from 'axios';
import { SERVER_IPV4_ADDRESS, SERVER_PORT } from '@env';
import { useNavigation } from '@react-navigation/native';

export default function App({ username }) {
  const [error, setError] = useState(null);

  const navigation = useNavigation();

  return (
    <View style={styles.container}>
        <Button title = "Create Ridepool" onPress = {() => navigation.navigate('Create Ridepool')}/>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
