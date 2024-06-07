// UserList.js
import React from 'react';
import { ScrollView, Text, StyleSheet } from 'react-native';
import { Card, Paragraph } from 'react-native-paper';

const UserCard = ({ user }) => {
    return (
        <Card style={styles.card}>
            <Card.Content>
                <Text style={styles.userName}>{user.firstName} {user.lastName}</Text>
                <Paragraph style={styles.userRating}>Rating: {user.averageRating}</Paragraph>
            </Card.Content>
        </Card>
    );
};

const UserList = ({ users }) => {
    return (
        <ScrollView style={styles.container}>
            {users.map((user, index) => (
                <UserCard key={`user-${index}`} user={user} />
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
