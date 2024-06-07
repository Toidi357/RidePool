// ActiveRides.jsx
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import UserList from '../components/UserList';  // Assuming UserList is in the same directory
import { fetchToken } from '../components/token_funcs';
import { sendAuthorizedPostRequest, sendAuthorizedGetRequest } from "../components/sendRequest"

const ActiveRides = ({ route }) => {
    const { rideId } = route.params;
    const [users, setUsers] = useState([]);
    const [error, setError] = useState('');

    const handleFetchToken = async () => {
        return await fetchToken();
      };

    useEffect(() => {
        const fetchUsers = async () => {
            let token = await handleFetchToken();
            try {
                const response = await sendAuthorizedGetRequest(`/rides/${rideId}/members`);
                setUsers(response.data);  // Assuming the response is directly usable
            } catch (err) {
                console.error('Failed to fetch users:', err);
                setError('Failed to fetch users');
            }
        };

        fetchUsers();
    }, [rideId]);

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Active Ride Members</Text>
            {error ? <Text style={styles.error}>{error}</Text> : <UserList users={users} />}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 10,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 20,
    },
    error: {
        color: 'red',
        fontSize: 16,
        padding: 10,
    },
});

export default ActiveRides;
