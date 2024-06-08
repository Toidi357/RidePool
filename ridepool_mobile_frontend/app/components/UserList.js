// UserList.js
import React, { useState, useEffect } from 'react';
import { ScrollView, Text, StyleSheet, View } from 'react-native';
import { Card, Paragraph, Button } from 'react-native-paper';
import { sendAuthorizedPostRequest, sendAuthorizedGetRequest } from "../components/sendRequest"

const UserCard = ({ user, requesters = [], rideId }) => {
    const [accepted, setAccepted] = useState(false);

    const acceptRequester = async (requesterId, rideId) => {
        try {
            await sendAuthorizedPostRequest(`/rides/${rideId}/accept_requester/${requesterId}`);
            setAccepted(true);
        } catch (err) {
            console.error('Failed to accept requester: ', err);
        }
    }

    const isRequester = requesters.some(requester => requester.userId === user.userId);
    return (
        <Card style={styles.card}>
            <Card.Content>

                <Text style={styles.userName}>{user.firstName} {user.lastName}</Text>
                <Paragraph style={styles.userRating}>Username: {user.username}</Paragraph>
                <Paragraph style={styles.userRating}>Rating: {user.averageRating}</Paragraph>
                <Paragraph style={styles.userRating}>Phone Number: {user.phoneNumber}</Paragraph>
                {isRequester && (
                    <View style={styles.buttonContainer}>
                        {(!accepted) ? (
                            <Button mode="contained" onPress={() => acceptRequester(user.userId, rideId)}>Accept</Button>
                        ) : (
                            <Button mode="contained" disabled style={styles.disabledButton}>Accepted</Button>
                        )}
                    </View>
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
    buttonContainer: {
        flexDirection: 'row',
        justifyContent: 'flex-end',
        marginTop: 10,
      },
});

export default UserList;
