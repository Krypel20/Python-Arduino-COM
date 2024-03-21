#include "DHT.h"
#include "Arduino.h"
#include "RGBLed.h"
#include "string.h"

// Pin Definitions
#define RGBLED_PIN_B	7
#define RGBLED_PIN_G	6
#define RGBLED_PIN_R	5
#define DHT11_PIN 4
#define rgbLed_TYPE COMMON_ANODE
#define soundSensor A1
#define waterSensor A2

RGBLed rgbLed(RGBLED_PIN_R,RGBLED_PIN_G,RGBLED_PIN_B,rgbLed_TYPE); //RGB LED light
DHT dht; //temperature & humidity sensor

struct DataPair {
    String prefix;
    String data;
};

DataPair extractData(const String& receivedData)
{
  // Find first ':' in string that indicate end of PREFIX. Example data: ("PREFIX:*someData*")
  size_t pos = receivedData.indexOf(':');
  if (pos == NULL || pos == 0) {
      return {"",""}; // Could not find prefix or string is empty
  }
  String prefix = receivedData.substring(0, pos);
  String data = receivedData.substring(pos + 1);
  DataPair result = {prefix, data};
  return result;
}

void extractRGBdata(const String& input, int& R, int& G, int& B) {
    // Find positions of: 'R', 'G', 'B'
    int posR = input.indexOf('R');
    int posG = input.indexOf('G');
    int posB = input.indexOf('B');

    // Check if all components has been found
    if (posR == -1 || posG == -1 || posB == -1) {
        Serial.println("Nieprawidłowy format danych!");
        return;
    }

    R = input.substring(posR + 1, posG).toInt();
    G = input.substring(posG + 1, posB).toInt();
    B = input.substring(posB + 1).toInt();
}

void setup()
{
  Serial.begin(9600);
  while (!Serial);
  dht.setup(DHT11_PIN);
  Serial.println("Program start");
  rgbLed.setRGB(255, 255, 255);
  delay(1000);
  rgbLed.turnOff();
}

static int currentTemp = -999; // Inicjalizacja zmiennej przechowującej poprzednią temperaturę
static int currentHum = -999;  // Inicjalizacja zmiennej przechowującej poprzednią wilgotność
static int currentWaterLVL = -999;
static int currentSoundLVL = -999;
static int currentR = -1;
static int currentG = -1;     
static int currentB = -1; 
int R,G,B;
unsigned long previousMillis = 0;  // Zmienna przechowująca czas ostatniego odczytu

void loop()
{
  unsigned long currentMillis = millis();  // Aktualny czas
  //Pobranie informacji o wilgotnosci
  int wilgotnosc = dht.getHumidity();
  //Pobranie informacji o temperaturze
  int temperatura = dht.getTemperature();
  //Pobieranie informacji o natzezniu dzwieku
  int nowSoundLVL = analogRead(soundSensor);
  //Pobieranie informacji o poziomie wody
  int nowWaterLVL = analogRead(waterSensor);

  //Wysylanie danych
    //Wysłanie danych z czujnika DHT11
  if((currentTemp!=temperatura || currentHum!=wilgotnosc) )
  {
    currentTemp = temperatura;
    currentHum = wilgotnosc;
    if (dht.getStatusString() == "OK") {
      Serial.print("DHT11: ");
      Serial.print(wilgotnosc);
      Serial.print("%RH | ");
      Serial.print(temperatura);
      Serial.println("*C");
    }
  }

  //Wysłanie danych z czujnika natezenia dzwieku
  if(nowSoundLVL!=currentSoundLVL){
    Serial.print("SoundSensorLM393:");
    Serial.println(nowSoundLVL);
    currentSoundLVL = nowSoundLVL;
  }

  //Wysłanie danych z czujnika poziomu wody
  // if(nowWaterLVL!=currentWaterLVL){
  //   Serial.print("WaterLVL:");
  //   Serial.println(nowWaterLVL);
  //   currentWaterLVL = nowWaterLVL;
  // }

  //Odebranie danych
  if (Serial.available()>0) {
    String receivedData = Serial.readString();
    receivedData.trim();
    String data = extractData(receivedData).data;
    String prefix = extractData(receivedData).prefix;

    //Interpretacja danych
    if (prefix == "RGB LED"){
      extractRGBdata(data, R, G, B);

      if (R != currentR || G != currentG || B != currentB) {
        rgbLed.setRGB(R, G, B);
        Serial.print("Przekonwertowano dane RGB: ");
        Serial.println(data);
        // Zaktualizuj poprzednie wartości
        currentR = R;
        currentG = G;
        currentB = B;
      }
    }
  }
}