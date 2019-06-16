// See https://github.com/dialogflow/dialogflow-fulfillment-nodejs
// for Dialogflow fulfillment library docs, samples, and to report issues
'use strict';
var counter = 0;
const fallback_count = 1; //on 2nd fail will prompt to contact poc
const functions = require('firebase-functions');
const {WebhookClient} = require('dialogflow-fulfillment');
const {Card, Suggestion,Payload} = require('dialogflow-fulfillment');

process.env.DEBUG = 'dialogflow:debug'; // enables lib debugging statements
 
exports.dialogflowFirebaseFulfillment = functions.https.onRequest((request, response) => {
  const agent = new WebhookClient({ request, response });
  console.log('Dialogflow Request headers: ' + JSON.stringify(request.headers));
  console.log('Dialogflow Request body: ' + JSON.stringify(request.body));
  
  function welcome(agent) {
    
    agent.add(`Welcome to the freshman chatbot! My name is Lyona`);
    agent.add(`How may I help you today?`);
    
    //agent.end(`Lyona is busy today. You would have to wait until Monday for someone to fix this. Meanwhile, Cheers and don't overwork yourself!`);
  }
  
  function fallback(agent) {
    if (counter == fallback_count) {
      	var today = new Date();
    	var hour = today.getHours()+today.getMinutes()/60 +8 /*Singapore GMT offset*/;
        //someone help me implement date check for sat and sun
  		if (hour > 8.5 && hour < 17.5) {// trigger to working hour
          agent.setFollowupEvent('staffPLSWorkHour');
        }
    	else { //trigger to non working hour
          agent.setFollowupEvent('staffPLSNonWorkHour');
        }
    	
        counter = 0;
    }
    else {
      agent.add(`I'm sorry, I didn't understand what you said. Could you rephrase the question again for me please?`);
      counter++;
    }
  }
  function hallGenInfoFlow(agent) {
  	switch (agent.parameters.Neptune) {
      case 'Application': agent.setFollowupEvent('hallapp');break;
      case 'Amenities': agent.setFollowupEvent('hallamenities');break;
      case 'Price': agent.setFollowupEvent('hallprice');break;
    }
  }
 function TR(agent) {
   const p = agent.parameters.NTU_location;
   const n = agent.intent.length ;
   if (p == "LHS" || p =="LHN") {
     if (isNaN(agent.intent[n-2])){
     	agent.setFollowupEvent(`${p}`+`TR`+`${agent.intent[n-1]}`); //take the last digit
    	}
   	 else if (!isNaN(agent.intent[n-2])){
        agent.setFollowupEvent(`${p}`+`TR`+`${agent.intent.slice(n-2)}`); //take last 2 digits
    	}
  	}
  }
  
  function eatery(agent) {
    switch (agent.parameters.NTU_Eatery) {
      case 'Starbucks': agent.setContext('FreshmenLifestyleFoodSnacksAndDrinks-followup');
        				agent.setFollowupEvent('Starbucks');break;
      case 'Bakery Cuisine': agent.setContext('FreshmenLifestyleFoodSnacksAndDrinks-followup');
        				agent.setFollowupEvent('BakeryCuisine');break;
      case 'Co-Op@NTU Cafe': agent.setContext('FreshmenLifestyleFoodSnacksAndDrinks-followup');
        				agent.setFollowupEvent('CoOpCafe');break;
      case 'Coffee Bean': agent.setContext('FreshmenLifestyleFoodSnacksAndDrinks-followup');
        				agent.setFollowupEvent('CoffeeBean');break;
      case 'Each-A-Cup': agent.setContext('FreshmenLifestyleFoodSnacksAndDrinks-followup');
        				agent.setFollowupEvent('EachACup');break;
      case 'LiHo': agent.setContext('FreshmenLifestyleFoodSnacksAndDrinks-followup');
        				agent.setFollowupEvent('LiHo');break;
      case 'MrBean': agent.setContext('FreshmenLifestyleFoodSnacksAndDrinks-followup');
        				agent.setFollowupEvent('MrBean');break;
      
      //case 'Eatery':agent.add('where do you want to eat');break;
    }
  	switch (agent.parameters.NTU_Canteen) {
      case "Can 1": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("Can1");break;
      case "Can 2": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("Can2");break;
      case "Can 9": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("Can9");break;
      case "Can 11": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("Can11");break;
      case "Can 13": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("Can13");break;
      case "Can 14": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("Can14");break;
      case "Can 16": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("Can16");break;
      case "Crespion Canteen": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("Crespion");break;
      case "Koufu": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("Koufu");break;
      case "North Hill Canteen": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("NorthHill");break;
      case "Northspine": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("Northspine");break;
      case "Tamarind": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("Tamarind");break;
      case "Quad": agent.setContext("FreshmenLifestyleFoodCanteen-followup");
        			agent.setFollowupEvent("Quad");break;
    }
  }
  // Run the proper function handler based on the matched Dialogflow intent name
  let intentMap = new Map();
  intentMap.set('Default Fallback Intent', fallback);
  //intentMap.set('Default Welcome Intent', welcome);
  var list = [];  var j = 2;  while (j<57) {list.push(j);j++;}
  for (var i = 0; i < list.length; i++) {
      intentMap.set(`Freshmen.Facts.Lifestyle.Location.TR-${list[i]}`,TR);
  }
  
  intentMap.set('Freshmen.AccommodationAndTransport.Hall.GeneralInfo',hallGenInfoFlow);
  intentMap.set('Freshmen.Lifestyle.Food',eatery);
  // intentMap.set('your intent name here', yourFunctionHandler);
  // intentMap.set('your intent name here', googleAssistantHandler);
  agent.handleRequest(intentMap);
});
// // Sample Code from Google
  // // Uncomment and edit to make your own intent handler
  // // uncomment `intentMap.set('your intent name here', yourFunctionHandler);`
  // // below to get this function to be run when a Dialogflow intent is matched
  // function yourFunctionHandler(agent) {
  //   agent.add(`This message is from Dialogflow's Cloud Functions for Firebase editor!`);
  //   agent.add(new Card({
  //       title: `Title: this is a card title`,
  //       imageUrl: 'https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png',
  //       text: `This is the body text of a card.  You can even use line\n  breaks and emoji! 💁`,
  //       buttonText: 'This is a button',
  //       buttonUrl: 'https://assistant.google.com/'
  //     })
  //   );
  //   agent.add(new Suggestion(`Quick Reply`));
  //   agent.add(new Suggestion(`Suggestion`));
  //   agent.setContext({ name: 'weather', lifespan: 2, parameters: { city: 'Rome' }});
  // }

  // // Uncomment and edit to make your own Google Assistant intent handler
  // // uncomment `intentMap.set('your intent name here', googleAssistantHandler);`
  // // below to get this function to be run when a Dialogflow intent is matched
  // function googleAssistantHandler(agent) {
  //   let conv = agent.conv(); // Get Actions on Google library conv instance
  //   conv.ask('Hello from the Actions on Google client library!') // Use Actions on Google library
  //   agent.add(conv); // Add Actions on Google library responses to your agent's response
  // }
  // // See https://github.com/dialogflow/dialogflow-fulfillment-nodejs/tree/master/samples/actions-on-google
  // // for a complete Dialogflow fulfillment library Actions on Google client library v2 integration sample
