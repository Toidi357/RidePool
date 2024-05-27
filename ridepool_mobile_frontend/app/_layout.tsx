import React, { useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';

import { TabBarIcon } from '@/components/navigation/TabBarIcon';
import Login from '@/app/login';
import OverviewScreen from '@/app/tabs/overview';
import MyRidepoolsScreen from '@/app/tabs/my_ridepools';
import ProfileScreen from '@/app/tabs/profile';

import CreateRidepoolScreen from '@/app/inner_pages/create_ridepool'


const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function MyRidepoolsStack() {
  return(
    <Stack.Navigator>
      <Stack.Screen name="My Ridepools" component={MyRidepoolsScreen} />
      <Stack.Screen name="Create Ridepool" component={CreateRidepoolScreen} />
    </Stack.Navigator>

  )
}

function TabLayout() {
  const colorScheme = useColorScheme();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  return (
    <>
      {!isLoggedIn ? (
        <Login changeLogin={setIsLoggedIn}/>
      ) : (
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ color, focused }) => {
              let iconName;

              if (route.name === 'tabs/overview') {
                iconName = focused ? 'search' : 'search-outline';
              } else if (route.name === 'tabs/my_ridepools') {
                iconName = focused ? 'car' : 'car-outline';
              } else if (route.name === 'tabs/profile') {
                iconName = focused ? 'person' : 'person-outline';
              }

              return <TabBarIcon name={iconName} color={color} />;
            },
            tabBarActiveTintColor: Colors[colorScheme ?? 'light'].tint,
            headerShown: false,
          })}
        >
          <Tab.Screen
            name="tabs/overview"
            component={OverviewScreen}
            options={{ title: 'All Ridepools' }}
          />
          <Tab.Screen
            name="tabs/my_ridepools"
            component={MyRidepoolsStack}
            options={{ title: 'My Ridepools' }}
          />
          <Tab.Screen
            name="tabs/profile"
            component={ProfileScreen}
            options={{ title: 'Profile' }}
          />
        </Tab.Navigator>
      )}
    </>
  );
}

export default function App() {
  return <TabLayout />;
}
