import React, { useState } from 'react';
import { View, StyleSheet, Text } from 'react-native';
import { TextInput, Button } from 'react-native-paper';
import DateTimePickerModal from 'react-native-modal-datetime-picker';
import LocationInput from '../components/LocationInput';

const RidepoolForm = () => {
  const [pickupRadius, setPickupRadius] = useState('');
  const [description, setDescription] = useState('');
  const [earliestPickupTime, setEarliestPickupTime] = useState(new Date());
  const [destinationRadius, setDestinationRadius] = useState('');
  const [latestPickupTime, setLatestPickupTime] = useState(new Date());
  const [isEarliestPickerVisible, setEarliestPickerVisible] = useState(false);
  const [isLatestPickerVisible, setLatestPickerVisible] = useState(false);

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

  return (
    <View style={styles.container}>
      <LocationInput label="Pickup location" onLocationSelected={(loc) => console.log(loc)} />
      <TextInput
        label="Pickup radius (miles)"
        value={pickupRadius}
        onChangeText={text => setPickupRadius(text)}
        keyboardType="decimal-pad"
        style={{ marginBottom: 10 }}
      />
      <LocationInput label="Destination location" onLocationSelected={(loc) => console.log(loc)} />
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
        label="Description"
        value={description}
        onChangeText={text => setDescription(text)}
        style={{ marginBottom: 10 }}
        multiline = {true}
      />
      
      <Button mode="contained" onPress={() => console.log('Form submitted!')}>
        Create Ridepool
      </Button>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  dateTimeContainer: {
    marginBottom: 10,
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
