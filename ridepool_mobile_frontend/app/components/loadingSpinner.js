import React from 'react';
import { View, Image, StyleSheet } from 'react-native';

const LoadingSpinner = () => {
  return (
    <View style={styles.container}>
      <Image
        source={require('../../assets/loading.gif')}
        style={styles.spinner}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.3)', 
  },
  spinner: {
    width: 33,
    height: 33,
  },
});

export default LoadingSpinner;