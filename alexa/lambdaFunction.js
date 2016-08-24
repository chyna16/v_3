/**
 Copyright 2014-2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.

 Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at
  http://aws.amazon.com/apache2.0/

  To setup the skill loosely follow this toutorial https://developer.amazon.com/public/community/post/Tx2YNDI2WP6O21S/New-Alexa-Skills-Kit-Template-Step-by-Step-Guide-to-Build-a-Flash-Cards-Skill
*/

'use strict';

// Route the incoming request based on type (LaunchRequest, IntentRequest,
// etc.) The JSON body of the request is provided in the event parameter.
exports.handler = function (event, context) {
    try {
        console.log("event.session.application.applicationId=" + event.session.application.applicationId);

        /**
         * Uncomment this if statement and populate with your skill's application ID to
         * prevent someone else from configuring a skill that sends requests to this function.
         */

//     if (event.session.application.applicationId !== "amzn1.echo-sdk-ams.app.05aecccb3-1461-48fb-a008-822ddrt6b516") {
//         context.fail("Invalid Application ID");
//      }

        if (event.session.new) {
            onSessionStarted({requestId: event.request.requestId}, event.session);
        }

        if (event.request.type === "LaunchRequest") {
            onLaunch(event.request,
                event.session,
                function callback(sessionAttributes, speechletResponse) {
                    context.succeed(buildResponse(sessionAttributes, speechletResponse));
                });
        } else if (event.request.type === "IntentRequest") {
            onIntent(event.request,
                event.session,
                function callback(sessionAttributes, speechletResponse) {
                    context.succeed(buildResponse(sessionAttributes, speechletResponse));
                });
        } else if (event.request.type === "SessionEndedRequest") {
            onSessionEnded(event.request, event.session);
            context.succeed();
        }
    } catch (e) {
        context.fail("Exception: " + e);
    }
};

/**
 * Called when the session starts.
 */
function onSessionStarted(sessionStartedRequest, session) {
    console.log("onSessionStarted requestId=" + sessionStartedRequest.requestId
        + ", sessionId=" + session.sessionId);

    // add any session init logic here
}

/**
 * Called when the user invokes the skill without specifying what they want.
 */
function onLaunch(launchRequest, session, callback) {
    console.log("onLaunch requestId=" + launchRequest.requestId
        + ", sessionId=" + session.sessionId);

    getWelcomeResponse(callback);
}

/**
 * Called when the user specifies an intent for this skill.
 */
function onIntent(intentRequest, session, callback) {
    console.log("onIntent requestId=" + intentRequest.requestId
        + ", sessionId=" + session.sessionId);

    var intent = intentRequest.intent,
        intentName = intentRequest.intent.name;

    // handle yes/no intent after the user has been prompted
    if (session.attributes && session.attributes.userPromptedToContinue) {
        delete session.attributes.userPromptedToContinue;
        if ("AMAZON.NoIntent" === intentName) {
            handleFinishSessionRequest(intent, session, callback);
        } else if ("AMAZON.YesIntent" === intentName) {
            handleRepeatRequest(intent, session, callback);
        }
    }

    // dispatch custom intents to handlers here
    if ("RepoIntent" === intentName) {
        handleRepoRequest(intent, session, callback);
    } else if ("AnalysisIntent" === intentName) {
        handleAnalysisRequest(intent, session, callback);
    } else if ("DateIntent" === intentName) {
        handleDateRequest(intent, session, callback);
    } else if ("AMAZON.YesIntent" === intentName) {
        getWelcomeResponse(callback);
    } else if ("AMAZON.NoIntent" === intentName) {
        handleFinishSessionRequest(intent, session, callback);
    } else if ("AMAZON.StartOverIntent" === intentName) {
        getWelcomeResponse(callback);
    } else if ("AMAZON.RepeatIntent" === intentName) {
        handleRepeatRequest(intent, session, callback);
    } else if ("AMAZON.HelpIntent" === intentName) {
        handleGetHelpRequest(intent, session, callback);
    } else if ("AMAZON.StopIntent" === intentName) {
        handleFinishSessionRequest(intent, session, callback);
    } else if ("AMAZON.CancelIntent" === intentName) {
        handleFinishSessionRequest(intent, session, callback);
    }
}

/**
 * Called when the user ends the session.
 * Is not called when the skill returns shouldEndSession=true.
 */
function onSessionEnded(sessionEndedRequest, session) {
    console.log("onSessionEnded requestId=" + sessionEndedRequest.requestId
        + ", sessionId=" + session.sessionId);

    // Add any cleanup logic here
}

// ------- Skill specific business logic -------

