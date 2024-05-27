// LocationInput.js
import React, { useState, useRef } from 'react';
import { View, Text, FlatList, TouchableOpacity, TouchableWithoutFeedback, Keyboard } from 'react-native';
import { TextInput } from 'react-native-paper';
import axios from 'axios';

const LocationInput = ({ label, onLocationSelected }) => {
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

  const handleOutsidePress = () => {
    if (isFocused) {
        // console.log("NOT FOCUSED!")
      setIsFocused(false);
      setSuggestions([]);
      Keyboard.dismiss();
    }
  };

  return (
    <TouchableWithoutFeedback >
      <View>
        <TextInput
        onEndEditing={handleOutsidePress}
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
            <FlatList
              data={suggestions}
              keyExtractor={(item) => item.place_id.toString()}
              renderItem={({ item }) => (
                <TouchableOpacity
                  onPress={() => {
                    setQuery(item.display_name);
                    setSuggestions([]);
                    onLocationSelected(item);
                  }}
                >
                  <Text style={{ padding: 10 }}>{item.display_name}</Text>
                </TouchableOpacity>
              )}
              style={{ flexGrow: 0 }}
            />
          </View>
        )}
      </View>
    </TouchableWithoutFeedback>
  );
};

export default LocationInput;
