import React, { Component } from 'react';
import { StyleSheet, Button, KeyboardAvoidingView, Alert, Text, ScrollView, TextInput, View } from 'react-native';
import { StackNavigator } from 'react-navigation';

class App extends React.Component {

  state = {
    username: ''
  }

  handleUsername = (text) => {
    this.setState({ username: text})
  }


  render() {
    const { navigate } = this.props.navigation;
      return (
      <KeyboardAvoidingView
        style={styles.container}
        behavior="position"
        >
        <Text style={styles.namely}>Like.ly</Text>

        <ScrollView
          scrollEnabled={false}
          contentContainerStyle={styles.main}
        >
        <TextInput
          onSubmitEditing={this.handleEditComplete}
          style={styles.username}
          placeholder="Enter Instagram Username"
          autoCorrect={false}
          onChangeText = {this.handleUsername}
          onSubmitEditing={() => validate(this.state.username, this)}
          returnKeyType={"done"}
          caretHidden={false}
        />
        <Button style={styles.submitButton}
                  onPress={() => validate(this.state.username, this)}
                  title="SUBMIT"
                />
        <Text style={styles.disclaimer}> {"\n"} Name.ly currently only works for public Instagram accounts. We apologize for any inconvenience this might cause. </Text>
        </ScrollView>
        </KeyboardAvoidingView>
    );
  }
}

function validate(text, object) {
  const { navigate } = object.props.navigation;
  console.log(text);
  if  (text === ''){
    Alert.alert('Empty Field', 'Please enter a valid Instagram username')
  }
  // else {
  //   //This is where API call to our backend would be. We run the scraper, and get an http response if it was successful or not
  // }
  //}

  if (text === 'Chat' || text === 'Chat ') {
    navigate('Chat')
  }
}

class ChatScreen extends React.Component {
  render() {
    const { navigate } = this.props.navigation;
      return (
      <View>
        <Text>Chat with Lucy</Text>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    //justifyContent: 'center',
  },
  namely: {
    textAlign: 'center',
    color: 'blue',
    fontWeight: 'bold',
    fontSize: 30,
    marginTop: 150,
  },
  username: {
    marginTop: 275,
    textAlign: 'center',
  },
  submitButton: {
    color: '#007AFF',
    borderRadius: 2,
  },
  disclaimer: {
    textAlign: 'center',
    fontSize: 13,
  }
});


const SimpleApp = StackNavigator({
  Home: { screen: App, navigationOptions: { header: null }},
  Chat: { screen: ChatScreen, navigationOptions: { header: null }}},
);


export default SimpleApp;