function getWelcomeResponse(callback) {
    var sessionAttributes = {},
        speechOutput = "Welcome to the future of project management. What project would you like me to tell you about?",
        shouldEndSession = false,
        repromptText = 'Project, please.'

    sessionAttributes = {
        "speechOutput": speechOutput,
        "repromptText": repromptText,
        "selectedRepo": 'NULL',
        "analysis": 'NULL'
    };
    callback(sessionAttributes,
        buildSpeechletResponse(speechOutput, repromptText, shouldEndSession));
}

var http = require('http');

function handleRepoRequest(intent, session, callback) {
  var speechOutput = "";
  var sessionAttributes = {};

  // This is what resopitory alexa heard you say.
  var verbalrepo = intent.slots.repo.value.toLowerCase();

  // V3 Api url
  var url = "http://ec2-52-7-214-244.compute-1.amazonaws.com/api/v1/data";

  // alexa compatable nicknames and their corresponding names
  // add additional values to add repos, keys should match LIST_OF_REPOS
  var repos = {
    'version visualizer': 'v3',
    'ark user interface': 'arc-ui',
    'crab apple': 'crabapple'
  };

  // check for what alexa heard against valid nicknames
  if (verbalrepo in repos) {
    // if found that means we have successfully selected a project
    var selrepo = repos[verbalrepo];

    // make v3 api call
    http.get(url, (res) => {
        res.setEncoding('utf8');
         res.on('data', function(chunk){
            // parse JSON response
            var returnData = JSON.parse(chunk);

            // Check if selected repo has an existing analysis
            if (selrepo in returnData['available-analysis']){
              // if found populate session attributes
              var fromDT = returnData['available-analysis'][selrepo][0]['from'],
                  toDT = returnData['available-analysis'][selrepo][0]['to'];
              sessionAttributes = {
                'speechOutput': 'An analysis exists for ' + verbalrepo + ', from ' + fromDT + ', to ' + toDT +'.',
                'repromptText': 'Tell me what analysis you would like.',
                'selectedRepo': selrepo,
                'from-date': fromDT,
                'to-date': toDT,
                'availableDates': returnData['available-analysis'][selrepo],
                'chosenDates': 0,
                'available': true
              };
            } else {
              // assign failure attributes and prompt user to continue
              sessionAttributes = {
                'speechOutput': 'The repository ' + verbalrepo + ' is not available. Would you like to try a different project?',
                'repromptText': 'Tell me what analysis you would like.',
                'available': false,
                'userPromptedToContinue': true
              };
            }
            callback(sessionAttributes,
                buildSpeechletResponse(sessionAttributes.speechOutput, sessionAttributes.repromptText, false));
        });
    }).on('error', (e) => {
      callback(sessionAttributes,
          buildSpeechletResponse('Code Metrics server error, sorry.', '', true));
    });

} else {
    sessionAttributes = {
      'speechOutput': 'The repository ' + verbalrepo + ' is not available. Would you like to try a different project?',
      'repromptText': 'Tell me what analysis you would like.',
      'available': false,
      'userPromptedToContinue': true
    };
    callback(sessionAttributes,
        buildSpeechletResponse(sessionAttributes.speechOutput, sessionAttributes.repromptText, false));
  }
}

// function calls v3 api to get specific analysis data
function handleAnalysisRequest(intent, session, callback) {
  var analysis = intent.slots.analysis.value,
      repo = session.attributes.selectedRepo,
      fromDT = session.attributes['from-date'],
      toDT = session.attributes['to-date'],
      sessionAttributes = {};

  // assemble api call url
  var url = "http://ec2-52-7-214-244.compute-1.amazonaws.com/api/v1/data/"
            + repo + '&' + analysis + '&' + fromDT + '&' + toDT;
  // make api call
  http.get(url, (res) => {
    res.setEncoding('utf8');
     res.on('data', function(chunk){
        var returnData = JSON.parse(chunk);
        sessionAttributes = {
          'speechOutput': 'Something is wrong.',
          'repromptText': 'Try doing something else.',
          'selectedRepo': repo,
          'from-date': fromDT,
          'to-date': toDT,
          'availableDates': session.attributes.availableDates,
          'chosenDates': 0,
          'available': true
        };

        // process the data and update the session attributes as depending on analysis
        if (analysis === 'summary') {
          sessionAttributes = summaryHelper(returnData, sessionAttributes);
        } else if (analysis === 'coupling') {
          sessionAttributes = couplingHelper(returnData, sessionAttributes);
        } else if (analysis === 'lines') {
          sessionAttributes = linesHelper(returnData, sessionAttributes);
        } else {
          sessionAttributes.speechOutput = 'I interpreted that as, ' + analysis + ', which does not seem to be valid. Could you, please, repeat yourself?'
          sessionAttributes.repromptText = 'I had a senior moment. Could you repeat yourself?'
        }
        callback(sessionAttributes,
            buildSpeechletResponse(sessionAttributes.speechOutput, sessionAttributes.repromptText, false));
    });
  }).on('error', (e) => {
    callback(sessionAttributes,
        buildSpeechletResponse('Code Metrics server error, sorry.', '', true));
  });
}

