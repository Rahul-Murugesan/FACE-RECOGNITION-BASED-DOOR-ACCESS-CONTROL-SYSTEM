#if defined(ESP32)
#include <WiFi.h>
#elif defined(ESP8266)
#include <ESP8266WiFi.h>
#endif

#include <Firebase_ESP_Client.h>

// Include token generation and helper functions
#include <addons/TokenHelper.h>
#include <addons/RTDBHelper.h>

// WiFi Credentials
#define WIFI_SSID "ROCKSTAR"         // Replace with your Wi-Fi SSID
#define WIFI_PASSWORD "1234567890" // Replace with your Wi-Fi Password

// Firebase Configuration
#define API_KEY "AIzaSyAZiwEWb7rEHtml1KqOV6iapEQ8Yorc2c8"                 // Replace with your Firebase API Key
#define DATABASE_URL "https://iotpro-ea2f4-default-rtdb.asia-southeast1.firebasedatabase.app/"     // Replace with your Firebase Database URL

// Firebase Objects
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// Variables for Firebase
bool signupOK = false;

// Relay Pin Configuration
#define RELAY_PIN1 4 // Pin for Relay 1
#define RELAY_PIN2 5 // Pin for Relay 2 (Adjust as needed)

// WiFi Connection Function
void connectToWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\nConnected to Wi-Fi");
}

// Function to Post Initial Data to Firebase
void postInitialData() {
  String initialPersonData = "No face detected";
  String initialConfidenceData = "0"; // Confidence is 0 when no face detected

  Firebase.RTDB.setString(&fbdo, "Face_Recognition/Person", initialPersonData);  // Post "No face detected"
  Firebase.RTDB.setString(&fbdo, "Face_Recognition/Confidence", initialConfidenceData);  // Post confidence 0

  Serial.println("Initial data posted to Firebase:");
  Serial.println("Person: No face detected, Confidence: 0");
}

// Setup Function
void setup() {
  Serial.begin(115200);

  // Initialize Relay Pins
  pinMode(RELAY_PIN1, OUTPUT);
  digitalWrite(RELAY_PIN1, LOW); // Ensure Relay 1 is off initially
  pinMode(RELAY_PIN2, OUTPUT);
  digitalWrite(RELAY_PIN2, LOW); // Ensure Relay 2 is off initially

  // Connect to WiFi
  connectToWiFi();

  // Firebase Initialization
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;

  // Firebase sign-up (optional for anonymous auth)
  if (Firebase.signUp(&config, &auth, "", "")) {
    signupOK = true;
    Serial.println("Firebase Sign-Up Successful");
  } else {
    Serial.printf("Sign-Up Error: %s\n", config.signer.signupError.message.c_str());
  }

  // Begin Firebase
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  // Post initial data to Firebase (Person: "No face detected", Confidence: 0)
  postInitialData();
}

void loop() {
  if (Firebase.ready() && signupOK) {
    // Fetch data for Relay 1 (Confidence)
    String databasePath1 = "Face_Recognition/Confidence";
    if (Firebase.RTDB.getString(&fbdo, databasePath1)) {
      if (fbdo.dataType() == "string") {
        String confidenceData = fbdo.stringData();
        Serial.println("Data fetched successfully for Relay 1:");
        Serial.println("Confidence: " + confidenceData);

        // Convert confidenceData to integer
        int confidence = confidenceData.toInt();

        // Control Relay 1 based on Confidence
        if (confidence > 80) {
          digitalWrite(RELAY_PIN1, HIGH); // Turn Relay 1 ON
          Serial.println("Relay 1 ON (Confidence > 80)");
        } else {
          digitalWrite(RELAY_PIN1, LOW); // Turn Relay 1 OFF
          Serial.println("Relay 1 OFF (Confidence <= 80)");
        }
      } else {
        Serial.println("Unexpected data type for Confidence");
      }
    } else {
      Serial.printf("Firebase Get Error for Confidence: %s\n", fbdo.errorReason().c_str());
    }

    // Fetch data for Relay 2 (Person Detection)
    String databasePath2 = "Face_Recognition/Person";
    if (Firebase.RTDB.getString(&fbdo, databasePath2)) {
      if (fbdo.dataType() == "string") {
        String personData = fbdo.stringData();
        Serial.println("Data fetched successfully for Person:");
        Serial.println("Person: " + personData);

        // Check if "No face detected" and control Relay 2
        if (personData == "No face detected") {
          digitalWrite(RELAY_PIN2, HIGH); // Turn Relay 2 OFF
          Serial.println("Relay 2 OFF (No face detected)");
        } else {
          digitalWrite(RELAY_PIN2, LOW); // Turn Relay 2 ON
          Serial.println("Relay 2 ON (Face detected: " + personData + ")");
        }
      } else {
        Serial.println("Unexpected data type for Person");
      }
    } else {
      Serial.printf("Firebase Get Error for Person: %s\n", fbdo.errorReason().c_str());
    }
  }

  delay(2000); // Fetch data every 2 seconds
}
