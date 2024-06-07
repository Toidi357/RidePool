import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TextInput, Button, Alert, StyleSheet, ScrollView } from 'react-native';
import axios from 'axios';
import { SERVER_IPV4_ADDRESS, SERVER_PORT } from '@/config.js'
import { saveToken } from './components/token_funcs';
import { useAuth } from './components/AuthContext';

export default function Login() {
  const [error, setError] = useState(null);
  const [isLogin, setIsLogin] = useState(true);
  const { isLoggedIn, setIsLoggedIn } = useAuth();

  const usernameRef = useRef('');
  const passwordRef = useRef('');
  const firstNameRef = useRef('');
  const lastNameRef = useRef('');
  const emailRef = useRef('');
  const phoneNumberRef = useRef('');

  const handleInputChange = (ref, value) => {
    ref.current = value;
  };

  const submitLogin = async () => {
    const form = {
      username: usernameRef.current,
      password: passwordRef.current,
    };
    try {
      const response = await axios.post(`http://${SERVER_IPV4_ADDRESS}:${SERVER_PORT}/login`, form, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      await saveToken(response.data.auth_token);
      setIsLoggedIn(true);
    } catch (error) {
      if (error.response.status == 401) {
        Alert.alert('Login Failed', 'Incorrect username or password.');
        this.textInput.clear()
      }
      else console.error('Error during login:', error);
    }
  };

  const submitRegister = async () => {
    const form = {
      username: usernameRef.current,
      password: passwordRef.current,
      firstName: firstNameRef.current,
      lastName: lastNameRef.current,
      email: emailRef.current,
      phoneNumber: phoneNumberRef.current,
    };
    try {
      const response = await axios.post(`http://${SERVER_IPV4_ADDRESS}:${SERVER_PORT}/register`, form, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      await saveToken(response.data.auth_token);
      setIsLoggedIn(true)
    } catch (error) {
      console.error('Error during registration:', error);
    }
  };

  useEffect(() => {
    const testConnect = async () => {
      try {
        console.log(`network check: http://${SERVER_IPV4_ADDRESS}:${SERVER_PORT}/test`)
        const response = await axios.get(`http://${SERVER_IPV4_ADDRESS}:${SERVER_PORT}/test`);
        
        console.log(response.data); // {"response": "connection successful"}

      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err);
      }
    };

    testConnect();
  }, []);

  const FormComponent = () => (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.formContainer}>
        {isLogin ? (
          <View>
            <Text style={styles.title}>Login</Text>
            <TextInput
              style={styles.input}
              placeholder="Username"
              onChangeText={(text) => handleInputChange(usernameRef, text)}
              ref={input => {this.textInput = input}}
            />
            <TextInput
              style={styles.input}
              placeholder="Password"
              secureTextEntry
              onChangeText={(text) => handleInputChange(passwordRef, text)}
              ref={input => {this.textInput = input}}
            />
            <Button title="Submit" onPress={submitLogin} />
          </View>
        ) : (
          <View>
            <Text style={styles.title}>Sign Up</Text>
            <TextInput
              style={styles.input}
              placeholder="Username"
              onChangeText={(text) => handleInputChange(usernameRef, text)}
            />
            <TextInput
              style={styles.input}
              placeholder="Password"
              secureTextEntry
              onChangeText={(text) => handleInputChange(passwordRef, text)}
            />
            <TextInput
              style={styles.input}
              placeholder="First Name"
              onChangeText={(text) => handleInputChange(firstNameRef, text)}
            />
            <TextInput
              style={styles.input}
              placeholder="Last Name"
              onChangeText={(text) => handleInputChange(lastNameRef, text)}
            />
            <TextInput
              style={styles.input}
              placeholder="Email"
              onChangeText={(text) => handleInputChange(emailRef, text)}
            />
            <TextInput
              style={styles.input}
              placeholder="Phone Number"
              onChangeText={(text) => handleInputChange(phoneNumberRef, text)}
            />
            <Button title="Submit" onPress={submitRegister} />
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
    </ScrollView>
  );

  return (
    <View style={styles.outerContainer}>
      {error ? (
        <Text>Error: Network Connection</Text>
      ) : (
        <FormComponent/>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  outerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
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
