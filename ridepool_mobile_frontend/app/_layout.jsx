import React, { useState, useEffect } from 'react';
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
import Gemini from '@/app/tabs/gemini_help';

import CreateRidepoolScreen from '@/app/inner_pages/create_ridepool'
import FilterRidepoolScreen from '@/app/inner_pages/filter_ridepool'

import { saveToken, fetchToken } from './components/token_funcs';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function MyRidepoolsStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="My Ridepools" component={MyRidepoolsScreen} />
      <Stack.Screen name="Create Ridepool" component={CreateRidepoolScreen} />
    </Stack.Navigator>

  )
}

function OverviewStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="Search for Ridepools" component={OverviewScreen} />
      <Stack.Screen name="Filter Ridepools" component={FilterRidepoolScreen} />
    </Stack.Navigator>
  )
}

function TabLayout() {
  const colorScheme = useColorScheme();
  const [token, setToken] = useState(null);

  const handleSaveToken = async (token) => {
    await saveToken(token);
  };

  const handleFetchToken = async () => {
    const storedToken = await fetchToken();
    setToken(storedToken);
  };


  if (!token) { // auto-login, and to login once we already have a token
    console.log("Not yet logged in! token is " + token)
    return <Login setToken={setToken} />
  }
  else {
  console.log("cool, logged in. token is " +token )

  handleSaveToken(token)
  return (
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
          } else if (route.name === 'tabs/gemini_help') {
            iconName = focused ? 'information-circle-outline' : 'information-circle-outline';
          }

          return <TabBarIcon name={iconName} color={color} />;
        },
        tabBarActiveTintColor: Colors[colorScheme ?? 'light'].tint,
        headerShown: false,
      })}
    >
      <Tab.Screen
        name="tabs/overview"
        component={OverviewStack}
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
      <Tab.Screen
        name="tabs/gemini_help"
        component={Gemini}
        options={{ title: 'Help by Gemini' }}
      />
    </Tab.Navigator>
  )
}
}

export default function App() { 
  return <TabLayout />;
}
