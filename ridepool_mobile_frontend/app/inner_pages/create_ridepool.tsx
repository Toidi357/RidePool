import React, { useState } from 'react';
import { View, StyleSheet, Text, ScrollView } from 'react-native';
import { TextInput, Button, Switch } from 'react-native-paper';
import axios from 'axios';
import { SERVER_IPV4_ADDRESS, SERVER_PORT } from '@env';
import DateTimePickerModal from 'react-native-modal-datetime-picker';
import LocationInput from '../components/LocationInput';
import { useNavigation } from '@react-navigation/native';

const RidepoolForm = () => {
  const [pickupRadius, setPickupRadius] = useState('');
  const [description, setDescription] = useState('');
  const [pickupLocation, setPickupLocation] = useState({});
  const [destinationLocation, setDestinationLocation] = useState({});
  const [earliestPickupTime, setEarliestPickupTime] = useState(new Date());
  const [destinationRadius, setDestinationRadius] = useState('');
  const [maxGroupSize, setMaxGroupSize] = useState('');
  const [latestPickupTime, setLatestPickupTime] = useState(new Date());
  const [isEarliestPickerVisible, setEarliestPickerVisible] = useState(false);
  const [isLatestPickerVisible, setLatestPickerVisible] = useState(false);
  const [isPrivate, setIsPrivate] = useState(false);

  const showEarliestPicker = () => setEarliestPickerVisible(true);
  const hideEarliestPicker = () => setEarliestPickerVisible(false);

  const showLatestPicker = () => setLatestPickerVisible(true);
  const hideLatestPicker = () => setLatestPickerVisible(false);

  const handleConfirmEarliest = (date) => {
    setEarliestPickupTime(date);
    hideEarliestPicker();
  };

  const handleConfirmLatest = (date) => {
    setLatestPickupTime(date);
    hideLatestPicker();
  };

  const navigation = useNavigation();
  const handleSubmission = async () => {
    console.log('Form submitted!')

    form = {
      'pickupLongitude': pickupLocation['lat'],
      'pickupLatitude': pickupLocation['lon'],
      'destinationLongitude': destinationLocation['lat'],
      'destinationLatitude': destinationLocation['lon'],
      'pickupThreshold': pickupRadius,
      'destinationThreshold': destinationRadius,
      'earliestPickupTime': earliestPickupTime,
      'latestPickupTime': latestPickupTime,
      'maxGroupSize': maxGroupSize,
      'private': isPrivate,
      'description': description,
      // 'preferredApps':
    }

    try {
      const response = await axios.post(`http://${SERVER_IPV4_ADDRESS}:${SERVER_PORT}/rides`, form, {
        headers: {
          'Content-Type': 'application/json',
        }
      });
      console.log(response)

      
      navigation.navigate('My Ridepools')

    } catch (err) {
      console.error('Error fetching data:', err);
    }



  }

  return (
    <ScrollView style={styles.container}>
      <LocationInput label="Pickup location" onLocationSelected={setPickupLocation} />
      <TextInput
        label="Pickup radius (miles)"
        value={pickupRadius}
        onChangeText={text => setPickupRadius(text)}
        keyboardType="decimal-pad"
        style={{ marginBottom: 10 }}
      />
      <LocationInput label="Destination location" onLocationSelected={setDestinationLocation} />
      <TextInput
        label="Destination radius (miles)"
        value={destinationRadius}
        onChangeText={text => setDestinationRadius(text)}
        keyboardType="decimal-pad"
        style={{ marginBottom: 10 }}
      />
      <View style={styles.dateTimeContainer}>
        <Text style={styles.label}>Earliest pickup time:</Text>
        <Text style={styles.dateTime}>{earliestPickupTime.toLocaleString()}</Text>
        <Button
          mode="outlined"
          onPress={showEarliestPicker}
          style={{ marginBottom: 10 }}
        >
          Set Earliest Pickup Time
        </Button>
      </View>
      <DateTimePickerModal
        isVisible={isEarliestPickerVisible}
        mode="datetime"
        onConfirm={handleConfirmEarliest}
        onCancel={hideEarliestPicker}
      />
      
      <View style={styles.dateTimeContainer}>
        <Text style={styles.label}>Latest pickup time:</Text>
        <Text style={styles.dateTime}>{latestPickupTime.toLocaleString()}</Text>
        <Button
          mode="outlined"
          onPress={showLatestPicker}
          style={{ marginBottom: 10 }}
        >
          Set Latest Pickup Time
        </Button>
      </View>
      <DateTimePickerModal
        isVisible={isLatestPickerVisible}
        mode="datetime"
        onConfirm={handleConfirmLatest}
        onCancel={hideLatestPicker}
      />
      
      <TextInput
        label="Max Group Size"
        value={maxGroupSize}
        onChangeText={text => setMaxGroupSize(text)}
        style={{ marginBottom: 10 }}
        keyboardType="decimal-pad"
      />

      <TextInput
        label="Description"
        value={description}
        onChangeText={text => setDescription(text)}
        style={{ marginBottom: 10 }}
      />

      <View style={styles.switchContainer}>
        <Text style={styles.label}>Private:</Text>
        <Switch label = "heck" value={isPrivate} onValueChange={value => setIsPrivate(value)} />
      </View>
      
      <Button mode="contained" onPress={() => handleSubmission()}>
        Create Ridepool
      </Button>
      <View
        style={{ marginBottom: 10, height: 10 }}
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  dateTimeContainer: {
    marginBottom: 10,
  },
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
    justifyContent: 'space-between', 
  },
  label: {
    fontWeight: 'bold',
    marginBottom: 5,
  },
  dateTime: {
    marginBottom: 10,
  },
});

export default RidepoolForm;
