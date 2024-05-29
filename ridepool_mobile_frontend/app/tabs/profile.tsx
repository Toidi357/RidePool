import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import axios from 'axios';
import { SERVER_IPV4_ADDRESS, SERVER_PORT } from '@/config.js' // from '@env';

export default function App({ username }) {
  const [error, setError] = useState(null);

  return (
    <View style={styles.container}>
        <Text>profile</Text>
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
