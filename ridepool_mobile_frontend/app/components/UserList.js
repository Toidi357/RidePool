// UserList.js
import React, { useState, useEffect } from 'react';
import { ScrollView, Text, StyleSheet } from 'react-native';
import { Card, Paragraph, Button } from 'react-native-paper';
import { sendAuthorizedPostRequest, sendAuthorizedGetRequest } from "../components/sendRequest"


const acceptRequester = async (requesterId, rideId) => {
    try {
        await sendAuthorizedPostRequest(`/rides/${rideId}/accept_requester/${requesterId}`);
    } catch (err) {
        console.error('Failed to accept requester: ', err);
    }
}

const UserCard = ({ user, requesters = [], rideId }) => {
    const isRequester = requesters.some(requester => requester.userId === user.userId);
    return (
        <Card style={styles.card}>
            <Card.Content>

                <Text style={styles.userName}>{user.firstName} {user.lastName}</Text>
                <Paragraph style={styles.userRating}>Username: {user.username}</Paragraph>
                <Paragraph style={styles.userRating}>Rating: {user.averageRating}</Paragraph>
                <Paragraph style={styles.userRating}>Phone Number: {user.phoneNumber}</Paragraph>
                {isRequester && (
                    <Card.Actions>
                        <Button mode="contained" onPress={() => acceptRequester(user.userId, rideId)}>Accept</Button>
                    </Card.Actions>
                )}
            </Card.Content>
        </Card>
    );
};

const UserList = ({ users, requesters = [], rideId }) => {
    return (
        <ScrollView style={styles.container}>
            {users.map((user, index) => (
                <UserCard key={`user-${index}`} user={user} requesters={requesters} rideId={rideId} />
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

export default UserList;
