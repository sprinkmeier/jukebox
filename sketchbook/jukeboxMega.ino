// -*- Mode:c++ -*-

/**
 * Jukebox interface for Mega.
 */

#include <ctype.h>

boolean TEST_MODE = false;

// DIO pins are attached to buttons with certain labels
typedef struct
{
    unsigned char pin;
    char label;
} Button;

// define the buttons
Button buttons[] = {

//    { 7,'!'}, // brown
//    { 6,'@'},
    { 5,'A'},
    { 4,'B'},
    { 3,'L'},
    { 2,'M'}, // blue

    {14,'8'}, // grey
    {15,'7'},
    {16,'6'},
    {17,'5'},
    {18,'4'},
    {19,'3'},
    {20,'2'},
    {21,'1'},
    ///// +5V // orange
 //   {22,'\0'},
 //   {24,' \0'}, // brown

    ////// +5V brown
    {23,'C'}, //red
    {25,'D'},
    {27,'E'},
    {29,'F'},
    {31,'G'},
    {33,'H'},
    {35,'J'},
    {37,'K'}, // white

    {39,'N'},//brown
    {41,'P'},
    {43,'Q'},
    {45,'R'},
    {47,'S'},
    {49,'T'},
    {51,'U'},
    {53,'V'}, // grey
    ////// GND, white

    //// Pushbuttons
    //// GND blue
//    {50,'!'},//green
//    {42,'@'},
//    {34,'#'},
//    {26,'$'},//red


};

#define NUM_BUTTONS (sizeof(buttons) / sizeof(Button))

void setup()
{
    //start serial connection
    Serial.begin(9600);

    // All the buttons are tied-high inputs
    for (unsigned i = 0; i < NUM_BUTTONS; ++i)
    {
        pinMode(buttons[i].pin, INPUT);
        digitalWrite(buttons[i].pin, HIGH);
    }

    // The on-shield pushbuttons 'borrow' some DIO lines to use as ground
    pinMode     (46, OUTPUT);
    digitalWrite(46, LOW);

    pinMode     (38, OUTPUT);
    digitalWrite(38, LOW);

    pinMode     (30, OUTPUT);
    digitalWrite(30, LOW);
}

char getLetter()
{
    for (unsigned i = 0; i < NUM_BUTTONS; ++i)
    {
        if (digitalRead(buttons[i].pin)) continue;
        if (isdigit(buttons[i].label))   continue;
        if (!isupper(buttons[i].label))
        {
            Serial.println(buttons[i].label);
            delay(50);
            while (!digitalRead(buttons[i].pin));
            continue;
        }

        return buttons[i].label;
    }
    return '\0';
}

char getNumber()
{
    for (unsigned i = 0; i < NUM_BUTTONS; ++i)
    {
        if (digitalRead(buttons[i].pin)) continue;
        if (isupper(buttons[i].label))   continue;
        if (!isdigit(buttons[i].label))
        {
            Serial.println(buttons[i].label);
            delay(50);
            while (!digitalRead(buttons[i].pin));
            continue;
        }

        return buttons[i].label;
    }
    return '\0';
}

bool timeout(unsigned long line)
{
    // spin for at most 5 seconds on any givne line
    static unsigned      lastLine = 0;
    static unsigned long lastTime = 0;

    if (line == lastLine)
    {
        return (millis() - lastTime) > 5000;
    }
    lastLine = line;
    lastTime = millis();
    return false;
}

#define TIMEOUT  { if (timeout(__LINE__)) return; }

void loop()
{
    // test mode, just print out any/all pressed buttons
    while(TEST_MODE)
    {
      for (unsigned i = 0; i < NUM_BUTTONS; ++i)
      {
          if (digitalRead(buttons[i].pin)) continue;
          Serial.println(buttons[i].label);
      }
    }

    // reset the timeout line
    timeout(-1);

    // print out the current timestamp
    Serial.print  ('$');
    Serial.print  (millis());
    Serial.println('$');

    // wait until a letter is pressed
    char letter;
    while(!(letter = getLetter())) TIMEOUT;
    Serial.println(letter); // redundant?

    // now wait until a number is pressed
    char number;
    while(!(number = getNumber())) TIMEOUT;
    // print out "$LETTER $NUMBER\n"
    Serial.print(letter);
    Serial.print(' ');
    Serial.println(number);

}
