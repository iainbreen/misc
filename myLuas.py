import urllib2
import json

API_BASE="https://data.dublinked.ie/cgi-bin/rtpi/"

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.8a9b3196-0ecf-4e91-a11c-c0f652f223f4"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "GetTimes":
        return get_train_times(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "MyLuas - Thanks"
    speech_output = "Thank you for using the MyLuas skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "MyLUAS"
    speech_output = "Welcome to the Alexa MyLuas times skill. " \
                    "You can ask me for tram times from any station."
    reprompt_text = "Please ask me for trains times from a station, " \
                    "for example Heuston."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_train_times(intent):
    session_attributes = {}
    card_title = "MyLuas Departures"
    speech_output = "I'm not sure which station you wanted train times for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which station you wanted train times for. " \
                    "Try asking about Abbey Street or The Point for example."
    should_end_session = False

    if "Stop" in intent["slots"]:
        station_name = intent["slots"]["Stop"]["value"]
        station_code = get_station_code(station_name.lower())

        if (station_code != "unkn"):
            card_title = "MyLuas Departures from " + station_name.title()

            print API_BASE + "realtimebusinformation?stopid=" + station_code + "&format=json"
            
            response = urllib2.urlopen(API_BASE + "realtimebusinformation?stopid=" + station_code + "&format=json")
            station_departures = json.load(response)   

            speech_output = "Tram departures from " + station_name + " are as follows. "
            for tram in station_departures["results"]:
                speech_output += tram["direction"] + " towards " + get_tram["destination"][5:] + ": " ;
                if tram["departureduetime"] == "Due":
                	speech_output += "Due now: "
                elif tram["departureduetime"] == "1":
                    speech_output += "Departing in one minute. "
                else:
                    speech_output += "Departing in " + tram["departureduetime"] + " minutes. "

            reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_station_code(station_name):
    return {
		"blackhorse": "LUAS9",
		"bluebell": "LUAS8",
		"kylemore": "LUAS7",
		"red cow": "LUAS6",
		"the point": "LUAS57",
		"spencer dock": "LUAS56",
		"mayor square": "LUAS55",
		"george's dock": "LUAS54",
		"saggart": "LUAS53",
		"fortunestown": "LUAS52",
		"citywest": "LUAS51",
		"cheeverstown": "LUAS50",
		"kingswood": "LUAS5",
		"fettercairn": "LUAS49",
		"belgard": "LUAS4",
		"cookstown": "LUAS3",
		"connolly": "LUAS23",
		"busaras": "LUAS22",
		"abbey street": "LUAS21",
		"jervis": "LUAS20",
		"hospital": "LUAS2",
		"four courts": "LUAS19",
		"smithfield": "LUAS18",
		"museum": "LUAS17",
		"heuston": "LUAS16",
		"james's": "LUAS15",
		"fatima": "LUAS14",
		"rialto": "LUAS13",
		"suir road": "LUAS12",
		"goldenbridge": "LUAS11",
		"drimnagh": "LUAS10",
		"tallaght": "LUAS1",
		"st. stephen's green": "LUAS24",
		"harcourt": "LUAS25",
		"charlemont": "LUAS26",
		"ranelagh": "LUAS27",
		"beechwood": "LUAS28",
		"cowper": "LUAS29",
		"milltown": "LUAS30",
		"windy arbour": "LUAS31",
		"dundrum": "LUAS32",
		"balally": "LUAS33",
		"kilmacud": "LUAS34",
		"stillorgan": "LUAS35",
		"sandyford": "LUAS36",
		"central park": "LUAS37",
		"glencairn": "LUAS38",
		"the gallops": "LUAS39",
		"leopardstown valley": "LUAS40",
		"ballyogan wood": "LUAS42",
		"carrickmines": "LUAS44",
		"laughanstown": "LUAS46",
		"cherrywood": "LUAS47",
		"bride's glen": "LUAS48",
    }.get(station_name, "unkn")

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }