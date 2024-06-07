import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { TextInput, Button, Card, Title, Paragraph } from 'react-native-paper';

import LoadingSpinner from '../components/loadingSpinner';
import { sendAuthorizedPostRequest } from '../components/sendRequest';

export default function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState ('');
  const [loading, setLoading] = useState(false);

  const handleQueryChange = (text) => {
    setQuery(text);
  };

  const handleQuerySubmit = async() => {
    try{
      setLoading(true)
      const response = await sendAuthorizedPostRequest('/gemini_query', { query })
      setResponse(response.data.response);
      console.log(response);
      setLoading(false)
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
        {loading ? (
          <Button mode="contained" styles ={styles.button}>
            <LoadingSpinner />
          </Button>
        ) : (
          <Button mode="contained" onPress={handleQuerySubmit} styles ={styles.button}>
            Ask Gemini
          </Button>
        )}
        
      </View>
      {response && (
        <Card style={styles.responseCard}>
          <Card.Content>
            <Title>Response: </Title>
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
  responseCard: {
    marginTop: 20,
  },
});