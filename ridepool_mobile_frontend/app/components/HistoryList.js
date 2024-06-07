// Assuming HistoryList is in a separate file like HistoryList.js
import React, { useState, useEffect, useCallback } from 'react';
import { ScrollView, View, Text, StyleSheet } from 'react-native';
import { Card, Paragraph, Button } from 'react-native-paper'; // if you use picker in your cards
import { Picker } from '@react-native-picker/picker'; // if rratings are handled within cards
import { fetchToken} from './token_funcs';
import { sendAuthorizedGetRequest } from "./sendRequest";


 

const HistoryCard = ({ user, onRatingChange, ratings, currentUser }) => {
    console.log('Current User ID:', currentUser, 'Type:', typeof currentUser);
    console.log('User ID:', user.userId, 'Type:', typeof user.userId);
    return (
        <Card style={styles.card}>
            <Card.Content>
                <Text style={styles.userName}>{user.firstName} {user.lastName}</Text>
                <Paragraph style={styles.userRating}>Username: {user.username}</Paragraph>
                {currentUser !== user.userId && (
                    <Picker
                        selectedValue={ratings[user.userId] === undefined ? null : ratings[user.userId]}
                        style={{ height: 50, width: 150 }}
                        onValueChange={(itemValue) => onRatingChange(user.userId, itemValue)}
    >
                    <Picker.Item label="Unrated" value={null} />
                    {[1, 2, 3, 4, 5].map(value => (
                        <Picker.Item key={value} label={`${value}`} value={value} />
                    ))}
                </Picker>
            )}
            </Card.Content>
        </Card>
    );
};

const HistoryList = ({ users, onRatingChange, ratings, currentUser }) => {
    return (
        <ScrollView style={styles.container}>
            {users.map(user => (
                <HistoryCard key={user.userId} user={user} onRatingChange={onRatingChange} ratings={ratings} currentUser={currentUser} />
            ))}
        </ScrollView>
    );
};



const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 10,
    },
    card: {
        marginBottom: 10,
    },
    userName: {
        fontSize: 18,
        fontWeight: 'bold',
    },
    userRating: {
        fontSize: 16,
    },
});

export default HistoryList;
