import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Button, Text } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import RideList from "../components/RideList"

import { sendAuthorizedPostRequest } from '../components/sendRequest'

export default function App() {



  const [error, setError] = useState(null);
  const [currentRides, setCurrentRides] = useState(null)
  const [historyRides, setHistoryRides] = useState(null)

  const navigation = useNavigation();

  const reloadScreen = () => {
    navigation.replace('My Ridepools'); // This will unmount and remount the screen
  };

  useEffect(() => {
    
    getUserRides('current', setCurrentRides);
    getUserRides('history', setHistoryRides);

  }, []);


  const getUserRides = async (time, setWhat) => {
    try {
      const response = await sendAuthorizedPostRequest(`/users/rides`, {
        'time' : time
      })
      console.log("USER RIDES: ")
      console.log(response.data)

      response.data['created_rides'].forEach(ride => {
        ride.relationship = 'creator';
      });
      response.data['member_rides'].forEach(ride => {
        ride.relationship = 'member';
      });
      response.data['requested_rides'].forEach(ride => {
        ride.relationship = 'requester';
      });
      let _ = response.data['created_rides'].concat(response.data['member_rides'])
      setWhat(_.concat(response.data['requested_rides']))


    } catch (err) {
      console.error('Error fetching data IN MY RIDEPOOLS:', err);
      setError(err);
    }
  };


  return (
    <ScrollView style={styles.container}>
      <Button title="Reload Screen" onPress={reloadScreen}>refresh</Button>
      <View style={styles.listContainer}>
        <Button mode="outlined" onPress={() => navigation.navigate('Create Ridepool')}>
          Create Ridepool
        </Button>
      </View>   

      <View style={styles.listContainer}>
        <Text style={styles.label}>Active</Text>
      </View>

      {currentRides != null ? <RideList displayRelationship = {true} rides = {currentRides}/> : (<></>)}

      <View style={styles.listContainer}>
        <Text style={styles.label}>History</Text>
      </View>

      {historyRides != null ? <RideList displayRelationship = {true} rides = {historyRides}/> : (<></>)}
      
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