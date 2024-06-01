import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { TextInput, Button, Switch, Card, Text, Title, Paragraph } from 'react-native-paper';
import axios from 'axios';
import { SERVER_IPV4_ADDRESS, SERVER_PORT } from '@/config.js'; // from '@env';
import { useNavigation } from '@react-navigation/native';
import RideList from "../components/RideList"

import { saveToken, fetchToken } from '../components/token_funcs';

import { sendAuthorizedPostRequest } from "../components/sendRequest"

export default function App() {

  const handleSaveToken = async (token) => {
    await saveToken(newToken);
  };

  const handleFetchToken = async () => {
    return await fetchToken();
  };

  const [error, setError] = useState(null);
  const [currentRides, setCurrentRides] = useState(null)

  const navigation = useNavigation();


  return (
    <ScrollView style={styles.container}>
      <View style={styles.listContainer}>
        <Button mode="outlined" onPress={() => navigation.navigate('Filter Ridepools', {
          setCurrentRides: setCurrentRides,
        })}>
          Filter Ridepools
        </Button>
      </View>   

      <View style={styles.listContainer}>
        <Text style={styles.label}>Search Results</Text>
      </View>

      {currentRides != null ? <RideList rides = {currentRides}/> : (<></>)}

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: "#ffffff"
  },
  listContainer: {
    marginBottom: 10,
  },
  label: {
    fontWeight: 'bold',
    marginBottom: 5,
    fontSize: 20
  },
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
    justifyContent: 'space-between', 
  },
  dateTime: {
    marginBottom: 10,
  },
});