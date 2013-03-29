// -*- Mode:c++ -*-
/**
 * Jukebox interface
 */


// Pins 2 to 7 strobe the rows
// ping 8 to 12 srobe the columnsk
// if D2 os connected to D12
const char * button[] = { "1234*",
                          "5678#",
                          "ABCDE",
                          "FGHJK",
                          "LMNPQ",
                          "RSTUV"};

#define BAUD 9600
#define RLY  13
void setup()
{
    Serial.begin(BAUD);

    // row: tied high
    for (unsigned pin = 8; pin <= 12 ; pin++)
    {
        pinMode(pin, INPUT);
        digitalWrite(pin, HIGH);
    }

    // column: high-impedance
    for (unsigned pin = 2; pin <= 7 ; pin++)
    {
        pinMode(pin, INPUT);
        digitalWrite(pin, LOW);
    }

    pinMode(RLY, OUTPUT);
}

char scanRow(unsigned row)
{
    char ret = '\0';
    // strobe the row LOW
    pinMode(row, OUTPUT);
    digitalWrite(row, LOW);
    // wait a ludicrously long time for things to settle down
    delay(10);

    for (unsigned col = 8; col <= 12 ; ++col)
    {
        // sense the button state
        if (digitalRead(col) == LOW)
        {
            ret = button[row-2][col-8];
            break;
        }
    }
    pinMode(row, INPUT);
    digitalWrite(row, LOW);

    return ret;
}

char scanRows(unsigned first, unsigned last)
{
    for (unsigned row = first; row <= last; ++row)
    {
        char ret = scanRow(row);
        if (ret)
        {
            return ret;
        }
    }
    return '\0';
}

char getNumber()
{
    return scanRows(2,3);
}

char getLetter()
{
    return scanRows(4,7);
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
    while(scanRows(2, 7));
    digitalWrite(RLY, LOW);

    timeout(-1);
    char letter;
    char number;

    Serial.print('$');
    Serial.print(millis());
    Serial.println('$');

    while(!(letter = getLetter())) TIMEOUT;
    Serial.println(letter);

    digitalWrite(RLY, HIGH);

    while(!(number = getNumber())) TIMEOUT;
    Serial.print(letter);
    Serial.print(' ');
    Serial.println(number);
}
