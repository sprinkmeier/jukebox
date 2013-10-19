// -*- Mode:c++ -*-

/**
 * Jukebox interface for Mega.
 */

#include <ctype.h>

boolean TEST_MODE = false;

/// Store the data about a button/GPIO pin
typedef struct
{
    /// Which GPIO pin is this button hooked up to
    unsigned char pin;
    /// which number/letter does this button represent
    char label;
} Button;

/// These are the buttons in use
Button buttons[] = {

    //{ 7,'!'}, // brown
    //{ 6,'@'},
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
    //{22,'\0'},
    //{24,' \0'}, // brown

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
    //{50,'!'},//green
    //{42,'@'},
    //{34,'#'},
    //{26,'$'},//red
};

/// how many buttons there are
#define NUM_BUTTONS (sizeof(buttons) / sizeof(Button))

void setup()
{
    // start serial connection
    Serial.begin(9600);

    // set up all the buttons for input with pullup enabled
    for (unsigned i = 0; i < NUM_BUTTONS; ++i)
    {
        const Button & btn(buttons[i]);
        pinMode     (btn.pin, INPUT_PULLUP);
    }

    // 3 of the remaining DIO lines are used as ground.
    // a cheat to make the wiring easier.
    pinMode     (46, OUTPUT);
    digitalWrite(46, LOW);

    pinMode     (38, OUTPUT);
    digitalWrite(38, LOW);

    pinMode     (30, OUTPUT);
    digitalWrite(30, LOW);
}

/// get a letter
char getLetter()
{
    // iterate through the buttons
    for (unsigned i = 0; i < NUM_BUTTONS; ++i)
    {
        const Button & btn(buttons[i]);
        // if high (i.e. button not pressed), continue
        if (digitalRead(btn.pin)  ) continue;
        // if it's not what we want, continue
        if (isdigit    (btn.label)) continue;
        // not a number, not a letter. it's a special character.
        if (!isupper   (btn.label))
        {
            // don't print it out yet, the Pi doesn't know what to
            // do with it yet.
            // Serial.println(buttons[i].label);
            delay(50);
            while (!digitalRead(btn.pin));
            continue;
        }

        return btn.label;
    }
    return '\0';
}

/// get a number. SSDD
char getNumber()
{
    for (unsigned i = 0; i < NUM_BUTTONS; ++i)
    {
        const Button & btn(buttons[i]);
        if (digitalRead(btn.pin)  ) continue;
        if (isupper    (btn.label)) continue;
        if (!isdigit   (btn.label))
        {
            // Serial.println(buttons[i].label);
            delay(50);
            while (!digitalRead(btn.pin));
            continue;
        }

        return btn.label;
    }
    return '\0';
}

/// timeout function, makes sure we don't get stuck in one
/// place for too long.
bool timeout(unsigned long line)
{
    // where we are
    static unsigned      lastLine = 0;
    // when we got there
    static unsigned long lastTime = 0;

    // if we're still in the sae place as last time
    if (line == lastLine)
    {
        // return true if we've been her for more than 5 seconds
        return (millis() - lastTime) > 5000;
    }
    // record the new position and start time
    lastLine = line;
    lastTime = millis();
    return false;
}

// helper macro to implement the timeout
#define TIMEOUT  { if (timeout(__LINE__)) return; }

void loop()
{
    // if in test mode just keep printing out the buttons pushed
    while(TEST_MODE)
    {
        for (unsigned i = 0; i < NUM_BUTTONS; ++i)
        {
            const Button & btn(buttons[i]);
            if (digitalRead(btn.pin)) continue;
            Serial.println (btn.label);
        }
    }

    // reset the timeout
    timeout(-1);

    // print out the time
    Serial.print  ('$');
    Serial.print  (millis());
    Serial.println('&');

    char letter;

    // wait for a limited time for a letter
    while(!(letter = getLetter())) TIMEOUT;
    Serial.println(letter);

    char number;

    // wait for a limited time for a number
    while(!(number = getNumber())) TIMEOUT;
    // now print out the letter-space-number sequence
    Serial.print(letter);
    Serial.print(' ');
    Serial.println(number);

    // wait for the buttons to be released
    while(getLetter() || getNumber());// TIMEOUT;
}
