import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import axios from 'axios';

import { PC_IPV4_ADDRESS } from '@env';

export default function App() {
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://${PC_IPV4_ADDRESS}/test`);
        
        // On the backend, there is a simple get endpoint that returns this object
        // {"response": "connection successful"}
        // here's how to unpack it: 

        console.log(response.data); // {"response": "connection successful"}
        console.log(response.data["response"]) // connection successful

      } 
      catch (err) {
        console.error('Error fetching data:', err);
        setError(err);
      }
    };

    fetchData();
  }, []);

  return (
    <View style={styles.container}>
      {error ? (
        <Text>Error: Unable to connect to the backend.</Text>
      ) : (
        <Text>Insert login screen</Text>
      )}
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
