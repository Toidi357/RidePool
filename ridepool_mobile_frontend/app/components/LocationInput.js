import React, { useState, useRef } from 'react';
import { View, Text, ScrollView, TouchableOpacity, TouchableWithoutFeedback, Keyboard } from 'react-native';
import { TextInput } from 'react-native-paper';
import axios from 'axios';

// need default parameters or sum shi
const LocationInput = ({ label = "Location", onLocationSelected = () => {} } ) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef(null);

  const fetchSuggestions = async (text) => {
    if (text.length > 2) {
      const response = await axios.get(`https://nominatim.openstreetmap.org/search?format=json&countrycodes=us&q=${text}`);
      setSuggestions(response.data);
    } else {
      setSuggestions([]);
    }
  };


  const handleItemPress = (item) => {
    setQuery(item.display_name);
    setSuggestions([]);
    setIsFocused(false);
    onLocationSelected(item);
    Keyboard.dismiss();
  };

  return (
    <TouchableWithoutFeedback >
      <View>
        <TextInput
          
          label={label}
          value={query}
          onChangeText={(text) => {
            setQuery(text);
            fetchSuggestions(text);
          }}
          onFocus={() => setIsFocused(true)}
          ref={inputRef}
          style={{ marginBottom: 10 }}
        />
        {isFocused && suggestions.length > 0 && (
          <View style={{ maxHeight: 200 }}>
            <ScrollView style={{ flexGrow: 0 }} nestedScrollEnabled={true} >
              {suggestions.map((item) => (
                <TouchableOpacity
                  key={item.place_id}
                  onPress={() => handleItemPress(item)}
                >
                  <Text style={{ padding: 10 }}>{item.display_name}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}
      </View>
    </TouchableWithoutFeedback>
  );
};

export default LocationInput;
