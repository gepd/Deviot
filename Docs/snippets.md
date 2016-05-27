##### Snippets

*Whether you are coding or writing the next vampire best-seller, you’re likely to need certain short fragments of text again and again. Use snippets to save yourself tedious typing. Snippets are smart templates that will insert text for you and adapt it to their context.* [Source](http://sublimetext.info/docs/en/extensibility/snippets.html)

| Trigger | Function |
|---------|----------|
|abs| abs()|
|analogRead|analogRead()|
|analogWrite|analogWrite()|
|attachInterrupt|attachInterrupt()|
|byte|byte()|
|char|char()|
|constrain|constrain()|
|define|define()|
|delay|delay()|
|delayMicroseconds|delayMicroseconds()|
|detachInterrupt|detachInterrupt()|
|digitalRead|digitalRead()|
|digitalRead|digitalRead()|
|digitalWrite|digitalWrite()|
|dowhile|do {} while():
|float|float()|
|for|for(int i=0; i<; i++){}|
|if|if(){}|
|ifdef|ifdef constant-expression|
|ifelse|if(){} else {}|
|ifndef|ifndef constant-expression|
|include (userlib)|include "lib.h"|
|include (syslib)|include <lib.h>|
|int|int()|
|long|long()|
|loop|void loop(){}|
|map|map()|
|max|max(x, y);|
|elif|elif constant-expression|
|micros|micros()|
|if|if constant-expression|
|millis|millis()|
|min|min(x, y)|
|noTone|noTone()|
|pinMode|pinMode()|
|pow|pow()|
|pulseIn|pulseIn(pin, value, timeout);|
|random|random(min, max);|
|randomSeed|randomSeed(seed);|
|savailable|if (Serial.available() > 0) {}|
|sbegin|Serial.begin(9600);|
|send|Serial.end();|
|sevent|void serialEvent(){}|
|sfind|Serial.find(target);|
|sfindUntil|Serial.findUntil(target, terminal);|
|sflush|Serial.flush();|
|sfloat|Serial.parseFloat();|
|spint|Serial.parseInt();|
|speek|Serial.peek();|
|sprint|Serial.print(val, format);|
|sread|Serial.read();|
|sreadbytes|Serial.readBytes(buffer, length);|
|sreadbytesUntil|Serial.readBytesUntil(character, buffer, length);|
|stimeout|Serial.setTimeout(time);|
|swrite|Serial.write(data);|
|setup|void setup(){}|
|shiftIn|shiftIn(dataPin, clockPin, bitOrder);|
|shiftOut|shiftOut(dataPin, clockPin, bitOrder, value);|
|sizeof|sizeof(variable);|
|sqrt|sqrt(x);|
|switch|switch () { case : break; case : break; default: }|
|tone|tone(pin, frequency, duration);|
|undef|undef constant-expression|
|while|while(){}|

#### How to write my own snippet(s)?

Follow [this guide ](http://sublimetext.info/docs/en/extensibility/snippets.html)

If you want to share your(s) snippet(s) with others Deviot users, please paste the `.sublime-snippet` file in `Deviot\snippets` folder and push a PR