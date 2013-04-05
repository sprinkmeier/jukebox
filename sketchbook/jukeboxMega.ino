// -*- Mode:c++ -*-

/**
 * Jukebox interface for Mega.
 */

#include <ctype.h>

typedef struct
{
    unsigned char pin;
    char label;
} Button;

Button buttons[] = {

    { 7,'!'}, // brown
    { 6,'@'},
    { 5,'#'},
    { 4,'$'},
    { 3,'%'},
    { 2,'^'}, // blue

    {14,'1'}, // grey
    {15,'2'},
    {16,'3'},
    {17,'4'},
    {18,'5'},
    {19,'6'},
    {20,'7'},
    {21,'8'},
    ///// +5V // orange
    {22,'0'},
    {24,'-'}, // brown

    ////// +5V brown
    {23,'Q'}, //red
    {25,'W'},
    {27,'E'},
    {29,'R'},
    {31,'T'},
    {33,'Y'},
    {35,'U'},
/////////  {37,'I'}, // white

    {39,'A'},//brown
    {41,'S'},
    {43,'D'},
    {45,'F'},
    {47,'G'},
    {49,'H'},
    {51,'J'},
    {53,'K'}, // grey
    ////// GND, white

    //// Pushbuttons
    //// GND blue
    {50,'Z'},//green
    {42,'X'},
    {34,'C'},
    {26,'V'},//red


};

#define NUM_BUTTONS (sizeof(buttons) / sizeof(Button))

void setup(){
    //start serial connection
    Serial.begin(9600);

    for (unsigned i = 0; i < NUM_BUTTONS; ++i)
    {
        pinMode(buttons[i].pin, INPUT);
        digitalWrite(buttons[i].pin, HIGH);
    }

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
    timeout(-1);

    Serial.print  ('$');
    Serial.print  (millis());
    Serial.println('$');

    char letter;

    while(!(letter = getLetter())) TIMEOUT;
    Serial.println(letter);

    char number;

    while(!(number = getNumber())) TIMEOUT;
    Serial.print(letter);
    Serial.print(' ');
    Serial.println(number);

}
