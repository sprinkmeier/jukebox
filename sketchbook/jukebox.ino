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

void loop()
{
    char letter;
    char number;
    while(1)
    {
        while(!(letter = getLetter()));
        Serial.println(letter);

        while(!(number = getNumber()));
        Serial.print(letter);
        Serial.print(' ');
        Serial.println(number);

        while(scanRows(2, 7));
        Serial.println("$");
    }
}
