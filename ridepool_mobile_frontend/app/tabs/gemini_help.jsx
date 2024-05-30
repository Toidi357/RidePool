import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { TextInput, Button, Switch, Card, Text, Title, Paragraph } from 'react-native-paper';
import axios from 'axios';
import { SERVER_IPV4_ADDRESS, SERVER_PORT } from '@/config.js'; // from '@env';
import { useNavigation } from '@react-navigation/native';

export default function App({ username }) {


  return (
    <ScrollView style={styles.container}>

    </ScrollView>
  );
}

const styles = StyleSheet.create({
});