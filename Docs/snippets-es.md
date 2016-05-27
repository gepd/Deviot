##### Snippets

*Durante la redacción de muchos tipos de texto, es frecuente que se repitan algunos fragmentos. Las plantillas permiten ahorrar tiempo y esfuerzo en dicho caso..* [Source](http://sublimetext.info/docs/es/extensibility/snippets.html)

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

#### ¿Cómo escribir mis propias plantillas?

Sigue [esta guía](http://sublimetext.info/docs/es/extensibility/snippets.html)

Si quieres compartir tu(s) plantilla(s) con otros usuarios de Deviot, por favor pega el archivo `.sublime-snippet` en la carpeta `Deviot\snippets` y solicita una PR

If you want to share your(s) snippet(s) with others Deviot users, please paste the `.sublime-snippet` file in `Deviot\snippets` folder and push a PR