function handleDateRequest(intent, session, callback) {
  var sessionAttributes = session.attributes;

  // handle switching between analysis date ranges
  if (sessionAttributes.availableDates.length === 1) {
    sessionAttributes.speechOutput = 'There is only one analysis. With range '
  } else if (sessionAttributes.availableDates.length <= (sessionAttributes.chosenDates + 1)) {
    sessionAttributes.speechOutput = 'You have gone through all of the available analysis. Here is the first range ';
    sessionAttributes.chosenDates = 0;
  } else {
    sessionAttributes.speechOutput = 'The next date range is ';
    sessionAttributes.chosenDates += 1;
  }

  //update sessionAttributes and append to speechOutput
  var dates = sessionAttributes.availableDates[sessionAttributes.chosenDates];
  sessionAttributes['from-date'] = dates['from'];
  sessionAttributes['to-date'] = dates['to'];
  sessionAttributes.speechOutput += dates['from'] + ' to ' + dates['to'];

  callback(sessionAttributes,
      buildSpeechletResponse(sessionAttributes.speechOutput, sessionAttributes.repromptText, false));
}

function handleRepeatRequest(intent, session, callback) {
    // Repeat the previous speechOutput and repromptText from the session attributes if available
    // else start a new game session
    if (!session.attributes || !session.attributes.speechOutput) {
        getWelcomeResponse(callback);
    } else {
        callback(session.attributes,
            buildSpeechletResponse(session.attributes.speechOutput, session.attributes.repromptText, false));
    }
}

function handleGetHelpRequest(intent, session, callback) {
    var speechOutput = "Are you lost? Well, I have not been programmed to help. So, Goodbye!",
        repromptText = "";
        var shouldEndSession = true;
    callback(session.attributes,
        buildSpeechletResponse(speechOutput, repromptText, shouldEndSession));
}

function handleFinishSessionRequest(intent, session, callback) {
    // End the session with a custom closing statment when the user wants to quit the game
    callback(session.attributes,
        buildSpeechletResponse("Thanks for using code metrics!", "", true));
}

function summaryHelper(returnData, attr) {
  // pulls number of commits and autors out of summary JSON
  var commits = returnData.data[0].value,
      authors = returnData.data[3].value;

  attr.speechOutput = 'There were ' + commits + ' commits made by ' + authors + ' authors, in the analysis period. Anything else?',
  attr.repromptText = 'Is there anything else you would like to talk about?';

  return attr;
}

function couplingHelper(returnData, attr) {
  // pulls number of coupled files and max degree of coupling out of JSON
  if (returnData.null) {
    attr.speechOutput = 'Congratulations! This project is free of coupling.';
  }
  else {
    var numCoupled = returnData.data.length,
        maxCouple = 0;

    returnData.data.forEach(function(element) {
        if (element.degree > maxCouple) {
          maxCouple = element.degree;
        }
    });
    attr.speechOutput = 'There are ' + numCoupled + ' instances of coupling. ' + maxCouple + ' percent is the highest degree.';
  }

  attr.repromptText = 'Is there anything else you would like to talk about?';
  return attr;
}

function linesHelper(returnData, attr) {
  // adds up the total number of lines of code from JSON
  // TODO BUGGY doesn't work with large repos.
  var total = 0,
      languages = {};

  returnData.data.forEach(function(file) {
    total += int(file.code);
    /* This populates a dictionary creating a by-language count of lines
    if (languages[file.language]) {
      languages[file.language] += file.code;
    } else {
      languages[file.language] = file.code;
    }
    */
  });

  attr.speechOutput = 'There are ' + total + ' lines of code.';
  attr.repromptText = 'Anything else?';
  return attr;
}

// ------- Helper functions to build responses -------


function buildSpeechletResponse(output, repromptText, shouldEndSession) {
    return {
        outputSpeech: {
            type: "PlainText",
            text: output
        },
        reprompt: {
            outputSpeech: {
                type: "PlainText",
                text: repromptText
            }
        },
        shouldEndSession: shouldEndSession
    };
}

function buildResponse(sessionAttributes, speechletResponse) {
    return {
        version: "1.0",
        sessionAttributes: sessionAttributes,
        response: speechletResponse
    };
}
