import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { TextInput, Button, Switch, Card, Text, Title, Paragraph } from 'react-native-paper';
import axios from 'axios';
import { SERVER_IPV4_ADDRESS, SERVER_PORT } from '@/config.js'; // from '@env';
import { useNavigation } from '@react-navigation/native';

import { saveToken, fetchToken } from '../components/token_funcs';

export default function App({ username }) {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState ('');

  const handleSaveToken = async (token) => {
    await saveToken(newToken);
  };
 
  const handleFetchToken = async () => {
    return await fetchToken();
  };

  const handleQueryChange = (text) => {
    setQuery(text);
  };

  const handleQuerySubmit = async() => {
    try{
      let token = await handleFetchToken();
      console.log(`requesting http://${SERVER_IPV4_ADDRESS}:${SERVER_PORT}/gemini_query`);
      const res = await axios.post(`http://${SERVER_IPV4_ADDRESS}:${SERVER_PORT}/gemini_query`, { query }, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      setResponse(res.data.response);
      console.log(response);
    } catch (error) {
      console.error('Error querying Gemini AI: ', error);
      setResponse('An error occurred. Please try again.');
    }
  };


  return (
    <ScrollView style={styles.container}>
      <View style={styles.inputContainer}>
        <TextInput
          label="Enter your question"
          value={query}
          onChangeText={handleQueryChange}
          style={styles.input}
        />
        <Button mode ="contained" onPress={handleQuerySubmit} styles ={styles.button}>
          Submit
        </Button>
      </View>
      {response && (
        <Card style={styles.responseCard}>
          <Card.Content>
            <Title>Response</Title>
            <Paragraph>{response}</Paragraph>
          </Card.Content>
        </Card>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: "#ffffff"
  },
  inputContainer: {
    marginBottom: 20,
    marginTop: 70, 
  },
  input: {
    marginBottom: 10,
  },
  button: {
    marginTop: 20,
  },
  listContainer: {
    marginBottom: 10,
  },
  responseCard: {
    marginTop: 20,
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