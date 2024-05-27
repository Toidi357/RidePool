import React, { useEffect, useState } from 'react';
import { ScrollView, View, StyleSheet } from 'react-native';
import { Card, Text, Title, Paragraph } from 'react-native-paper';
import axios from 'axios';

const reverseGeocode = async (latitude, longitude) => {
  try {
    const response = await axios.get(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=14&addressdetails=1`
    );
    return response.data.display_name.split(',')[0]; // Get the first part of the display name
  } catch (error) {
    console.error('Error reverse geocoding:', error);
    return `${latitude}, ${longitude}`; // Fallback to coordinates if reverse geocoding fails
  }
};

const RideCard = ({ ride, displayRelationship }) => {
  const [pickupLocation, setPickupLocation] = useState('');
  const [destinationLocation, setDestinationLocation] = useState('');

  useEffect(() => {
    const fetchLocations = async () => {
      const pickup = await reverseGeocode(ride.pickupLatitude, ride.pickupLongitude);
      const destination = await reverseGeocode(ride.destinationLatitude, ride.destinationLongitude); // Assuming destination coordinates exist
      setPickupLocation(pickup);
      setDestinationLocation(destination);
    };

    if (ride) {
      fetchLocations();
    }
  }, [ride]);

  if (!ride) {
    return null;
  }

  let status;
  if (displayRelationship) {
    if (ride.relationship === "creator") {
        status = "Created by You";
    } else if (ride.relationship === "member") {
        status = "You're a member";
    } else if (ride.relationship === "requesting") {
        status = "Request Pending";
    }
    }

  return (
    <Card style={styles.card}>
      <Card.Content>
        <Text style = {styles.locations}>{pickupLocation} to {destinationLocation}</Text>
        {displayRelationship ? (<Paragraph style={styles.italics}>{status}</Paragraph>) : (<></>) }
        <Paragraph>{ride.members.length} / {ride.maxGroupSize} riders</Paragraph>
        <Paragraph>Description: {ride.description.substring(0, 50)}...</Paragraph>
      </Card.Content>
    </Card>
  );
};

export default RideList = ({ rides, displayRelationship }) => {
  return (
    <>
      {rides != null ? (
        <ScrollView style={styles.container}>
          {rides.map(ride => (
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
  }
});
