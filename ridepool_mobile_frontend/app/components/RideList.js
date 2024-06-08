import React, { useEffect, useState } from 'react';
import { ScrollView, View, StyleSheet } from 'react-native';
import { Card, Text, Title, Paragraph, Button, TouchableRipple } from 'react-native-paper';
import axios from 'axios';

import { sendAuthorizedPostRequest, sendAuthorizedGetRequest } from "../components/sendRequest"
import { useNavigation } from '@react-navigation/native';
import { fetchToken, setToken} from '../components/token_funcs';

const reverseGeocode = async (latitude, longitude) => {
  try {
    const response = await axios.get(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=14&addressdetails=1`
    );
    // console.log("OSM DATA FOR REVERSE GEOCODE")
    // console.log(response.data)
    return response.data.display_name.split(',')[0]; // Get the first part of the display name
  } catch (error) {
    console.error('Error reverse geocoding:', error);
    return `${latitude}, ${longitude}`; // Fallback to coordinates if reverse geocoding fails
  }
};

const RideCard = ({ ride, displayRelationship }) => {
  const [pickupLocation, setPickupLocation] = useState('');
  const [destinationLocation, setDestinationLocation] = useState('');
  const [active, setActive] = useState('')
  const [error, setError] = useState(null);
  const navigation = useNavigation();
  

  const handleFetchToken = async () => {
    return await fetchToken();
  };

  useEffect(() => {
    const fetchLocations = async () => {
      const pickup = await reverseGeocode(ride.pickupLatitude, ride.pickupLongitude);
      const destination = await reverseGeocode(ride.destinationLatitude, ride.destinationLongitude); // Assuming destination coordinates exist
      setPickupLocation(pickup);
      setDestinationLocation(destination);
    };

    const fetchStatus = async () => {
      let token = await handleFetchToken();
      try {
        console.log("Set the Status");
        const response = await sendAuthorizedGetRequest(`/rides/active/${ride.rideId}`);
        setActive(response.data.ride_status);
      } catch (err) {
        console.error('Error fetching getting ride status', err);
        setError(err.toString());
      }
    };

    if (ride) {
      fetchLocations();
      fetchStatus();
    }
  }, [ride]);

  if (!ride) {
    return null;
  }

  const handlePress = () => {
    if (active === 'active') {
      console.log("Active Rides Pressed");
      navigation.navigate('Active Rides', { rideId: ride.rideId, ride: ride });
    } else if (active === 'history') {
      console.log("History Rides Pressed");
      navigation.navigate('History Rides', { rideId: ride.rideId });
    }
  };

  let status;
  if (displayRelationship) {
    if (ride.relationship === "creator") {
        status = "Created by You";
    } else if (ride.relationship === "member") {
        status = "You're a member";
    } else if (ride.relationship === "requester") {
        status = "Request Pending";
    }
    }
    const [currentRides, setCurrentRides] = useState(null)
    const [requested, setRequested] = useState(ride.relationship === "requester");
    const onLeave = async (rideId) => {
      try {
        await sendAuthorizedPostRequest(`/rides/${rideId}/leave`);
      } catch (err) {
        console.error('Error leaving ride: ', err);
      }
    };

    const handleRequest = async(rideId) => {
      setRequested(true);
      try {
        await sendAuthorizedPostRequest(`/rides/${rideId}/join`);
      } catch (err) {
        console.error('Error requesting ride: ', err);
      }
    };

    const unRequest = async(rideId) => {
      setRequested(false);
      try {
        await sendAuthorizedPostRequest(`/rides/${rideId}/cancel_request`);
      } catch (err) {
        console.error('Error unrequesting: ', err);
      }
    }

  return (
    <TouchableRipple onPress={handlePress}>
      <Card style={styles.card}>
        <Card.Content>
          <Text style = {styles.locations}>{pickupLocation} to {destinationLocation}</Text>
          {displayRelationship ? (<Paragraph style={styles.italics}>{status}</Paragraph>) : (<></>) }
          <Paragraph>{ride.members.length} / {ride.maxGroupSize} riders</Paragraph>
          <Paragraph>Description: {ride.description.substring(0, 50)}...</Paragraph>
          {(ride.relationship !== "member" && ride.relationship !== "creator" && active !== "history") && (
            <View style={styles.buttonContainer}>
              {requested ? (
                <>
                  <Button mode="contained" disabled>
                    Requested
                  </Button>
                  <Button mode="contained" onPress={() => unRequest(ride.rideId)}>
                    Leave
                  </Button>
                </>
              ) : (
                <Button mode="contained" onPress={() => handleRequest(ride.rideId)}>
                  Request
                </Button>
              )}
            </View>
          )}
        </Card.Content>
        {(ride.relationship === "member" && active !== "history") && (
          <Card.Actions>
            <Button mode="contained" onPress={() => onLeave(ride.rideId)}>Leave</Button>
          </Card.Actions>
        )}
      </Card>
      </TouchableRipple>
  );
};

export default RideList = ({ rides, displayRelationship }) => {
  return (
    <>
      {rides != null ? (
        <ScrollView style={styles.container}>
          {rides
          .filter((ride, index, self) =>
            ride.relationship === "creator" ||
            self.findIndex(r => r.rideId === ride.rideId && r.relationship === "creator") === -1)
          .map(ride => (
            <RideCard key={ride.rideId} ride={ride} displayRelationship={displayRelationship} />
          ))}

        </ScrollView>
      ) : (
        <></>
      )}
    </>
  );
};
  
const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
  }, 
  locations: {
    fontSize: 15,
    fontWeight: 'bold'
  },
  listContainer: {
    marginBottom: 10,
  },
  card: {
    marginBottom: 10,
  },
  italics: {
    fontStyle: 'italic',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 10,
  }
});
