import React, { useState } from 'react';
import { View, StyleSheet, Text, ScrollView } from 'react-native';
import { TextInput, Button, Switch } from 'react-native-paper';
import axios from 'axios';
import { SERVER_IPV4_ADDRESS, SERVER_PORT } from '../../config' // '@env';
import DateTimePickerModal from 'react-native-modal-datetime-picker';
import LocationInput from '../components/LocationInput';
import { useNavigation } from '@react-navigation/native';


import { sendAuthorizedPostRequest } from "../components/sendRequest"
import { Picker } from '@react-native-picker/picker';

const RidepoolForm = ({ route }) => {
  const { setCurrentRides } = route.params;

  const [pickupLocation, setPickupLocation] = useState({});
  const [destinationLocation, setDestinationLocation] = useState({});
  const [minDate, setMinDate] = useState(new Date());
  const [maxDate, setMaxDate] = useState(new Date());
  const [pickupRadiusThreshold, setPickupRadiusThreshold] = useState('');
  const [dropoffRadiusThreshold, setDropoffRadiusThreshold] = useState('');
  const [sortBy, setSortBy] = useState('');
  const [isMinPickerVisible, setMinPickerVisible] = useState(false);
  const [isMaxPickerVisible, setMaxPickerVisible] = useState(false);
  // const [isPrivate, setIsPrivate] = useState(false);

  const showMinPicker = () => setMinPickerVisible(true);
  const hideMinPicker = () => setMinPickerVisible(false);

  const showMaxPicker = () => setMaxPickerVisible(true);
  const hideMaxPicker = () => setMaxPickerVisible(false);

  

  const handleConfirmMin = (date) => {
    setMinDate(date);
    hideMinPicker();
  };

  const handleConfirmMax = (date) => {
    setMaxDate(date);
    hideMaxPicker();
  };

  const navigation = useNavigation();
  const handleSubmission = async () => {
    console.log('Form submitted!')

    form = {
      'desiredPickupLongitude': pickupLocation['lon'],
      'desiredPickupLatitude': pickupLocation['lat'],
      'desiredDestinationLongitude': destinationLocation['lon'],
      'desiredDestinationLatitude': destinationLocation['lat'],
      'pickupRadiusThreshold': pickupRadiusThreshold,
      'dropoffRadiusThreshold': dropoffRadiusThreshold,
      'minDate': minDate,
      'maxDate': maxDate,
      'sortBy': sortBy
    }

    try {
      response = await sendAuthorizedPostRequest('/searchrides', form)
      setCurrentRides(response.data)
      navigation.navigate('Search for Ridepools')

    } catch (err) {
      console.log(err)
    }
  }

  return (
    <ScrollView style={styles.container}>
      <LocationInput label="Desired Pickup Location" onLocationSelected={setPickupLocation} />
      <TextInput
        label="Acceptable Pickup Range (in miles)"
        value={pickupRadiusThreshold}
        onChangeText={text => setPickupRadiusThreshold(text)}
        keyboardType="decimal-pad"
        style={{ marginBottom: 10 }}
      />
      <LocationInput label="Desired Destination" onLocationSelected={setDestinationLocation} />
      <TextInput
        label="Acceptable Destination Range (in miles)"
        value={dropoffRadiusThreshold}
        onChangeText={text => setDropoffRadiusThreshold(text)}
        keyboardType="decimal-pad"
        style={{ marginBottom: 10 }}
      />
      <View style={styles.dateTimeContainer}>
        <Text style={styles.label}>Earliest pickup time:</Text>
        <Text style={styles.dateTime}>{minDate.toLocaleString()}</Text>
        <Button
          mode="outlined"
          onPress={showMinPicker}
          style={{ marginBottom: 10 }}
        >
          Set Earliest Pickup Time
        </Button>
      </View>
      <DateTimePickerModal
        isVisible={isMinPickerVisible}
        mode="datetime"
        onConfirm={handleConfirmMin}
        onCancel={hideMinPicker}
      />
      
      <View style={styles.dateTimeContainer}>
        <Text style={styles.label}>Latest pickup time:</Text>
        <Text style={styles.dateTime}>{maxDate.toLocaleString()}</Text>
        <Button
          mode="outlined"
          onPress={showMaxPicker}
          style={{ marginBottom: 10 }}
        >
          Set Latest Pickup Time
        </Button>
      </View>
      <DateTimePickerModal
        isVisible={isMaxPickerVisible}
        mode="datetime"
        onConfirm={handleConfirmMax}
        onCancel={hideMaxPicker}
      />

    <Picker
      selectedValue={sortBy}
      onValueChange={(itemValue, itemIndex) => setSortBy(itemValue)}
      style={{ marginBottom: 10 }}
    >
      <Picker.Item label="Sort By Pickup Time" value="pickup_time" />
      <Picker.Item label="Sort By Distance to Pickup Location" value="pickup_location" />
      <Picker.Item label="Sort By Distance to Destination Location" value="destination_location" />
    </Picker>
      
      <Button mode="contained" onPress={() => handleSubmission()}>
        Submit Search
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
