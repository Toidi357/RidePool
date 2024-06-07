// history_rides.jsx
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Button } from 'react-native';
import HistoryList from '../components/HistoryList';  // Assuming HistoryList is in the same directory
import { sendAuthorizedGetRequest, sendAuthorizedPostRequest } from "../components/sendRequest";
import { useNavigation } from '@react-navigation/native';

const HistoryRides = ({ route }) => {
    const { rideId } = route.params;
    const [users, setUsers] = useState([]);
    const [ratings, setRatings] = useState({});
    const [error, setError] = useState('');
    const [id, setId] = useState(null);
    const navigation = useNavigation();

    const fetchCurrentUser = async () => {
        try {
          const response = await sendAuthorizedGetRequest('/profile');
          console.log(response.data.userId);
          setId(response.data.userId);
        } catch (err) {
          console.error('Error fetching current user profile:', err);
          setError(err.toString());
        }
    
    }

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const response = await sendAuthorizedGetRequest(`/rides/${rideId}/members_to_rate`);
                setUsers(response.data); // Assuming the response data is directly usable
                const newRatings = {};
                response.data.forEach(user => {
                    newRatings[user.userId] = null;  // Initialize ratings to 3
                });
                setRatings(newRatings);
                fetchCurrentUser();
            } catch (err) {
                console.error('Failed to fetch users:', err);
                setError('Failed to fetch users');
            }
        };

        fetchUsers();
    }, [rideId]);

    const handleRatingChange = (userId, newRating) => {
        setRatings(prevRatings => ({
            ...prevRatings,
            [userId]: newRating
        }));
    };

   
    const submitRatings = async() => {
        console.log('Submitted Ratings:', ratings);
        try {
            const response = await sendAuthorizedPostRequest(`/rides/${rideId}/rate_members`, ratings);
            console.log(response)
            navigation.navigate('My Ridepools')
          } catch (err) {
            console.error('Error fetching data:', err);
          }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>History Ride Members</Text>
            {error ? <Text style={styles.error}>{error}</Text> : <HistoryList users={users} ratings={ratings} onRatingChange={handleRatingChange} currentUser={id}/>}
            <Button title="Submit Ratings" onPress={submitRatings} color="#6200EE" />
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

export default HistoryRides;
