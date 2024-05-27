import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import axios from 'axios';
import { PC_IPV4_ADDRESS } from '@env';

export default function Login({ changeLogin }) {
  const [error, setError] = useState(null);
  const [isLogin, setIsLogin] = useState(true);

  const [form, setForm] = useState({
    username: '',
    password: '',
    firstName: '',
    lastName: '',
    email: '',
    phoneNumber: ''
  });

  const handleInputChange = (name, value) => {
    setForm({ ...form, [name]: value });
  };

  const submitLogin = async () => {
    /*
    some sample data

    {
        'username': 'A',
        'password': 'B',
      }

    
    */

    try {
      const response = await axios.post(`http://${PC_IPV4_ADDRESS}/login`, form, {
        headers: {
          'Content-Type': 'application/json',
        }
      });
  
      console.log(response.data);
      changeLogin(true); 
    } catch (error) {
      console.error('Error during login:', error);
    }
  };

  const submitRegister = async () => {
    try {
      const response = await axios.post(`http://${PC_IPV4_ADDRESS}/register`, form, {
        headers: {
          'Content-Type': 'application/json',
        }
      });
  
      console.log(response.data);
      changeLogin(true); 
    } catch (error) {
      console.error('Error during login:', error);
    }
  };

  useEffect(() => { // the same as componentDidMount
    const testConnect = async () => {
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

    testConnect();
  }, []);

  const Form_component = () => (
    <View style={styles.container}>
      <View style={styles.formContainer}>
        {isLogin ? (
          <View>
            <Text style={styles.title}>Login</Text>
            <TextInput
              style={styles.input}
              placeholder="Username"
              value={form.username}
              onChangeText={(text) => handleInputChange('username', text)}
            />
            <TextInput
              style={styles.input}
              placeholder="Password"
              secureTextEntry
              value={form.password}
              onChangeText={(text) => handleInputChange('password', text)}
            />
            <Button title="Submit" onPress={() => submitLogin()} />
          </View>
        ) : (
          <View>
            <Text style={styles.title}>Sign Up</Text>
            <TextInput
              style={styles.input}
              placeholder="Username"
              value={form.username}
              onChangeText={(text) => handleInputChange('username', text)}
            />
            <TextInput
              style={styles.input}
              placeholder="Password"
              secureTextEntry
              value={form.password}
              onChangeText={(text) => handleInputChange('password', text)}
            />
            <TextInput
              style={styles.input}
              placeholder="First Name"
              value={form.firstName}
              onChangeText={(text) => handleInputChange('firstName', text)}
            />
            <TextInput
              style={styles.input}
              placeholder="Last Name"
              value={form.lastName}
              onChangeText={(text) => handleInputChange('lastName', text)}
            />
            <TextInput
              style={styles.input}
              placeholder="Email"
              value={form.email}
              onChangeText={(text) => handleInputChange('email', text)}
            />
            <TextInput
              style={styles.input}
              placeholder="Phone Number"
              value={form.phoneNumber}
              onChangeText={(text) => handleInputChange('phoneNumber', text)}
            />
            <Button title="Submit" onPress={() => submitRegister()} />
          </View>
        )}
        <View style={styles.switchContainer}>
          <Button
            color="#000000"
            title={isLogin ? "New User? Click to Sign Up." : "Returning User? Click to Login."}
            onPress={() => setIsLogin(!isLogin)}
          />
        </View>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      {error ? (
        <Text>Error: Network Connection</Text>
      ) : (
        <Form_component/>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  formContainer: {
    width: 300,
    padding: 16,
    borderRadius: 10,
    backgroundColor: '#f0f0f0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 2,
    elevation: 5,
  },
  title: {
    fontSize: 24,
    marginBottom: 16,
    textAlign: 'center',
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 12,
    paddingLeft: 8,
    borderRadius: 5,
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
  },
});
